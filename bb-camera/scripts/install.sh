#!/bin/bash
# Run this on the Pi after deploying files
# Should be run from /opt/betaboard-camera

set -e

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