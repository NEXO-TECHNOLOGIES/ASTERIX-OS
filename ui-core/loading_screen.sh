#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════╗
# ║   ASTERIX OS — Pure Bash Cybernetic Boot Animation v3.0            ║
# ║   Glitch Banner • Dual Progress • Dark ANSI HUD • Fallback Safe    ║
# ╚══════════════════════════════════════════════════════════════════════╝

R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
FG_DARKGRAY='\033[38;5;237m'; FG_GRAY='\033[38;5;243m'
FG_GREEN='\033[38;5;46m';     FG_DKGREEN='\033[38;5;22m'
FG_CYAN='\033[38;5;51m'
FG_MAGENTA='\033[38;5;201m';  FG_PURPLE='\033[38;5;141m'
FG_RED='\033[38;5;196m'
FG_YELLOW='\033[38;5;220m';   FG_WHITE='\033[38;5;231m'

COLS=$(tput cols 2>/dev/null || echo 76)
FAST=0; [[ "$1" == "--fast" || -n "$CI" ]] && FAST=1
_sleep() { [[ $FAST -eq 0 ]] && sleep "$1"; }
hrule() {
    local char="${1:--}" col="${2:-$FG_CYAN}" w="${3:-$COLS}"
    echo -e "${col}$(printf "%${w}s" | tr ' ' "$char")${R}"
}

# ── Glitch Banner ──────────────────────────────────────────────────────
_glitch_line() {
    local s="$1" intensity="$2" out="" gl=('#' '@' '%' '!' '?' '0' '1' 'X' '<' '>')
    for (( i=0; i<${#s}; i++ )); do
        if (( RANDOM % 100 < intensity )); then
            out+="${gl[$(( RANDOM % ${#gl[@]} ))]}"
        else
            out+="${s:$i:1}"
        fi
    done
    echo -n "$out"
}

BLINES=(
"    █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗ ███████╗"
"   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔═══██╗██╔════╝"
"   ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║   ██║███████╗"
"   ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║   ██║╚════██║"
"   ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╔╝███████║"
"   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝"
"                      >> NEXT-GEN CYBERNETIC PLATFORM <<"
)

_glitch_banner() {
    local colors=("$FG_RED" "$FG_MAGENTA" "$FG_CYAN" "$FG_GREEN")
    local ints=(38 22 10 3)
    [[ $FAST -eq 1 ]] && ints=(0 0 0 0)
    for idx in 0 1 2 3; do
        [[ $FAST -eq 0 ]] && clear; echo ""
        echo -e "${colors[$idx]}${BOLD}"
        for line in "${BLINES[@]}"; do echo "  $(_glitch_line "$line" "${ints[$idx]}")"; done
        echo -e "${R}"
        _sleep 0.07
    done
}

# ── Boot Steps ─────────────────────────────────────────────────────────
BOOT_STEPS=(
    "INIT_CORE_KERNEL:Mounting ASTERIX Microkernel v4.9.0-sec"
    "MEMORY_TABLES:Allocating locked DMA ring buffers"
    "CHACHA20_VAULT:AES-256-GCM + ChaCha20 key initialization"
    "SYSCALL_HOOKS:eBPF bytecode injection & raw sockets"
    "PERSISTENCE_MNT:Mounting ASTERIX_PERSISTENT storage"
    "PROOT_SANDBOX:Rootless Debian container runtime"
    "NET_SENTINEL:Multi-threaded TCP/UDP port sentinel"
    "CRYPTO_ENGINE:ARX-512 cipher & AXCIPH02 container"
    "DARK_ENGINES:DarkTrace + LogHunter analysis modules"
    "AUDIT_ENGINE:Guard engine & kernel sysctl audit"
    "SHELL_INTERFACE:ASTERIX Master Control Hub online"
)

_step_bar() {
    local pct="$1" w=24
    local f=$(( pct * w / 100 )) e=$(( w - pct * w / 100 ))
    printf "${FG_CYAN}%s${FG_DARKGRAY}%s${R}" \
        "$(printf "%${f}s" | tr ' ' '█')" "$(printf "%${e}s" | tr ' ' '░')"
}

_master_bar() {
    local pct="$1" w=42
    local f=$(( pct * w / 100 )) e=$(( w - pct * w / 100 ))
    local col="$FG_GREEN"; (( pct>55 )) && col="$FG_CYAN"; (( pct>80 )) && col="$FG_MAGENTA"
    printf "${col}%s${FG_DARKGRAY}%s${R}" \
        "$(printf "%${f}s" | tr ' ' '▓')" "$(printf "%${e}s" | tr ' ' '░')"
}

_run_boot() {
    local total="${#BOOT_STEPS[@]}" count=0 delay=0.07
    [[ $FAST -eq 1 ]] && delay=0.005
    echo ""
    hrule "═" "$FG_CYAN"
    printf " ${FG_WHITE}${BOLD}%-78s${R}\n" "[ ASTERIX KERNEL INITIALIZATION — SYSTEM BOOT SEQUENCE ]"
    hrule "═" "$FG_CYAN"
    echo ""
    for item in "${BOOT_STEPS[@]}"; do
        IFS=':' read -r sub desc <<< "$item"
        count=$(( count + 1 ))
        local mpct=$(( count * 100 / total ))
        for p in 33 66 100; do
            printf "\r ${FG_CYAN}[${BOLD}%-20s${R}${FG_CYAN}]${R} ${FG_WHITE}%-38s${R} %b ${FG_YELLOW}%3d%%${R}" \
                "$sub" "$desc" "$(_step_bar $p)" "$p"
            [[ $FAST -eq 0 ]] && sleep 0.01
        done
        printf "\r ${FG_CYAN}[${BOLD}%-20s${R}${FG_CYAN}]${R} ${FG_WHITE}%-38s${R} ${FG_GREEN}[ OK ]${R}\n" "$sub" "$desc"
        _sleep "$delay"
        if (( count % 4 == 0 || count == total )); then
            printf "  ${FG_GRAY}MASTER${R} [%b] ${FG_YELLOW}%3d%%${R}\n" "$(_master_bar $mpct)" "$mpct"
        fi
    done
    echo ""
}

# ── Final Splash ───────────────────────────────────────────────────────
_final_splash() {
    hrule "═" "$FG_MAGENTA"
    if [[ $FAST -eq 0 ]]; then
        local msg=" [*] ALL ASTERIX SUBSYSTEMS ONLINE & OPERATIONAL"
        local out=""
        for (( i=0; i<${#msg}; i++ )); do
            out+="${msg:$i:1}"
            printf "\r ${FG_GREEN}${BOLD}%s${R}" "$out"
            sleep 0.012
        done
        echo ""
    else
        echo -e " ${FG_GREEN}${BOLD}[*] ALL ASTERIX SUBSYSTEMS ONLINE & OPERATIONAL${R}"
    fi
    echo -e " ${FG_YELLOW}Storage Mode:${R}  ${FG_GREEN}PERSISTENT — ASTERIX_PERSISTENT volume active${R}"
    echo -e " ${FG_YELLOW}Rust Engines:${R}  ${FG_CYAN}bin-inspector | net-sentinel | crypto-core | sys-mon | guard | dark-engine | log-hunter${R}"
    hrule "═" "$FG_MAGENTA"
    echo ""
}

# ── Main ───────────────────────────────────────────────────────────────
clear
_glitch_banner
clear
echo ""
echo -e "${FG_CYAN}${BOLD}"
for line in "${BLINES[@]}"; do echo "  $line"; done
echo -e "${R}"
_run_boot
_final_splash
