#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Persistent Storage Subsystem
# Creates directories on Android internal storage and bridges to PRoot
# =====================================================================

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}[*] Setting up ASTERIX Persistence on Android...${NC}"

# Request Android storage permission
termux-setup-storage

LOCAL_VAULT="$HOME/asterix_persistent"
SDCARD_VAULT="/sdcard/ASTERIX_PERSISTENCE"

mkdir -p "$LOCAL_VAULT"
mkdir -p "$LOCAL_VAULT/reports"
mkdir -p "$LOCAL_VAULT/scans"
mkdir -p "$LOCAL_VAULT/custom_scripts"

if [ -d "/sdcard" ]; then
    mkdir -p "$SDCARD_VAULT"
    ln -sf "$SDCARD_VAULT" "$LOCAL_VAULT/sdcard_bridge"
    echo -e "${GREEN}[✔] Linked Android storage: ${SDCARD_VAULT}${NC}"
fi

echo -e "${GREEN}[✔] ASTERIX Persistence is ready at: ${LOCAL_VAULT}${NC}"
