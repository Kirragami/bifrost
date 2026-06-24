#!/bin/bash
set -e

# Define clear paths
APP_DIR="$HOME/.local/share/bifrost"
BIN_DIR="$HOME/.local/bin"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/bifrost.service"

echo "==> Installing Bifrost to $APP_DIR..."

mkdir -p "$APP_DIR"
# Copy files (excluding the install script itself to avoid clutter)
rsync -av --exclude='install.sh' . "$APP_DIR/"

mkdir -p "$BIN_DIR"
mkdir -p "$SERVICE_DIR"

# Setup venv
echo "==> Setting up system venv..."
python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip
"$APP_DIR/.venv/bin/pip" install -e "$APP_DIR"

echo "==> Linking binary..."
ln -sf "$APP_DIR/.venv/bin/bifrost" "$BIN_DIR/bifrost"

# Create Service file with correct paths
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Bifrost Hardware Engine
After=graphical-session.target

[Service]
ExecStart=$APP_DIR/.venv/bin/python -u $APP_DIR/src/bifrost/main.py
WorkingDirectory=$APP_DIR
Restart=always
RestartSec=5
SyslogIdentifier=bifrost

[Install]
WantedBy=default.target
EOF

# Reload and Start
echo "==> Configuring systemd..."
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
systemctl --user daemon-reload
systemctl --user enable --now bifrost.service

echo "==> Installation complete! You can now run 'bifrost' from anywhere."