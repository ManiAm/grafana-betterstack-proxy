# BetterStack REST Proxy for Grafana

This project provides a lightweight Python-based REST server that proxies monitoring data from [BetterStack](https://betterstack.com) and exposes it in a Grafana-friendly format. It enables Grafana to visualize website response times and availability metrics using the Infinity plugin or other JSON-compatible data sources.

---

## Features

- REST API endpoint to serve BetterStack uptime and SLA data
- Supports multiple regions (US, EU, AS, AU)
- Timestamp conversion to Unix milliseconds (Grafana-compatible)
- Query filtering by node hostname

---

## Getting Started

### Prerequisites
- Python 3.7+
- A BetterStack API token
- Grafana with the [Infinity plugin](https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/)

### Install Dependencies
```bash
pip install flask flask-compress requests
```

### Set Environment Variable
```bash
export BetterStack_API_TOKEN=your_betterstack_token
```

### Run the Server
```bash
python3 grafana_server.py
```

The server will be available at `http://<your_host>:5006`

---

## Available Endpoints

### `GET /response_time`
Returns response time data per region.

**Query parameters:**
- `nodename`: hostname to match the node
- `url`: monitored website URL
- `region`: comma-separated list of regions (default: `us,eu,as,au`)

**Sample response:**
```json
[
  {
    "timestamp": 1744539757000,
    "region": "us",
    "response_time": 0.47273
  },
]
```

---

### `GET /sla`
Returns website availability (SLA) data.

**Query parameters:**
- `nodename`: hostname to match the node
- `url`: monitored website URL

**Sample response:**
```json
{
  "availability": 99.97
}
```

---

## Run as a systemd Service

To run the project in the background and start it on system boot:

1. Copy the service file:
```bash
sudo cp grafana-betterstack.service /etc/systemd/system/grafana-betterstack.service
```

2. Reload systemd and start the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable grafana-betterstack
sudo systemctl start grafana-betterstack
```

3. Check status and logs:

```bash
sudo systemctl status grafana-betterstack
```

4. On service failure check the journal logs:

```bash
journalctl -u grafana-betterstack -n 50 --no-pager
```

Ensure that your virtual environment and script paths are correctly set in the service file.

---

## Architecture

The server uses the `UPTIME_REST_API_Client` class to interact with BetterStack's API:
- Fetch monitor ID by URL
- Retrieve response time history
- Retrieve SLA/availability metrics

The `Flask` app exposes data as Grafana-friendly JSON endpoints.
