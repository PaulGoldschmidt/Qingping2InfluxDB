# DOCKERFILE FOR MEROSSTOINFLUXDB BY P3G3, 2023-01-27

FROM python:3.9-alpine
COPY requirements.txt ./

# Declare arguments with default values
ARG QINGPING_APPKEY=dQw4w9WgXcQ
ARG QINGPING_APPSECRET=dQw4w9WgXcQ
ARG INFLUXDB_URL=http://default-influxdb-url
ARG INFLUXDB_TOKEN=default_token
ARG INFLUXDB_ORG=default_org
ARG INFLUXDB_BUCKET=default_bucket

# Set environment variables from arguments or default values
ENV QINGPING_APPKEY=$QINGPING_APPKEY \
    QINGPING_APPSECRET=$QINGPING_APPSECRET \
    INFLUXDB_URL=$INFLUXDB_URL \
    INFLUXDB_TOKEN=$INFLUXDB_TOKEN \
    INFLUXDB_ORG=$INFLUXDB_ORG \
    INFLUXDB_BUCKET=$INFLUXDB_BUCKET \
    FETCH_INTERVAL=$FETCH_INTERVAL \
    DEBUG=$DEBUG

# Install necessary system dependencies
RUN apk update && apk add --no-cache \
    gcc \
    libc-dev \
    libffi-dev

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY connector.py .
CMD python -u connector.py

COPY deviceinfo.py .

# Health check
COPY healthcheck.py .
HEALTHCHECK --interval=300s --timeout=30s --retries=3 CMD python healthcheck.py
