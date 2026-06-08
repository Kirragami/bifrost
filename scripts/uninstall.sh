#!/bin/bash

set -e

if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root (sudo ./uninstall.sh)"
  exit 1
fi

APP_DIR="$HOME/.local/share/bifrost"
BIN_TARGET="$HOME/.local/bin/bifrost"

echo "==> Uninstalling Bifrost..."

if [ -L "$BIN_TARGET" ]; then
    rm "$BIN_TARGET"
    echo "Removed binary link."
fi

if [ -d "$APP_DIR" ]; then
    rm -rf "$APP_DIR"
    echo "Removed application files from $APP_DIR."
fi

echo "==> Bifrost has been uninstalled successfully."