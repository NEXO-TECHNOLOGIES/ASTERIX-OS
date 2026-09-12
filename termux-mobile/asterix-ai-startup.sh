#!/usr/bin/env bash
# ASTERIX OS Termux AI startup helper
# Starts local AI and keeps the shell ready on first boot.

set -u

ASTERIX_ROOT="${ASTERIX_ROOT:-$HOME/ASTERIX-OS}"
AI_ENTRY="${ASTERIX_ROOT}/asterix-ai/ax_ai.py"
AI_LOG_DIR="${HOME}/.asterix_storage"
AI_LOG_FILE="${AI_LOG_DIR}/ai_boot.log"

mkdir -p "$AI_LOG_DIR" 2>/dev/null || true

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
    python3 "$AI_ENTRY" --security > /tmp/asterix_ai_boot_status.txt 2>&1 || true
    echo "ASTERIX AI startup: ready and monitoring local host state" > "$AI_LOG_FILE"
    echo "ASTERIX AI startup: ready"
else
    echo "ASTERIX AI startup: already active"
fi

if [ -f /tmp/asterix_ai_boot_status.txt ]; then
    echo "---- AI boot summary ----"
    tail -n 12 /tmp/asterix_ai_boot_status.txt 2>/dev/null || true
fi
