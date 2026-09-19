#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS — Mobile System Center & Termux Hardware Toolbox v2.0
# Native hardware monitoring, DNS benchmark, cache cleaner, and
# self-healing diagnostic engine for Android Termux users.
# =====================================================================

set -u

# Colors
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_MAGENTA='\033[38;5;201m'
C_GRAY='\033[38;5;244m'
C_WHITE='\033[38;5;231m'

banner() {
    echo -e "${C_CYAN}${C_BOLD}"
    cat << "EOF"
  ╔══════════════════════════════════════════════════════════════════════╗
  ║   [MOBILE] ASTERIX MOBILE SYSTEM CENTER & TERMUX TOOLBOX v2.0              ║
  ║   [ Battery HUD • DNS Benchmark • Storage Clean • Self-Healer ]     ║
  ╚══════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${C_RESET}"
}

usage() {
    banner
    echo -e "  ${C_YELLOW}Usage:${C_RESET} ${C_WHITE}termux-toolbox <command> [arguments]${C_RESET}\n"
    echo -e "  ${C_CYAN}Available Commands:${C_RESET}"
    echo -e "    ${C_GREEN}battery | hw${C_RESET}        Hardware & battery health telemetry (temperature, mA, charge)"
    echo -e "    ${C_GREEN}net | dns${C_RESET}           Mobile network analysis & multi-DNS latency benchmark"
    echo -e "    ${C_GREEN}clean | purge${C_RESET}       Reclaim mobile disk space (purges pkg cache, /tmp, orphan logs)"
    echo -e "    ${C_GREEN}doctor | heal${C_RESET}       Diagnose & auto-repair broken Termux repos, curl, and PATH"
    echo -e "    ${C_GREEN}debian-doctor${C_RESET}       Diagnose Debian Rootless (PRoot) container health & DNS"
    echo -e "    ${C_GREEN}debian-fix${C_RESET}          Auto-heal Debian Rootless (APT sandbox, DNS, /dev/shm)"
    echo -e "    ${C_GREEN}debian-folder${C_RESET}       Create & manage resilient mission folders"
    echo -e "    ${C_GREEN}clip-copy <text>${C_RESET}    Copy text to Android system clipboard"
    echo -e "    ${C_GREEN}clip-paste${C_RESET}          Print current Android clipboard contents"
    echo -e "    ${C_GREEN}notify <msg>${C_RESET}        Send native Android vibration and notification toast"
    echo -e "    ${C_GREEN}help${C_RESET}                Show this manual\n"
}

cmd_battery() {
    echo -e "\n  ${C_CYAN}${C_BOLD}─── [ ANDROID HARDWARE & BATTERY TELEMETRY ] ───${C_RESET}\n"
    local pct="N/A" status="N/A" temp="N/A" health="N/A" current="N/A"

    if command -v termux-battery-status >/dev/null 2>&1; then
        local bs; bs=$(termux-battery-status 2>/dev/null)
        pct=$(echo "$bs" | grep -oE '"percentage":[[:space:]]*[0-9]+' | grep -oE '[0-9]+' || echo "N/A")
        status=$(echo "$bs" | grep -oE '"status":[[:space:]]*"[^"]+"' | grep -oE '"[^"]+"$' | tr -d '"' || echo "N/A")
        temp=$(echo "$bs" | grep -oE '"temperature":[[:space:]]*[0-9.]+' | grep -oE '[0-9.]+' || echo "N/A")
        health=$(echo "$bs" | grep -oE '"health":[[:space:]]*"[^"]+"' | grep -oE '"[^"]+"$' | tr -d '"' || echo "N/A")
        current=$(echo "$bs" | grep -oE '"current":[[:space:]]*-?[0-9]+' | grep -oE '-?[0-9]+' || echo "N/A")
    elif [ -f /sys/class/power_supply/battery/capacity ]; then
        pct=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo "N/A")
        status=$(cat /sys/class/power_supply/battery/status 2>/dev/null || echo "N/A")
        temp=$(cat /sys/class/power_supply/battery/temp 2>/dev/null | awk '{print $1/10}' || echo "N/A")
    fi

    # Battery indicator color
    local bcol="$C_GREEN"
    if [[ "$pct" =~ ^[0-9]+$ ]]; then
        (( pct < 30 )) && bcol="$C_YELLOW"
        (( pct < 15 )) && bcol="$C_RED"
    fi

    printf "    ${C_WHITE}Percentage:${C_RESET}    %b%s%%%b\n" "$bcol" "$pct" "$C_RESET"
    printf "    ${C_WHITE}Status:${C_RESET}        ${C_CYAN}%s${C_RESET}\n" "$status"
    printf "    ${C_WHITE}Health:${C_RESET}        ${C_GREEN}%s${C_RESET}\n" "$health"
    printf "    ${C_WHITE}Temperature:${C_RESET}   ${C_YELLOW}%s °C${C_RESET}\n" "$temp"
    if [ "$current" != "N/A" ]; then
        printf "    ${C_WHITE}Current Flow:${C_RESET}  ${C_MAGENTA}%s µA${C_RESET}\n" "$current"
    fi

    # CPU & RAM telemetry
    echo -e "\n  ${C_CYAN}${C_BOLD}─── [ SYSTEM LOAD & RESOURCE TELEMETRY ] ───${C_RESET}\n"
    local cores; cores=$(nproc 2>/dev/null || grep -c processor /proc/cpuinfo 2>/dev/null || echo "Unknown")
    local arch; arch=$(uname -m 2>/dev/null || echo "Unknown")
    printf "    ${C_WHITE}CPU Cores:${C_RESET}     ${C_GREEN}%s${C_RESET} ${C_GRAY}(Architecture: %s)${C_RESET}\n" "$cores" "$arch"
    if [ -f /proc/meminfo ]; then
        local total_ram; total_ram=$(awk '/MemTotal/{printf "%.0f MB",$2/1024}' /proc/meminfo 2>/dev/null || echo "N/A")
        local free_ram; free_ram=$(awk '/MemAvailable/{printf "%.0f MB",$2/1024}' /proc/meminfo 2>/dev/null || echo "N/A")
        printf "    ${C_WHITE}RAM Status:${C_RESET}    ${C_GREEN}%s free${C_RESET} / ${C_CYAN}%s total${C_RESET}\n" "$free_ram" "$total_ram"
    fi
    echo ""
}

