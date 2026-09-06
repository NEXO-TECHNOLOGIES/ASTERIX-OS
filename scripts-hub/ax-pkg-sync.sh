#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Package & External Dependency Synchronizer
# Manages external cybersecurity tool repositories (Anti-Network, THUNDER)
# =====================================================================

# Disable interactive git auth prompts so background/curl installs never hang
export GIT_TERMINAL_PROMPT=0

C_RESET='\033[0m'
C_BOLD='\033[1m'
C_GREEN='\033[38;5;46m'
C_CYAN='\033[38;5;51m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_MAGENTA='\033[38;5;201m'
C_GRAY='\033[38;5;242m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AX_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PACKAGES_DIR="${AX_ROOT}/packages"
mkdir -p "$PACKAGES_DIR"

# Detect target binary install directory
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    INSTALL_DIR="$PREFIX/bin"
    SUDO=""
elif [ "$(id -u)" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    SUDO=""
elif command -v sudo >/dev/null 2>&1; then
    INSTALL_DIR="/usr/local/bin"
    SUDO="sudo"
else
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    SUDO=""
fi

# Package Registry Definitions: name|repo_url|display_name|description
PACKAGES=(
    "Asterix-Anti-Network-Attack|https://github.com/alexhack235-code/Asterix-Anti-Network-Attack.git|Anti-Network Attack Suite|Active ARP, SYN flood, DNS hijack, port scan traps, anti-reverse sentinel, email shield"
    "THUNDER|https://github.com/alexhack235-code/THUNDER.git|THUNDER Enterprise Defender|Wi-Fi deauth defense, reverse shell monitor, ransomware honeypots, BadUSB shield, 105-endpoint IP rotator"
    "ASTERISK-Web-Frality-scanner|https://github.com/Alex-dot-dot/ASTERISK-Web-Frality-scanner.git|WSCAN Web Weakness Scanner|Web vulnerability auditor (SQLi, XSS, headers, sensitive files, cookies, open redirect)"
    "LIGHTNING-|https://github.com/alexhack235-code/LIGHTNING-.git|LIGHTNING WAF & Web SOC|Autonomous WAF reverse-proxy, real-time Web SOC dashboard, IDS, honeypot, threat feeds, DLP (16-module defense stack)"
    "APEX-OVERDRIVE-|https://github.com/alexhack235-code/APEX-OVERDRIVE-.git|APEX OVERDRIVE Kernel Gaming Suite|Low-latency eSports kernel accelerator, sub-0.5ms timer resolution, standby RAM purge, TCP BBR anti-lag"
)

# Helper: Find actual directory inside cloned repo (handles nested folders)
resolve_package_path() {
    local pkg_name="$1"
    local base="${PACKAGES_DIR}/${pkg_name}"
    if [ ! -d "$base" ]; then
        echo ""
        return
    fi
    # Check for upper-case nested folder
    if [ "$pkg_name" = "Asterix-Anti-Network-Attack" ]; then
        if [ -d "${base}/ASTERIX-ANTI-NETWORK ATTACK" ]; then
            echo "${base}/ASTERIX-ANTI-NETWORK ATTACK"
            return
        fi
    elif [ "$pkg_name" = "THUNDER" ]; then
        if [ -d "${base}/THUNDER" ]; then
            echo "${base}/THUNDER"
            return
        fi
    fi
    echo "$base"
}

print_header() {
    echo -e "${C_CYAN}${C_BOLD}"
    cat << 'EOF'
  ___   _____ ______ ______ ____     ____  __ _____
 /   | / ___//_  __// ____// __ \   / __ \/ //_/   |
/ /| | \__ \  / /  / __/  / /_/ /  / /_/ / ,< / /| |
/ ___ |___/ / / /  / /___ / _, _/  / ____/ /| / ___ |
/_/  |_/____/ /_/  /_____//_/ |_|  /_/   /_/ |/_/  |_|
       PACKAGE & DEPENDENCY SYNCHRONIZER
EOF
    echo -e "${C_RESET}"
}

cmd_list() {
    print_header
    echo -e "${C_BOLD}Managed Security Packages Registry:${C_RESET}\n"
    printf "  %-30s %-12s %-45s\n" "PACKAGE NAME" "STATUS" "REPOSITORY URL"
    printf "  %-30s %-12s %-45s\n" "------------" "------" "--------------"

    for entry in "${PACKAGES[@]}"; do
        IFS='|' read -r pkg_name repo_url display_name desc <<< "$entry"
        pkg_path=$(resolve_package_path "$pkg_name")
        if [ -n "$pkg_path" ] && [ -d "$pkg_path" ]; then
            status_str="${C_GREEN}[INSTALLED]${C_RESET}"
        else
            status_str="${C_YELLOW}[MISSING]${C_RESET}"
        fi
        printf "  %-30s %-20b %-45s\n" "$pkg_name" "$status_str" "$repo_url"
        echo -e "    ${C_GRAY}↳ ${desc}${C_RESET}\n"
    done
}

cmd_status() {
    print_header
    echo -e "${C_BOLD}Package Synchronizer Status:${C_RESET}\n"
    for entry in "${PACKAGES[@]}"; do
        IFS='|' read -r pkg_name repo_url display_name desc <<< "$entry"
        pkg_base="${PACKAGES_DIR}/${pkg_name}"
        pkg_path=$(resolve_package_path "$pkg_name")

        echo -e "${C_CYAN}▶ ${C_BOLD}${display_name}${C_RESET} (${pkg_name})"
        if [ -d "${pkg_base}/.git" ]; then
            cd "${pkg_base}"
            commit_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
            branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
            last_commit=$(git log -1 --format="%cd (%cr)" --date=short 2>/dev/null || echo "unknown")
            echo -e "    Status:      ${C_GREEN}Active (Git Cloned)${C_RESET}"
            echo -e "    Path:        ${pkg_path}"
            echo -e "    Branch:      ${C_YELLOW}${branch}${C_RESET} @ ${C_MAGENTA}${commit_hash}${C_RESET}"
            echo -e "    Last Update: ${last_commit}"
            cd "$AX_ROOT"
        else
            echo -e "    Status:      ${C_RED}Not Installed${C_RESET}"
            echo -e "    Action:      Run ${C_YELLOW}ax pkg sync${C_RESET} to download"
        fi
        echo ""
    done
}

build_sentinel() {
    local sentinel_dir="$1"
    if [ ! -d "$sentinel_dir" ]; then
        return
    fi
    echo -e "    ${C_CYAN}[*] Compiling anti-reverse-sentinel...${C_RESET}"
    cd "$sentinel_dir"
    local bin_out=""
    if command -v cargo >/dev/null 2>&1; then
        cargo build --release 2>/dev/null || true
        if [ -f "target/release/anti-reverse-sentinel" ]; then
            bin_out="target/release/anti-reverse-sentinel"
        fi
    fi
    if [ -z "$bin_out" ] && command -v rustc >/dev/null 2>&1; then
        rustc -O -C lto=yes src/main.rs -o anti-reverse-sentinel 2>/dev/null || true
        if [ -f "anti-reverse-sentinel" ]; then
            bin_out="anti-reverse-sentinel"
        fi
    fi

    if [ -n "$bin_out" ] && [ -f "$bin_out" ]; then
        $SUDO cp "$bin_out" "${INSTALL_DIR}/anti-reverse-sentinel" 2>/dev/null || true
        $SUDO chmod 755 "${INSTALL_DIR}/anti-reverse-sentinel" 2>/dev/null || true
        $SUDO ln -sf "${INSTALL_DIR}/anti-reverse-sentinel" "${INSTALL_DIR}/anti-rev" 2>/dev/null || true
        echo -e "    ${C_GREEN}[✔] anti-reverse-sentinel installed to ${INSTALL_DIR}${C_RESET}"
    else
        echo -e "    ${C_YELLOW}[!] rustc/cargo not available or compilation skipped.${C_RESET}"
    fi
    cd "$AX_ROOT"
}

cmd_sync() {
    print_header
    local target_pkg="$1"

    if ! command -v git >/dev/null 2>&1; then
        echo -e "${C_RED}[!] Error: 'git' is required to synchronize packages.${C_RESET}"
        echo -e "    Install git: ${C_YELLOW}apt install git${C_RESET} or ${C_YELLOW}pkg install git${C_RESET}"
        exit 1
    fi

    echo -e "${C_CYAN}[*] Synchronizing packages into: ${C_YELLOW}${PACKAGES_DIR}${C_RESET}"
    echo -e "${C_CYAN}[*] Binary install directory:   ${C_YELLOW}${INSTALL_DIR}${C_RESET}\n"

    for entry in "${PACKAGES[@]}"; do
        IFS='|' read -r pkg_name repo_url display_name desc <<< "$entry"

        # If specific package requested, skip others
        if [ -n "$target_pkg" ] && [ "$target_pkg" != "$pkg_name" ] && [ "$target_pkg" != "all" ]; then
            continue
        fi

        pkg_base="${PACKAGES_DIR}/${pkg_name}"
        echo -e "${C_YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${C_RESET}"
        echo -e "${C_BOLD}▶ Processing: ${C_CYAN}${display_name}${C_RESET} (${pkg_name})"

        if [ -d "${pkg_base}/.git" ]; then
            echo -e "  ${C_CYAN}[*] Repository exists. Pulling latest updates...${C_RESET}"
            cd "${pkg_base}"
            git pull --ff-only 2>/dev/null || git pull --rebase 2>/dev/null || echo -e "  ${C_YELLOW}[!] Git pull encountered conflicts or is up-to-date.${C_RESET}"
            cd "$AX_ROOT"
        else
            echo -e "  ${C_CYAN}[*] Cloning from ${repo_url}...${C_RESET}"
            if ! GIT_TERMINAL_PROMPT=0 git clone --depth 1 "$repo_url" "$pkg_base" 2>/dev/null; then
                echo -e "  ${C_YELLOW}[!] Warning: Repository ${pkg_name} is private or unreachable. Skipping without error.${C_RESET}"
                continue
            fi
        fi

        pkg_path=$(resolve_package_path "$pkg_name")
        if [ -d "$pkg_path" ]; then
            echo -e "  ${C_GREEN}[✔] Resolved package path:${C_RESET} ${pkg_path}"

            # Make all shell scripts executable
            find "$pkg_path" -maxdepth 3 -name "*.sh" -exec chmod +x {} + 2>/dev/null || true

            # Package-specific installations
            if [ "$pkg_name" = "Asterix-Anti-Network-Attack" ]; then
                # Link anti-net scripts into INSTALL_DIR
                local scripts=(
                    "anti-net-shield.sh:anti-net"
                    "anti-email-shield.sh:anti-email"
                    "anti-arp-spoof.sh:anti-arp"
                    "anti-synflood.sh:anti-syn"
                    "anti-dns-hijack.sh:anti-dns"
                    "anti-portscan.sh:anti-scan"
                )
                for pair in "${scripts[@]}"; do
                    IFS=':' read -r src alias_name <<< "$pair"
                    if [ -f "${pkg_path}/${src}" ]; then
                        $SUDO cp "${pkg_path}/${src}" "${INSTALL_DIR}/${src}" 2>/dev/null || true
                        $SUDO chmod 755 "${INSTALL_DIR}/${src}" 2>/dev/null || true
                        $SUDO ln -sf "${INSTALL_DIR}/${src}" "${INSTALL_DIR}/${alias_name}" 2>/dev/null || true
                        echo -e "  ${C_GREEN}[✔] Linked command:${C_RESET} ${alias_name}"
                    fi
                done

                # Build sentinel
                if [ -d "${pkg_path}/anti-reverse-sentinel" ]; then
                    build_sentinel "${pkg_path}/anti-reverse-sentinel"
                fi

            elif [ "$pkg_name" = "THUNDER" ]; then
                # Link THUNDER scripts into INSTALL_DIR
                if [ -f "${pkg_path}/thunder.sh" ]; then
                    $SUDO cp "${pkg_path}/thunder.sh" "${INSTALL_DIR}/thunder.sh" 2>/dev/null || true
                    $SUDO chmod 755 "${INSTALL_DIR}/thunder.sh" 2>/dev/null || true
                    $SUDO ln -sf "${INSTALL_DIR}/thunder.sh" "${INSTALL_DIR}/thunder" 2>/dev/null || true
                    echo -e "  ${C_GREEN}[✔] Linked command:${C_RESET} thunder"
                fi
                if [ -f "${pkg_path}/ip-rotator/ip_rotator.sh" ]; then
                    $SUDO chmod +x "${pkg_path}/ip-rotator/ip_rotator.sh" 2>/dev/null || true
                    $SUDO ln -sf "${pkg_path}/ip-rotator/ip_rotator.sh" "${INSTALL_DIR}/ip-rotator" 2>/dev/null || true
                    echo -e "  ${C_GREEN}[✔] Linked command:${C_RESET} ip-rotator"
                fi
            elif [ "$pkg_name" = "ASTERISK-Web-Frality-scanner" ]; then
                if [ -f "${pkg_path}/run.sh" ]; then
                    $SUDO chmod +x "${pkg_path}/run.sh" "${pkg_path}/wscan.py" 2>/dev/null || true
                    $SUDO cp "${pkg_path}/run.sh" "${INSTALL_DIR}/wscan" 2>/dev/null || true
                    $SUDO chmod 755 "${INSTALL_DIR}/wscan" 2>/dev/null || true
                    $SUDO ln -sf "${INSTALL_DIR}/wscan" "${INSTALL_DIR}/asterisk-wscan" 2>/dev/null || true
                    echo -e "  ${C_GREEN}[✔] Linked command:${C_RESET} wscan"
                fi
            elif [ "$pkg_name" = "LIGHTNING-" ]; then
                local lightning_main="${pkg_path}/Lightning/main.py"
                if [ ! -f "$lightning_main" ]; then
                    lightning_main="${pkg_path}/main.py"
                fi
                if [ -f "$lightning_main" ]; then
                    local lightning_dir
                    lightning_dir=$(dirname "$lightning_main")
                    cat > /tmp/lightning-launcher.sh << LAUNCHER_EOF
#!/usr/bin/env bash
LIGHTNING_DIR="${lightning_dir}"
cd "\$LIGHTNING_DIR" || exit 1
if ! python3 -c "import requests" 2>/dev/null; then
    pip3 install requests --quiet 2>/dev/null || true
fi
exec python3 main.py "\$@"
LAUNCHER_EOF
                    $SUDO cp /tmp/lightning-launcher.sh "${INSTALL_DIR}/lightning" 2>/dev/null || true
                    $SUDO chmod 755 "${INSTALL_DIR}/lightning" 2>/dev/null || true
                    $SUDO ln -sf "${INSTALL_DIR}/lightning" "${INSTALL_DIR}/ax-lightning" 2>/dev/null || true
                    echo -e "  ${C_GREEN}[✔] Linked commands:${C_RESET} lightning, ax-lightning"
                fi
            elif [ "$pkg_name" = "APEX-OVERDRIVE-" ]; then
                if [ -f "${pkg_path}/Launch-ApexOverdrive.sh" ]; then
                    $SUDO chmod +x "${pkg_path}/Launch-ApexOverdrive.sh" "${pkg_path}/Launch-ApexOverdrive-Termux.sh" 2>/dev/null || true
                    if [ -d "${pkg_path}/rust_core" ] && command -v cargo >/dev/null 2>&1; then
                        (cd "${pkg_path}/rust_core" && cargo build --release >/dev/null 2>&1 || true)
                    fi
                    $SUDO ln -sf "${pkg_path}/Launch-ApexOverdrive.sh" "${INSTALL_DIR}/apex-overdrive" 2>/dev/null || true
                    $SUDO ln -sf "${pkg_path}/Launch-ApexOverdrive.sh" "${INSTALL_DIR}/ax-overdrive" 2>/dev/null || true
                    $SUDO ln -sf "${pkg_path}/Launch-ApexOverdrive.sh" "${INSTALL_DIR}/overdrive" 2>/dev/null || true
                    echo -e "  ${C_GREEN}[✔] Linked commands:${C_RESET} apex-overdrive, ax-overdrive, overdrive"
                fi
            fi
        fi
        echo ""
    done

    echo -e "${C_GREEN}${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}"
    echo -e "${C_GREEN}${C_BOLD}[✔] All Security & Performance Packages Synchronized Successfully!${C_RESET}"
    echo -e "${C_CYAN}Commands ready to use:${C_RESET}"
    echo -e "  ${C_YELLOW}ax anti-net${C_RESET}     - Anti-Network Attack Master Dashboard"
    echo -e "  ${C_YELLOW}ax thunder${C_RESET}      - THUNDER Enterprise Network & Device Defender"
    echo -e "  ${C_YELLOW}ax anti-email${C_RESET}   - Email & Account Security Shield"
    echo -e "  ${C_YELLOW}ax ip-rotator${C_RESET}   - 105-Endpoint IP Rotator & MAC Changer"
    echo -e "  ${C_YELLOW}ax anti-arp${C_RESET}     - ARP Poisoning & Gateway Armor"
    echo -e "  ${C_YELLOW}ax anti-syn${C_RESET}     - TCP SYN Flood Shield"
    echo -e "  ${C_YELLOW}ax anti-dns${C_RESET}     - DNS Hijacking & Resolver Armor"
    echo -e "  ${C_YELLOW}ax anti-scan${C_RESET}    - Port Scan Traps & Dynamic Quarantine"
    echo -e "  ${C_YELLOW}ax anti-rev${C_RESET}     - Anti-Reverse Engineering Sentinel"
    echo -e "  ${C_YELLOW}ax wscan${C_RESET}        - WSCAN Web Weakness & Vulnerability Scanner"
    echo -e "  ${C_YELLOW}ax lightning${C_RESET}    - LIGHTNING WAF Proxy, Web SOC Dashboard & IDS"
    echo -e "  ${C_YELLOW}ax overdrive${C_RESET}    - APEX OVERDRIVE Kernel Gaming & FPS Accelerator"
    echo -e "${C_GREEN}${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}\n"
}

# CLI Router
case "${1:-sync}" in
    list|ls)
        cmd_list
        ;;
    status|check)
        cmd_status
        ;;
    sync|install|get)
        shift || true
        cmd_sync "$@"
        ;;
    update|pull)
        shift || true
        cmd_sync "$@"
        ;;
    build)
        print_header
        echo -e "${C_CYAN}[*] Rebuilding package native binaries...${C_RESET}"
        for entry in "${PACKAGES[@]}"; do
            IFS='|' read -r pkg_name repo_url display_name desc <<< "$entry"
            pkg_path=$(resolve_package_path "$pkg_name")
            if [ -d "${pkg_path}/anti-reverse-sentinel" ]; then
                build_sentinel "${pkg_path}/anti-reverse-sentinel"
            fi
        done
        ;;
    help|--help|-h)
        print_header
        echo -e "${C_BOLD}Usage:${C_RESET} ax pkg <command> [options]\n"
        echo -e "  ${C_YELLOW}status${C_RESET}   Check git branch, commit hash, and health of packages"
        echo -e "  ${C_YELLOW}sync${C_RESET}     Clone or pull latest packages and install symlinks"
        echo -e "  ${C_YELLOW}list${C_RESET}     List registered packages in the ASTERIX catalog"
        echo -e "  ${C_YELLOW}update${C_RESET}   Update all packages to latest upstream commits"
        echo -e "  ${C_YELLOW}build${C_RESET}    Rebuild native components (Rust sentinel, etc.)"
        echo ""
        ;;
    *)
        cmd_sync "$@"
        ;;
esac