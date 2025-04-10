#!/usr/bin/env python3

""" REST Server for grafana """

__author__    = "Mani Amoozadeh"
__version__   = "1.0"
__email__     = "mani.amoozadeh2@gmail.com"

import datetime
import logging
import socket

from flask import Flask
from flask import request, jsonify, make_response
from flask_compress import Compress

from uptime_betterstack import UPTIME_REST_API_Client

app = Flask(__name__)
compress = Compress(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log = logging.getLogger(__name__)

rest_obj = UPTIME_REST_API_Client(host="uptime.betterstack.com/api", api_ver="v2")


# Should respond with 200 OK.
# Used for "Test connection" on the datasource config page.
@app.route("/", methods=['POST', 'GET'])
def index():

    return jsonify({"message": "REST server is working"}), 200


@app.route("/response_time", methods=['GET'])
def get_uptime():

    start_time_dt = datetime.datetime.today()
    start_time_dt_tz = start_time_dt.astimezone()
    start_time_str = start_time_dt_tz.strftime('%Y-%m-%d %H:%M:%S %Z')
    log.info("Received query: %s", start_time_str)

    #########

    grafana_req = request.args.to_dict()

    nodename = grafana_req.get("nodename", None)
    hostname = socket.gethostname()
    if nodename != hostname:
        return jsonify([])

    range_from = grafana_req.get("range_from", None)
    range_to = grafana_req.get("range_to", None)
    url = grafana_req.get("url", None)
    req_region = grafana_req.get("region", "us,eu,as,au")

    #########

    status, output = rest_obj.get_monitor_id(url)
    if not status:
        error_message = {"error": output}
        return make_response(jsonify(error_message), 400)

    monitor_id = output

    #########

    status, output = rest_obj.get_response_times(monitor_id)
    if not status:
        error_message = {"error": output}
        return make_response(jsonify(error_message), 400)

    attributes = output.get("attributes", {})
    regions = attributes.get("regions", [])

    output_list = []

    for region_data in regions:

        region_name = region_data.get("region", "N/A")
        if region_name not in req_region:
            continue

        region_data_list = region_data.get("response_times", [])

        for entry in region_data_list:

            iso_timestamp = entry.get("at", None) # 2025-04-09T21:02:37.000Z
            dt = datetime.datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            unix_timestamp_ms = int(dt.timestamp() * 1000)

            output_list.append({
                "timestamp": unix_timestamp_ms,
                "region": region_name,
                "response_time": entry.get("response_time", None)
            })

            # "response_time": entry.get("response_time", None),
            # "name_lookup_time": entry.get("name_lookup_time", None),
            # "connection_time": entry.get("connection_time", None),
            # "tls_handshake_time": entry.get("tls_handshake_time", None),
            # "data_transfer_time": entry.get("data_transfer_time", None)

    return jsonify(output_list)


@app.route("/sla", methods=['GET'])
def get_sla():

    start_time_dt = datetime.datetime.today()
    start_time_dt_tz = start_time_dt.astimezone()
    start_time_str = start_time_dt_tz.strftime('%Y-%m-%d %H:%M:%S %Z')
    log.info("Received query: %s", start_time_str)

    #########

    grafana_req = request.args.to_dict()

    nodename = grafana_req.get("nodename", None)
    hostname = socket.gethostname()
    if nodename != hostname:
        return jsonify([])

    range_from = grafana_req.get("range_from", None)
    range_to = grafana_req.get("range_to", None)
    url = grafana_req.get("url", None)

    #########

    status, output = rest_obj.get_monitor_id(url)
    if not status:
        error_message = {"error": output}
        return make_response(jsonify(error_message), 400)

    monitor_id = output

    #########

    status, output = rest_obj.get_sla(monitor_id)
    if not status:
        error_message = {"error": output}
        return make_response(jsonify(error_message), 400)

    attributes = output.get("attributes", {})

    # "availability"
    # "total_downtime"
    # "number_of_incidents"
    # "longest_incident"
    # "average_incident"

    result = {
        "availability": attributes.get("availability", 0)
    }

    return jsonify(result)


if __name__ == '__main__':

    app.run(debug=False, threaded=True, host="0.0.0.0", port=5006)
