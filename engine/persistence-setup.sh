#!/usr/bin/env bash
# =====================================================================
# 🌌 ASTERIX OS - Live USB Dual-Mode Persistence Engine
# Supports: Standard Ext4 Persistence & Military-Grade LUKS Encrypted Persistence
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << "EOF"
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
   DUAL-MODE LIVE USB PERSISTENCE & LUKS ENGINE
EOF
echo -e "${NC}"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] ERROR: This script must be run as root (sudo ./persistence-setup.sh <target-device>)${NC}"
    exit 1
fi

DEVICE="$1"

if [ -z "$DEVICE" ]; then
    echo -e "${YELLOW}Available storage block devices on this system:${NC}\n"
    lsblk -o NAME,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINT
    echo ""
    read -rp "[?] Enter target USB drive (e.g. /dev/sdb): " DEVICE
fi

if [ ! -b "$DEVICE" ]; then
    echo -e "${RED}[!] Error: Device $DEVICE does not exist or is not a block device!${NC}"
    exit 1
fi

echo ""
echo -e "${CYAN}${BOLD}Select Persistence Security Profile:${NC}"
echo -e "  ${GREEN}1)${NC} Standard High-Speed Persistence (Ext4 - Instant Auto-Mount)"
echo -e "  ${MAGENTA}2)${NC} Encrypted LUKS Persistence Vault (AES-256-XTS - Passphrase Protected)"
echo -e "  ${YELLOW}3)${NC} Inspect & Verify Existing Persistence Volume"
echo ""
read -rp "Enter choice [1-3] (Default: 1): " MODE_CHOICE
MODE_CHOICE="${MODE_CHOICE:-1}"

if [ "$MODE_CHOICE" == "3" ]; then
    echo -e "${CYAN}[*] Inspecting partitions on ${DEVICE}...${NC}"
    lsblk -f "$DEVICE"
    exit 0
fi

echo -e "\n${RED}${BOLD}⚠ CAUTION: You are configuring a persistent partition on: $DEVICE${NC}"
echo -e "${YELLOW}Ensure you have flashed the ASTERIX ISO onto this drive first.${NC}"
read -rp "Do you want to proceed? (y/N): " CONFIRM

if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
    echo -e "${YELLOW}[*] Operation cancelled.${NC}"
    exit 0
fi

echo -e "${CYAN}[*] Analyzing partition table and remaining free space...${NC}"
PART_COUNT=$(parted -s "$DEVICE" print | grep -c "^ [0-9]" || true)
NEXT_PART=$((PART_COUNT + 1))

FREE_START=$(parted -s "$DEVICE" unit s print free | grep "Free Space" | tail -n1 | awk '{print $1}')

if [ -z "$FREE_START" ]; then
    echo -e "${RED}[!] Error: No unallocated free space found on ${DEVICE} to create persistence partition.${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Creating persistence partition ${NEXT_PART} starting at sector ${FREE_START}...${NC}"
parted -s "$DEVICE" mkpart primary ext4 "${FREE_START}" 100% || true

# Identify the newly created partition block device
NEW_PARTITION="${DEVICE}${NEXT_PART}"
if [ ! -b "$NEW_PARTITION" ]; then
    NEW_PARTITION="${DEVICE}p${NEXT_PART}"
fi

if [ ! -b "$NEW_PARTITION" ]; then
    echo -e "${RED}[!] Error: Could not locate new partition device (${NEW_PARTITION}).${NC}"
    exit 1
fi

# Let kernel settle
sleep 2
partprobe "$DEVICE" 2>/dev/null || true

MOUNT_DIR="/mnt/asterix_persistence_tmp"
mkdir -p "$MOUNT_DIR"

