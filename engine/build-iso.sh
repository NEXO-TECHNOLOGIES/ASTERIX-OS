#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Live ISO Build Engine
# Automated Builder using Debian live-build & Custom Hooks
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
          LIVE ISO BUILD ENGINE v1.0
EOF
echo -e "${NC}"

if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[!] ERROR: This build engine must be run as root (sudo ./build-iso.sh)${NC}"
    exit 1
fi

WORK_DIR="$(pwd)/asterix-live-build"
DISTRIBUTION="bookworm"
ARCH="amd64"
IMAGE_NAME="asterix-os-v1.0-${ARCH}.iso"

echo -e "${YELLOW}[*] Step 1: Installing Host Build Dependencies...${NC}"
apt-get update
apt-get install -y live-build debootstrap squashfs-tools xorriso isolinux syslinux-efi grub-pc-bin grub-efi-amd64-bin mtools git

echo -e "${YELLOW}[*] Step 2: Initializing Live Build Workspace in ${WORK_DIR}...${NC}"
rm -rf "${WORK_DIR}"
mkdir -p "${WORK_DIR}"
cd "${WORK_DIR}"

echo -e "${YELLOW}[*] Step 3: Configuring Live System Parameters...${NC}"
lb config \
    --distribution "${DISTRIBUTION}" \
    --architectures "${ARCH}" \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootloader grub-efi \
    --binary-images iso-hybrid \
    --iso-application "ASTERIX Security OS" \
    --iso-preparer "ASTERIX OS Project" \
    --iso-publisher "ASTERIX Labs" \
    --iso-volume "ASTERIX_LIVE" \
    --linux-packages "linux-image" \
    --memtest none \
    --system live \
    --bootappend-live "boot=live components quiet splash persistence persistence-encryption=none"

echo -e "${YELLOW}[*] Step 4: Injecting ASTERIX Package Manifest...${NC}"
mkdir -p config/package-lists
if [ -f "../../engine/packages.list" ]; then
    cp "../../engine/packages.list" config/package-lists/asterix.list.chroot
else
    cat << 'EOF' > config/package-lists/asterix.list.chroot
bash zsh tmux screen htop btop curl wget git sudo ca-certificates
wireshark tshark tcpdump netcat-traditional socat nmap
python3 python3-pip python3-rich dialog whiptail
fdisk parted e2fsprogs dosfstools cryptsetup rsync
plymouth plymouth-themes live-boot live-config live-config-systemd
EOF
fi

echo -e "${YELLOW}[*] Step 5: Injecting ASTERIX Custom Hooks, Rust Engine & UI Assets...${NC}"
mkdir -p config/includes.chroot/usr/local/bin
mkdir -p config/includes.chroot/etc/skel/.config
mkdir -p config/includes.chroot/etc/asterix

# Compile Rust loader if source exists
if [ -d "../../ui-core/asterix-loader" ]; then
    echo -e "${CYAN}[*] Compiling Native Rust Loader & Control Center...${NC}"
    cd "../../ui-core/asterix-loader"
    if command -v cargo >/dev/null 2>&1; then
        cargo build --release
        cp target/release/asterix-loader "$WORK_DIR/config/includes.chroot/usr/local/bin/asterix-loader"
    elif command -v rustc >/dev/null 2>&1; then
        rustc -O -C lto=yes src/main.rs -o "$WORK_DIR/config/includes.chroot/usr/local/bin/asterix-loader"
    fi
    cd "$WORK_DIR"
    chmod +x config/includes.chroot/usr/local/bin/asterix-loader 2>/dev/null || true
fi

# Set up main asterix launcher wrapper
cat << 'EOF' > config/includes.chroot/usr/local/bin/asterix
#!/bin/bash
if [ -x /usr/local/bin/asterix-loader ]; then
    /usr/local/bin/asterix-loader "$@"
elif [ -f /etc/asterix/loading_screen.sh ]; then
    /etc/asterix/loading_screen.sh
fi
EOF
chmod +x config/includes.chroot/usr/local/bin/asterix

