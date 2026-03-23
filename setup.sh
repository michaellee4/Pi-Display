#!/bin/bash
set -e

echo "=== PiDisplay Setup ==="

# Update package list
echo "[1/6] Updating package list..."
sudo apt-get update

# Install system dependencies
echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-full \
    git \
    fonts-dejavu-core

# Create virtual environment
echo "[3/6] Creating virtual environment (.venv)..."
python3 -m venv .venv

# Install Python dependencies into venv
echo "[4/6] Installing Python packages into virtual environment..."
.venv/bin/pip install RPi.GPIO spidev pillow numpy

# Enable SPI if not already enabled
echo "[5/6] Enabling SPI interface..."
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI enabled — a reboot will be required."
else
    echo "SPI already enabled."
fi

# Clone Waveshare e-Paper library
echo "[6/6] Cloning Waveshare e-Paper library..."
if [ ! -d "e-Paper" ]; then
    git clone https://github.com/waveshare/e-Paper.git
else
    echo "e-Paper directory already exists, pulling latest..."
    git -C e-Paper pull
fi

echo ""
echo "=== Setup complete! ==="
echo "Run hello_world.py with the virtual environment:"
echo "  .venv/bin/python3 hello_world.py"
echo ""
echo "Or activate the venv first:"
echo "  source .venv/bin/activate"
echo "  python3 hello_world.py"
echo ""
echo "If SPI was just enabled, reboot first: sudo reboot"
