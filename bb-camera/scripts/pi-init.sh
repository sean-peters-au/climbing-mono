#!/bin/bash
# Run this on the Pi to initialize the environment
# This should be run first, before any deployment

set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-flask \
    python3-flask-cors \
    python3-libcamera \
    python3-picamera2 \
    python3-pip \
    python3-venv \
    python3.9 \
    python3.9-venv \
    git

echo "Installing pipenv..."
sudo pip3 install pipenv

echo "Creating application directory..."
sudo mkdir -p /opt/betaboard-camera
sudo chown pi:pi /opt/betaboard-camera

if [ "$REBOOT_NEEDED" = "1" ]; then
    echo "Setup complete! Please reboot the Pi with 'sudo reboot'"
    echo "After reboot, run deploy.sh from your development machine"
else
    echo "Setup complete! Now run deploy.sh from your development machine"
fi