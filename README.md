# Ticki Radio Alarm

<img src="static/ticki-wallpaper.webp" alt="Ticki Radio Interface" width="700">

A web-based internet radio player for Raspberry Pi with alarm functionality.

## Features

- Web interface for controlling the radio
- Play/Stop controls
- Alarm functionality to start playing at a specific time

## Prerequisites

- Raspberry Pi 3 Model A+
- 8GB (minimum) microSD card
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

### 2. Copy the repository to your Raspberry Pi

1. Make sure you have SSH access to your Raspberry Pi

1. Use the sync script to copy the repository to your Raspberry Pi:

```bash
./sync.sh
```

1. On your Raspberry Pi, setup the virtual environment and install the dependencies:

```bash
cd ticki
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

1. Create a systemd service to run the application:

```bash
sudo cp ticki.service /etc/systemd/system/ticki.service
sudo systemctl daemon-reload
sudo systemctl enable ticki
sudo systemctl start ticki
```

1. Access the web interface:

<http://<raspberry-pi-ip:8888>

## Usage

Use the web interface to:

- Play/Stop the radio
- Set an alarm time

## Adding More Stations

To add more stations, modify the `current_station` dictionary in `app.py` with additional station URLs.

## Optional: Deploy with Docker

```bash
./sync.sh
```### 1. Build and Deploy the Application

On your development machine:

1. Build and save the Docker image:

```bash
docker buildx create --use
docker buildx build --platform linux/arm/v7 -t raspi-ticki --load . && docker save raspi-ticki > raspi-ticki.tar
scp raspi-ticki.tar ticki:~
```

1. On the Raspberry Pi, load and run the image:

```bash
sudo docker load < raspi-ticki.tar
rm raspi-ticki.tar

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


### Troubleshooting

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
