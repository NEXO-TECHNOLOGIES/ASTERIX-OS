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
echo -e "${C_YELLOW}[4/5] Building Go Tools...${C_RESET}"
if command -v go &>/dev/null; then
    cd "${SCRIPT_DIR}/core-utils-go/asterix-webrecon"
    go build -ldflags="-s -w" -o asterix-webrecon .
    sudo cp asterix-webrecon "$INSTALL_DIR/" 2>/dev/null || cp asterix-webrecon "${SCRIPT_DIR}/dist/"
    echo -e "${C_GREEN}[✔] Go suite done${C_RESET}"
else
    echo -e "${C_YELLOW}[!] go not found — install: apt install golang${C_RESET}"
fi

# ── Rust Core & Master ax / asterix CLI ──────────────────────────────
echo -e "${C_YELLOW}[5/5] Compiling Rust Control Core & Installing ax/asterix CLI...${C_RESET}"
if [ -d "${SCRIPT_DIR}/ui-core/asterix-loader" ]; then
    cd "${SCRIPT_DIR}/ui-core/asterix-loader"
    if command -v cargo &>/dev/null; then
        cargo build --release
        sudo cp target/release/asterix-loader "$INSTALL_DIR/" 2>/dev/null || cp target/release/asterix-loader "${SCRIPT_DIR}/dist/"
        echo -e "${C_GREEN}[✔] asterix-loader compiled via cargo${C_RESET}"
    elif command -v rustc &>/dev/null; then
        rustc -O -C lto=yes src/main.rs -o asterix-loader
        sudo cp asterix-loader "$INSTALL_DIR/" 2>/dev/null || cp asterix-loader "${SCRIPT_DIR}/dist/"
        echo -e "${C_GREEN}[✔] asterix-loader compiled via rustc${C_RESET}"
    else
        echo -e "${C_YELLOW}[!] rustc/cargo not found — skipping loader compile${C_RESET}"
    fi
fi

# Install master ax unified script & symlink asterix
if [ -f "${SCRIPT_DIR}/bin/ax" ]; then
    sudo cp "${SCRIPT_DIR}/bin/ax" "$INSTALL_DIR/ax" 2>/dev/null || cp "${SCRIPT_DIR}/bin/ax" "${SCRIPT_DIR}/dist/ax"
    sudo chmod 755 "$INSTALL_DIR/ax" 2>/dev/null || chmod 755 "${SCRIPT_DIR}/dist/ax" 2>/dev/null || true
    sudo ln -sf "$INSTALL_DIR/ax" "$INSTALL_DIR/asterix" 2>/dev/null || ln -sf "${SCRIPT_DIR}/dist/ax" "${SCRIPT_DIR}/dist/asterix" 2>/dev/null || true
    echo -e "${C_GREEN}[✔] Master 'ax' and 'asterix' CLI installed${C_RESET}"
fi

echo ""
echo -e "${C_GREEN}${C_BOLD}[✔] ASTERIX OS Master Build Complete!${C_RESET}"
echo -e "${C_CYAN}    Binaries installed to: ${INSTALL_DIR}${C_RESET}"
echo -e "${C_CYAN}    Commands available:    ax, asterix, asterix-*, as-*${C_RESET}"
echo ""
ls -l "${INSTALL_DIR}"/ax "${INSTALL_DIR}"/asterix* 2>/dev/null || true
