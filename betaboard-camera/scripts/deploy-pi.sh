#!/bin/bash

set -e

# Function for deploy messages
deploy_msg() {
    echo -e "\033[35m[DEPLOY] $1\033[0m"
}

# Load environment variables
set -a
source /home/pi/betaboard-camera/.env
set +a

deploy_msg "Setting up FFmpeg recording service"
sudo cp $DEPLOY_DIR/scripts/ffmpeg-record.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ffmpeg-record.service
sudo systemctl restart ffmpeg-record.service

deploy_msg "Preparing betaboard-camera Docker image"
gunzip -c $DEPLOY_DIR/betaboard-camera.tar.gz | docker load

deploy_msg "Stopping existing betaboard-camera (if it exists)"
docker stop betaboard-camera 2>/dev/null || true
docker rm betaboard-camera 2>/dev/null || true

deploy_msg "Running betaboard-camera"
docker run -d \
    --name betaboard-camera \
    --restart unless-stopped \
    --security-opt seccomp=unconfined \
    -p 8000:8000 \
    --env-file $DEPLOY_DIR/.env \
    -v "$DEPLOY_DIR/videos:$DEPLOY_DIR/videos" \
    betaboard-camera

deploy_msg "Deployment complete"