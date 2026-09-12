#!/usr/bin/env bash
# ASTERIX OS Termux AI startup helper
# Starts local AI and keeps the shell ready on first boot.

set -u

ASTERIX_ROOT="${ASTERIX_ROOT:-$HOME/ASTERIX-OS}"
AI_ENTRY="${ASTERIX_ROOT}/asterix-ai/ax_ai.py"
AI_LOG_DIR="${HOME}/.asterix_storage"
AI_LOG_FILE="${AI_LOG_DIR}/ai_boot.log"

mkdir -p "$AI_LOG_DIR" 2>/dev/null || true

run_auto_fix_engine() {
    local max_attempts=5
    local attempt=1
    local repaired=0

    echo "ASTERIX auto-heal: entering repair loop (max ${max_attempts} passes)..." >> "$AI_LOG_DIR/auto_heal.log" 2>/dev/null || true

    while [ "$attempt" -le "$max_attempts" ]; do
        echo "ASTERIX auto-heal: pass ${attempt}/${max_attempts}" >> "$AI_LOG_DIR/auto_heal.log" 2>/dev/null || true

        if command -v termux-change-repo >/dev/null 2>&1; then
            termux-change-repo >/dev/null 2>&1 || true
        fi

        if command -v pkg >/dev/null 2>&1; then
            pkg update -y >/dev/null 2>&1 || true
            pkg upgrade -y >/dev/null 2>&1 || true
            pkg reinstall -y curl libcurl >/dev/null 2>&1 || true
            pkg install -y git wget openssl >/dev/null 2>&1 || true
        fi

        if command -v git >/dev/null 2>&1 && [ -d "$ASTERIX_ROOT" ]; then
            git -C "$ASTERIX_ROOT" pull --ff-only >/dev/null 2>&1 || true
        fi

        if command -v ax >/dev/null 2>&1 || [ -x "$HOME/ASTERIX-OS/bin/ax" ]; then
            ax doctor --fix >/tmp/asterix_auto_fix.log 2>&1 || true
        fi

        if [ -f "$AI_ENTRY" ]; then
            python3 "$AI_ENTRY" --security >/tmp/asterix_ai_boot_status.txt 2>&1 || true
        fi

        if command -v git >/dev/null 2>&1 && command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
            repaired=1
        fi

        if [ "$repaired" -eq 1 ] && (command -v git >/dev/null 2>&1 && command -v curl >/dev/null 2>&1); then
            echo "ASTERIX auto-heal: environment stable on pass ${attempt}." >> "$AI_LOG_DIR/auto_heal.log" 2>/dev/null || true
            break
        fi

        attempt=$((attempt + 1))
        sleep 1 2>/dev/null || true
    done

    if [ "$repaired" -ne 1 ]; then
        echo "ASTERIX auto-heal: max repair attempts reached; continuing with degraded mode." >> "$AI_LOG_DIR/auto_heal.log" 2>/dev/null || true
    fi

    echo "ASTERIX auto-heal complete." >> "$AI_LOG_DIR/auto_heal.log" 2>/dev/null || true
}

if [ ! -f "$AI_ENTRY" ]; then
    echo "ASTERIX AI bootstrap: local AI entry not found at $AI_ENTRY"
    echo "Status: waiting for project files"
    exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ASTERIX AI bootstrap: python3 not available; startup deferred"
    exit 0
fi

if [ ! -f "$AI_LOG_FILE" ] || [ "$(stat -c %Y "$AI_LOG_FILE" 2>/dev/null || echo 0)" -lt "$(date +%s)" ]; then
    echo "ASTERIX AI bootstrap: starting local intelligence..."
    run_auto_fix_engine
    echo "ASTERIX AI startup: ready and monitoring local host state" > "$AI_LOG_FILE"
    echo "ASTERIX AI startup: ready"
else
    echo "ASTERIX AI startup: already active"
fi

if [ -f /tmp/asterix_ai_boot_status.txt ]; then
    echo "---- AI boot summary ----"
    tail -n 12 /tmp/asterix_ai_boot_status.txt 2>/dev/null || true
fi
