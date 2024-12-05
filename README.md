# Raspberry Pi Internet Radio

A web-based internet radio player for Raspberry Pi with alarm functionality.

## Features

- Web interface for controlling the radio
- Play/Stop controls
- Alarm functionality to start playing at a specific time
- Currently supports SRF2 radio station

## Prerequisites

- Raspberry Pi 3 Model A+
- 32GB (minimum) microSD card
- Docker installed on your development machine
- Raspberry Pi Imager (for flashing the SD card)

## Setup Instructions

### 1. Prepare the Raspberry Pi

1. Download and install [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert your microSD card into your computer
3. Open Raspberry Pi Imager and:
   - Choose OS: Select "Raspberry Pi OS Lite (32-bit)"
   - Choose Storage: Select your microSD card
   - Click on settings (gear icon) and:
     - Enable SSH
     - Set a username and password
     - Configure your WiFi settings
   - Click "Write" and wait for the process to complete

4. Insert the microSD card into your Raspberry Pi and power it on
5. Find your Raspberry Pi's IP address (you can use your router's admin panel or `nmap -sn 192.168.1.0/24` on your network)

### 2. Install Docker on Raspberry Pi

SSH into your Raspberry Pi and run:

```bash
# SSH into your Pi
ssh <username>@<raspberry-pi-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Reboot the Pi
sudo reboot
```

### 3. Build and Deploy the Application

On your development machine:

1. Clone this repository:

```bash
git clone <repository-url>
cd raspi-ticki
```

1. Build and save the Docker image:

```bash
docker buildx create --use
docker buildx build --platform linux/arm/v7 -t raspi-ticki --load .
docker save raspi-ticki > raspi-ticki.tar
```

1. Transfer the image to Raspberry Pi:

```bash
scp raspi-ticki.tar ticki:~
```

1. On the Raspberry Pi, load and run the image:

```bash
# SSH into your Pi
ssh <username>@<raspberry-pi-ip>
docker load < raspi-ticki.tar

# Run the container
docker run -d \
  --name ticki \
  --restart unless-stopped \
  --dns 8.8.8.8 \
  --dns 8.8.4.4 \
  -p 8888:8888 \
  --device /dev/snd \
  --group-add audio \
  raspi-ticki
```

1. Access the web interface:

<http://<raspberry-pi-ip:8888>

## Usage

Use the web interface to:

- Play/Stop the radio
- Set an alarm time

## Adding More Stations

To add more stations, modify the `current_station` dictionary in `app.py` with additional station URLs.

## Troubleshooting

1. If you get audio permission errors:

```bash
# Add your user to the audio group
sudo usermod -aG audio $USER
sudo usermod -aG audio root
```

1. If the container fails to start:

```bash
# Check container logs
docker logs radio
```
