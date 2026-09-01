#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Rust Loader Build Script
# Supports both Cargo and standalone rustc direct compilation
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}[*] Compiling ASTERIX Rust Boot & Control Engine...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if command -v cargo >/dev/null 2>&1; then
    echo -e "${GREEN}[*] Detected Cargo. Building optimized release binary...${NC}"
    cargo build --release
    cp target/release/asterix-loader ./asterix-loader
    echo -e "${GREEN}${BOLD}[✔] Binary built successfully: ./asterix-loader${NC}"
elif command -v rustc >/dev/null 2>&1; then
    echo -e "${YELLOW}[*] Detected standalone rustc. Compiling src/main.rs directly...${NC}"
    rustc -O -C lto=yes -C panic=abort src/main.rs -o asterix-loader
    echo -e "${GREEN}${BOLD}[✔] Binary compiled successfully: ./asterix-loader${NC}"
else
    echo -e "${RED}[!] ERROR: Neither 'cargo' nor 'rustc' was found in PATH.${NC}"
    echo -e "${YELLOW}Install Rust using:${NC}"
    echo "  - Debian/Ubuntu: sudo apt install rustc cargo"
    echo "  - Termux:        pkg install rust"
    echo "  - Arch Linux:    sudo pacman -S rust"
    echo "  - Generic:       curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi

chmod +x ./asterix-loader
echo -e "${CYAN}[*] Test running binary with:${NC} ./asterix-loader --boot-only"
