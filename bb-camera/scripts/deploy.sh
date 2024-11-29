#!/bin/bash
# Run this locally to deploy to the Pi
# Usage: ./deploy.sh pi@raspberrypi.local

set -e

if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh pi@hostname"
    exit 1
fi

PI_TARGET=$1
REMOTE_DIR=/opt/betaboard-camera

echo "Cleaning up old files on Raspberry Pi..."
ssh "$PI_TARGET" "sudo rm -rf $REMOTE_DIR/*"

echo "Copying files to Raspberry Pi..."
# Copy the source code and dependencies
rsync -aq --exclude '.git' \
    --exclude 'dist' \
    --exclude '*.pyc' \
    --exclude '__pycache__' \
    --exclude '.pytest_cache' \
    . "$PI_TARGET:$REMOTE_DIR/"

echo "Setting permissions..."
ssh "$PI_TARGET" "sudo chown -R pi:pi $REMOTE_DIR && sudo chmod +x $REMOTE_DIR/scripts/*.sh"

echo "Installing service..."
ssh "$PI_TARGET" "sudo cp $REMOTE_DIR/scripts/betaboard-camera.service /etc/systemd/system/"
ssh "$PI_TARGET" "sudo systemctl daemon-reload"
ssh "$PI_TARGET" "sudo systemctl enable betaboard-camera"

echo "Starting service..."
ssh "$PI_TARGET" "sudo systemctl restart betaboard-camera"

echo "Installation complete!"