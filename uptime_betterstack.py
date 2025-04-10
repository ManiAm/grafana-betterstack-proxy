#!/usr/bin/env python3

__author__    = "Mani Amoozadeh"
__version__   = "1.0"
__email__     = "mani.amoozadeh2@gmail.com"

# https://betterstack.com/docs/uptime/api/getting-started-with-uptime-api/

import os
import sys
import getpass
import json
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log = logging.getLogger(__name__)


class UPTIME_REST_API_Client():

    def __init__(self,
                 host=None,
                 port=None,
                 api_ver=None,
                 base=None,
                 user=getpass.getuser()):

        if not host:
            log.error("host is missing!")
            sys.exit(2)

        if not UPTIME_REST_API_Client.__with_http_prefix(host):
            host_address = f'https://{host}'
        else:
            host_address = host

        if port:
            host_address += f':{port}'

        self.baseurl = f'{host_address}'

        if api_ver:
            self.baseurl += f'/{api_ver}'

        if base:
            self.baseurl += f'/{base}'

        self.user = user

        self.headers = {
            'Content-Type': 'application/json',
        }

        access_token = os.getenv('BetterStack_API_TOKEN', None)
        if access_token:
            self.headers['Authorization'] = f'Bearer {access_token}'

        self.monitor_id_cache = {}


    ########################
    ####### Monitors #######
    ########################

    def list_monitors(self):

        url = f"{self.baseurl}/monitors"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        monitor_list = output.get("data", [])

        return True, monitor_list


    def get_monitor(self, monitor_id):

        url = f"{self.baseurl}/monitors/{monitor_id}"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        monitor_data = output.get("data", [])

        return True, monitor_data


    def get_response_times(self, monitor_id):

        url = f"{self.baseurl}/monitors/{monitor_id}/response-times"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        response_times = output.get("data", [])

        return True, response_times


    def get_sla(self, monitor_id):

        url = f"{self.baseurl}/monitors/{monitor_id}/sla"

        status, output = self.__request("GET", url)
        if not status:
            return False, output

        sla_data = output.get("data", [])

        return True, sla_data


    ###############################
    ####### Monitor Helpers #######
    ###############################

    def get_monitor_id(self, url):

        if url in self.monitor_id_cache:
            return True, self.monitor_id_cache[url]

        status, output = self.list_monitors()
        if not status:
            log.error(output)
            sys.exit(2)

        if not output:
            return False, "no monitors found in the remote server"

        for monitor in output:

            monitor_id = monitor.get("id", "")
            attributes = monitor.get("attributes", {})
            url_remote = attributes.get("url", "")

            if url_remote == url:
                self.monitor_id_cache[url] = monitor_id
                return True, monitor_id

        return False, f"cannot find monitor id for {url}"


    ##############################
    ####### Helper Methods #######
    ##############################

    @staticmethod
    def __with_http_prefix(host):

        if host.startswith("http://"):
            return True

        if host.startswith("https://"):
            return True

        return False


    def __request(self, method, url, timeout=10, verify=True, stream=False, decode=True, **kwargs):

        try:
            response = requests.request(method,
                                        url,
                                        headers=self.headers,
                                        timeout=timeout,
                                        verify=verify,
                                        stream=stream,
                                        **kwargs)
        except Exception as E:
            return False, str(E)

        try:
            response.raise_for_status()
        except Exception as E:
            return False, f'Return code={response.status_code}, {E}\n{response.text}'

        if stream:
            return True, response

        if not decode:
            return True, response.content

        try:
            content_decoded = response.content.decode('utf-8')
            if not content_decoded:
                return True, {}

            data_dict = json.loads(content_decoded)
        except Exception as E:
            return False, f'Error while decoding content: {E}'

        return True, data_dict
