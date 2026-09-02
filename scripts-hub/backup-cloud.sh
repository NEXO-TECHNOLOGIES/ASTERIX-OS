#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Automated Cloud Vault Sync & Backup
# Syncs the persistent vault to Discord and/or Cloud Panel
# =====================================================================

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

PERSIST_DIR="${1:-/asterix_persistent}"
[ -d "$PERSIST_DIR" ] || PERSIST_DIR="${HOME}/asterix_persistent"
mkdir -p "$PERSIST_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE="/tmp/asterix_vault_${TIMESTAMP}.tar.gz"

echo -e "${C_CYAN}${C_BOLD}[*] ASTERIX OS Cloud Vault Sync${C_RESET}"
echo -e "${C_YELLOW}[*] Compressing: ${PERSIST_DIR}${C_RESET}"
tar -czf "$ARCHIVE" -C "$PERSIST_DIR" . 2>/dev/null && \
    echo -e "${C_GREEN}[✔] Archive created: ${ARCHIVE}${C_RESET}"

# Sync via as-cloud if panel is configured
if command -v as-cloud >/dev/null 2>&1; then
    echo -e "${C_CYAN}[*] Uploading to Cloud Panel...${C_RESET}"
    as-cloud push "$ARCHIVE" && echo -e "${C_GREEN}[✔] Cloud panel upload done!${C_RESET}"
elif [ -f /etc/asterix/ui-core/asterix-cloud.sh ]; then
    /etc/asterix/ui-core/asterix-cloud.sh push "$ARCHIVE"
fi

# Sync via as-discord if webhook is configured
if command -v as-discord >/dev/null 2>&1; then
    echo -e "${C_CYAN}[*] Uploading to Discord Vault...${C_RESET}"
    as-discord send "$ARCHIVE" "Automated Vault Backup ${TIMESTAMP}"
elif [ -f /etc/asterix/ui-core/asterix-discord.sh ]; then
    /etc/asterix/ui-core/asterix-discord.sh send "$ARCHIVE" "Automated Vault Backup ${TIMESTAMP}"
fi

rm -f "$ARCHIVE"
echo -e "${C_GREEN}[✔] Backup cloud sync complete!${C_RESET}"
