#!/data/data/com.termux/files/usr/bin/bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║   ASTERIX OS — Termux Cybernetic Boot Engine v3.0                  ║
# ║   RGB Matrix Rain • Glitch Effects • Hardware HUD • Dark Mode       ║
# ╚══════════════════════════════════════════════════════════════════════╝

# ── Color palette (256-color ANSI) ────────────────────────────────────
R='\033[0m';   BOLD='\033[1m';   DIM='\033[2m'
FG_DARKGRAY='\033[38;5;237m'
FG_GRAY='\033[38;5;243m'
FG_GREEN='\033[38;5;46m';    FG_DKGREEN='\033[38;5;22m'
FG_CYAN='\033[38;5;51m';     FG_DKCYAN='\033[38;5;30m'
FG_LTBLUE='\033[38;5;75m'
FG_MAGENTA='\033[38;5;201m'; FG_PURPLE='\033[38;5;141m'
FG_RED='\033[38;5;196m'
FG_YELLOW='\033[38;5;220m';  FG_WHITE='\033[38;5;231m'

COLS=$(tput cols 2>/dev/null || echo 72)
FAST=0
STEALTH=0

# Detect Undercover / Stealth Camouflage flags
if [[ "$*" == *"--stealth"* || "$*" == *"--undercover"* || "$*" == *"--silent"* || -f "$HOME/.asterix_undercover" ]]; then
    STEALTH=1
    FAST=1
fi

[[ "$1" == "--fast" || -n "$CI" ]] && FAST=1
_sleep() { [[ $FAST -eq 0 ]] && sleep "$1"; }

hrule() {
    local char="${1:--}"; local color="${2:-$FG_CYAN}"; local width="${3:-$COLS}"
    echo -e "${color}$(printf "%${width}s" | tr ' ' "$char")${R}"
}

# ── Phase 0: Matrix Rain ───────────────────────────────────────────────
MCHARS='01ABCDEFXYZ0123456789!#$%&@*+=~'
_matrix_rain() {
    [[ $FAST -eq 1 ]] && return
    local width=$(( COLS < 70 ? COLS : 70 ))
    local cols=$(( width / 2 ))
    declare -a pos
    for (( c=0; c<cols; c++ )); do pos[$c]=$(( RANDOM % 10 )); done
    for (( f=0; f<18; f++ )); do
        for (( r=0; r<3; r++ )); do
            local row=""
            for (( c=0; c<cols; c++ )); do
                local ch="${MCHARS:$(( RANDOM % ${#MCHARS} )):1}"
                local d=${pos[$c]}
                if (( r == d )); then
                    row+="\033[38;5;231m\033[1m${ch}\033[0m"
                elif (( r > d && r < d+5 )); then
                    local lv=$(( 46 - (r-d)*8 ))
                    (( lv < 22 )) && lv=22
                    row+="\033[38;5;${lv}m${ch}\033[0m"
                else
                    row+="\033[38;5;22m${ch}\033[0m"
                fi
                row+=" "
            done
            echo -e "$row"
        done
        for (( c=0; c<cols; c++ )); do
            (( RANDOM % 3 == 0 )) && pos[$c]=$(( (pos[$c]+1) % 12 ))
        done
        sleep 0.04
    done
}

