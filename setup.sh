#!/bin/bash
set -e

echo "=== PiDisplay Setup ==="

# Update package list
echo "[1/5] Updating package list..."
sudo apt-get update

# Install system dependencies
echo "[2/5] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-pil \
    python3-numpy \
    git \
    fonts-dejavu-core

# Install Python dependencies
echo "[3/5] Installing Python packages..."
pip3 install RPi.GPIO spidev

# Enable SPI if not already enabled
echo "[4/5] Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI enabled — a reboot will be required."
else
    echo "SPI already enabled."
fi

# Clone Waveshare e-Paper library
echo "[5/5] Cloning Waveshare e-Paper library..."
if [ ! -d "e-Paper" ]; then
    git clone https://github.com/waveshare/e-Paper.git
else
    echo "e-Paper directory already exists, pulling latest..."
    git -C e-Paper pull
fi

echo ""
echo "=== Setup complete! ==="
echo "If SPI was just enabled, reboot before running hello_world.py:"
echo "  sudo reboot"
