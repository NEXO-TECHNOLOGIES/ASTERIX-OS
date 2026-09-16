#!/usr/bin/env bash
# ASTERIX mobile command helper
# Easier commands for the Termux demo OS

set -u

ASTERIX_ROOT="${ASTERIX_ROOT:-$HOME/ASTERIX-OS}"
MOBILE_DIR="${ASTERIX_ROOT}/termux-mobile"
TARGET_SCRIPT="${MOBILE_DIR}/target-tracker.sh"
AI_SCRIPT="${MOBILE_DIR}/asterix-ai-startup.sh"
BOOT_SCRIPT="${MOBILE_DIR}/asterix-termux-init.sh"
WEB_SCRIPT="${MOBILE_DIR}/web-structure.sh"
TOOLBOX_SCRIPT="${MOBILE_DIR}/termux-toolbox.sh"
DEBIAN_SCRIPT="${MOBILE_DIR}/debian-rootless.sh"

usage() {
    cat <<'USAGE'
ASTERIX Mobile Helper

Usage:
  asterix-mobile start [--theme=neon]
  asterix-mobile debian [shell|run|doctor|repair|status]
  asterix-mobile folder [create|tree|list|fix-perms]
  asterix-mobile ai
  asterix-mobile web-structure <url> [--tree|--source|--endpoints|--dump <dir>]
  asterix-mobile curl-tree <url>
  asterix-mobile webdump <url> <dir>
  asterix-mobile toolbox [battery|dns|clean|doctor]
  asterix-mobile tracker <ip-or-host> [--geo|--save|--json|--history]
  asterix-mobile sweep <ip-range>
  asterix-mobile theme <matrix|neon|pulse|glitch|stealth>
  asterix-mobile help

Examples:
  asterix-mobile debian shell
  asterix-mobile folder create my_recon --template=recon
  asterix-mobile debian repair
  asterix-mobile start --theme=neon
  asterix-mobile curl-tree https://example.com
  asterix-mobile webdump https://example.com ./site_dump
  asterix-mobile toolbox battery
  asterix-mobile tracker 8.8.8.8 --geo
  asterix-mobile sweep 192.168.1.0/24
  asterix-mobile theme pulse
USAGE
}

ensure_scripts() {
    [ -f "$TARGET_SCRIPT" ] && chmod +x "$TARGET_SCRIPT" 2>/dev/null || true
    [ -f "$AI_SCRIPT" ] && chmod +x "$AI_SCRIPT" 2>/dev/null || true
    [ -f "$BOOT_SCRIPT" ] && chmod +x "$BOOT_SCRIPT" 2>/dev/null || true
    [ -f "$WEB_SCRIPT" ] && chmod +x "$WEB_SCRIPT" 2>/dev/null || true
    [ -f "$TOOLBOX_SCRIPT" ] && chmod +x "$TOOLBOX_SCRIPT" 2>/dev/null || true
    [ -f "$DEBIAN_SCRIPT" ] && chmod +x "$DEBIAN_SCRIPT" 2>/dev/null || true
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
    debian|proot|rootless)
        if [ -f "$DEBIAN_SCRIPT" ]; then
            "$DEBIAN_SCRIPT" "$@"
        elif [ -f "${ASTERIX_ROOT}/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
            python3 "${ASTERIX_ROOT}/scripts-hub/ax-debian-manager.py" "$@"
        else
            echo "Debian rootless script not found: $DEBIAN_SCRIPT"
            exit 1
        fi
        ;;
    folder|folders)
        if [ -f "${ASTERIX_ROOT}/scripts-hub/ax-debian-manager.py" ] && command -v python3 >/dev/null 2>&1; then
            python3 "${ASTERIX_ROOT}/scripts-hub/ax-debian-manager.py" folder "$@"
        elif [ -f "$DEBIAN_SCRIPT" ]; then
            "$DEBIAN_SCRIPT" folder "$@"
        else
            echo "Folder manager engine not found."
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
    web-structure|webstructure|web-source)
        if [ -f "$WEB_SCRIPT" ]; then
            "$WEB_SCRIPT" "$@"
        else
            echo "Web structure script not found: $WEB_SCRIPT"
            exit 1
        fi
        ;;
    curl-tree)
        if [ -f "$WEB_SCRIPT" ]; then
            "$WEB_SCRIPT" --tree "$@"
        else
            echo "Web structure script not found: $WEB_SCRIPT"
            exit 1
        fi
        ;;
    webdump)
        if [ -f "$WEB_SCRIPT" ]; then
            url="${1:-}"
            dir="${2:-./site_dump}"
            if [ -z "$url" ]; then
                echo "Usage: asterix-mobile webdump <url> [output_dir]"
                exit 1
            fi
            "$WEB_SCRIPT" "$url" --dump "$dir"
        else
            echo "Web structure script not found: $WEB_SCRIPT"
            exit 1
        fi
        ;;
    toolbox|sys|mobile-sys)
        if [ -f "$TOOLBOX_SCRIPT" ]; then
            "$TOOLBOX_SCRIPT" "$@"
        else
            echo "Toolbox script not found: $TOOLBOX_SCRIPT"
            exit 1
        fi
        ;;
    battery|hw|hardware)
        if [ -f "$TOOLBOX_SCRIPT" ]; then
            "$TOOLBOX_SCRIPT" battery "$@"
        else
            echo "Toolbox script not found: $TOOLBOX_SCRIPT"
            exit 1
        fi
        ;;
    clean|purge|optimize)
        if [ -f "$TOOLBOX_SCRIPT" ]; then
            "$TOOLBOX_SCRIPT" clean "$@"
        else
            echo "Toolbox script not found: $TOOLBOX_SCRIPT"
            exit 1
        fi
        ;;
    doctor|heal|repair)
        if [ -f "$TOOLBOX_SCRIPT" ]; then
            "$TOOLBOX_SCRIPT" doctor "$@"
        else
            echo "Toolbox script not found: $TOOLBOX_SCRIPT"
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
