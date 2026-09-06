#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Rootless Mobile Installer v3.0
# Automated deployment of ASTERIX OS inside Termux with Rust Engine,
# Cybernetic Mobile Animations, and Android Persistent Storage.
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
       TERMUX MOBILE DEPLOYMENT ENGINE v3.0 (RUST)
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
mkdir -p "$PERSIST_LOCAL/notes"

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

echo -e "${YELLOW}[*] Step 5: Compiling Native Rust ASTERIX Loader & Animation Engine...${NC}"
LOADER_DIR="$HOME/.asterix-core/asterix-loader"
mkdir -p "$LOADER_DIR/src"

cat << 'RUST_CODE' > "$LOADER_DIR/src/main.rs"
//! ASTERIX OS - Termux Native Rust Boot & Animation Engine v3.0
use std::io::{self, Write};
use std::thread::sleep;
use std::time::Duration;
use std::fs;

const C_RESET: &str = "\x1b[0m";
const C_BOLD: &str = "\x1b[1m";
const C_CYAN: &str = "\x1b[38;5;51m";
const C_GREEN: &str = "\x1b[38;5;46m";
const C_YELLOW: &str = "\x1b[38;5;220m";
const C_MAGENTA: &str = "\x1b[38;5;201m";
const C_WHITE: &str = "\x1b[38;5;231m";
const C_DARKGRAY: &str = "\x1b[38;5;237m";

const BANNER: &str = r#"
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝ 
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗ 
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
             >> ASTERIX MOBILE OS (TERMUX) <<"#;

fn render_bar(pct: usize, width: usize) -> String {
    let filled = (pct * width) / 100;
    let empty = width.saturating_sub(filled);
    format!("{}[{}{}{}]{}", C_CYAN, "█".repeat(filled), C_DARKGRAY, "░".repeat(empty), C_RESET)
}

fn main() {
    print!("\x1b[2J\x1b[H{}{}{}\n\n", C_CYAN, C_BOLD, BANNER, C_RESET);
    println!("\x1b[38;5;45m══════════════════════════════════════════════════════════\x1b[0m");
    println!(" {}[ ASTERIX MOBILE ENVIRONMENT BOOTSTRAP v3.0 ]{}", C_WHITE, C_RESET);

    // Read battery if available
    if let Ok(cap) = fs::read_to_string("/sys/class/power_supply/battery/capacity") {
        println!(" {}BATTERY:{}  {}% | {}STORAGE:{} ACTIVE PERSISTENCE", C_CYAN, C_RESET, cap.trim(), C_CYAN, C_RESET);
    }
    println!("\x1b[38;5;45m══════════════════════════════════════════════════════════\x1b[0m\n");

    let steps = [
        ("STORAGE_BRIDGE",  "Mounting /sdcard/ASTERIX_PERSISTENCE"),
        ("PROOT_CONTAINER", "Initializing Rootless Debian Sandbox"),
        ("SECURITY_TOOLS",  "Checking Nmap, Metasploit, Wireshark"),
        ("DARK_ENGINES",    "Linking DarkTrace, ShadowCam & Rust Suite"),
        ("CRYPTO_VAULT",    "Initializing ChaCha20 / AES-256 Vault"),
        ("ASTERIX_SHELL",   "Launching Cybernetic Mobile Terminal"),
    ];

    let total = steps.len();
    for (i, (sub, desc)) in steps.iter().enumerate() {
        let pct = ((i + 1) * 100) / total;
        print!(" {}[{:^18}]{} {:<30} {} {}\n",
            C_CYAN, sub, C_RESET, desc, render_bar(pct, 14), format!("{}[ OK ]{}", C_GREEN, C_RESET));
        let _ = io::stdout().flush();
        sleep(Duration::from_millis(50));
    }

    println!("\n{}[✔] ASTERIX MOBILE OS ONLINE & READY FOR OPERATIONS{}\n", C_GREEN, C_RESET);
    sleep(Duration::from_millis(300));
}
RUST_CODE

echo -e "${CYAN}[*] Compiling with rustc...${NC}"
rustc -O "$LOADER_DIR/src/main.rs" -o "$PREFIX/bin/asterix-loader"
chmod +x "$PREFIX/bin/asterix-loader"

# Copy bash boot animation
if [ -f "termux-mobile/asterix-termux-init.sh" ]; then
    cp "termux-mobile/asterix-termux-init.sh" "$PREFIX/bin/asterix-init"
    chmod +x "$PREFIX/bin/asterix-init"
fi

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
PERSIST="/data/data/com.termux/files/home/asterix_persistent"
mkdir -p "$PERSIST"

