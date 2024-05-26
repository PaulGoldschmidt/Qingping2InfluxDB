![Docker Image Version (latest semver)](https://img.shields.io/docker/v/quantensittich/qingping2influxdb)
![Docker Image Size (tag)](https://img.shields.io/docker/image-size/quantensittich/qingping2influxdb/latest)
![Docker Pulls](https://img.shields.io/docker/pulls/quantensittich/qingping2influxdb)
# Qingping2InfluxDB :chart_with_upwards_trend:

Qingping2InfluxDB is a project that enables the collection of environment data from Qingping smart devices (especially the Qingping Air Monitor Light) and stores it in an InfluxDB database. The [connector.py](connector.py) script is designed to be run in the background and pushes every 20 seconds to influxdb the power metrics of the power plugs you choose. It was build upon the [Qingping OpenAPI Spec](https://developer.qingping.co/) and currently (2024-05-25) working with the latest Qingping API version. It utilizes the official python [InfluxDB Client](https://github.com/influxdata/influxdb-client-python) in order to publish data to your InfluxDB instance. Thanks to the authors of these packages which made this little project possible.
It comes ready-to-use in a docker package which can be used multi-platform. Out-of-the box the script scrapes every 20 seconds the power metrics from the chosen devices and pushes them to InfluxDB. This can be changed in the source code quite easily.

## Features

- **Device Discovery:** Finds all devices and adds them without any further needed setup to your InfluxDB Bucket as devices with the respectable tags. 
- **Data Extraction:** Retrieves real-time environment data (temperature, humidity, co2, pm2.5, pm10, aqi) from the all qingping devices in your account. Automatically adds all data provided as datapoints to influxdb.
- **Data Storage:** Efficiently stores the extracted data in an InfluxDB database for further analysis and visualization.
- **Customizable Fetch Interval:** Allows setting a custom interval for data fetching.

# Recommended Installation: Docker Image :star:
There is a multiplatform docker image for this code available on docker hub, an example setup is provided with [docker-compose.yml](docker-compose.yml). Just put the [docker-compose.yml](docker-compose.yml) _somewhere_ on your computer, change the environment variables to your setup and start the container with `docker compose up -d` (older docker installation: `docker-compose up -d`).
If you want to use docker run instead of docker compose (not recommended! :shipit:), you can use:
```
docker run -d --restart unless-stopped --name Qingping2InfluxDB \
  -e QINGPING_APPKEY=user_email@example.com \
  -e QINGPING_APPSECRET=user_password \
  -e API_BASE_URL=http://user-api-base-url \
  -e INFLUXDB_URL=http://user-influxdb-url \
  -e INFLUXDB_TOKEN=user_token \
  -e INFLUXDB_ORG=user_org \
  -e INFLUXDB_BUCKET=user_bucket \
  -e DEVICE_NAMES_TO_MONITOR=DEVICE1,DEVICE2 \
  quantensittich/qingping2influxdb:latest
```


## Requirements

- Python 3.x
- Access to quingping devices.
- An InfluxDB server (either local or remote) to store the data.

## Testing your quingping setup & get device overview
In order to test the quingping setup and see all devices that are currently available, the script [deviceinfo.py](deviceinfo.py) is included in this repository. After filling out the [config.env](config.env.example) file with your credentials and removing the .example file ending, run the device info script once to get an overview over all avaiable devices. For each device you want to write the data to InfluxDB, please fill the exact names into line 31 in [connector.py](connector.py).

## Installation Instructions (localy) :potato:

1. **Set Up Python Environment:**
   - Ensure Python 3.x is installed on your system.
   - It's recommended to use a virtual environment:
     ```bash
     python -m venv quingping-env
     source quingping-env/bin/activate  # On Windows, use `quingping-env\Scripts\activate`
     ```

2. **Install Dependencies:**
   - Navigate to the project directory.
   - Install required Python packages using:
     ```bash
     pip install -r requirements.txt
     ```

3. **Configuration:**
   - Create a `config.env` file in the project directory with the following content, filling in your own details (see [config.env.example](config.env.example)):
     ```
     QINGPING_APPKEY=your_QINGPING_APPKEY_account_email
     QINGPING_APPSECRET=your_QINGPING_APPSECRET_account_password
     API_BASE_URL=api_base_region
     INFLUXDB_URL=your_influxdb_url
     INFLUXDB_TOKEN=your_influxdb_token
     INFLUXDB_ORG=your_influxdb_org
     INFLUXDB_BUCKET=your_influxdb_bucket
     DEVICE_NAMES_TO_MONITOR=your_devices_seperated_by_comma
     FETCH_INTERVAL=20
     #DEBUG=TRUE #comment out if shell be enabled.
     ```

4. **Running the Script:**
   - Run the script using:
     ```bash
     python connector.py
     ```

5. **Monitoring:**
   - The script will continuously monitor the specified Quingping devices and log data to your InfluxDB database at the set interval.

## Usage

- Before running the script, ensure that the Quingping devices you want to monitor are set up and connected to your network.
- Set the `fetch_interval` in the script to control how often data is fetched from the devices.
- The script will output the current readings to the console and write the data to the specified InfluxDB bucket.

## Docker Build process :boom:

There is a [dockerfile](Dockerfile) provided in this repository which allows you to build your own image of QingpingToInfluxDB. If you want to build the image multi-platform, there is a [buildx-example-script](buildx.sh) provided aswell.

## Additional Information
I wrote a blog article in German about this Project. [Check it out!](https://p3g3.de/2024/05/qingping-air-monitor-light/)

## Docker Hub
This project is published multi-platform on the [Docker-Hub](https://hub.docker.com/r/quantensittich/qingping2influxdb).


## Notes

- This project requires an active internet connection for the Qingping API to function :trollface:.
- Ensure your InfluxDB instance is properly set up and accessible from the script :accessibility:.
- Handle your credentials securely and avoid exposing them in public or unsecured files :bowtie:.

## Troubleshooting :basecampy:

- If you encounter issues with device discovery, ensure your devices are correctly set up with the Qingping app and are online.
- For any connection issues with InfluxDB, verify your InfluxDB URL, token, organization, and bucket details.
- Check your Python environment and dependencies if you encounter any script execution errors.

![QingpingToInfluxDB](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExNmQ5NWZjeW9ja3I4anRoaHEzcjh2b3o2NGoyc2E5OXk5d3lhaTI3ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9ADoZQgs0tyww/giphy.gif)