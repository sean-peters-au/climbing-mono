# betaboard-camera

This is a very simple service that provides recent video feed queryable by timestamp.

## Deploy

1. (First time only) Setup SSH keys with your Raspberry Pi
```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" # if you haven't got a key pair already
ssh-copy-id "$PI_USER@$PI_HOST"
```

2. (First time only) Initialise the Pi
```
./scripts/pi-init.sh
```

3. (Every deployment) Deploy the camera service to the Pi
```
./scripts/deploy.sh
```