# ── Phase 1: Glitch Banner ─────────────────────────────────────────────
_glitch_line() {
    local line="$1" intensity="$2" out="" gl=('@' '#' '%' '&' '!' '?' '0' '1' 'X' 'Z')
    for (( i=0; i<${#line}; i++ )); do
        local ch="${line:$i:1}"
        if (( RANDOM % 100 < intensity )); then
            out+="${gl[$(( RANDOM % ${#gl[@]} ))]}"
        else
            out+="$ch"
        fi
    done
    echo -n "$out"
}

_show_banner() {
    echo -e "${FG_CYAN}${BOLD}"
    echo "  ░█████╗ ░██████╗████████╗███████╗██████╗ ░██╗██╗░░██╗"
    echo "  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝"
    echo "  ███████║╚█████╗░░░░██║░░░█████╗░░██████╔╝██║░╚███╔╝░"
    echo "  ██╔══██║░╚═══██╗░░░██║░░░██╔══╝░░██╔══██╗██║░██╔██╗░"
    echo "  ██║░░██║██████╔╝░░░██║░░░███████╗██║░░██║██║██╔╝░██╗"
    echo "  ╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝╚═╝░░╚═╝"
    echo "    ─── [ C Y B E R N E T I C   M O B I L E   O S ] ───  "
    echo -e "${R}"
}

_glitch_banner() {
    [[ $FAST -eq 1 ]] && { _show_banner; return; }
    local colors=("$FG_RED" "$FG_MAGENTA" "$FG_CYAN" "$FG_GREEN")
    local ints=(30 20 10 0)
    local banner_text=("  ░█████╗ ░██████╗████████╗███████╗██████╗ ░██╗██╗░░██╗" \
                       "  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝" \
                       "  ███████║╚█████╗░░░░██║░░░█████╗░░██████╔╝██║░╚███╔╝░" \
                       "  ██╔══██║░╚═══██╗░░░██║░░░██╔══╝░░██╔══██╗██║░██╔██╗░" \
                       "  ██║░░██║██████╔╝░░░██║░░░███████╗██║░░██║██║██╔╝░██╗" \
                       "  ╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚══════╝╚═╝░░╚═╝╚═╝╚═╝░░╚═╝" \
                       "    ─── [ C Y B E R N E T I C   M O B I L E   O S ] ───  ")
    for idx in 0 1 2 3; do
        clear; echo ""
        echo -e "${colors[$idx]}${BOLD}"
        for line in "${banner_text[@]}"; do
            echo "  $(_glitch_line "$line" "${ints[$idx]}")"
        done
        echo -e "${R}"; sleep 0.05
    done
}

# ── Phase 2: Hardware HUD ──────────────────────────────────────────────
_battery_bar() {
    local pct="$1" w=20
    local filled=$(( pct * w / 100 )) empty=$(( w - pct * w / 100 ))
    local col="$FG_GREEN"
    (( pct < 40 )) && col="$FG_YELLOW"
    (( pct < 15 )) && col="$FG_RED"
    echo -e "${col}$(printf "%${filled}s" | tr ' ' '█')${FG_DARKGRAY}$(printf "%${empty}s" | tr ' ' '░')${R}"
}

_hw_hud() {
    local bat_cap="N/A" bat_status="N/A" total_ram="N/A" free_ram="N/A"
    local cpu_cores arch ip_addr persist_status
    if command -v termux-battery-status &>/dev/null; then
        local bs; bs=$(termux-battery-status 2>/dev/null)
        bat_cap=$(echo "$bs"   | grep -oE '"percentage":[[:space:]]*[0-9]+' | grep -oE '[0-9]+' || echo "N/A")
        bat_status=$(echo "$bs" | grep -oE '"status":[[:space:]]*"[^"]+"'   | grep -oE '"[^"]+"$' | tr -d '"' || echo "N/A")
    elif [[ -f /sys/class/power_supply/battery/capacity ]]; then
        bat_cap=$(cat /sys/class/power_supply/battery/capacity 2>/dev/null || echo "N/A")
    fi

    if [[ -f /proc/meminfo ]]; then
        total_ram=$(awk '/MemTotal/{printf "%.0f MB",$2/1024}' /proc/meminfo 2>/dev/null || echo "N/A")
        free_ram=$(awk '/MemAvailable/{printf "%.0f MB",$2/1024}' /proc/meminfo 2>/dev/null || echo "N/A")
    fi
    cpu_cores=$(nproc 2>/dev/null || grep -c processor /proc/cpuinfo 2>/dev/null || echo "?")
    arch=$(uname -m 2>/dev/null || echo "?")
    ip_addr=$(ip route get 1.1.1.1 2>/dev/null | awk '/src/{print $7}' | head -1); [[ -z "$ip_addr" ]] && ip_addr="127.0.0.1"
    persist_status="${FG_RED}NOT MOUNTED${R}"
    { [[ -d "$HOME/asterix_persistent" ]] || [[ -d "/asterix_persistent" ]]; } && persist_status="${FG_GREEN}ACTIVE${R}"

    hrule "═" "$FG_CYAN"
    printf " ${FG_CYAN}${BOLD}NODE:${R} ${FG_YELLOW}%-20s${R}  ${FG_CYAN}${BOLD}IP:${R} ${FG_GREEN}%s${R}\n" \
        "$(hostname 2>/dev/null || echo 'asterix-mobile')" "$ip_addr"
    printf " ${FG_CYAN}${BOLD}CPU:${R}  ${FG_WHITE}%s cores %-10s${R}  ${FG_CYAN}${BOLD}RAM:${R} ${FG_GREEN}%s free / %s${R}\n" \
        "$cpu_cores" "[$arch]" "$free_ram" "$total_ram"
    if [[ "$bat_cap" =~ ^[0-9]+$ ]]; then
        local bbar; bbar=$(_battery_bar "$bat_cap")
        printf " ${FG_CYAN}${BOLD}BAT:${R}  [%b] ${FG_YELLOW}%s%%${R} ${FG_GRAY}(%s)${R}\n" "$bbar" "$bat_cap" "$bat_status"
    fi
    printf " ${FG_CYAN}${BOLD}PERSIST:${R} %b  ${FG_CYAN}${BOLD}TERMUX:${R} ${FG_GRAY}v%s${R}\n" \
        "$persist_status" "${TERMUX_VERSION:-unknown}"
    hrule "═" "$FG_CYAN"
    echo ""
}

# ── Phase 3: Boot Sequence ─────────────────────────────────────────────
BOOT_STEPS=(
    "KERNEL_BOOTSTRAP:Mounting ASTERIX Microkernel v4.9.0-sec"
    "MEMORY_ALLOC:Locking DMA ring buffers & page tables"
    "CHACHA20_VAULT:AES-256-GCM + ChaCha20-Poly1305 keys"
    "SYSCALL_HOOKS:Injecting eBPF bytecode & raw sockets"
    "PERSIST_VOLUME:Verifying ASTERIX_PERSISTENCE volume"
    "PROOT_SANDBOX:Rootless Debian PRoot container ready"
    "ANDROID_BRIDGE:/sdcard + shared storage bridge active"
    "NET_SENTINEL:Multi-threaded TCP/UDP port sentinel"
    "CRYPTO_ENGINE:ARX-512 cipher matrix & AXCIPH02 ready"
    "DARK_ENGINES:DarkTrace + LogHunter modules online"
    "SHELL_MATRIX:ASTERIX Cybernetic Control Hub online"
)

_step_bar() {
    local pct="$1" w=22 filled empty
    filled=$(( pct * w / 100 )); empty=$(( w - filled ))
    printf "${FG_CYAN}%s${FG_DARKGRAY}%s${R}" \
        "$(printf "%${filled}s" | tr ' ' '█')" "$(printf "%${empty}s" | tr ' ' '░')"
}

_master_bar() {
    local pct="$1" w=38
    local filled=$(( pct * w / 100 )) empty=$(( w - pct * w / 100 ))
    local col="$FG_GREEN"; (( pct>60 )) && col="$FG_CYAN"; (( pct>85 )) && col="$FG_MAGENTA"
    printf "${col}%s${FG_DARKGRAY}%s${R}" \
        "$(printf "%${filled}s" | tr ' ' '▓')" "$(printf "%${empty}s" | tr ' ' '░')"
}

_run_boot() {
    local total="${#BOOT_STEPS[@]}" count=0 delay=0.06
    [[ $FAST -eq 1 ]] && delay=0.005
    echo -e " ${FG_CYAN}${BOLD}[ ASTERIX SUBSYSTEM BOOT MATRIX ]${R}\n"
    for item in "${BOOT_STEPS[@]}"; do
        IFS=':' read -r sub desc <<< "$item"
        count=$(( count + 1 ))
        local mpct=$(( count * 100 / total ))
        for p in 33 66 100; do
            printf "\r ${FG_CYAN}[${BOLD}%-22s${R}${FG_CYAN}]${R} ${FG_WHITE}%-36s${R} %b ${FG_YELLOW}%3d%%${R}" \
                "$sub" "$desc" "$(_step_bar $p)" "$p"
            [[ $FAST -eq 0 ]] && sleep 0.012
        done
        printf "\r ${FG_CYAN}[${BOLD}%-22s${R}${FG_CYAN}]${R} ${FG_WHITE}%-36s${R} ${FG_GREEN}[ OK ]${R}\n" "$sub" "$desc"
        _sleep "$delay"
        if (( count % 4 == 0 || count == total )); then
            printf "  ${FG_GRAY}MASTER${R} [%b] ${FG_YELLOW}%3d%%${R}\n" "$(_master_bar $mpct)" "$mpct"
        fi
    done
}

# ── Phase 4: Tool Matrix ───────────────────────────────────────────────
_tool_check() {
    local tools=("rustc" "cargo" "nmap" "tshark" "proot-distro" "python3" "git" "curl" "ax")
    echo ""
    hrule "-" "$FG_DARKGRAY"
    echo -e " ${FG_PURPLE}${BOLD}[ TOOL AVAILABILITY MATRIX ]${R}"
    hrule "-" "$FG_DARKGRAY"
    local i=0
    for t in "${tools[@]}"; do
        if command -v "$t" &>/dev/null; then
            printf "  ${FG_GREEN}✔${R} ${FG_WHITE}%-16s${R}" "$t"
        else
            printf "  ${FG_RED}✖${R} ${FG_GRAY}%-16s${R}" "$t"
        fi
        i=$(( i + 1 ))
        (( i % 3 == 0 )) && echo ""
    done
    (( i % 3 != 0 )) && echo ""
    hrule "-" "$FG_DARKGRAY"
}

# ── Phase 5: Final Splash ──────────────────────────────────────────────
_final_splash() {
    echo ""
    hrule "═" "$FG_MAGENTA"
    if [[ $FAST -eq 0 ]]; then
        local msg=" [*] ALL ASTERIX SUBSYSTEMS ONLINE & OPERATIONAL"
        local revealed=""
        for (( i=0; i<${#msg}; i++ )); do
            revealed+="${msg:$i:1}"
            printf "\r ${FG_GREEN}${BOLD}%s${R}" "$revealed"
            sleep 0.012
        done
        echo ""
    else
        echo -e " ${FG_GREEN}${BOLD}[*] ALL ASTERIX SUBSYSTEMS ONLINE & OPERATIONAL${R}"
    fi
    echo -e " ${FG_CYAN}${BOLD}[*] TERMUX CYBERNETIC ENVIRONMENT READY${R}"
    hrule "═" "$FG_MAGENTA"
    echo ""
    echo -e " ${FG_YELLOW}${BOLD}LAUNCH COMMANDS:${R}"
    echo -e "   ${FG_CYAN}ax${R}              Full Cybernetic Command & Control Hub"
    echo -e "   ${FG_CYAN}asterix${R}         Alias for ax"
    echo -e "   ${FG_CYAN}ax darktrace${R}    Stealth memory, entropy & log triage"
    echo -e "   ${FG_CYAN}ax shadowcam${R}    Camera & RTSP/ONVIF security auditor"
    echo -e "   ${FG_CYAN}ax dark-engine${R}  Pure-Rust stealth & entropy engine"
    echo -e "   ${FG_CYAN}ax log-hunter${R}   Pure-Rust threat-pattern log scanner"
    echo -e "   ${FG_CYAN}ax help${R}         Full arsenal reference"
    echo ""
}

# ── Entry Point ────────────────────────────────────────────────────────
main() {
    if [[ $STEALTH -eq 1 ]]; then
        clear 2>/dev/null || true
        echo -e "${FG_DARKGRAY}[*] ASTERIX Mobile Cybernetic PRoot Subsystem Initialized (Linux 6.6.0-asterix-arm64)${R}"
        echo -e "${FG_DARKGRAY}[*] Stealth Camouflage Active (All ASTERIX defenses operational in background)${R}"
        echo ""
    else
        clear
        _matrix_rain
        clear
        _glitch_banner
        echo ""
        echo -e " ${FG_GRAY}${DIM}Probing Android hardware telemetry...${R}"
        _sleep 0.3
        _hw_hud
        _sleep 0.1
        _run_boot
        _tool_check
        _sleep 0.2
        _final_splash
    fi

    # Setup persistence dirs
    mkdir -p "$HOME/asterix_persistent"/{loot,captures,scripts,notes} 2>/dev/null

    # Ensure DNS resolver is valid in PRoot Debian container so internet works out of the box
    local deb_resolv="$PREFIX/var/lib/proot-distro/installed-rootfs/debian/etc/resolv.conf"
    if [ -f "$deb_resolv" ]; then
        if ! grep -q "nameserver" "$deb_resolv" 2>/dev/null; then
            printf "nameserver 1.1.1.1\nnameserver 8.8.8.8\nnameserver 9.9.9.9\n" > "$deb_resolv" 2>/dev/null || true
        fi
    fi

    # Launch PRoot if debian is healthy, otherwise launch native ax shell
    local args=("$@")
    local passthrough=()
    for a in "${args[@]}"; do
        [[ "$a" != "--fast" && "$a" != "--stealth" && "$a" != "--undercover" && "$a" != "--silent" ]] && passthrough+=("$a")
    done
    local deb_sh="$PREFIX/var/lib/proot-distro/installed-rootfs/debian/bin/sh"
    if command -v proot-distro &>/dev/null && [ -f "$deb_sh" ]; then
        if [[ ${#passthrough[@]} -gt 0 ]]; then
            exec proot-distro login --bind "$HOME/asterix_persistent:/asterix_persistent" debian -- "${passthrough[@]}"
        else
            exec proot-distro login --bind "$HOME/asterix_persistent:/asterix_persistent" debian
        fi
    elif [ -x "$PREFIX/bin/ax" ]; then
        exec "$PREFIX/bin/ax" "${passthrough[@]}"
    fi
}
main "$@"