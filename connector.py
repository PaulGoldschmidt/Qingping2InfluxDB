import asyncio
import os
from datetime import datetime
import time
import requests
from requests.auth import HTTPBasicAuth
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def load_config(filename):
    configs = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split('=')
                key = parts[0]
                value = '='.join(parts[1:])  # This handles the case where the value contains '='
                configs[key] = value
    except FileNotFoundError:
        print(f"Using system environment variables.")
        return {}
    return configs

config = load_config('config.env')
APPKEY = os.environ.get('QINGPING_APPKEY') or config['QINGPING_APPKEY']
APPSECRET = os.environ.get('QINGPING_APPSECRET') or config['QINGPING_APPSECRET']
INFLUXDB_URL = os.environ.get('INFLUXDB_URL') or config['INFLUXDB_URL']
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN') or config['INFLUXDB_TOKEN']
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG') or config['INFLUXDB_ORG']
INFLUXDB_BUCKET = os.environ.get('INFLUXDB_BUCKET') or config['INFLUXDB_BUCKET']
FETCH_INTERVAL = int(os.environ.get('FETCH_INTERVAL') or config['FETCH_INTERVAL'])
DEBUG = os.environ.get('DEBUG') or config.get('DEBUG', '')

url_token = "https://oauth.cleargrass.com/oauth2/token"
url_devices = "https://apis.cleargrass.com/v1/apis/devices"
url_setting = "https://apis.cleargrass.com/v1/apis/devices/settings"
access_token = None

def update_interval(mac):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    timestamp = int(time.time())
    data = {
        "mac": [mac],
        "report_interval": FETCH_INTERVAL,
        "collect_interval": FETCH_INTERVAL,
        "timestamp": timestamp
    }
    print(data)
    response = requests.put(url_setting, json=data, headers=headers)

    if DEBUG: print(response.text)

async def fetch_token():
    global access_token
    while True:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "scope": "device_full_access"
        }
        auth = HTTPBasicAuth(APPKEY, APPSECRET)

        response = requests.post(url_token, headers=headers, data=data, auth=auth)

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get('access_token')
            if DEBUG: print("Access token retrieved at", datetime.now(), ":", access_token)
        else:
            if DEBUG: print("Failed to retrieve access token:", response.status_code)
            if DEBUG: print(response.json())

        await asyncio.sleep(59 * 60)

def validate_data(data):
    for key in data:
        if isinstance(data[key]["value"], (int, float)):
            data[key]["value"] = float(data[key]["value"])
    return data

async def main(FETCH_INTERVAL):
    influxdb_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    global access_token
    while access_token is None:
        if DEBUG: print(f"Waiting for token to be generated")
        await asyncio.sleep(1)
    try:
        while True:
            headers_devices = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response_devices = requests.get(url_devices, headers=headers_devices)
            if response_devices.status_code == 200:
                devices_data = response_devices.json()
            else:
                if DEBUG: print("Failed to retrieve devices:", response_devices.status_code)
                if DEBUG: print(response_devices.json())
                await asyncio.sleep(FETCH_INTERVAL)
                continue

            for device in devices_data["devices"]:
                report_interval = device['info']['setting']['report_interval']
                collect_interval = device['info']['setting']['collect_interval']
                
                if report_interval != FETCH_INTERVAL or collect_interval != FETCH_INTERVAL:
                    macadress = device['info']['mac']
                    if DEBUG: print("Updating FETCH_INTERVAL for the following MAC address:", macadress)
                    update_interval(macadress)

                dynamic_point = Point("qingping_data").tag("device", device["info"]["name"])
                validated_data = validate_data(device["data"])
                for key, value in validated_data.items():
                    dynamic_point = dynamic_point.field(key, value["value"])
                    if DEBUG: print(key, value["value"])
                
                if DEBUG: print(f"Writing the following to InfluxDB:", dynamic_point)
                write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=dynamic_point)

            await asyncio.sleep(FETCH_INTERVAL)

    except KeyboardInterrupt:
        if DEBUG: print("Interrupted by user, closing...")

if __name__ == '__main__':
    print("##############################################")
    print("Starting Qingping2InfluxDB by p3g3, Version 1.0")
    if DEBUG: print(f"         DEBUG LOGGING ENABLED.    ")
    print("##############################################")
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(fetch_token(), main(FETCH_INTERVAL)))
    loop.close()
