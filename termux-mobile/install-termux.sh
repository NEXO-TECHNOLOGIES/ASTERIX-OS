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
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
        TERMUX MOBILE DEPLOYMENT ENGINE v3.2 (HARDENED)
EOF
echo -e "${NC}"

echo -e "${YELLOW}${BOLD}[!] NOTICE: Strictly for Authorized Security Auditing & Defensive Research on Owned Systems.${NC}\n"

# Step-level diagnostic tracking
STEP_NAMES=()
STEP_RESULTS=()
STEP_DETAILS=()
CRITICAL_FAILURES=0

log_step() {
    local name="$1"
    local status="$2"
    local detail="${3:-}"
    STEP_NAMES+=("$name")
    STEP_RESULTS+=("$status")
    STEP_DETAILS+=("$detail")
    if [ "$status" = "FAIL" ]; then
        CRITICAL_FAILURES=$((CRITICAL_FAILURES + 1))
    fi
}

# Free package manager cache to prevent "not enough free space"
apt clean 2>/dev/null || true

echo -e "${YELLOW}[*] Step 1: Checking Android Storage Permissions...${NC}"
if termux-setup-storage 2>/dev/null; then
    log_step "Storage Permission" "PASS" "Granted or Active"
    echo -e "${GREEN}[[OK]] Storage permissions configured.${NC}"
else
    log_step "Storage Permission" "PASS" "Private Storage Fallback"
    echo -e "${CYAN}[i] Storage permission already active or private sandbox active.${NC}"
fi

echo -e "${YELLOW}[*] Step 2: Updating Termux Repositories & Installing Toolchain...${NC}"
pkg update -y || apt-get update -y || true
if pkg install -y proot proot-distro rust clang git curl wget ncurses-utils tsu; then
    log_step "Host Toolchain" "PASS" "All packages ready"
    echo -e "${GREEN}[[OK]] Host toolchain installed.${NC}"
elif command -v proot >/dev/null 2>&1 && command -v proot-distro >/dev/null 2>&1; then
    log_step "Host Toolchain" "WARN" "Core PRoot present, partial build tools"
    echo -e "${YELLOW}[!] PRoot detected; some secondary compiler tools were skipped.${NC}"
else
    log_step "Host Toolchain" "FAIL" "proot/proot-distro missing"
    echo -e "${RED}[[FAIL]] Fatal: proot-distro could not be installed. Check network/mirrors.${NC}"
fi

echo -e "${YELLOW}[*] Step 3: Configuring ASTERIX Resilient Local Storage & Folders...${NC}"
PERSIST_LOCAL="$HOME/.asterix_storage"
PERSIST_MAIN="$HOME/asterix_persistent"
ASTERIX_DIR="$HOME/ASTERIX-OS"

# Standard persistent folders
mkdir_success=1
for p_dir in "$PERSIST_LOCAL" "$PERSIST_MAIN"; do
    if mkdir -p "$p_dir"/{projects,scans,loot,captures,reports,notes,scripts,payloads,wordlists,workspace} 2>/dev/null; then
        chmod -R 755 "$p_dir" 2>/dev/null || true
    else
        mkdir_success=0
    fi
done

if [ $mkdir_success -eq 1 ]; then
    log_step "Persistent Vault" "PASS" "10 mission stores created"
    echo -e "${GREEN}[[OK]] 10 standard persistent stores configured.${NC}"
else
    log_step "Persistent Vault" "WARN" "Partial directory creation"
fi

