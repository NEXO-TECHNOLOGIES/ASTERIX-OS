#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS - Secure Localhost Chat Vault Launcher
# Launches the zero-knowledge ephemeral encrypted chat server and opens browser.
# ==============================================================================

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[38;5;51m"
C_GREEN="\033[38;5;46m"
C_YELLOW="\033[38;5;220m"
C_RED="\033[38;5;196m"
C_GRAY="\033[38;5;244m"

DIR="$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")"
PORT="${2:-8765}"
ACTION="${1:-start}"

banner() {
    echo -e "\n${C_CYAN}${C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗${C_RESET}"
    echo -e "${C_CYAN}║${C_BOLD}  [ ASTERIX SECURE CHAT // ZERO-KNOWLEDGE LOCALHOST VAULT v1.0 ]       ║${C_RESET}"
    echo -e "${C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝${C_RESET}\n"
}

check_python() {
    if ! command -v python3 >/dev/null 2>&1; then
        echo -e "  ${C_RED}[✘] Error: Python 3 is required to launch the Secure Chat Vault server.${C_RESET}"
        echo -e "  ${C_GRAY}Install with: sudo apt install python3  or  pkg install python${C_RESET}\n"
        exit 1
    fi
}

cmd_start() {
    check_python
    echo -e "  ${C_CYAN}[*] Starting ASTERIX Secure Chat Vault on http://127.0.0.1:${PORT}...${C_RESET}"
    exec python3 "${DIR}/server.py" --port "${PORT}" --open
}

cmd_lan() {
    check_python
    echo -e "  ${C_CYAN}[*] Starting ASTERIX Secure Chat Vault in LAN Mode on 0.0.0.0:${PORT}...${C_RESET}"
    exec python3 "${DIR}/server.py" --port "${PORT}" --lan --open
}

cmd_cli() {
    check_python
    exec python3 "${DIR}/client.py" "http://127.0.0.1:${PORT}"
}

cmd_status() {
    banner
    if command -v curl >/dev/null 2>&1; then
        local st
        st=$(curl -sf --max-time 2 "http://127.0.0.1:${PORT}/api/status" 2>/dev/null)
        if [ -n "$st" ]; then
            echo -e "  Vault Status:   ${C_GREEN}ONLINE${C_RESET}"
            echo -e "  Address:        ${C_CYAN}http://127.0.0.1:${PORT}${C_RESET}"
            echo -e "  API Telemetry:  ${C_GRAY}${st}${C_RESET}\n"
            return
        fi
    fi
    echo -e "  Vault Status:   ${C_GRAY}OFFLINE (Not running on port ${PORT})${C_RESET}\n"
}

case "$ACTION" in
    start|run|launch)   cmd_start ;;
    lan|network)        cmd_lan   ;;
    client|cli|talk)    cmd_cli   ;;
    status)             cmd_status ;;
    *)
        banner
        echo -e "  ${C_YELLOW}Usage:${C_RESET} ax secure-chat <command> [port]\n"
        echo -e "  Commands:"
        echo -e "    start       - Start localhost encrypted web vault (default: 8765)"
        echo -e "    lan         - Start vault accessible across local network (0.0.0.0)"
        echo -e "    client      - Launch interactive terminal chat client"
        echo -e "    status      - Check if local vault is running\n"
        ;;
esac