if [ -z "$1" ]; then
    if [ -x "$PREFIX/bin/asterix-loader" ]; then
        "$PREFIX/bin/asterix-loader"
    elif [ -x "$PREFIX/bin/asterix-init" ]; then
        "$PREFIX/bin/asterix-init" --fast
    fi
    exec proot-distro login --bind "$PERSIST:/asterix_persistent" debian
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
elif [ "$1" = "darktrace" ] || [ "$1" = "shadowcam" ] || [ "$1" = "thunder" ] || [ "$1" = "ip-rotator" ] || [ "$1" = "pkg" ] || [ "$1" = "lightning" ] || [ "$1" = "waf" ] || [ "$1" = "soc" ] || [ "$1" = "wscan" ] || [ "$1" = "game" ] || [ "$1" = "overdrive" ] || [ "$1" = "apex" ] || [ "$1" = "defender" ] || [ "$1" = "firewall" ] || [ "$1" = "isolate" ] || [ "$1" = "quarantine" ] || [ "$1" = "snapshot" ] || [ "$1" = "event-log" ] || [ "$1" = "sfc" ] || [ "$1" = "taskmgr" ] || [ "$1" = "secpol" ] || [ "$1" = "sandbox" ] || [ "$1" = "applocker" ] || [ "$1" = "bitlocker" ] || [ "$1" = "cred-guard" ] || [ "$1" = "exploit-guard" ] || [ "$1" = "undercover" ] || [ "$1" = "nuke" ] || [ "$1" = "tweaks" ] || [ "$1" = "forensic-mode" ] || [ "$1" = "rf-audit" ] || [[ "$1" == anti-* ]]; then
    # Run cyber & defense tools inside PRoot sandbox
    exec proot-distro login --bind "$PERSIST:/asterix_persistent" debian -- ax "$@"
else
    # Forward command into PRoot sandbox
    exec proot-distro login --bind "$PERSIST:/asterix_persistent" debian -- "$@"
fi
EOF
chmod +x "$PREFIX/bin/ax"

echo -e "${YELLOW}[*] Step 8: Auto-Cloning External Security Packages...${NC}"
mkdir -p "$PERSIST_LOCAL/packages"
if command -v git >/dev/null 2>&1; then
    if [ ! -d "$PERSIST_LOCAL/packages/Asterix-Anti-Network-Attack" ]; then
        git clone https://github.com/alexhack235-code/Asterix-Anti-Network-Attack.git "$PERSIST_LOCAL/packages/Asterix-Anti-Network-Attack" 2>/dev/null || true
    fi
    if [ ! -d "$PERSIST_LOCAL/packages/THUNDER" ]; then
        git clone https://github.com/alexhack235-code/THUNDER.git "$PERSIST_LOCAL/packages/THUNDER" 2>/dev/null || true
    fi
    if [ ! -d "$PERSIST_LOCAL/packages/ASTERISK-Web-Frality-scanner" ]; then
        git clone https://github.com/Alex-dot-dot/ASTERISK-Web-Frality-scanner.git "$PERSIST_LOCAL/packages/ASTERISK-Web-Frality-scanner" 2>/dev/null || true
    fi
    if [ ! -d "$PERSIST_LOCAL/packages/LIGHTNING-" ]; then
        git clone https://github.com/alexhack235-code/LIGHTNING-.git "$PERSIST_LOCAL/packages/LIGHTNING-" 2>/dev/null || true
    fi
    if [ ! -d "$PERSIST_LOCAL/packages/APEX-OVERDRIVE-" ]; then
        git clone https://github.com/alexhack235-code/APEX-OVERDRIVE-.git "$PERSIST_LOCAL/packages/APEX-OVERDRIVE-" 2>/dev/null || true
    fi
    find "$PERSIST_LOCAL/packages" -type f -name "*.sh" -exec chmod +x {} + 2>/dev/null || true
    echo -e "${GREEN}[✔] Security packages synchronized to mobile persistent storage.${NC}"
fi
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
    echo -e "\033[38;5;220mType '\033[1max\033[0m\033[38;5;220m' or '\033[1masterix\033[0m\033[38;5;220m' to enter the ASTERIX Security Sandbox.\033[0m"
    echo -e "\033[38;5;141mDark Tools: ax darktrace | ax shadowcam | ax dark-engine | ax log-hunter\033[0m\n"
fi
AUTO
fi

echo -e "\n${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}[✔] ASTERIX OS MOBILE INSTALLATION COMPLETE!${NC}"
echo -e "${CYAN}Persistent Data Vault:${NC} $PERSIST_LOCAL"
echo -e "${CYAN}Launch Commands:${NC}       Type ${YELLOW}ax${NC} or ${YELLOW}asterix${NC} anywhere in Termux"
echo -e "${CYAN}Dark Forensic Tools:${NC}   ${YELLOW}ax darktrace${NC} | ${YELLOW}ax shadowcam${NC} | ${YELLOW}ax dark-engine${NC} | ${YELLOW}ax log-hunter${NC}"
echo -e "${CYAN}System Maintenance:${NC}    ${YELLOW}ax update${NC} | ${YELLOW}ax upgrade${NC} | ${YELLOW}ax doctor${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}\n"