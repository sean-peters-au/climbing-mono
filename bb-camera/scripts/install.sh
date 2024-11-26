#!/bin/bash
# Run this on the Pi after deploying files
# Should be run from /opt/betaboard-camera

set -e

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-flask \
    python3-flask-cors \
    python3-libcamera \
    python3-picamera2

# Create videos directory if it doesn't exist
sudo mkdir -p /home/pi/videos
sudo chown pi:pi /home/pi/videos

echo "Installing service..."
sudo cp scripts/betaboard-camera.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable betaboard-camera

echo "Starting service..."
sudo systemctl restart betaboard-camera

echo "Installation complete! Check status with:"
echo "sudo systemctl status betaboard-camera" 