#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Master Installation & Environment Bootstrap
# Auto-clones dependencies (Anti-Network Attack & THUNDER), compiles
# multi-language native engines, and installs global ax CLI.
# =====================================================================

# Disable interactive prompts so background/curl installation never halts
export GIT_TERMINAL_PROMPT=0

C_RESET='\033[0m'
C_BOLD='\033[1m'
C_GREEN='\033[38;5;46m'
C_CYAN='\033[38;5;51m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_MAGENTA='\033[38;5;201m'
C_GRAY='\033[38;5;242m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"

# Clean package manager cache on Termux to free memory
if [ -n "$PREFIX" ]; then
    apt clean 2>/dev/null || true
fi

# If executed via curl | bash or outside repo, auto-clone the entire ASTERIX OS repository
if [ ! -f "${SCRIPT_DIR}/bin/ax" ]; then
    TARGET_REPO_DIR="${HOME}/ASTERIX-OS"
    echo -e "\033[38;5;51m[*] Full ASTERIX OS codebase not found in current directory.\033[0m"
    echo -e "\033[38;5;220m[*] Cloning entire ASTERIX OS operating system into ${TARGET_REPO_DIR}...\033[0m"
    if [ -d "$TARGET_REPO_DIR/.git" ]; then
        cd "$TARGET_REPO_DIR" && git pull 2>/dev/null || true
    else
        git clone https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS.git "$TARGET_REPO_DIR" || \
        git clone https://gitlab.com/nexo-technologies-group/asterix-os.git "$TARGET_REPO_DIR"
    fi
    SCRIPT_DIR="$TARGET_REPO_DIR"
    cd "$SCRIPT_DIR"
fi

# Detect environment and permissions
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    ENV_TYPE="Termux (Android)"
    INSTALL_DIR="$PREFIX/bin"
    SUDO=""
elif [ "$(id -u)" -eq 0 ]; then
    ENV_TYPE="Linux Root"
    INSTALL_DIR="/usr/local/bin"
    SUDO=""
elif command -v sudo >/dev/null 2>&1; then
    ENV_TYPE="Linux (Sudo)"
    INSTALL_DIR="/usr/local/bin"
    SUDO="sudo"
else
    ENV_TYPE="Linux (User Local)"
    INSTALL_DIR="$HOME/.local/bin"
    mkdir -p "$INSTALL_DIR"
    SUDO=""
fi

clear 2>/dev/null || true
echo -e "${C_CYAN}${C_BOLD}"
cat << 'EOF'
     ___   _____ ______ ______ ____     __  _____   ____  _____
    /   | / ___//_  __// ____// __ \   /  |/  /  | / __ \/ ___/
   / /| | \__ \  / /  / __/  / /_/ /  / /|_/ / /| / / / /\__ \ 
  / ___ |___/ / / /  / /___ / _, _/  / /  / / ___ / /_/ /___/ / 
 /_/  |_/____/ /_/  /_____//_/ |_|  /_/  /_/_/  |_\____//____/  
       MASTER OS BOOTSTRAP & DEPENDENCY SYNCHRONIZER
EOF
echo -e "${C_RESET}"

echo -e "${C_CYAN}[*] Target Environment:${C_RESET} ${C_YELLOW}${ENV_TYPE}${C_RESET}"
echo -e "${C_CYAN}[*] Installation Root:${C_RESET}  ${C_YELLOW}${INSTALL_DIR}${C_RESET}\n"

# Step 1: Check Core Prerequisites
echo -e "${C_YELLOW}[1/4] Checking System Toolchain & Prerequisites...${C_RESET}"
PREREQS=("git" "curl" "bash")
MISSING_PREREQS=()
for tool in "${PREREQS[@]}"; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo -e "  ${C_GREEN}[✔]${C_RESET} ${tool}"
    else
        echo -e "  ${C_RED}[✘]${C_RESET} ${tool} is missing!"
        MISSING_PREREQS+=("$tool")
    fi
done

if [ ${#MISSING_PREREQS[@]} -gt 0 ]; then
    echo -e "\n${C_RED}[!] Critical tools missing: ${MISSING_PREREQS[*]}${C_RESET}"
    echo -e "    Please install them using your package manager (apt/pkg/pacman/dnf) and retry."
    exit 1
fi

# Step 2: Synchronize External Security Packages (Anti-Network Attack & THUNDER)
echo -e "\n${C_YELLOW}[2/4] Synchronizing External Security Packages from GitHub...${C_RESET}"
if [ -f "${SCRIPT_DIR}/scripts-hub/ax-pkg-sync.sh" ]; then
    chmod +x "${SCRIPT_DIR}/scripts-hub/ax-pkg-sync.sh"
    bash "${SCRIPT_DIR}/scripts-hub/ax-pkg-sync.sh" sync || true
else
    echo -e "${C_RED}[!] scripts-hub/ax-pkg-sync.sh not found!${C_RESET}"
fi

# Step 3: Compile Multi-Language Native Engines (C, C++, Assembly, Go, Rust)
echo -e "\n${C_YELLOW}[3/4] Compiling Native ASTERIX Multi-Language Engines...${C_RESET}"
if [ -f "${SCRIPT_DIR}/build-all.sh" ]; then
    chmod +x "${SCRIPT_DIR}/build-all.sh"
    bash "${SCRIPT_DIR}/build-all.sh" "$INSTALL_DIR" || true
else
    echo -e "${C_YELLOW}[!] build-all.sh not found. Skipping native compilation.${C_RESET}"
fi

# Step 4: Finalize CLI & Shell Integrations
echo -e "\n${C_YELLOW}[4/4] Configuring Global Commands & Shell Aliases...${C_RESET}"
if [ -f "${SCRIPT_DIR}/bin/ax" ]; then
    $SUDO cp "${SCRIPT_DIR}/bin/ax" "${INSTALL_DIR}/ax" 2>/dev/null || cp "${SCRIPT_DIR}/bin/ax" "${SCRIPT_DIR}/dist/ax"
    $SUDO chmod 755 "${INSTALL_DIR}/ax" 2>/dev/null || chmod 755 "${SCRIPT_DIR}/dist/ax" 2>/dev/null || true
    $SUDO ln -sf "${INSTALL_DIR}/ax" "${INSTALL_DIR}/asterix" 2>/dev/null || ln -sf "${SCRIPT_DIR}/dist/ax" "${SCRIPT_DIR}/dist/asterix" 2>/dev/null || true
    echo -e "  ${C_GREEN}[✔]${C_RESET} Installed master 'ax' and 'asterix' to ${INSTALL_DIR}"
fi

echo -e "\n${C_GREEN}${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}[✔] ASTERIX OS SETUP & INITIALIZATION COMPLETE!${C_RESET}"
echo -e "${C_CYAN}Launch the master terminal HUD:${C_RESET} ${C_YELLOW}ax${C_RESET} or ${C_YELLOW}asterix${C_RESET}"
echo -e "${C_CYAN}Manage packages:${C_RESET}               ${C_YELLOW}ax pkg status${C_RESET} | ${C_YELLOW}ax pkg sync${C_RESET}"
echo -e "${C_CYAN}Anti-Network Defense Suite:${C_RESET}    ${C_YELLOW}ax anti-net${C_RESET} | ${C_YELLOW}ax anti-email${C_RESET} | ${C_YELLOW}ax anti-rev${C_RESET}"
echo -e "${C_CYAN}THUNDER Enterprise Defender:${C_RESET}   ${C_YELLOW}ax thunder${C_RESET} | ${C_YELLOW}ax ip-rotator${C_RESET}"
echo -e "${C_CYAN}Dark Forensic Suite:${C_RESET}           ${C_YELLOW}ax darktrace${C_RESET} | ${C_YELLOW}ax shadowcam${C_RESET}"
echo -e "${C_GREEN}${C_BOLD}══════════════════════════════════════════════════════════════════════${C_RESET}\n"