# Copy visual assets and desktop configurations to /etc/asterix
if [ -d "../../ui-core" ]; then
    cp -r ../../ui-core/* config/includes.chroot/etc/asterix/
fi
if [ -d "../../desktop-env" ]; then
    cp -r ../../desktop-env config/includes.chroot/etc/asterix/
    mkdir -p config/includes.chroot/usr/share/applications
    cp ../../desktop-env/applications/*.desktop config/includes.chroot/usr/share/applications/
    mkdir -p config/includes.chroot/etc/xdg/autostart
    cat << 'EOF' > config/includes.chroot/etc/xdg/autostart/asterix-desktop.desktop
[Desktop Entry]
Type=Application
Name=ASTERIX Desktop Initializer
Exec=/etc/asterix/desktop-env/autostart/asterix-init-desktop.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
fi
if [ -d "../../assets" ]; then
    mkdir -p config/includes.chroot/etc/asterix/assets
    cp -r ../../assets/* config/includes.chroot/etc/asterix/assets/
fi
if [ -d "../../web-dashboard" ]; then
    mkdir -p config/includes.chroot/etc/asterix/web-dashboard
    cp -r ../../web-dashboard/* config/includes.chroot/etc/asterix/web-dashboard/
fi
if [ -d "../../cloud-panel" ]; then
    mkdir -p config/includes.chroot/etc/asterix/cloud-panel
    cp -r ../../cloud-panel/* config/includes.chroot/etc/asterix/cloud-panel/
fi

# Make helper scripts executable and symlink globally
chmod +x config/includes.chroot/etc/asterix/*.sh 2>/dev/null || true
chmod +x config/includes.chroot/etc/asterix/ui-core/*.sh 2>/dev/null || true
ln -sf /etc/asterix/ui-core/asterix-discord.sh config/includes.chroot/usr/local/bin/as-discord 2>/dev/null || true
ln -sf /etc/asterix/ui-core/asterix-web-portal.sh config/includes.chroot/usr/local/bin/as-portal 2>/dev/null || true
ln -sf /etc/asterix/ui-core/asterix-cloud.sh config/includes.chroot/usr/local/bin/as-cloud 2>/dev/null || true

# Inject GRUB Boot Theme
if [ -d "../../engine/grub-theme" ]; then
    echo -e "${CYAN}[*] Injecting GRUB Bootloader Splash Theme...${NC}"
    mkdir -p config/bootloaders/grub-pc
    mkdir -p config/bootloaders/grub-efi
    cp -r ../../engine/grub-theme/* config/bootloaders/grub-pc/ 2>/dev/null || true
    cp -r ../../engine/grub-theme/* config/bootloaders/grub-efi/ 2>/dev/null || true
fi

# Metasploit installer hook
mkdir -p config/hooks/normal
cat << 'EOF' > config/hooks/normal/0900-install-metasploit.hook.chroot
#!/bin/sh
set -e
echo ">>> [ASTERIX HOOK] Installing Metasploit Framework..."
curl -fsSL https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall
chmod 755 /tmp/msfinstall
/tmp/msfinstall || echo "[!] Notice: Metasploit setup can be finished post-boot."
rm -f /tmp/msfinstall

# Configure default user bashrc and nanorc
if [ -f "../../desktop-env/nanorc" ]; then
    cp "../../desktop-env/nanorc" config/includes.chroot/etc/skel/.nanorc
fi

if [ -f "../../ui-core/asterix-shell-env.sh" ]; then
    cp "../../ui-core/asterix-shell-env.sh" config/includes.chroot/etc/asterix/asterix-shell-env.sh
fi

cat << 'AUTORUN' >> /etc/skel/.bashrc

# Source ASTERIX Cyber Shell Environment
if [ -f /etc/asterix/asterix-shell-env.sh ]; then
    source /etc/asterix/asterix-shell-env.sh
fi

# Launch ASTERIX OS Native Rust Banner on interactive terminal session
if [ -x /usr/local/bin/asterix-loader ] && [ "$TERM" != "dumb" ]; then
    /usr/local/bin/asterix-loader --boot-only --fast
fi
AUTORUN
EOF
chmod +x config/hooks/normal/0900-install-metasploit.hook.chroot

# Plymouth Boot Animation Theme hook
cat << 'EOF' > config/hooks/normal/0950-install-plymouth.hook.chroot
#!/bin/sh
set -e
echo ">>> [ASTERIX HOOK] Configuring Plymouth Cybernetic Boot Animation..."
if [ -f /etc/asterix/desktop-env/plymouth/install-plymouth.sh ]; then
    bash /etc/asterix/desktop-env/plymouth/install-plymouth.sh || true
fi
EOF
chmod +x config/hooks/normal/0950-install-plymouth.hook.chroot

echo -e "${YELLOW}[*] Step 6: Building ASTERIX ISO Image (this may take several minutes)...${NC}"
lb build

if [ -f "live-image-amd64.hybrid.iso" ]; then
    mv "live-image-amd64.hybrid.iso" "../${IMAGE_NAME}"
    echo -e "${GREEN}${BOLD}[✔] SUCCESS: Built ASTERIX OS ISO: ../${IMAGE_NAME}${NC}"
else
    echo -e "${RED}[!] Notice: Check build logs for artifact output.${NC}"
fi
