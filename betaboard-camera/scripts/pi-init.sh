#!/bin/bash

# Load environment variables from .env
set -a
source .env
set +a

# Transfer the remote init script to the Raspberry Pi
scp scripts/pi-init-remote.sh "$PI_USER@$PI_HOST:/home/$PI_USER/"

# Run the remote init script on the Raspberry Pi
ssh "$PI_USER@$PI_HOST" "bash /home/$PI_USER/pi-init-remote.sh"

# Optional: Remove the remote init script from the Raspberry Pi
ssh "$PI_USER@$PI_HOST" "rm /home/$PI_USER/pi-init-remote.sh"