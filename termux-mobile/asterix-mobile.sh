#!/usr/bin/env bash
# ASTERIX mobile command helper
# Easier commands for the Termux demo OS

set -u

ASTERIX_ROOT="${ASTERIX_ROOT:-$HOME/ASTERIX-OS}"
MOBILE_DIR="${ASTERIX_ROOT}/termux-mobile"
TARGET_SCRIPT="${MOBILE_DIR}/target-tracker.sh"
AI_SCRIPT="${MOBILE_DIR}/asterix-ai-startup.sh"
BOOT_SCRIPT="${MOBILE_DIR}/asterix-termux-init.sh"

usage() {
    cat <<'USAGE'
ASTERIX Mobile Helper

Usage:
  asterix-mobile start [--theme=neon]
  asterix-mobile ai
  asterix-mobile tracker <ip-or-host> [--geo|--save|--json|--history]
  asterix-mobile sweep <ip-range>
  asterix-mobile theme <matrix|neon|pulse|glitch|stealth>
  asterix-mobile help

Examples:
  asterix-mobile start --theme=neon
  asterix-mobile tracker 8.8.8.8 --geo
  asterix-mobile sweep 192.168.1.0/24
  asterix-mobile theme pulse
USAGE
}

ensure_scripts() {
    [ -f "$TARGET_SCRIPT" ] && chmod +x "$TARGET_SCRIPT" 2>/dev/null || true
    [ -f "$AI_SCRIPT" ] && chmod +x "$AI_SCRIPT" 2>/dev/null || true
    [ -f "$BOOT_SCRIPT" ] && chmod +x "$BOOT_SCRIPT" 2>/dev/null || true
}

cmd="${1:-help}"
shift || true

ensure_scripts

case "$cmd" in
    start)
        if [ -f "$BOOT_SCRIPT" ]; then
            "$BOOT_SCRIPT" "$@"
        else
            echo "Boot script not found: $BOOT_SCRIPT"
            exit 1
        fi
        ;;
    ai)
        if [ -f "$AI_SCRIPT" ]; then
            "$AI_SCRIPT"
        else
            echo "AI startup script not found: $AI_SCRIPT"
            exit 1
        fi
        ;;
    tracker)
        if [ -f "$TARGET_SCRIPT" ]; then
            "$TARGET_SCRIPT" "$@"
        else
            echo "Tracker script not found: $TARGET_SCRIPT"
            exit 1
        fi
        ;;
    sweep)
        if [ -f "$TARGET_SCRIPT" ]; then
            "$TARGET_SCRIPT" "$@" --sweep
        else
            echo "Tracker script not found: $TARGET_SCRIPT"
            exit 1
        fi
        ;;
    theme)
        theme_name="${1:-matrix}"
        shift || true
        if [ -f "$BOOT_SCRIPT" ]; then
            "$BOOT_SCRIPT" --theme="$theme_name" "$@"
        else
            echo "Boot script not found: $BOOT_SCRIPT"
            exit 1
        fi
        ;;
    help|-h|--help)
        usage
        ;;
    *)
        usage
        exit 1
        ;;
esac