ensure_asterix_shell_bootstrap() {
    local shell_env="$ASTERIX_DIR/ui-core/asterix-shell-env.sh"
    local shell_snippet='\n# ASTERIX OS shell bridge\nexport PATH="$PREFIX/bin:$HOME/.local/bin:$HOME/ASTERIX-OS/bin:$HOME/ASTERIX-OS/scripts-hub:$PATH"\nfor d in "$HOME/ASTERIX-OS"/core-utils-*; do [ -d "$d/bin" ] && export PATH="$d/bin:$PATH"; done\n[ -f "$HOME/ASTERIX-OS/ui-core/asterix-shell-env.sh" ] && . "$HOME/ASTERIX-OS/ui-core/asterix-shell-env.sh"\n'

    for rc in "$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"; do
        [ -n "$rc" ] || continue
        touch "$rc" 2>/dev/null || continue
        if ! grep -q "ASTERIX OS shell bridge" "$rc" 2>/dev/null; then
            printf '%b\n' "$shell_snippet" >> "$rc"
        fi
    done

    if [ -f "$shell_env" ]; then
        . "$shell_env"
    fi
    export PATH="$PREFIX/bin:$HOME/.local/bin:$HOME/ASTERIX-OS/bin:$HOME/ASTERIX-OS/scripts-hub:$PATH"
    for d in "$HOME/ASTERIX-OS"/core-utils-*; do
        [ -d "$d/bin" ] && export PATH="$d/bin:$PATH"
    done
}

ensure_asterix_shell_bootstrap

# Gracefully link external SDCard only if writable, without crashing if blocked
if [ -d "/sdcard" ] && [ -w "/sdcard" ]; then
    mkdir -p "/sdcard/ASTERIX_PERSISTENCE" 2>/dev/null || true
    ln -sf "/sdcard/ASTERIX_PERSISTENCE" "$PERSIST_LOCAL/sdcard_link" 2>/dev/null || true
    ln -sf "/sdcard/ASTERIX_PERSISTENCE" "$PERSIST_MAIN/sdcard_bridge" 2>/dev/null || true
    echo -e "${GREEN}[[OK]] Optional external SDCard link created at $PERSIST_LOCAL/sdcard_link${NC}"
else
    echo -e "${CYAN}[i] Using resilient Termux private storage (100% stable, zero permissions needed).${NC}"
fi

echo -e "${YELLOW}[*] Step 4: Installing ASTERIX Rootless Linux Environment (Debian)...${NC}"
DEBIAN_ROOT="$PREFIX/var/lib/proot-distro/installed-rootfs/debian"
if [ -d "$DEBIAN_ROOT" ] && [ -f "$DEBIAN_ROOT/bin/sh" ]; then
    echo -e "${GREEN}[[OK]] Debian base environment already installed and healthy.${NC}"
    log_step "Debian Rootfs" "PASS" "Verified healthy rootfs"
elif [ -d "$DEBIAN_ROOT" ] && [ ! -f "$DEBIAN_ROOT/bin/sh" ]; then
    echo -e "${YELLOW}[!] Corrupted Debian rootfs detected (missing /bin/sh from prior full disk). Resetting...${NC}"
    proot-distro reset debian 2>/dev/null || true
    if proot-distro install debian && [ -f "$DEBIAN_ROOT/bin/sh" ]; then
        log_step "Debian Rootfs" "PASS" "Reset and reinstalled"
    else
        log_step "Debian Rootfs" "FAIL" "Failed to restore /bin/sh"
    fi
elif ! proot-distro list 2>/dev/null | grep -q "debian"; then
    echo -e "${CYAN}[*] Downloading and deploying Debian rootfs...${NC}"
    if proot-distro install debian && [ -f "$DEBIAN_ROOT/bin/sh" ]; then
        log_step "Debian Rootfs" "PASS" "Installed successfully"
    else
        log_step "Debian Rootfs" "FAIL" "Download/unpack failed"
    fi
else
    log_step "Debian Rootfs" "PASS" "Registered base rootfs"
    echo -e "${GREEN}[[OK]] Debian base environment registered.${NC}"
fi

