#!/bin/bash

DEPLOY_DIR=/opt/betaboard-camera

set -e

# Function for deploy messages
deploy_msg() {
    echo -e "\033[35m[DEPLOY] $1\033[0m"
}

# Load environment variables from .env
set -a
source .env
set +a

# Ensure DEPLOY_DIR is set
if [ -z "$DEPLOY_DIR" ]; then
    deploy_msg "DEPLOY_DIR is not set in .env"
    exit 1
fi

deploy_msg "Preparing betaboard-camera Docker image"

# Use Docker Buildx for cross-platform builds
mkdir -p /tmp/docker-cache
docker buildx create --name betaboard-builder --use || true
docker buildx build \
    --platform linux/arm/v6 \
    --cache-from type=local,src=/tmp/docker-cache \
    --cache-to type=local,dest=/tmp/docker-cache \
    -t betaboard-camera \
    --load .

# Save the Docker image to a tar file
docker save betaboard-camera | gzip > betaboard-camera.tar.gz

# Ensure scripts directory exists on the Pi
ssh "$PI_USER@$PI_HOST" "mkdir -p $DEPLOY_DIR/scripts"

# Copy the Docker image and .env file to the Raspberry Pi
deploy_msg "Copying files to Raspberry Pi"
scp betaboard-camera.tar.gz "$PI_USER@$PI_HOST:$DEPLOY_DIR"
scp .env "$PI_USER@$PI_HOST:$DEPLOY_DIR"

# Copy scripts and service file
scp scripts/deploy-pi.sh "$PI_USER@$PI_HOST:$DEPLOY_DIR/scripts"
scp scripts/ffmpeg-record.sh "$PI_USER@$PI_HOST:$DEPLOY_DIR/scripts"
scp scripts/ffmpeg-record.service "$PI_USER@$PI_HOST:$DEPLOY_DIR/scripts"

# Remove the local Docker image tar file
rm betaboard-camera.tar.gz

deploy_msg "Files copied to Raspberry Pi"
deploy_msg "Run './deploy-pi.sh' on the Raspberry Pi to complete deployment"