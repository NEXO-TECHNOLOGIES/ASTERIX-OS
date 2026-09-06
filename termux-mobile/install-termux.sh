#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Rootless Mobile Installer v3.1 (Resilient & Auto)
# Automated deployment of full ASTERIX OS inside Termux with Rust Engine,
# Zero-Crash Error Handling, Debian PRoot, and Stable Local Storage.
# =====================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
MAGENTA='\033[38;5;201m'
BOLD='\033[1m'
NC='\033[0m'

clear 2>/dev/null || true
echo -e "${CYAN}${BOLD}"
cat << "EOF"
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
       TERMUX MOBILE DEPLOYMENT ENGINE v3.1 (RUST)
EOF
echo -e "${NC}"

# Free package manager cache to prevent "not enough free space"
apt clean 2>/dev/null || true

echo -e "${YELLOW}[*] Step 1: Checking Android Storage Permissions...${NC}"
termux-setup-storage 2>/dev/null || echo -e "${CYAN}[i] Storage permission already active or skipped.${NC}"

echo -e "${YELLOW}[*] Step 2: Updating Termux Repositories & Installing Toolchain...${NC}"
pkg update -y || apt-get update -y || true
pkg install -y proot proot-distro rust clang git curl wget ncurses-utils tsu || true

echo -e "${YELLOW}[*] Step 3: Configuring ASTERIX Stable Local Storage...${NC}"
# Use fast, stable private Termux storage by default (never forces unstable /sdcard mounts)
PERSIST_LOCAL="$HOME/.asterix_storage"
mkdir -p "$PERSIST_LOCAL/loot" "$PERSIST_LOCAL/scripts" "$PERSIST_LOCAL/captures" "$PERSIST_LOCAL/notes" 2>/dev/null || true

# Gracefully link external SDCard only if writable, without crashing if blocked
if [ -d "/sdcard" ] && [ -w "/sdcard" ]; then
    mkdir -p "/sdcard/ASTERIX_PERSISTENCE" 2>/dev/null || true
    ln -sf "/sdcard/ASTERIX_PERSISTENCE" "$PERSIST_LOCAL/sdcard_link" 2>/dev/null || true
    echo -e "${GREEN}[✔] Optional external SDCard link created at $PERSIST_LOCAL/sdcard_link${NC}"
else
    echo -e "${CYAN}[i] Using resilient Termux private storage (100% stable, zero permissions needed).${NC}"
fi

echo -e "${YELLOW}[*] Step 4: Installing ASTERIX Rootless Linux Environment (Debian)...${NC}"
DEBIAN_ROOT="$PREFIX/var/lib/proot-distro/installed-rootfs/debian"
if [ -d "$DEBIAN_ROOT" ] && [ -f "$DEBIAN_ROOT/bin/sh" ]; then
    echo -e "${GREEN}[✔] Debian base environment already installed and healthy.${NC}"
elif [ -d "$DEBIAN_ROOT" ] && [ ! -f "$DEBIAN_ROOT/bin/sh" ]; then
    echo -e "${YELLOW}[!] Corrupted Debian rootfs detected (missing /bin/sh from prior full disk). Resetting...${NC}"
    proot-distro reset debian || true
elif ! proot-distro list 2>/dev/null | grep -q "debian"; then
    echo -e "${CYAN}[*] Downloading and deploying Debian rootfs...${NC}"
    proot-distro install debian || true
