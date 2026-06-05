#!/bin/bash

set -e

APP_DIR="/opt/bifrost"
BIN_TARGET="/usr/bin/bifrost"

echo "==> Installing Bifrost to $APP_DIR..."

sudo mkdir -p "$APP_DIR"
sudo cp -r . "$APP_DIR"

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it to use Bifrost."
    exit 1
fi

if ! python3 -m venv --help &> /dev/null; then
    echo "Error: python-venv is missing."
    exit 1
fi

echo "==> Setting up system venv..."
sudo python3 -m venv "$APP_DIR/.venv"
sudo "$APP_DIR/.venv/bin/pip" install --upgrade pip
sudo "$APP_DIR/.venv/bin/pip" install .

echo "==> Linking binary..."

sudo ln -sf "$APP_DIR/.venv/bin/bifrost" "$BIN_TARGET"

echo "==> Installation complete! You can now run 'bifrost' from anywhere."