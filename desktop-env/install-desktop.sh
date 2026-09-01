#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Desktop Environment Installer
# Registers .desktop entries, autostart triggers, and desktop profiles
# =====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_ROOT="${1:-/}"

echo "[*] Installing ASTERIX Desktop Environment shortcuts to ${TARGET_ROOT}/usr/share/applications..."
mkdir -p "${TARGET_ROOT}/usr/share/applications"
cp "${SCRIPT_DIR}/applications/"*.desktop "${TARGET_ROOT}/usr/share/applications/"
chmod +x "${TARGET_ROOT}/usr/share/applications/asterix-"*.desktop

echo "[*] Configuring XDG autostart hooks..."
mkdir -p "${TARGET_ROOT}/etc/xdg/autostart"
cat << 'EOF' > "${TARGET_ROOT}/etc/xdg/autostart/asterix-desktop.desktop"
[Desktop Entry]
Type=Application
Name=ASTERIX Desktop Initializer
Exec=/etc/asterix/desktop-env/autostart/asterix-init-desktop.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "${TARGET_ROOT}/etc/xdg/autostart/asterix-desktop.desktop"
chmod +x "${SCRIPT_DIR}/autostart/asterix-init-desktop.sh"

echo "[✔] ASTERIX OS Desktop Environment installed successfully."
