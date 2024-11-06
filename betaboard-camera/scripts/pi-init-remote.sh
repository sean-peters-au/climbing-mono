#!/bin/bash

set -e

# Update package lists
sudo apt-get update

# Install prerequisites
sudo apt-get install -y ffmpeg # libavcodec-extra

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  sudo usermod -aG docker "$USER"
  echo "Docker installed. Please log out and log back in for changes to take effect."
else
  echo "Docker is already installed."
fi

# Add Raspbian repository (if needed)
if ! grep -q "^deb .*raspbian\.raspberrypi\.org/raspbian/ bullseye main" /etc/apt/sources.list; then
  echo "Adding Raspbian bullseye main repository."
  echo "deb http://raspbian.raspberrypi.org/raspbian/ bullseye main" | sudo tee -a /etc/apt/sources.list
  sudo apt-get update
fi

# Create the video directory if it doesn't exist
if [ ! -d "$VIDEO_DIR" ]; then
  mkdir -p "$VIDEO_DIR"
fi