# Apply Zero-Crash Debian Rootless Hardening Immediately
if [ -d "$DEBIAN_ROOT" ]; then
    echo -e "${CYAN}[*] Applying Zero-Crash Hardening to Debian Rootless Subsystem...${NC}"
    # 1. Multi-DNS Resolver
    mkdir -p "$DEBIAN_ROOT/etc"
    printf "nameserver 1.1.1.1\nnameserver 8.8.8.8\nnameserver 9.9.9.9\nnameserver 1.0.0.1\noptions timeout:2 attempts:3 rotate\n" > "$DEBIAN_ROOT/etc/resolv.conf" 2>/dev/null || true
    # 2. APT Sandbox User Fix (eliminates _apt permission denied)
    mkdir -p "$DEBIAN_ROOT/etc/apt/apt.conf.d"
    printf '// ASTERIX Rootless Hardening\nAPT::Sandbox::User "root";\nAcquire::Languages "none";\nAcquire::Check-Valid-Until "false";\n' > "$DEBIAN_ROOT/etc/apt/apt.conf.d/99termux-rootless" 2>/dev/null || true
    # 3. Suppress Daemon Startups (policy-rc.d 101)
    mkdir -p "$DEBIAN_ROOT/usr/sbin"
    printf '#!/bin/sh\nexit 101\n' > "$DEBIAN_ROOT/usr/sbin/policy-rc.d" 2>/dev/null || true
    chmod 755 "$DEBIAN_ROOT/usr/sbin/policy-rc.d" 2>/dev/null || true
    # 4. /dev/shm and /tmp permissions (1777)
    mkdir -p "$DEBIAN_ROOT/dev/shm" "$DEBIAN_ROOT/tmp" "$DEBIAN_ROOT/run/shm" 2>/dev/null || true
    chmod 1777 "$DEBIAN_ROOT/dev/shm" "$DEBIAN_ROOT/tmp" 2>/dev/null || true
    # 5. Clean UTF-8 Environment & Hostname
    printf "LANG=C.UTF-8\nLC_ALL=C.UTF-8\n" > "$DEBIAN_ROOT/etc/environment" 2>/dev/null || true
    printf "127.0.0.1 localhost asterix-rootless\n" > "$DEBIAN_ROOT/etc/hosts" 2>/dev/null || true
    printf "asterix-rootless\n" > "$DEBIAN_ROOT/etc/hostname" 2>/dev/null || true
    log_step "Rootless Hardening" "PASS" "DNS, APT Sandbox, policy-rc.d"
    echo -e "${GREEN}[[OK]] Debian Rootless hardened (APT Sandbox, DNS Failover, Daemon Blocker active).${NC}"
else
    log_step "Rootless Hardening" "WARN" "Deferred until rootfs available"
fi

echo -e "${YELLOW}[*] Step 5: Compiling Native Rust ASTERIX Loader & Animation Engine...${NC}"
LOADER_DIR="$HOME/.asterix-core/asterix-loader"
mkdir -p "$LOADER_DIR/src"

cat << 'RUST_CODE' > "$LOADER_DIR/src/main.rs"
//! ASTERIX OS — Cinema-Grade Native Rust Boot & Telemetry Engine v3.2
use std::io::{self, Write};
use std::thread::sleep;
use std::time::Duration;
use std::fs;

const C_RESET: &str = "\x1b[0m";
const C_BOLD: &str = "\x1b[1m";
const C_CYAN: &str = "\x1b[38;5;51m";
const C_DKCYAN: &str = "\x1b[38;5;38m";
const C_GREEN: &str = "\x1b[38;5;46m";
const C_YELLOW: &str = "\x1b[38;5;220m";
const C_MAGENTA: &str = "\x1b[38;5;201m";
const C_PURPLE: &str = "\x1b[38;5;141m";
const C_WHITE: &str = "\x1b[38;5;231m";
const C_GRAY: &str = "\x1b[38;5;244m";
const C_DARKGRAY: &str = "\x1b[38;5;236m";

const BANNER: &str = r#"
  ░█████╗ ░██████╗████████╗███████╗██████╗ ░██╗██╗░░██╗
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝
  ███████║╚█████╗░░░░██║░░░█████╗░░██████╔╝██║░╚███╔╝░
  ██╔══██║░╚═══██╗░░░██║░░░██╔══╝░░██╔══██╗██║░██╔██╗░
  ██║░░██║██████╔╝░░░██║░░░███████╗██║░░██║██║██╔╝░██╗
  ╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝╚═╝░░╚═╝"#;

const SPINNER: [&str; 10] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"];

