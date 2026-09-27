#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS — Source-first bootstrap installer
#
# This installer is intentionally simple and honest:
# - If the project is already checked out locally, it uses that source tree.
# - Otherwise it fetches the repo via curl or git clone from GitHub/GitLab.
# - It then runs the project setup flow without pretending a packaged ISO exists.
# ==============================================================================
set -euo pipefail

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_RED="\033[91m"
C_GREEN="\033[92m"
C_YELLOW="\033[93m"
C_CYAN="\033[96m"

INSTALL_DIR="${INSTALL_DIR:-$HOME/ASTERIX-OS}"
GITHUB_URL="https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git"
GITLAB_URL="https://gitlab.com/nexo-technologies-group/asterix-os.git"

echo -e "${C_CYAN}${C_BOLD}"
cat <<'EOF'
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
EOF

echo -e "  ASTERIX OS source-first installer${C_RESET}\n"

echo -e "${C_YELLOW}[!] This project is source-first. The verified kernel is built from source, not from a fake prebuilt ISO.${C_RESET}\n"

if [ -f "${BASH_SOURCE[0]}" ] && [ -f "$(dirname "${BASH_SOURCE[0]}")/setup.sh" ]; then
    REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    INSTALL_DIR="$REPO_ROOT"
    echo -e "${C_GREEN}[OK]${C_RESET} Local repository detected at $INSTALL_DIR"
else
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo -e "${C_GREEN}[OK]${C_RESET} Existing repo found at $INSTALL_DIR"
    else
        echo -e "${C_CYAN}[1/3] Cloning ASTERIX OS from GitHub...${C_RESET}"
        if command -v curl >/dev/null 2>&1; then
            curl -L "$GITHUB_URL" -o /tmp/asterix-os.git
            git clone "$GITHUB_URL" "$INSTALL_DIR"
        else
            git clone "$GITHUB_URL" "$INSTALL_DIR"
        fi
    fi
fi

cd "$INSTALL_DIR"

echo -e "${C_CYAN}[2/3] Checking project files...${C_RESET}"

# Check if running inside Android Termux
if [ -n "${PREFIX:-}" ] && [ -d "/data/data/com.termux" ]; then
    echo -e "${C_GREEN}[OK]${C_RESET} Android Termux environment detected."
    if [ -f "$INSTALL_DIR/termux-mobile/install-termux.sh" ]; then
        echo -e "${C_CYAN}[3/3] Launching Termux Mobile Deployment Engine...${C_RESET}"
        chmod +x "$INSTALL_DIR/termux-mobile/install-termux.sh"
        exec bash "$INSTALL_DIR/termux-mobile/install-termux.sh"
    fi
fi

if [ ! -f "$INSTALL_DIR/setup.sh" ]; then
    echo -e "${C_RED}[!] setup.sh not found in $INSTALL_DIR${C_RESET}"
    exit 1
fi

echo -e "${C_CYAN}[3/3] Running project bootstrap...${C_RESET}"
if [ -x "$INSTALL_DIR/setup.sh" ]; then
    exec bash "$INSTALL_DIR/setup.sh"
else
    chmod +x "$INSTALL_DIR/setup.sh"
    exec bash "$INSTALL_DIR/setup.sh"
fi
