# betaboard-camera

This is a very simple service that provides recent video feed queryable by timestamp.

## Setup

1. Add the Pi to your hosts file for easier access:
```bash
echo "<your-rpi-ip-address> bb-camera-pi" | sudo tee -a /etc/hosts
```

2. Setup SSH keys with your Raspberry Pi (first time only):
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"  # if you haven't got a key pair already
ssh-copy-id pi@bb-camera-pi
```

## Deployment

The deployment process happens in three steps:

1. Initialize the Pi (first time only):
```bash
# Copy initialization script to Pi
scp scripts/pi-init.sh pi@bb-camera-pi:/tmp/
# Run initialization
ssh pi@bb-camera-pi "bash /tmp/pi-init.sh"
# If prompted, reboot the Pi
ssh pi@bb-camera-pi "sudo reboot"
```

2. Deploy updated code (from your development machine):
```bash
./scripts/deploy.sh pi@bb-camera-pi
```

3. Install and start the service (on the Pi):
```bash
ssh pi@bb-camera-pi
cd /opt/betaboard-camera && ./install.sh
```

## Service Management

Once installed, you can manage the service using standard systemd commands:

```bash
# Check service status
sudo systemctl status betaboard-camera

# View logs
sudo journalctl -u betaboard-camera

# Restart service
sudo systemctl restart betaboard-camera
```