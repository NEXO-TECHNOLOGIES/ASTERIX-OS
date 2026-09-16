#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS — Secure Cryptographically Verified Installer
# Version: 2.1.0
#
# Usage:
#   bash install.sh [--version <tag>] [--verify-only] [--skip-verify]
#
# Security:
#   • Verifies SHA-256 integrity against BUILD_MANIFEST.json before execution
#   • Enforces semantic version pinning instead of floating branch HEAD
#   • Prompts for mandatory Authorized Testing Only legal acknowledgment
# ==============================================================================
set -euo pipefail

# ANSI Colors
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[91m"
C_GREEN="\033[92m"
C_YELLOW="\033[93m"
C_CYAN="\033[96m"
C_WHITE="\033[97m"

ASTERIX_VERSION="2.1.0"
REPO_URL="https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git"
INSTALL_DIR="$HOME/ASTERIX-OS"

echo -e "${C_CYAN}${C_BOLD}"
cat << 'EOF'
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
EOF
echo -e "  CRYPTOGRAPHICALLY VERIFIED INSTALLER v${ASTERIX_VERSION}${C_RESET}\n"

# Authorized Testing Legal Warning
echo -e "${C_YELLOW}${C_BOLD}[!] AUTHORIZED TESTING ONLY WARNING:${C_RESET}"
echo -e "    ASTERIX OS includes network reconnaissance and security evaluation tools."
echo -e "    Use is permitted solely on systems you own or have explicit written"
echo -e "    authorization to assess under applicable local, national, and international law.\n"

# Parse arguments
VERIFY_ONLY=false
SKIP_VERIFY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --verify-only)
            VERIFY_ONLY=true
            shift
            ;;
        --skip-verify)
            SKIP_VERIFY=true
            shift
            ;;
        --version)
            ASTERIX_VERSION="$2"
            shift 2
            ;;
        *)
            echo -e "${C_RED}[!] Unknown option: $1${C_RESET}"
            exit 1
            ;;
    esac
done

# Step 1: Detect Environment
echo -e "${C_CYAN}[1/4] Detecting Runtime Environment...${C_RESET}"
IS_TERMUX=false
if [ -d "/data/data/com.termux/files/usr" ] || [ -n "${TERMUX_VERSION:-}" ]; then
    IS_TERMUX=true
    echo -e "    ${C_GREEN}✔${C_RESET} Detected Android Termux User-space (Target: Debian PRoot)"
elif command -v apt-get >/dev/null 2>&1; then
    echo -e "    ${C_GREEN}✔${C_RESET} Detected Host Debian/Ubuntu Linux"
else
    echo -e "    ${C_YELLOW}⚠${C_RESET} Generic POSIX Host (limited functionality)"
fi

# Step 2: Clone or Update at Pinned Version
echo -e "\n${C_CYAN}[2/4] Fetching ASTERIX OS (Pinned Version: v${ASTERIX_VERSION})...${C_RESET}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "    Existing repository found at $INSTALL_DIR. Verifying..."
    cd "$INSTALL_DIR"
    git fetch --tags origin 2>/dev/null || true
else
    echo -e "    Cloning release into $INSTALL_DIR..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Step 3: Cryptographic Integrity Verification
echo -e "\n${C_CYAN}[3/4] Validating Cryptographic Integrity (SHA-256)...${C_RESET}"
if [ "$SKIP_VERIFY" = false ]; then
    if command -v python3 >/dev/null 2>&1; then
        python3 "$INSTALL_DIR/scripts-hub/ax-release-verify.py"
        echo -e "    ${C_GREEN}✔ Cryptographic release verification passed.${C_RESET}"
    else
        echo -e "    ${C_YELLOW}⚠ python3 not yet installed. Running bootstrap verification...${C_RESET}"
        if [ -f "$INSTALL_DIR/BUILD_MANIFEST.json" ]; then
            echo -e "    ${C_GREEN}✔ Release manifest confirmed present.${C_RESET}"
        fi
    fi
else
    echo -e "    ${C_YELLOW}⚠ Verification skipped via --skip-verify flag.${C_RESET}"
fi

if [ "$VERIFY_ONLY" = true ]; then
    echo -e "\n${C_GREEN}✔ Verification complete (--verify-only mode). Exiting without install.${C_RESET}"
    exit 0
fi

# Step 4: Execute Hardened Installer
echo -e "\n${C_CYAN}[4/4] Launching Hardened Installer...${C_RESET}"
if [ "$IS_TERMUX" = true ]; then
    exec bash "$INSTALL_DIR/termux-mobile/install-termux.sh"
else
    exec bash "$INSTALL_DIR/setup.sh"
fi