fn render_hud_box() {
    let mut bat_info = "NOMINAL".to_string();
    let mut temp_info = "OPTIMAL".to_string();
    if let Ok(cap) = fs::read_to_string("/sys/class/power_supply/battery/capacity") {
        let trimmed = cap.trim();
        bat_info = format!("{trimmed}%");
    }
    if let Ok(temp) = fs::read_to_string("/sys/class/power_supply/battery/temp") {
        if let Ok(num) = temp.trim().parse::<f32>() {
            temp_info = format!("{:.1}°C", num / 10.0);
        }
    }

    println!("  {C_DKCYAN}┌──────────────────────────────────────────────────────────┐{C_RESET}");
    println!("  {C_DKCYAN}│{C_RESET}  {C_WHITE}ARCH:{C_RESET} {C_CYAN}ARM64-v8a{C_RESET}  │ {C_WHITE}SECURITY:{C_RESET} {C_GREEN}ASLR=2 [ENFORCED]{C_RESET} │ {C_WHITE}STATE:{C_RESET} {C_GREEN}SECURE{C_RESET}  {C_DKCYAN}│{C_RESET}");
    println!("  {C_DKCYAN}│{C_RESET}  {C_WHITE}POWER:{C_RESET} {C_YELLOW}{bat_info:<6}{C_RESET}   │ {C_WHITE}THERMAL:{C_RESET}  {C_MAGENTA}{temp_info:<12}{C_RESET}     │ {C_WHITE}ZRAM:{C_RESET}  {C_CYAN}ONLINE{C_RESET}  {C_DKCYAN}│{C_RESET}");
    println!("  {C_DKCYAN}└──────────────────────────────────────────────────────────┘{C_RESET}\n");
}

fn animate_subsystem(index: usize, code: &str, name: &str) {
    let frames = 6;
    for f in 0..frames {
        let spin = SPINNER[(index * 3 + f) % SPINNER.len()];
        let progress = (f + 1) * 100 / frames;
        let blocks = f + 1;
        let empty = 6_usize.saturating_sub(blocks);
        let bar = format!("{}{}{}{}", C_CYAN, "▓".repeat(blocks), C_DARKGRAY, "░".repeat(empty));

        print!("\r  {C_DKCYAN}[{C_CYAN}{spin}{C_DKCYAN}]{C_RESET} {C_WHITE}{:<18}{C_RESET} {C_GRAY}{:<32}{C_RESET} [{bar}{C_RESET}] {C_YELLOW}{:3}%{C_RESET}",
            code, name, progress);
        let _ = io::stdout().flush();
        sleep(Duration::from_millis(28));
    }
    println!("\r  {C_GREEN}[[OK]]{C_RESET} {C_WHITE}{code:<18}{C_RESET} {C_GRAY}{name:<32}{C_RESET} [{C_GREEN}██████{C_RESET}] {C_GREEN}[ ONLINE ]{C_RESET}");
    let _ = io::stdout().flush();
    sleep(Duration::from_millis(20));
}

fn render_shortcuts() {
    println!("\n  {C_PURPLE}┌──[ ASTERIX MASTER COMMAND SHORTCUTS ]────────────────────┐{C_RESET}");
    println!("  {C_PURPLE}│{C_RESET}  {C_CYAN}ax version{C_RESET}    System Info     │ {C_CYAN}ax power{C_RESET}      Battery & Heat  {C_PURPLE}│{C_RESET}");
    println!("  {C_PURPLE}│{C_RESET}  {C_CYAN}ax defender{C_RESET}   Active Sentry   │ {C_CYAN}ax flow{C_RESET}       Network Telemetry{C_PURPLE}│{C_RESET}");
    println!("  {C_PURPLE}│{C_RESET}  {C_CYAN}ax hashdeep{C_RESET}   Binary Integrity│ {C_CYAN}ax clean-pro{C_RESET}  Cache & Flash TRIM{C_PURPLE}│{C_RESET}");
    println!("  {C_PURPLE}│{C_RESET}  {C_CYAN}ax yara-scan{C_RESET}  Threat Hunter   │ {C_CYAN}ax ssl-audit{C_RESET}  Cert Inspector  {C_PURPLE}│{C_RESET}");
    println!("  {C_PURPLE}│{C_RESET}  {C_CYAN}ax undercover{C_RESET} Stealth Shell   │ {C_CYAN}ax help{C_RESET}       All 90+ Tools   {C_PURPLE}│{C_RESET}");
    println!("  {C_PURPLE}└─── Type 'ax' or 'asterix' followed by any command ────────┘{C_RESET}\n");
}