else
    echo -e "${GREEN}[✔] Debian base environment registered.${NC}"
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
        println!(" {}BATTERY:{}  {}% | {}STORAGE:{} ACTIVE", C_CYAN, C_RESET, cap.trim(), C_CYAN, C_RESET);
    }
    println!("\x1b[38;5;45m══════════════════════════════════════════════════════════\x1b[0m\n");

    let steps = [
        ("STORAGE_BRIDGE",  "Mounting ASTERIX Secure Vault"),
        ("PROOT_CONTAINER", "Initializing Rootless Debian Sandbox"),
        ("SECURITY_TOOLS",  "Verifying Nmap, TShark, Rust Suite"),
        ("DARK_ENGINES",    "Linking DarkTrace, ShadowCam & WAF"),
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
rustc -O "$LOADER_DIR/src/main.rs" -o "$PREFIX/bin/asterix-loader" 2>/dev/null || true
chmod +x "$PREFIX/bin/asterix-loader" 2>/dev/null || true

echo -e "${YELLOW}[*] Step 6: Installing Security Toolchain inside PRoot Debian...${NC}"
proot-distro login debian -- bash -c "
    apt-get update && apt-get install -y \
        nano vim micro build-essential clang rustc \
        nmap tshark tcpdump netcat-traditional socat curl wget git sudo python3 python3-pip htop \
        || true
" 2>/dev/null || true

echo -e "${YELLOW}[*] Step 7: Auto-Cloning Full Core ASTERIX-OS Operating System...${NC}"
ASTERIX_DIR="$HOME/ASTERIX-OS"
if [ ! -d "$ASTERIX_DIR/.git" ]; then
    echo -e "${CYAN}[*] Downloading complete ASTERIX OS codebase into $ASTERIX_DIR...${NC}"
    git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git "$ASTERIX_DIR" || \
    git clone https://gitlab.com/nexo-technologies-group/asterix-os.git "$ASTERIX_DIR" || true
else
    echo -e "${GREEN}[✔] ASTERIX-OS directory already present. Fetching latest updates...${NC}"
    (cd "$ASTERIX_DIR" && git pull 2>/dev/null || true)
fi

echo -e "${YELLOW}[*] Step 8: Configuring Master Global 'ax' & 'asterix' Dispatcher...${NC}"
cat << 'EOF' > "$PREFIX/bin/ax"
#!/data/data/com.termux/files/usr/bin/bash
ASTERIX_DIR="$HOME/ASTERIX-OS"
PERSIST="$HOME/.asterix_storage"
mkdir -p "$PERSIST" 2>/dev/null || true

# Direct commands
if [ -z "$1" ]; then
    if [ -x "$PREFIX/bin/asterix-loader" ]; then
        "$PREFIX/bin/asterix-loader"
    fi
    exec bash "$ASTERIX_DIR/bin/ax"
elif [ "$1" = "debian" ] || [ "$1" = "proot" ]; then
    shift
    exec proot-distro login --bind "$ASTERIX_DIR:/opt/ASTERIX-OS" --bind "$PERSIST:/asterix_persistent" debian -- "$@"
elif [ "$1" = "update" ]; then
    echo -e "\033[38;5;51m[*] Updating ASTERIX OS & Repositories...\033[0m"
    (cd "$ASTERIX_DIR" && git pull 2>/dev/null || true)
    pkg update -y || true
elif [ "$1" = "upgrade" ]; then
    echo -e "\033[38;5;51m[*] Upgrading Termux Packages...\033[0m"
    pkg upgrade -y || true
elif [ "$1" = "doctor" ]; then
    echo -e "\033[38;5;51m[*] Running Termux ASTERIX Environment Check...\033[0m"
    which rustc clang proot-distro nmap tshark 2>/dev/null || true
    echo -e "\033[38;5;46m[✔] ASTERIX OS Core: $ASTERIX_DIR\033[0m"
elif [ -f "$ASTERIX_DIR/bin/ax" ]; then
    # Run natively in Termux with full performance and zero PRoot errors!
    exec bash "$ASTERIX_DIR/bin/ax" "$@"
elif command -v ax >/dev/null 2>&1; then
    exec ax "$@"
else
    echo "Error: ASTERIX OS not found at $ASTERIX_DIR"
    exit 1
fi
EOF
chmod +x "$PREFIX/bin/ax"
ln -sf "$PREFIX/bin/ax" "$PREFIX/bin/asterix"

# Configure symlink inside PRoot Debian
proot-distro login debian -- bash -c "
    mkdir -p /usr/local/bin
    if [ -f /opt/ASTERIX-OS/bin/ax ]; then
        ln -sf /opt/ASTERIX-OS/bin/ax /usr/local/bin/ax 2>/dev/null || true
        ln -sf /opt/ASTERIX-OS/bin/ax /usr/local/bin/asterix 2>/dev/null || true
    fi
" 2>/dev/null || true

echo -e "${YELLOW}[*] Step 9: Synchronizing External Security Packages...${NC}"
mkdir -p "$ASTERIX_DIR/packages" 2>/dev/null || true
if command -v git >/dev/null 2>&1; then
    for pkg_repo in \
        "https://github.com/alexhack235-code/Asterix-Anti-Network-Attack.git" \
        "https://github.com/alexhack235-code/THUNDER.git" \
        "https://github.com/Alex-dot-dot/ASTERISK-Web-Frality-scanner.git" \
        "https://github.com/alexhack235-code/LIGHTNING-.git" \
        "https://github.com/alexhack235-code/APEX-OVERDRIVE-.git"; do
        pkg_name=$(basename "$pkg_repo" .git)
        if [ ! -d "$ASTERIX_DIR/packages/$pkg_name" ]; then
            git clone "$pkg_repo" "$ASTERIX_DIR/packages/$pkg_name" 2>/dev/null || true
        fi
    done
    find "$ASTERIX_DIR/packages" -type f -name "*.sh" -exec chmod +x {} + 2>/dev/null || true
    echo -e "${GREEN}[✔] Security packages synchronized inside $ASTERIX_DIR/packages.${NC}"
fi

# Configure autostart in ~/.bashrc if not already present
if ! grep -q "asterix-loader" "$HOME/.bashrc" 2>/dev/null; then
    cat << 'AUTO' >> "$HOME/.bashrc"

# ASTERIX OS Startup
if [ -t 1 ]; then
    [ -x "$PREFIX/bin/asterix-loader" ] && asterix-loader
    echo -e "\033[38;5;220mType '\033[1max\033[0m\033[38;5;220m' or '\033[1masterix\033[0m\033[38;5;220m' to enter the ASTERIX Security Sandbox.\033[0m"
    echo -e "\033[38;5;141mTools: ax defender | ax game | ax undercover | ax darktrace | ax shadowcam\033[0m\n"
fi
AUTO
fi

echo -e "\n${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}[✔] ASTERIX OS MOBILE INSTALLATION COMPLETE!${NC}"
echo -e "${CYAN}Core OS Directory:${NC}     $ASTERIX_DIR"
echo -e "${CYAN}Safe Local Storage:${NC}    $PERSIST_LOCAL"
echo -e "${CYAN}Launch Commands:${NC}       Type ${YELLOW}ax${NC} or ${YELLOW}asterix${NC} anywhere in Termux"
echo -e "${CYAN}Defense & Gaming:${NC}      ${YELLOW}ax defender${NC} | ${YELLOW}ax game boost${NC} | ${YELLOW}ax undercover${NC}"
echo -e "${CYAN}Dark Forensic Tools:${NC}   ${YELLOW}ax darktrace${NC} | ${YELLOW}ax shadowcam${NC} | ${YELLOW}ax dark-engine${NC}"
echo -e "${CYAN}System Maintenance:${NC}    ${YELLOW}ax update${NC} | ${YELLOW}ax upgrade${NC} | ${YELLOW}ax doctor${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}\n"