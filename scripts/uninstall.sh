#!/bin/bash

set -e

SERVICE_FILE="$HOME/.config/systemd/user/bifrost.service"
APP_DIR="$HOME/.local/share/bifrost"
BIN_TARGET="$HOME/.local/bin/bifrost"

echo "==> Uninstalling Bifrost..."

# 1. Stop and disable the service first
if [ -f "$SERVICE_FILE" ]; then
    echo "Stopping and disabling service..."
    systemctl --user stop bifrost.service || true
    systemctl --user disable bifrost.service || true
    rm "$SERVICE_FILE"
    systemctl --user daemon-reload
    systemctl --user reset-failed
    echo "Service removed."
fi

# 2. Remove binary link
if [ -L "$BIN_TARGET" ]; then
    rm "$BIN_TARGET"
    echo "Removed binary link."
fi

# 3. Remove application files
if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
    echo "Removed application files from $APP_DIR."
fi

echo "==> Bifrost has been uninstalled successfully."