if [ "$MODE_CHOICE" == "2" ]; then
    # Mode 2: Encrypted LUKS Persistence
    echo -e "\n${MAGENTA}${BOLD}[*] Initializing LUKS Encrypted Container on ${NEW_PARTITION}...${NC}"
    if ! command -v cryptsetup >/dev/null 2>&1; then
        echo -e "${RED}[!] Error: 'cryptsetup' utility is required. Install via: apt install cryptsetup${NC}"
        exit 1
    fi

    echo -e "${YELLOW}You will now be prompted to create your LUKS encryption passphrase.${NC}"
    cryptsetup luksFormat --type luks2 --cipher aes-xts-plain64 --key-size 512 --hash sha512 "$NEW_PARTITION"

    MAPPER_NAME="asterix_luks_prst"
    echo -e "${CYAN}[*] Opening encrypted volume /dev/mapper/${MAPPER_NAME}...${NC}"
    cryptsetup open "$NEW_PARTITION" "$MAPPER_NAME"

    echo -e "${CYAN}[*] Formatting encrypted container as ext4 with label 'persistence'...${NC}"
    mkfs.ext4 -L "persistence" -F "/dev/mapper/${MAPPER_NAME}"

    echo -e "${CYAN}[*] Mounting encrypted overlay and configuring live-boot rules...${NC}"
    mount "/dev/mapper/${MAPPER_NAME}" "$MOUNT_DIR"

    echo "/ union" > "$MOUNT_DIR/persistence.conf"
    mkdir -p "$MOUNT_DIR/asterix_vault"
    mkdir -p "$MOUNT_DIR/asterix_user_data"
    mkdir -p "$MOUNT_DIR/asterix_loot"

    cat << 'INFO' > "$MOUNT_DIR/asterix_vault/SECURITY_NOTICE.txt"
=====================================================================
ASTERIX OS - MILITARY-GRADE ENCRYPTED PERSISTENCE VAULT
=====================================================================
Cipher:     AES-256-XTS (512-bit total key)
Hash:       SHA-512
Standard:   LUKS2 (Linux Unified Key Setup)
Overlay:    Full root filesystem union (/ union)

To boot with this encrypted storage:
Select "ASTERIX OS Live (Encrypted LUKS Persistence Vault)" at the bootloader.
Enter your passphrase at the initramfs prompt to unlock your persistent workspace.
=====================================================================
INFO

    sync
    umount "$MOUNT_DIR"
    cryptsetup close "$MAPPER_NAME"

    echo -e "\n${GREEN}${BOLD}[✔] SUCCESS: Encrypted LUKS Persistence active on ${NEW_PARTITION}!${NC}"
    echo -e "${GREEN}Boot your USB and select 'Encrypted LUKS Persistence Vault' in the GRUB menu.${NC}\n"

else
    # Mode 1: Standard Ext4 Persistence
    echo -e "\n${CYAN}[*] Formatting partition ${NEW_PARTITION} as ext4 with label 'persistence'...${NC}"
    mkfs.ext4 -L "persistence" -F "$NEW_PARTITION"

    echo -e "${CYAN}[*] Mounting persistence partition and injecting configuration...${NC}"
    mount "$NEW_PARTITION" "$MOUNT_DIR"

    echo "/ union" > "$MOUNT_DIR/persistence.conf"
    mkdir -p "$MOUNT_DIR/asterix_user_data"
    mkdir -p "$MOUNT_DIR/asterix_loot"
    mkdir -p "$MOUNT_DIR/asterix_scripts"

    cat << 'INFO' > "$MOUNT_DIR/asterix_user_data/README_PERSISTENCE.txt"
=====================================================================
ASTERIX OS - SECURE PERSISTENCE STORAGE
=====================================================================
All user configurations, reports, logs, and custom tools stored in
this directory or throughout the OS will automatically persist across
reboots when booting with the "USB Persistence Enabled" option.
=====================================================================
INFO

    sync
    umount "$MOUNT_DIR"

    echo -e "\n${GREEN}${BOLD}[✔] SUCCESS: Standard Ext4 Persistence active on ${NEW_PARTITION}!${NC}"
    echo -e "${GREEN}Boot your USB and select 'USB Persistence Enabled' in the GRUB menu.${NC}\n"
fi

rm -rf "$MOUNT_DIR"
