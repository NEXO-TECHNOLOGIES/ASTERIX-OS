#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Pure Bash Boot Animation
# Minimal dependency terminal visualizer
# =====================================================================

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[38;5;196m"
C_GREEN="\033[38;5;46m"
C_CYAN="\033[38;5;51m"
C_YELLOW="\033[38;5;220m"
C_MAGENTA="\033[38;5;201m"

clear

echo -e "${C_CYAN}${C_BOLD}"
cat << 'EOF'
    █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗ ███████╗
   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔═══██╗██╔════╝
   ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║   ██║███████╗
   ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║   ██║╚════██║
   ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╔╝███████║
   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝
                     >> NEXT-GEN CYBERNETIC PLATFORM <<
EOF
echo -e "${C_RESET}"

steps=(
    "INIT_CORE_KERNEL:Mounting Microkernel"
    "MEMORY_TABLES:Allocating locked DMA ring buffers"
    "CRYPTO_VAULT:Establishing ChaCha20/AES256 keys"
    "PACKET_DRIVERS:Hooking raw network sockets"
    "PERSISTENCE_MNT:Mounting ASTERIX_PERSISTENT storage"
    "AUDIT_ENGINE:Loading Metasploit, Wireshark, Nmap"
    "SHELL_INTERFACE:Starting Asterix Main Control Hub"
)

total=${#steps[@]}
count=0

for item in "${steps[@]}"; do
    subsystem="${item%%:*}"
    desc="${item##*:}"
    count=$((count + 1))
    pct=$((count * 100 / total))

    # Render cyber progress bar
    filled=$((pct / 4))
    empty=$((25 - filled))
    bar=$(printf "%${filled}s" | tr ' ' '█')
    blank=$(printf "%${empty}s" | tr ' ' '░')

    printf " ${C_CYAN}[%-18s]${C_RESET} %-40s ${C_GREEN}[ OK ]${C_RESET} ${C_YELLOW}[%s%s %3d%%]${C_RESET}\n" \
        "$subsystem" "$desc" "$bar" "$blank" "$pct"
    sleep 0.08
done

echo ""
echo -e "${C_GREEN}${C_BOLD}[✔] ALL ASTERIX SUBSYSTEMS ARE ONLINE & OPERATIONAL${C_RESET}"
echo -e "${C_YELLOW}Storage Mode: ${C_GREEN}PERSISTENT (Saved to /asterix_persistent)${C_RESET}"
echo ""
