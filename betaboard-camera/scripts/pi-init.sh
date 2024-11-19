#!/bin/bash
# This script should be run on the Raspberry Pi Zero W you plan on deploying to
# NOTE: I haven't actually tested this. It's been constructed from memory.

set -e

# Add Raspbian repository (if needed)
if ! grep -q "^deb .*raspbian\.raspberrypi\.org/raspbian/ bullseye main" /etc/apt/sources.list; then
  echo "deb http://raspbian.raspberrypi.org/raspbian/ bullseye main" | sudo tee -a /etc/apt/sources.list
fi

# Update package lists
sudo apt-get --allow-releaseinfo-change update

# Install prerequisites
sudo apt-get install -y ffmpeg ufw libraspberrypi-bin libraspberrypi-dev apache2

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker "$USER"

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp  # Allow HTTP for streaming
sudo ufw --force enable

# Configure Apache and streaming directory
sudo mkdir -p /var/www/html/stream
sudo chown -R pi:pi /var/www/html/stream
sudo chmod 755 /var/www/html/stream

# Ensure Apache is running and enabled at startup
sudo systemctl enable apache2
sudo systemctl start apache2

# Create main project directory
sudo mkdir -p /opt/betaboard-camera
sudo chown -R pi:pi /opt/betaboard-camera