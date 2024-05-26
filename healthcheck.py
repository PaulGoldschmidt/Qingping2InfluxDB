import os
import asyncio
from influxdb_client import InfluxDBClient
import requests
from requests.auth import HTTPBasicAuth

# Load credentials from a file or environment variables
def load_credentials(filename):
    credentials = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split('=')
                key = parts[0]
                value = '='.join(parts[1:])
                credentials[key] = value
    except FileNotFoundError:
        print(f"Using system environment variables.")
        return {}
    return credentials

credentials = load_credentials('config.env')
APPKEY = os.environ.get('QINGPING_APPKEY') or credentials['QINGPING_APPKEY']
APPSECRET = os.environ.get('QINGPING_APPSECRET') or credentials['QINGPING_APPSECRET']
INFLUXDB_URL = os.environ.get('INFLUXDB_URL') or credentials['INFLUXDB_URL']
INFLUXDB_TOKEN = os.environ.get('INFLUXDB_TOKEN') or credentials['INFLUXDB_TOKEN']
INFLUXDB_ORG = os.environ.get('INFLUXDB_ORG') or credentials['INFLUXDB_ORG']
url_token = "https://oauth.cleargrass.com/oauth2/token"

async def check_qingping():
    try:
        # Get access token
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
            return True
        else:
            return False
    except Exception as e:
        print(f"Qingping API check failed: {e}")
        return False

def check_influxdb():
    try:
        client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        client.close()
        return True
    except Exception as e:
        print(f"InfluxDB check failed: {e}")
        return False

async def main():
    qingping_status = await check_qingping()
    influxdb_status = check_influxdb()

    if qingping_status and influxdb_status:
        print("Health check passed: Both InfluxDB and Qingping API are operational.")
        return 0
    else:
        print("Health check failed.")
        return 1

if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    status = loop.run_until_complete(main())
    loop.close()
    exit(status)
