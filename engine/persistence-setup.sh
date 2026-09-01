#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Live USB Persistence Provisioner
# Configures USB persistence partition labeled 'persistence'
# with ASTERIX user profile directories and persistent overlays.
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
       LIVE USB PERSISTENCE PROVISIONER
EOF
echo -e "${NC}"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] ERROR: This script must be run as root (sudo ./persistence-setup.sh <target-device>)${NC}"
    exit 1
fi

DEVICE="$1"

if [ -z "$DEVICE" ]; then
    echo -e "${YELLOW}Usage:${NC} sudo ./persistence-setup.sh /dev/sdX"
    echo ""
    echo "Available storage devices:"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,LABEL
    echo ""
    read -rp "[?] Enter target device (e.g. /dev/sdb): " DEVICE
fi

if [ ! -b "$DEVICE" ]; then
    echo -e "${RED}[!] Error: Device $DEVICE does not exist or is not a block device!${NC}"
    exit 1
fi

echo -e "${RED}${BOLD}[CAUTION] You are about to configure persistence on: $DEVICE${NC}"
echo -e "${YELLOW}Ensure you have already flashed the ASTERIX ISO onto this drive.${NC}"
read -rp "Do you want to proceed creating the ASTERIX persistence partition? (y/N): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo -e "${YELLOW}[*] Operation cancelled.${NC}"
    exit 0
fi

echo -e "${CYAN}[*] Inspecting partitions on ${DEVICE}...${NC}"
PART_COUNT=$(parted -s "$DEVICE" print | grep -c "^ [0-9]" || true)
NEXT_PART=$((PART_COUNT + 1))

echo -e "${CYAN}[*] Creating persistence partition (Partition ${NEXT_PART})...${NC}"
parted -s "$DEVICE" mkpart primary ext4 $(parted -s "$DEVICE" unit s print free | grep "Free Space" | tail -n1 | awk '{print $1}') 100% || true

# Identify the newly created partition
NEW_PARTITION="${DEVICE}${NEXT_PART}"
if [ ! -b "$NEW_PARTITION" ]; then
    NEW_PARTITION="${DEVICE}p${NEXT_PART}"
fi

echo -e "${CYAN}[*] Formatting partition ${NEW_PARTITION} as ext4 with label 'persistence'...${NC}"
mkfs.ext4 -L "persistence" -F "$NEW_PARTITION"

echo -e "${CYAN}[*] Mounting partition and injecting persistence configuration...${NC}"
MOUNT_DIR="/mnt/asterix_persistence_tmp"
mkdir -p "$MOUNT_DIR"
mount "$NEW_PARTITION" "$MOUNT_DIR"

# Write Debian live persistence rule: / union (persists all changes)
echo "/ union" > "$MOUNT_DIR/persistence.conf"

# Create ASTERIX custom persistence directories
mkdir -p "$MOUNT_DIR/asterix_user_data"
mkdir -p "$MOUNT_DIR/asterix_loot"
mkdir -p "$MOUNT_DIR/asterix_scripts"

cat << 'INFO' > "$MOUNT_DIR/asterix_user_data/README_PERSISTENCE.txt"
=====================================================================
ASTERIX OS - SECURE PERSISTENCE STORAGE
=====================================================================
All user configurations, reports, logs, and custom tools stored in
this directory or throughout the OS will automatically persist across
reboots when booting with the "Persistence" boot menu option.
=====================================================================
INFO

sync
umount "$MOUNT_DIR"
rm -rf "$MOUNT_DIR"

echo -e "${GREEN}${BOLD}[✔] SUCCESS: ASTERIX OS Persistence Partition is active on ${NEW_PARTITION}!${NC}"
echo -e "${GREEN}When booting your USB, select 'Live System (with persistence)' to automatically save your data.${NC}"