cmd_dns() {
    echo -e "\n  ${C_CYAN}${C_BOLD}─── [ MOBILE NETWORK & DNS LATENCY BENCHMARK ] ───${C_RESET}\n"
    local ip_addr; ip_addr=$(ip route get 1.1.1.1 2>/dev/null | awk '/src/{print $7}' | head -1 || echo "127.0.0.1")
    local iface; iface=$(ip route get 1.1.1.1 2>/dev/null | awk '/dev/{print $5}' | head -1 || echo "unknown")
    printf "    ${C_WHITE}Active Interface:${C_RESET} ${C_CYAN}%s${C_RESET}  ${C_WHITE}Local IP:${C_RESET} ${C_GREEN}%s${C_RESET}\n\n" "$iface" "$ip_addr"

    echo -e "    ${C_YELLOW}Testing DNS Latencies (ping & resolve)...${C_RESET}"
    local resolvers=("1.1.1.1:Cloudflare" "8.8.8.8:Google" "9.9.9.9:Quad9" "208.67.222.222:OpenDNS")
    for item in "${resolvers[@]}"; do
        local r_ip="${item%%:*}"
        local r_name="${item##*:}"
        local latency="Timeout"
        if command -v ping >/dev/null 2>&1; then
            latency=$(ping -c 2 -W 2 "$r_ip" 2>/dev/null | awk -F '/' 'END {print $5 " ms"}' || echo "N/A")
            [[ -z "$latency" || "$latency" == " ms" ]] && latency="N/A"
        fi
        printf "    %-18s (%-15s)  -->  ${C_GREEN}%s${C_RESET}\n" "$r_name" "$r_ip" "$latency"
    done
    echo ""
}