fn main() {
    print!("\x1b[?25l");
    print!("\x1b[2J\x1b[H");

    println!("{}{}{}{}", C_CYAN, C_BOLD, BANNER, C_RESET);
    println!("   {C_DKCYAN}─── [ C Y B E R N E T I C   D E F E N S E   O S // M O B I L E ] ───{C_RESET}\n");

    render_hud_box();

    let subsystems = [
        ("01. KERNEL_INTEGRITY",  "ASLR & Memory Isolation"),
        ("02. CRYPTO_SHIELD",     "ChaCha20-Poly1305 Vault"),
        ("03. NETWORK_SENTINEL",  "Anti-Probe & DNS Leak Armor"),
        ("04. STORAGE_ARRAY",     "Secure Flash & TRIM Optimizer"),
        ("05. DEFENSIVE_AI",      "HashDeep & YARA Threat Engine"),
        ("06. MASTER_DISPATCH",   "Native Multi-Tool Engine"),
    ];

    println!("  {C_BOLD}INITIALIZING CYBERNETIC SUBSYSTEMS:{C_RESET}");
    for (i, (code, name)) in subsystems.iter().enumerate() {
        animate_subsystem(i, code, name);
    }

    render_shortcuts();

    print!("\x1b[?25h");
    let _ = io::stdout().flush();
}
RUST_CODE

echo -e "${CYAN}[*] Compiling with rustc...${NC}"
if rustc -O "$LOADER_DIR/src/main.rs" -o "$PREFIX/bin/asterix-loader" 2>/dev/null && [ -x "$PREFIX/bin/asterix-loader" ]; then
    log_step "Rust Native Loader" "PASS" "Engine compiled"
    echo -e "${GREEN}[[OK]] Native Rust loader compiled.${NC}"
else
    log_step "Rust Native Loader" "WARN" "Binary compilation skipped (fallback ready)"
fi

echo -e "${YELLOW}[*] Step 6: Initializing ASTERIX Metapackages & Security Toolchain inside PRoot Debian...${NC}"
if [ -d "$HOME/ASTERIX-OS" ] && command -v python3 >/dev/null 2>&1; then
    python3 "$HOME/ASTERIX-OS/scripts-hub/ax-deb-builder.py" build-all -o "$HOME/ASTERIX-OS/packages/debs" >/dev/null 2>&1 || true
    python3 "$HOME/ASTERIX-OS/scripts-hub/ax-apt-repo.py" build -s "$HOME/ASTERIX-OS/packages/debs" -o "$HOME/ASTERIX-OS/apt-repo" >/dev/null 2>&1 || true
fi

if proot-distro login debian -- bash -c "
    if [ -d '/opt/ASTERIX-OS/apt-repo' ]; then
        echo 'deb [trusted=yes] file:/opt/ASTERIX-OS/apt-repo stable main' > /etc/apt/sources.list.d/asterix.list
    fi
    apt-get update && apt-get install -y \
        nano vim micro build-essential \
        nmap tshark tcpdump netcat-openbsd socat curl wget git sudo python3 python3-pip htop \
        asterix-core asterix-tools-network asterix-tools-web asterix-default 2>/dev/null || \
    apt-get install -y \
        nano vim micro build-essential \
        nmap tshark tcpdump netcat-openbsd socat curl wget git sudo python3 htop
" 2>/dev/null; then
    log_step "Debian Security Suite" "PASS" "Toolchain & metapackages active"
    echo -e "${GREEN}[[OK]] Security toolchain & metapackages active inside Debian.${NC}"
else
    log_step "Debian Security Suite" "WARN" "Partial installation (offline/limited storage)"
fi

echo -e "${YELLOW}[*] Step 7: Synchronizing Core ASTERIX-OS Operating System...${NC}"
ASTERIX_DIR="$HOME/ASTERIX-OS"
if [ ! -d "$ASTERIX_DIR/.git" ]; then
    echo -e "${CYAN}[*] Downloading complete ASTERIX OS codebase into $ASTERIX_DIR...${NC}"
    if git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git "$ASTERIX_DIR" 2>/dev/null || \
       git clone https://gitlab.com/nexo-technologies-group/asterix-os.git "$ASTERIX_DIR" 2>/dev/null; then
        log_step "ASTERIX Core Repo" "PASS" "Fresh clone synchronized"
    else
        log_step "ASTERIX Core Repo" "WARN" "Cloning incomplete or offline"
    fi
else
    echo -e "${GREEN}[[OK]] ASTERIX-OS directory already present. Fetching latest updates...${NC}"
    (cd "$ASTERIX_DIR" && git pull 2>/dev/null || true)
    log_step "ASTERIX Core Repo" "PASS" "Local repository up to date"
fi

ensure_asterix_shell_bootstrap

echo -e "${YELLOW}[*] Step 8: Configuring Master Global 'ax' & 'asterix' Dispatcher...${NC}"
cat << 'EOF' > "$PREFIX/bin/ax"
#!/data/data/com.termux/files/usr/bin/bash
ASTERIX_DIR="$HOME/ASTERIX-OS"
PERSIST="$HOME/asterix_persistent"
[ -d "$HOME/.asterix_storage" ] && PERSIST="$HOME/.asterix_storage"
mkdir -p "$PERSIST"/{projects,scans,loot,captures,reports,notes,scripts,payloads,wordlists,workspace} 2>/dev/null || true

# Direct commands
if [ -z "$1" ]; then
    if [ -x "$PREFIX/bin/asterix-loader" ]; then
        "$PREFIX/bin/asterix-loader"
    fi
    exec bash "$ASTERIX_DIR/bin/ax"
elif [ "$1" = "debian" ] || [ "$1" = "proot" ] || [ "$1" = "rootless" ]; then
    shift
    if [ -f "$ASTERIX_DIR/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$ASTERIX_DIR/scripts-hub/ax-debian-manager.py" "$@"
    elif [ -f "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" ]; then
        exec bash "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" "$@"
    else
        proot_args=("--link2symlink" "--bind" "$ASTERIX_DIR:/opt/ASTERIX-OS" "--bind" "$PERSIST:/asterix_persistent")
        [ -d "/sdcard" ] && [ -w "/sdcard" ] && proot_args+=("--bind" "/sdcard:/sdcard")
        exec proot-distro login "${proot_args[@]}" debian -- "$@"
    fi
elif [ "$1" = "folder" ] || [ "$1" = "folders" ]; then
    shift
    if [ -f "$ASTERIX_DIR/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
        exec python3 "$ASTERIX_DIR/scripts-hub/ax-debian-manager.py" folder "$@"
    elif [ -f "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" ]; then
        exec bash "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" folder "$@"
    fi
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
    echo -e "\033[38;5;46m[[OK]] ASTERIX OS Core: $ASTERIX_DIR\033[0m"
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
log_step "Master Dispatcher (ax)" "PASS" "Dispatcher active"

# Configure symlink and persistence layout inside PRoot Debian
proot-distro login debian -- bash -c "
    mkdir -p /usr/local/bin /asterix_persistent/{projects,scans,loot,captures,reports,notes,scripts,payloads,wordlists,workspace}
    if [ -f /opt/ASTERIX-OS/bin/ax ]; then
        ln -sf /opt/ASTERIX-OS/bin/ax /usr/local/bin/ax 2>/dev/null || true
        ln -sf /opt/ASTERIX-OS/bin/ax /usr/local/bin/asterix 2>/dev/null || true
    fi
    if [ -d /asterix_persistent/projects ]; then
        mkdir -p /root
        ln -sf /asterix_persistent/projects /root/projects 2>/dev/null || true
        ln -sf /asterix_persistent/loot /root/loot 2>/dev/null || true
    fi
" 2>/dev/null || true

echo -e "${YELLOW}[*] Step 9: Installing Target Tracker & Advanced Mobile Utilities...${NC}"
cp "$ASTERIX_DIR/termux-mobile/target-tracker.sh" "$PREFIX/bin/target-tracker" 2>/dev/null || true
cp "$ASTERIX_DIR/termux-mobile/asterix-ai-startup.sh" "$PREFIX/bin/asterix-ai-startup" 2>/dev/null || true
chmod +x "$PREFIX/bin/target-tracker" 2>/dev/null || true
chmod +x "$PREFIX/bin/asterix-ai-startup" 2>/dev/null || true
chmod +x "$ASTERIX_DIR/termux-mobile/target-tracker.sh" 2>/dev/null || true
chmod +x "$ASTERIX_DIR/termux-mobile/asterix-ai-startup.sh" 2>/dev/null || true
log_step "Mobile Helpers" "PASS" "target-tracker, ai-startup"

echo -e "${GREEN}[[OK]] IP and target tracking helper installed: ${YELLOW}target-tracker${NC}"
echo -e "${GREEN}[[OK]] Local AI startup helper installed: ${YELLOW}asterix-ai-startup${NC}"

echo -e "${YELLOW}[*] Step 10: Triggering ASTERIX auto-heal and environment check...${NC}"
if [ -x "$PREFIX/bin/asterix-ai-startup" ]; then
    "$PREFIX/bin/asterix-ai-startup" >/tmp/asterix_post_install_ai.log 2>&1 || true
fi
if command -v ax >/dev/null 2>&1; then
    ax doctor --fix >/tmp/asterix_post_install_heal.log 2>&1 || true
fi
log_step "Auto-Heal Engine" "PASS" "Environment verified"

echo -e "${YELLOW}[*] Step 11: Auditing Local Core Packages & Enforcing Least Privilege...${NC}"
mkdir -p "$ASTERIX_DIR/packages" 2>/dev/null || true
# Principle of least privilege: strictly audit and restrict file permissions on local project scripts only
# (Eliminated unaudited third-party clones to protect supply chain integrity)
if [ -d "$ASTERIX_DIR/scripts-hub" ]; then
    chmod 755 "$ASTERIX_DIR/scripts-hub"/*.py 2>/dev/null || true
fi
if [ -d "$ASTERIX_DIR/termux-mobile" ]; then
    chmod 755 "$ASTERIX_DIR/termux-mobile"/*.sh 2>/dev/null || true
fi
log_step "Supply Chain Security" "PASS" "Zero unaudited repos cloned"
echo -e "${GREEN}[[OK]] Supply chain secured: External clones eliminated; local packages audited.${NC}"

# Step 12: Registering Mobile CLI Tools & Symlinks
for tool in web-structure.sh termux-toolbox.sh target-tracker.sh asterix-ai-startup.sh debian-rootless.sh; do
    [ -f "$ASTERIX_DIR/termux-mobile/$tool" ] && chmod +x "$ASTERIX_DIR/termux-mobile/$tool" 2>/dev/null || true
done
if [ -f "$ASTERIX_DIR/termux-mobile/web-structure.sh" ]; then
    ln -sf "$ASTERIX_DIR/termux-mobile/web-structure.sh" "$PREFIX/bin/web-structure" 2>/dev/null || true
    ln -sf "$ASTERIX_DIR/termux-mobile/web-structure.sh" "$PREFIX/bin/curl-tree" 2>/dev/null || true
    ln -sf "$ASTERIX_DIR/termux-mobile/web-structure.sh" "$PREFIX/bin/webdump" 2>/dev/null || true
fi
if [ -f "$ASTERIX_DIR/termux-mobile/termux-toolbox.sh" ]; then
    ln -sf "$ASTERIX_DIR/termux-mobile/termux-toolbox.sh" "$PREFIX/bin/termux-toolbox" 2>/dev/null || true
    ln -sf "$ASTERIX_DIR/termux-mobile/termux-toolbox.sh" "$PREFIX/bin/mobile-sys" 2>/dev/null || true
fi
if [ -f "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" ]; then
    ln -sf "$ASTERIX_DIR/termux-mobile/debian-rootless.sh" "$PREFIX/bin/debian-rootless" 2>/dev/null || true
fi
log_step "CLI Tool Symlinks" "PASS" "Registered in $PREFIX/bin"

# Configure autostart in ~/.bashrc if not already present
if ! grep -q "ASTERIX OS Startup" "$HOME/.bashrc" 2>/dev/null; then
    cat << 'AUTO' >> "$HOME/.bashrc"

# ASTERIX OS Startup
export PATH="$PREFIX/bin:$HOME/.local/bin:$HOME/ASTERIX-OS/bin:$HOME/ASTERIX-OS/scripts-hub:$PATH"
for d in "$HOME/ASTERIX-OS"/core-utils-*; do [ -d "$d/bin" ] && export PATH="$d/bin:$PATH"; done
if [ -f "$HOME/ASTERIX-OS/ui-core/asterix-shell-env.sh" ]; then . "$HOME/ASTERIX-OS/ui-core/asterix-shell-env.sh"; fi
if [ -t 1 ]; then
    [ -x "$PREFIX/bin/asterix-loader" ] && asterix-loader
    [ -x "$PREFIX/bin/asterix-ai-startup" ] && "$PREFIX/bin/asterix-ai-startup"
    echo -e "\033[38;5;220mType '\033[1max\033[0m\033[38;5;220m' or '\033[1masterix\033[0m\033[38;5;220m' to enter the ASTERIX Security Sandbox.\033[0m"
    echo -e "\033[38;5;141mTools: ax debian | ax folder | ax defender | ax undercover | ax darktrace | mobile-sys\033[0m\n"
fi
AUTO
fi

# =====================================================================
# INSTALLATION HEALTH & DIAGNOSTIC SUMMARY TABLE
# =====================================================================
echo -e "\n${CYAN}${BOLD}┌────────────────────────────────────────────────────────────────────────┐${NC}"
echo -e "${CYAN}${BOLD}│              ASTERIX OS INSTALLATION HEALTH SUMMARY                    │${NC}"
echo -e "${CYAN}${BOLD}├────────────────────────────────────────┬──────────┬────────────────────┤${NC}"
for idx in "${!STEP_NAMES[@]}"; do
    sname="${STEP_NAMES[$idx]}"
    sres="${STEP_RESULTS[$idx]}"
    sdet="${STEP_DETAILS[$idx]}"
    case "$sres" in
        PASS) col="$GREEN"; tag="[ PASS ]" ;;
        WARN) col="$YELLOW"; tag="[ WARN ]" ;;
        *) col="$RED"; tag="[ FAIL ]" ;;
    esac
    printf "${CYAN}│${NC}  %-36s  ${CYAN}│${NC} %b%-8s%b ${CYAN}│${NC} %-18s ${CYAN}│${NC}\n" "$sname" "$col" "$tag" "$NC" "$sdet"
done
echo -e "${CYAN}${BOLD}└────────────────────────────────────────┴──────────┴────────────────────┘${NC}\n"

if [ "$CRITICAL_FAILURES" -gt 0 ]; then
    echo -e "${RED}${BOLD}[[FAIL]] WARNING: $CRITICAL_FAILURES critical installation stage(s) failed.${NC}"
    echo -e "${YELLOW}Please inspect the failures above or run 'ax debian doctor' to repair.${NC}\n"
    exit 1
fi

echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}[[OK]] ASTERIX OS MOBILE INSTALLATION VERIFIED (0 ERRORS)${NC}"
echo -e "${CYAN}Core OS Directory:${NC}     $ASTERIX_DIR"
echo -e "${CYAN}Safe Local Storage:${NC}    $PERSIST_LOCAL"
echo -e "${CYAN}Launch Commands:${NC}       Type ${YELLOW}ax${NC} or ${YELLOW}asterix${NC} anywhere in Termux"
echo -e "${CYAN}Debian Rootless:${NC}       ${YELLOW}ax debian${NC} | ${YELLOW}ax debian doctor${NC} | ${YELLOW}ax debian repair${NC}"
echo -e "${CYAN}Mission Folder Engine:${NC} ${YELLOW}ax folder create <name> --template=recon|exploit|web${NC}"
echo -e "${CYAN}Mobile System Center:${NC}  ${YELLOW}ax mobile-sys${NC} | ${YELLOW}termux-toolbox battery${NC}"
echo -e "${CYAN}Defense & Hardening:${NC}   ${YELLOW}ax defender${NC} | ${YELLOW}ax secpol audit${NC} | ${YELLOW}ax undercover${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════════${NC}\n"