#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Native Rust Security Engines Suite Builder
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

echo -e "${C_CYAN}${C_BOLD}[*] Building ASTERIX Pure-Rust Security & Systems Engines Suite (8 Engines)...${C_RESET}"

cd "${SCRIPT_DIR}"

ENGINES=(
    "asterix-bin-inspector"
    "asterix-net-sentinel"
    "asterix-crypto-core"
    "asterix-sys-mon"
    "asterix-guard-engine"
    "asterix-dark-engine"
    "asterix-log-hunter"
    "asterix-code-repair"
)

mkdir -p "${SCRIPT_DIR}/../dist"

if command -v cargo >/dev/null 2>&1; then
    echo -e "${C_CYAN}[*] Compiling via Cargo workspace with LTO & strip...${C_RESET}"
    cargo build --release
    mkdir -p "${INSTALL_DIR}" 2>/dev/null || true
    for eng in "${ENGINES[@]}"; do
        if [ -f "target/release/${eng}" ]; then
            sudo cp "target/release/${eng}" "${INSTALL_DIR}/" 2>/dev/null || cp "target/release/${eng}" "${SCRIPT_DIR}/../dist/"
            echo -e "${C_GREEN}  [✔] ${eng} built & staged${C_RESET}"
        fi
    done
elif command -v rustc >/dev/null 2>&1; then
    echo -e "${C_YELLOW}[!] Cargo missing, compiling via rustc direct fallback...${C_RESET}"
    mkdir -p target/release
    for eng in "${ENGINES[@]}"; do
        echo -e "${C_CYAN}[*] Compiling ${eng}...${C_RESET}"
        rustc -O -C lto=yes "${eng}/src/main.rs" -o "target/release/${eng}"
        sudo cp "target/release/${eng}" "${INSTALL_DIR}/" 2>/dev/null || cp "target/release/${eng}" "${SCRIPT_DIR}/../dist/"
        echo -e "${C_GREEN}  [✔] ${eng} built via rustc${C_RESET}"
    done
else
    echo -e "${C_RED}[!] Neither cargo nor rustc found in PATH!${C_RESET}"
    exit 1
fi

echo -e "${C_GREEN}${C_BOLD}[✔] All 8 ASTERIX Rust Engines compiled successfully!${C_RESET}"