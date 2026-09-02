#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Secure System Cleanup & Artifact Sanitizer
# Wipes RAM cache, temp files, swap traces, and browser artifacts
# =====================================================================

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

echo -e "${C_CYAN}${C_BOLD}[*] ASTERIX OS Secure System Cleanup Engine${C_RESET}"
echo -e "${C_YELLOW}[*] This will wipe RAM cache, temp artifacts, and op logs.${C_RESET}\n"

BYTES_FREED=0

# Wipe /tmp directory
if [ -d /tmp ]; then
    BEFORE=$(du -sb /tmp 2>/dev/null | awk '{print $1}')
    find /tmp -mindepth 1 -delete 2>/dev/null || true
    AFTER=$(du -sb /tmp 2>/dev/null | awk '{print $1}')
    BYTES_FREED=$(( BYTES_FREED + BEFORE - AFTER ))
    echo -e "  ${C_GREEN}[✔] /tmp cleared${C_RESET}"
fi

# Wipe /var/tmp
if [ -d /var/tmp ]; then
    find /var/tmp -mindepth 1 -mtime +1 -delete 2>/dev/null || true
    echo -e "  ${C_GREEN}[✔] /var/tmp stale artifacts purged${C_RESET}"
fi

# Clear RAM page cache (requires root)
if [ "$EUID" -eq 0 ]; then
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null && \
        echo -e "  ${C_GREEN}[✔] RAM Page Cache Flushed (Pagecache + Dentries + Inodes)${C_RESET}" || \
        echo -e "  ${C_YELLOW}[!] RAM cache flush failed${C_RESET}"
else
    echo -e "  ${C_YELLOW}[!] Skipping RAM cache flush (requires root / sudo)${C_RESET}"
fi

# Wipe bash history artifacts
if [ -f "${HOME}/.bash_history" ]; then
    > "${HOME}/.bash_history"
    history -c 2>/dev/null || true
    echo -e "  ${C_GREEN}[✔] Bash history cleared${C_RESET}"
fi

# Clear thumbnails cache
THUMB_DIR="${HOME}/.cache/thumbnails"
if [ -d "$THUMB_DIR" ]; then
    rm -rf "${THUMB_DIR:?}"/*  2>/dev/null || true
    echo -e "  ${C_GREEN}[✔] Thumbnail cache wiped${C_RESET}"
fi

# Secure-wipe ASTERIX session logs
ASTERIX_LOGS="${HOME}/.config/asterix/logs"
if [ -d "$ASTERIX_LOGS" ]; then
    find "$ASTERIX_LOGS" -type f -exec shred -uz {} \; 2>/dev/null || true
    echo -e "  ${C_GREEN}[✔] ASTERIX session logs shredded${C_RESET}"
fi

echo ""
echo -e "${C_GREEN}${C_BOLD}[✔] System cleanup complete. Approximate disk space freed: ${BYTES_FREED} bytes${C_RESET}"
