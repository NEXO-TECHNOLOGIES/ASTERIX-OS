#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS - Live Auto-Update Daemon v1.0 (Pure Bash Fallback)
# F-Droid style: polls git remote for new commits, auto-pulls on change.
# Zero external dependencies beyond git and curl/wget.
# ==============================================================================

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[38;5;51m"
C_GREEN="\033[38;5;46m"
C_YELLOW="\033[38;5;220m"
C_RED="\033[38;5;196m"
C_MAGENTA="\033[38;5;201m"
C_GRAY="\033[38;5;244m"

BRANCH="main"
POLL_INTERVAL=60
STATE_DIR="${HOME}/.asterix_vault/auto-updater"
LOG_FILE="${STATE_DIR}/update.log"
PID_FILE="${STATE_DIR}/daemon.pid"
DISABLED_FILE="${STATE_DIR}/disabled"

mkdir -p "${STATE_DIR}"

ts() { date -u '+%Y-%m-%d %H:%M:%S UTC'; }
log() { local msg="[$(ts)] [$2] $1"; echo -e "  ${C_GRAY}${msg}${C_RESET}"; echo "$msg" >> "${LOG_FILE}"; }

banner() {
    echo -e "\n${C_CYAN}${C_BOLD}======================================================================${C_RESET}"
    echo -e "${C_CYAN}${C_BOLD}  [ ASTERIX OS // LIVE AUTO-UPDATER DAEMON v1.0 - F-Droid Style ]${C_RESET}"
    echo -e "${C_CYAN}${C_BOLD}======================================================================${C_RESET}\n"
}

get_local_sha()  { git rev-parse HEAD 2>/dev/null || echo ""; }

fetch_remote_sha() {
    local url="https://api.github.com/repos/NEXO-TECHNOLOGIES/ASTERIX-OS/commits/${BRANCH}"
    local sha=""
    if command -v curl >/dev/null 2>&1; then
        sha=$(curl -sf --max-time 15 \
            -H "Accept: application/vnd.github.v3+json" \
            -H "User-Agent: ASTERIX-OS-AutoUpdater/1.0" \
            "$url" | grep '"sha"' | head -1 | sed 's/.*"sha": "\([^"]*\)".*/\1/')
    elif command -v wget >/dev/null 2>&1; then
        sha=$(wget -qO- --timeout=15 \
            --header="Accept: application/vnd.github.v3+json" \
            --header="User-Agent: ASTERIX-OS-AutoUpdater/1.0" \
            "$url" | grep '"sha"' | head -1 | sed 's/.*"sha": "\([^"]*\)".*/\1/')
    fi
    echo "$sha"
}

check_and_update() {
    if [ -f "${DISABLED_FILE}" ] && [ "$1" != "--force" ] && [ "$1" != "-f" ]; then
        echo -e "  ${C_YELLOW}[!] Auto-Update is currently DISABLED [OFF].${C_RESET}"
        echo -e "  ${C_GRAY}Run 'ax auto-update on' to enable, or 'ax auto-update check --force' to override.${C_RESET}\n"
        return
    fi
    echo -e "  ${C_CYAN}[*] Checking remote repository for updates...${C_RESET}"
    local remote_sha; remote_sha=$(fetch_remote_sha)
    local local_sha;  local_sha=$(get_local_sha)

    if [ -z "$remote_sha" ]; then
        log "Could not reach GitHub API - skipping" "WARN"
        return
    fi

    local short_r="${remote_sha:0:10}"
    local short_l="${local_sha:0:10}"

    if [ "$remote_sha" = "$local_sha" ]; then
        echo -e "  ${C_GREEN}[OK] Already up-to-date${C_RESET}  ${C_GRAY}(local=${short_l} | remote=${short_r})${C_RESET}\n"
        return
    fi

    echo -e "\n  ${C_MAGENTA}${C_BOLD}[ NEW COMMIT DETECTED - APPLYING UPDATE ]${C_RESET}"
    echo -e "  ${C_GRAY}Local  SHA: ${short_l}${C_RESET}"
    echo -e "  ${C_CYAN}Remote SHA: ${short_r}${C_RESET}\n"
    log "New commit: ${short_l} -> ${short_r}" "UPDATE"

    echo -e "  ${C_YELLOW}[v] Pulling latest changes from origin/${BRANCH}...${C_RESET}"
    if git pull origin "${BRANCH}" --rebase=false 2>&1; then
        local new_sha; new_sha=$(get_local_sha)
        echo -e "  ${C_GREEN}${C_BOLD}[OK] UPDATE APPLIED SUCCESSFULLY${C_RESET}  ${C_GRAY}(HEAD=${new_sha:0:10})${C_RESET}"
        log "Update applied: HEAD=${new_sha}" "UPDATE"
    else
        echo -e "  ${C_RED}[X] git pull failed!${C_RESET}"
        log "Pull failed" "ERROR"
    fi
    echo
}

cmd_start() {
    banner
    local pid=""
    [ -f "${PID_FILE}" ] && pid=$(cat "${PID_FILE}")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "  ${C_YELLOW}[!] Daemon already running (PID ${pid}).${C_RESET}\n"
        return
    fi
    echo $$ > "${PID_FILE}"
    echo -e "  ${C_GREEN}${C_BOLD}[ ASTERIX AUTO-UPDATER DAEMON STARTED ]{C_RESET}  ${C_GRAY}PID=$$ | interval=${POLL_INTERVAL}s${C_RESET}\n"
    log "Daemon started PID=$$ interval=${POLL_INTERVAL}s" "DAEMON"
    trap 'log "Daemon stopped" "DAEMON"; rm -f "${PID_FILE}"; exit 0' TERM INT
    while true; do
        check_and_update
        sleep "${POLL_INTERVAL}"
    done
}

cmd_stop() {
    banner
    if [ ! -f "${PID_FILE}" ]; then
        echo -e "  ${C_YELLOW}[!] No daemon PID file found.${C_RESET}\n"; return
    fi
    local pid; pid=$(cat "${PID_FILE}")
    if kill -TERM "$pid" 2>/dev/null; then
        echo -e "  ${C_GREEN}[OK] Stop signal sent to PID ${pid}.${C_RESET}\n"
        rm -f "${PID_FILE}"
    else
        echo -e "  ${C_GRAY}[i] PID ${pid} not running - cleaning up.${C_RESET}\n"
        rm -f "${PID_FILE}"
    fi
}

cmd_enable() {
    banner
    rm -f "${DISABLED_FILE}"
    log "Auto-update ENABLED by user" "CONFIG"
    echo -e "  ${C_GREEN}${C_BOLD}[✔] ASTERIX AUTO-UPDATE: ENABLED [ON]${C_RESET}"
    echo -e "  ${C_GRAY}Live repository synchronization is now active.${C_RESET}\n"
    local pid=""
    [ -f "${PID_FILE}" ] && pid=$(cat "${PID_FILE}")
    if [ -z "$pid" ] || ! kill -0 "$pid" 2>/dev/null; then
        echo -e "  ${C_CYAN}[*] Starting background auto-update daemon...${C_RESET}"
        cmd_start &
    fi
}

cmd_disable() {
    banner
    touch "${DISABLED_FILE}"
    log "Auto-update DISABLED by user" "CONFIG"
    echo -e "  ${C_YELLOW}${C_BOLD}[!] ASTERIX AUTO-UPDATE: DISABLED [OFF]${C_RESET}"
    echo -e "  ${C_GRAY}Automatic repository synchronization is now paused.${C_RESET}\n"
    cmd_stop
}

cmd_status() {
    banner
    echo -e "  ${C_CYAN}${C_BOLD}[ ASTERIX AUTO-UPDATER STATUS ]${C_RESET}\n"
    local toggle_str="${C_GREEN}ENABLED  [ON]${C_RESET}"
    [ -f "${DISABLED_FILE}" ] && toggle_str="${C_RED}DISABLED [OFF]${C_RESET}"
    echo -e "  Auto-Update: ${toggle_str}"
    local pid=""
    [ -f "${PID_FILE}" ] && pid=$(cat "${PID_FILE}")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "  Daemon     : ${C_GREEN}RUNNING  PID ${pid}${C_RESET}"
    else
        echo -e "  Daemon     : ${C_GRAY}STOPPED${C_RESET}"
    fi
    echo -e "  Remote     : ${C_CYAN}github.com/NEXO-TECHNOLOGIES/ASTERIX-OS (${BRANCH})${C_RESET}"
    echo -e "  Local HEAD : ${C_WHITE}$(get_local_sha | head -c14)${C_RESET}"
    echo -e "  Log file   : ${C_GRAY}${LOG_FILE}${C_RESET}\n"
}

cmd_check() { banner; check_and_update "$@"; }

cmd_log() {
    banner
    if [ -f "${LOG_FILE}" ]; then
        echo -e "  ${C_CYAN}${C_BOLD}[ AUTO-UPDATER LOG ]${C_RESET}\n"
        tail -n "${1:-20}" "${LOG_FILE}" | while read -r line; do
            echo -e "  ${C_GRAY}${line}${C_RESET}"
        done
        echo
    else
        echo -e "  ${C_YELLOW}[i] No log yet. Run: ax auto-update check${C_RESET}\n"
    fi
}

action="${1:-status}"
shift || true

case "$action" in
    on|enable|activate)      cmd_enable ;;
    off|disable|deactivate)  cmd_disable ;;
    start|daemon|run|watch)  cmd_start ;;
    stop|kill|halt)          cmd_stop  ;;
    status|info|state)       cmd_status ;;
    check|sync|now|force)    cmd_check "$@" ;;
    log|logs|history)        cmd_log "$1" ;;
    *)
        banner
        echo -e "  ${C_YELLOW}Usage:${C_RESET} ax auto-update <command>\n"
        echo -e "  Commands:"
        echo -e "    on / enable   - Turn live auto-update ON and start daemon"
        echo -e "    off / disable - Turn live auto-update OFF and stop daemon"
        echo -e "    start         - Start background daemon (poll every ${POLL_INTERVAL}s)"
        echo -e "    stop          - Stop the running daemon"
        echo -e "    status        - Show daemon status and sync telemetry"
        echo -e "    check         - One-shot check and pull"
        echo -e "    log [N]       - Show last N log entries\n"
        ;;
esac
