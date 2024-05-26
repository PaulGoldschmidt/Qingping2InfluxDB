import asyncio
import os

import requests
from requests.auth import HTTPBasicAuth
url_token = "https://oauth.cleargrass.com/oauth2/token"
url_devices = "https://apis.cleargrass.com/v1/apis/devices"

# Function to print all key-value pairs in a JSON object
def print_json(obj, indent=0):
    for key, value in obj.items():
        print('  ' * indent + f'{key}:', end=' ')
        if isinstance(value, dict):
            print()
            print_json(value, indent + 1)
        elif isinstance(value, list):
            print()
            for i, item in enumerate(value):
                print('  ' * (indent + 1) + f'[{i}]', end=' ')
                if isinstance(item, dict):
                    print()
                    print_json(item, indent + 2)
                else:
                    print(item)
        else:
            print(value)

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

    #Now get device data
    headers_devices = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response_devices = requests.get(url_devices, headers=headers_devices)
    if response_devices.status_code == 200:
        devices_data = response_devices.json()
        print_json(devices_data)
    else:
        print("Failed to retrieve devices:", response_devices.status_code)
        print(response_devices.json())


if __name__ == '__main__':
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.stop()
