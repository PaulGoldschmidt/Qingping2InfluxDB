# bash script for building multiplatform & pushing to docker hub
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t quantensittich/qingping2influxdb:latest --push .