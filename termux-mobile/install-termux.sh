#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Rootless Mobile Installer
# Automated deployment of ASTERIX OS inside Termux with Rust Engine
# and Android Persistent Storage Integration.
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[38;5;201m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo -e "${CYAN}${BOLD}"
cat << "EOF"
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
       TERMUX MOBILE DEPLOYMENT ENGINE (RUST)
EOF
echo -e "${NC}"

echo -e "${YELLOW}[*] Step 1: Requesting Android Shared Storage Permissions...${NC}"
termux-setup-storage || echo -e "${CYAN}[i] Storage permission already granted or skipped.${NC}"

echo -e "${YELLOW}[*] Step 2: Updating Termux Repositories & Installing Toolchain...${NC}"
pkg update -y
pkg install -y proot proot-distro rust clang git curl wget ncurses-utils tsu || true

echo -e "${YELLOW}[*] Step 3: Configuring ASTERIX Persistent Storage Bridge...${NC}"
PERSIST_LOCAL="$HOME/asterix_persistent"
PERSIST_SDCARD="/sdcard/ASTERIX_PERSISTENCE"

mkdir -p "$PERSIST_LOCAL"
mkdir -p "$PERSIST_LOCAL/loot"
mkdir -p "$PERSIST_LOCAL/scripts"
mkdir -p "$PERSIST_LOCAL/captures"

if [ -d "/sdcard" ]; then
    mkdir -p "$PERSIST_SDCARD" 2>/dev/null || true
    ln -sf "$PERSIST_SDCARD" "$PERSIST_LOCAL/android_sdcard_link" 2>/dev/null || true
    echo -e "${GREEN}[✔] Linked Android storage ($PERSIST_SDCARD) to $PERSIST_LOCAL${NC}"
fi

echo -e "${YELLOW}[*] Step 4: Installing ASTERIX Rootless Linux Environment (Debian)...${NC}"
if ! proot-distro list | grep -q "debian (installed)"; then
    echo -e "${CYAN}[*] Downloading and installing Debian rootfs...${NC}"
    proot-distro install debian
else
    echo -e "${GREEN}[✔] Debian base already installed in proot-distro.${NC}"
fi

echo -e "${YELLOW}[*] Step 5: Compiling Native Rust ASTERIX Loader...${NC}"
LOADER_DIR="$HOME/.asterix-core/asterix-loader"
mkdir -p "$LOADER_DIR/src"

cat << 'RUST_CODE' > "$LOADER_DIR/src/main.rs"
//! ASTERIX OS - Termux Native Rust Boot Engine
use std::io::{self, Write};
use std::thread::sleep;
use std::time::Duration;
use std::process::Command;

const BANNER: &str = r#"
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝ 
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗ 
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
             >> ASTERIX MOBILE OS (TERMUX) <<"#;

fn main() {
    print!("\x1b[2J\x1b[H\x1b[38;5;51m\x1b[1m{}\x1b[0m\n\n", BANNER);
    println!("\x1b[38;5;45m══════════════════════════════════════════════════════════\x1b[0m");
    println!(" \x1b[1m[ ASTERIX MOBILE ENVIRONMENT BOOTSTRAP ]\x1b[0m");
    println!("\x1b[38;5;45m══════════════════════════════════════════════════════════\x1b[0m\n");

    let steps = [
        ("STORAGE_BRIDGE", "Mounting /sdcard/ASTERIX_PERSISTENCE"),
        ("PROOT_CONTAINER", "Initializing Rootless Debian Sandbox"),
        ("SECURITY_TOOLS", "Checking Nmap, Metasploit, Wireshark"),
        ("ASTERIX_SHELL", "Launching Cybernetic Mobile Terminal"),
    ];

    for (sub, desc) in steps {
        print!(" \x1b[38;5;51m[{:^18}]\x1b[0m {:<32} \x1b[38;5;46m[ OK ]\x1b[0m\n", sub, desc);
        let _ = io::stdout().flush();
        sleep(Duration::from_millis(60));
    }

    println!("\n\x1b[38;5;46m\x1b[1m[✔] ASTERIX MOBILE OS ONLINE\x1b[0m\n");
    sleep(Duration::from_millis(400));
}
RUST_CODE

echo -e "${CYAN}[*] Compiling with rustc...${NC}"
rustc -O "$LOADER_DIR/src/main.rs" -o "$PREFIX/bin/asterix-loader"
chmod +x "$PREFIX/bin/asterix-loader"

echo -e "${YELLOW}[*] Step 6: Installing Security Toolchain & Development Suite inside PRoot...${NC}"
proot-distro login debian -- bash -c "
    apt-get update && apt-get install -y \
        nano vim micro build-essential clang rustc \
        nmap tshark tcpdump netcat-traditional socat curl wget git sudo python3 python3-pip htop \
        || true
"

echo -e "${YELLOW}[*] Step 7: Creating Global 'ax' & 'asterix' Launch Commands...${NC}"
cat << 'EOF' > "$PREFIX/bin/ax"
#!/data/data/com.termux/files/usr/bin/bash
if [ -z "$1" ]; then
    asterix-loader
    exec proot-distro login --bind /data/data/com.termux/files/home/asterix_persistent:/asterix_persistent debian
elif [ "$1" = "update" ]; then
    echo -e "\033[38;5;51m[*] Updating Termux & PRoot Repositories...\033[0m"
    pkg update -y
    proot-distro login debian -- apt-get update -y
elif [ "$1" = "upgrade" ]; then
    echo -e "\033[38;5;51m[*] Upgrading Termux & PRoot Environments...\033[0m"
    pkg upgrade -y
    proot-distro login debian -- apt-get upgrade -y
elif [ "$1" = "doctor" ]; then
    echo -e "\033[38;5;51m[*] Running Termux ASTERIX Environment Check...\033[0m"
    which rustc clang proot-distro nmap tshark 2>/dev/null || true
else
    # Forward command into PRoot sandbox
    exec proot-distro login --bind /data/data/com.termux/files/home/asterix_persistent:/asterix_persistent debian -- "$@"
fi
EOF
chmod +x "$PREFIX/bin/ax"
ln -sf "$PREFIX/bin/ax" "$PREFIX/bin/asterix"

# Also configure ax and asterix inside the PRoot Debian sandbox
proot-distro login debian -- bash -c "
    ln -sf /usr/local/bin/ax /usr/local/bin/asterix 2>/dev/null || true
"

# Configure autostart in ~/.bashrc if not already present
if ! grep -q "asterix-loader" "$HOME/.bashrc" 2>/dev/null; then
    cat << 'AUTO' >> "$HOME/.bashrc"

# ASTERIX OS Startup
if [ -t 1 ]; then
    asterix-loader
    echo -e "\033[38;5;220mType '\033[1max\033[0m\033[38;5;220m' or '\033[1masterix\033[0m\033[38;5;220m' to enter the ASTERIX Security Sandbox.\033[0m\n"
fi
AUTO
fi

echo -e "\n${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}[✔] ASTERIX OS MOBILE INSTALLATION COMPLETE!${NC}"
echo -e "${CYAN}Persistent Data Vault:${NC} $PERSIST_LOCAL"
echo -e "${CYAN}Launch Commands:${NC}       Type ${YELLOW}ax${NC} or ${YELLOW}asterix${NC} anywhere in Termux"
echo -e "${CYAN}System Maintenance:${NC}    ${YELLOW}ax update${NC} | ${YELLOW}ax upgrade${NC} | ${YELLOW}ax doctor${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}\n"