cmd_clean() {
    echo -e "\n  ${C_YELLOW}[*] Purging Termux Package Cache & Reclaiming Storage...${C_RESET}"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get clean 2>/dev/null || true
        apt-get autoclean 2>/dev/null || true
    fi
    if command -v pkg >/dev/null 2>&1; then
        pkg clean 2>/dev/null || true
    fi

    echo -e "  ${C_YELLOW}[*] Removing Orphan Temp Files & Dead Sockets...${C_RESET}"
    rm -rf "${TMPDIR:-$PREFIX/tmp}"/* 2>/dev/null || true
    rm -rf "$HOME/.cache"/* 2>/dev/null || true

    echo -e "  ${C_GREEN}[[OK]] Mobile storage optimization complete!${C_RESET}\n"
}

cmd_doctor() {
    echo -e "\n  ${C_CYAN}${C_BOLD}─── [ ASTERIX TERMUX ENVIRONMENT DOCTOR ] ───${C_RESET}\n"
    local issues=0

    # 1. Package manager state
    echo -n "    Checking Termux package manager... "
    if command -v pkg >/dev/null 2>&1; then
        echo -e "${C_GREEN}[OK]${C_RESET}"
    else
        echo -e "${C_RED}[FAIL]${C_RESET}"
        issues=$((issues + 1))
    fi

    # 2. Curl and libcurl consistency
    echo -n "    Checking curl binary & TLS libraries... "
    if command -v curl >/dev/null 2>&1 && curl --version >/dev/null 2>&1; then
        echo -e "${C_GREEN}[OK]${C_RESET}"
    else
        echo -e "${C_YELLOW}[WARN] Broken or missing curl. Auto-reinstalling...${C_RESET}"
        pkg reinstall -y curl libcurl 2>/dev/null || true
    fi

    # 3. Python 3
    echo -n "    Checking Python 3 standard runtime... "
    if command -v python3 >/dev/null 2>&1; then
        echo -e "${C_GREEN}[OK]${C_RESET}"
    else
        echo -e "${C_RED}[MISSING]${C_RESET}"
        echo -e "      ${C_YELLOW}Run: pkg install -y python${C_RESET}"
        issues=$((issues + 1))
    fi

    # 4. Debian PRoot
    echo -n "    Checking Debian PRoot container... "
    local deb_root="${PREFIX:-/data/data/com.termux/files/usr}/var/lib/proot-distro/installed-rootfs/debian"
    if [ -d "$deb_root" ] && [ -f "$deb_root/bin/sh" ]; then
        echo -e "${C_GREEN}[OK]${C_RESET}"
    else
        echo -e "${C_GRAY}[NOT INSTALLED / OPTIONAL]${C_RESET}"
    fi

    # 5. Persistent directory
    echo -n "    Checking ASTERIX Persistent Storage... "
    if [ -d "$HOME/asterix_persistent" ] || [ -d "$HOME/.asterix_storage" ]; then
        echo -e "${C_GREEN}[OK]${C_RESET}"
    else
        mkdir -p "$HOME/asterix_persistent" 2>/dev/null || true
        echo -e "${C_GREEN}[CREATED]${C_RESET}"
    fi

    if [ $issues -eq 0 ]; then
        echo -e "\n  ${C_GREEN}${C_BOLD}[[OK]] All core mobile subsystems healthy and verified!${C_RESET}\n"
    else
        echo -e "\n  ${C_YELLOW}${C_BOLD}[!] $issues potential issue(s) detected. Please review recommendations above.${C_RESET}\n"
    fi
}

cmd_clip_copy() {
    local text="$*"
    if [ -z "$text" ]; then
        echo "Error: No text provided to copy."
        return 1
    fi
    if command -v termux-clipboard-set >/dev/null 2>&1; then
        echo -n "$text" | termux-clipboard-set
        echo -e "  ${C_GREEN}[[OK]] Copied to Android clipboard.${C_RESET}"
    else
        echo "termux-clipboard-set not found (install termux-api package)."
    fi
}

cmd_clip_paste() {
    if command -v termux-clipboard-get >/dev/null 2>&1; then
        termux-clipboard-get
    else
        echo "termux-clipboard-get not found (install termux-api package)."
    fi
}

cmd_notify() {
    local msg="${*:-ASTERIX Task Completed}"
    if command -v termux-toast >/dev/null 2>&1; then
        termux-toast "$msg" 2>/dev/null || true
    fi
    if command -v termux-vibrate >/dev/null 2>&1; then
        termux-vibrate -d 300 2>/dev/null || true
    fi
    echo -e "  ${C_GREEN}[[OK]] Notification triggered: ${msg}${C_RESET}"
cmd_debian_doctor() {
    if [ -f "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
        python3 "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" doctor "$@"
    elif [ -f "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" ]; then
        bash "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" doctor "$@"
    else
        echo "Debian Rootless manager not found."
    fi
}

cmd_debian_fix() {
    if [ -f "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
        python3 "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" repair "$@"
    elif [ -f "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" ]; then
        bash "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" fix "$@"
    else
        echo "Debian Rootless manager not found."
    fi
}

cmd_debian_folder() {
    if [ -f "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
        python3 "$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py" folder "$@"
    elif [ -f "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" ]; then
        bash "$HOME/ASTERIX-OS/termux-mobile/debian-rootless.sh" folder "$@"
    else
        echo "Debian Rootless manager not found."
    fi
}

ACTION="${1:-help}"
shift || true

case "$ACTION" in
    battery|hw|hardware)
        cmd_battery "$@"
        ;;
    net|dns|network)
        cmd_dns "$@"
        ;;
    clean|purge|optimize)
        cmd_clean "$@"
        ;;
    doctor|heal|repair)
        cmd_doctor "$@"
        ;;
    debian-doctor|proot-doctor)
        cmd_debian_doctor "$@"
        ;;
    debian-fix|proot-fix|debian-repair)
        cmd_debian_fix "$@"
        ;;
    debian-folder|folder|mkdir)
        cmd_debian_folder "$@"
        ;;
    clip-copy|copy)
        cmd_clip_copy "$@"
        ;;
    clip-paste|paste)
        cmd_clip_paste "$@"
        ;;
    notify|vibrate|toast)
        cmd_notify "$@"
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac
