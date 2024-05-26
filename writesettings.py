import asyncio
import os
import time
import requests
from requests.auth import HTTPBasicAuth

url_token = "https://oauth.cleargrass.com/oauth2/token"
url_devices = "https://apis.cleargrass.com/v1/apis/devices"

def load_config(filename):
    config = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                parts = line.strip().split('=')
                key = parts[0]
                value = '='.join(parts[1:])  # This handles the case where the value contains '='
                config[key] = value
    except FileNotFoundError:
        print(f"Using system environment variables.")
        return {}
    return config

config = load_config('config.env')
APPKEY = config['QINGPING_APPKEY']
APPSECRET = config['QINGPING_APPSECRET']
url_setting = "https://apis.cleargrass.com/v1/apis/devices/settings"

async def main():
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
        print("Access token:", access_token)
    else:
        print("Failed to retrieve access token:", response.status_code)
        print(response.json())
    
    # Define the headers and data
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    timestamp = int(time.time())
    data = {
        "mac": ["7CC294CA4302"],
        "report_interval": 30,
        "collect_interval": 30,
        "timestamp": timestamp
    }
    print(data)
    # Make the PUT request
    #response = requests.put(url_setting, json=data, headers=headers)

    # Print the response
    print(response.text)


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()
