#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Master Build Script: All Languages
# Compiles C, C++, Assembly (NASM), and Go tools in one shot
# =====================================================================
set -e

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-/usr/local/bin}"

echo -e "${C_CYAN}${C_BOLD}"
cat << 'EOF'
    ___   _____ ______ ______ ____     __  _____   _____ ________________
   /   | / ___//_  __// ____// __ \   /  |/  /  | / ___//  _/_  __/ ____/
  / /| | \__ \  / /  / __/  / /_/ /  / /|_/ / /| |\__ \ / /  / / / __/   
 / ___ |___/ / / /  / /___ / _, _/  / /  / / ___ /___/ // /  / / / /___  
/_/  |_/____/ /_/  /_____//_/ |_|  /_/  /_/_/  |_/____/___/ /_/ /_____/  
     MULTI-LANGUAGE MASTER BUILD ENGINE
EOF
echo -e "${C_RESET}"

# ── C Suite ──────────────────────────────────────────────────────────
echo -e "${C_YELLOW}[1/4] Building Native C Suite...${C_RESET}"
if command -v gcc &>/dev/null; then
    cd "${SCRIPT_DIR}/core-utils-c"
    make all
    sudo make install DESTDIR="$INSTALL_DIR" 2>/dev/null || make install DESTDIR="${SCRIPT_DIR}/dist"
    echo -e "${C_GREEN}[✔] C suite done${C_RESET}"
else
    echo -e "${C_RED}[!] gcc not found — skipping C suite${C_RESET}"
fi

# ── C++ Suite ────────────────────────────────────────────────────────
echo -e "${C_YELLOW}[2/4] Building C++ Suite...${C_RESET}"
if command -v g++ &>/dev/null; then
    cd "${SCRIPT_DIR}/core-utils-cpp"
    make all
    sudo make install DESTDIR="$INSTALL_DIR" 2>/dev/null || make install DESTDIR="${SCRIPT_DIR}/dist"
    echo -e "${C_GREEN}[✔] C++ suite done${C_RESET}"
else
    echo -e "${C_RED}[!] g++ not found — skipping C++ suite${C_RESET}"
fi

# ── Assembly (NASM) ──────────────────────────────────────────────────
echo -e "${C_YELLOW}[3/4] Assembling NASM Bootloader & Tools...${C_RESET}"
if command -v nasm &>/dev/null && command -v ld &>/dev/null; then
    cd "${SCRIPT_DIR}/boot-asm"
    make all
    sudo make install DESTDIR="$INSTALL_DIR" 2>/dev/null || make install DESTDIR="${SCRIPT_DIR}/dist"
    echo -e "${C_GREEN}[✔] Assembly tools done${C_RESET}"
else
    echo -e "${C_YELLOW}[!] nasm/ld not found — install: apt install nasm binutils${C_RESET}"
fi

# ── Go Suite ─────────────────────────────────────────────────────────
echo -e "${C_YELLOW}[4/4] Building Go Tools...${C_RESET}"
if command -v go &>/dev/null; then
    cd "${SCRIPT_DIR}/core-utils-go/asterix-webrecon"
    go build -ldflags="-s -w" -o asterix-webrecon .
    sudo cp asterix-webrecon "$INSTALL_DIR/" 2>/dev/null || cp asterix-webrecon "${SCRIPT_DIR}/dist/"
    echo -e "${C_GREEN}[✔] Go suite done${C_RESET}"
else
    echo -e "${C_YELLOW}[!] go not found — install: apt install golang${C_RESET}"
fi

echo ""
echo -e "${C_GREEN}${C_BOLD}[✔] ASTERIX OS Master Build Complete!${C_RESET}"
echo -e "${C_CYAN}    Binaries installed to: ${INSTALL_DIR}${C_RESET}"
echo ""
ls "${INSTALL_DIR}"/asterix-* 2>/dev/null || true
