#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Discord Cloud Storage & Task Notification Bridge
# Supports: File Uploads, Webhook Vault Backups, Task Alerts & Telemetry
# =====================================================================

set -e

CONFIG_DIR="${HOME}/.config/asterix"
PERSIST_CONFIG="/asterix_persistent/discord.env"
CONFIG_FILE="${CONFIG_DIR}/discord.env"

# Colors
C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_MAGENTA='\033[38;5;201m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

mkdir -p "${CONFIG_DIR}"

load_webhook() {
    if [ -f "${PERSIST_CONFIG}" ]; then
        source "${PERSIST_CONFIG}"
    elif [ -f "${CONFIG_FILE}" ]; then
        source "${CONFIG_FILE}"
    fi

    if [ -z "${DISCORD_WEBHOOK_URL}" ]; then
        echo -e "${C_RED}[!] Discord Webhook URL not configured.${C_RESET}"
        echo -e "${C_YELLOW}[*] Run: as-discord setup${C_RESET}"
        exit 1
    fi
}

cmd_setup() {
    echo -e "${C_CYAN}${C_BOLD}"
    cat << 'EOF'
    ___   _____ ______ ______ ____     ____  ____ _____ ______ ____  ____  ____ 
   /   | / ___//_  __// ____// __ \   / __ \/  _// ___// ____// __ \/ __ \/ __ \
  / /| | \__ \  / /  / __/  / /_/ /  / / / // /  \__ \/ /    / / / / /_/ / / / /
 / ___ |___/ / / /  / /___ / _, _/  / /_/ // /  ___/ / /___ / /_/ / _, _/ /_/ / 
/_/  |_/____/ /_/  /_____//_/ |_|  /_____/___/ /____/\____/ \____/_/ |_/_____/  
        DISCORD CLOUD VAULT & NOTIFICATION SETUP
EOF
    echo -e "${C_RESET}"

    echo -e "${C_YELLOW}Paste your Discord Webhook URL below:${C_RESET}"
    read -r -p "Webhook URL > " input_url
    input_url=$(echo "$input_url" | tr -d '\r\n ')

    if [[ ! "$input_url" =~ ^https://discord\.com/api/webhooks/ ]]; then
        echo -e "${C_RED}[!] Invalid Discord Webhook URL. Format must start with https://discord.com/api/webhooks/...${C_RESET}"
        exit 1
    fi

    echo "DISCORD_WEBHOOK_URL=\"${input_url}\"" > "${CONFIG_FILE}"
    chmod 600 "${CONFIG_FILE}"

    # If persistence directory is present, save copy there too
    if [ -d "/asterix_persistent" ]; then
        echo "DISCORD_WEBHOOK_URL=\"${input_url}\"" > "${PERSIST_CONFIG}"
        chmod 600 "${PERSIST_CONFIG}"
    fi

    echo -e "${C_GREEN}[✔] Discord Webhook saved successfully!${C_RESET}"
    
    # Send test ping
    curl -s -H "Content-Type: application/json" \
         -X POST \
         -d '{"username":"ASTERIX OS NODE","avatar_url":"https://raw.githubusercontent.com/alexhack235-code/ASTERIX-BOOTING-SEQUENCE/main/assets/iso-branding/asterix_boot_01_electric_cyan_1788292127536.jpg","embeds":[{"title":"⚡ ASTERIX OS Node Online","description":"Discord Webhook & Cloud Storage Bridge successfully linked to this ASTERIX node.","color":65535,"footer":{"text":"ASTERIX Cybernetic Platform"}}]}' \
         "${input_url}" >/dev/null

    echo -e "${C_CYAN}[✔] Test payload transmitted to Discord channel!${C_RESET}"
}

cmd_notify() {
    load_webhook
    local msg="$1"
    if [ -z "$msg" ]; then
        echo -e "${C_RED}Usage: as-discord notify \"Your notification message\"${C_RESET}"
        exit 1
    fi

    local host
    host=$(hostname 2>/dev/null || echo "asterix-node")
    local payload
    payload=$(jq -n --arg m "$msg" --arg h "$host" \
      '{"username":"ASTERIX OS ALERT","embeds":[{"title":"⚡ Task Notification","description":$m,"color":32768,"fields":[{"name":"Node Host","value":$h,"inline":true},{"name":"Timestamp","value":(now|todate),"inline":true}],"footer":{"text":"ASTERIX OS System Dispatcher"}}]}')

    curl -s -H "Content-Type: application/json" -X POST -d "$payload" "$DISCORD_WEBHOOK_URL" >/dev/null
    echo -e "${C_GREEN}[✔] Notification dispatched to Discord!${C_RESET}"
}

cmd_send() {
    load_webhook
    local file_path="$1"
    local note="${2:-ASTERIX OS Data Artifact}"

    if [ ! -f "$file_path" ]; then
        echo -e "${C_RED}[!] File not found: ${file_path}${C_RESET}"
        exit 1
    fi

    local file_size
    file_size=$(stat -c%s "$file_path" 2>/dev/null || wc -c < "$file_path")
    if [ "$file_size" -gt 26214400 ]; then
        echo -e "${C_RED}[!] File size exceeds Discord 25MB limit (${file_size} bytes). Split or compress the file first.${C_RESET}"
        exit 1
    fi

    echo -e "${C_CYAN}[*] Uploading ${file_path} to Discord Cloud Vault...${C_RESET}"
    local filename
    filename=$(basename "$file_path")

    curl -s -F "file1=@${file_path}" \
         -F "content=💾 **ASTERIX CLOUD STORAGE ARTIFACT**\n📄 File: \`${filename}\`\n📝 Note: *${note}*\n⏱️ $(date)" \
         "$DISCORD_WEBHOOK_URL" >/dev/null

    echo -e "${C_GREEN}[✔] File uploaded to Discord storage channel successfully!${C_RESET}"
}

cmd_backup() {
    load_webhook
    local backup_src="/asterix_persistent"
    if [ ! -d "$backup_src" ]; then
        backup_src="${HOME}/asterix_persistent"
    fi

    mkdir -p "$backup_src"
    local timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    local archive_file="/tmp/asterix_vault_backup_${timestamp}.tar.gz"

    echo -e "${C_CYAN}[*] Compacting persistent vault: ${backup_src}...${C_RESET}"
    tar -czf "$archive_file" -C "$backup_src" . 2>/dev/null || tar -czf "$archive_file" "$backup_src"

    cmd_send "$archive_file" "Automated Persistent Vault Snapshot (${timestamp})"
    rm -f "$archive_file"
}

cmd_status() {
    load_webhook
    local host
    host=$(hostname 2>/dev/null || echo "asterix-node")
    local kernel
    kernel=$(uname -r)
    local ip
    ip=$(curl -s ifconfig.me 2>/dev/null || echo "127.0.0.1")
    local mem
    mem=$(free -h 2>/dev/null | awk '/Mem:/ {print $3 "/" $2}' || echo "N/A")

    local payload
    payload=$(jq -n --arg h "$host" --arg k "$kernel" --arg ip "$ip" --arg mem "$mem" \
      '{"username":"ASTERIX OS TELEMETRY","embeds":[{"title":"📊 Node Health & Telemetry Report","color":16711807,"fields":[{"name":"Hostname","value":$h,"inline":true},{"name":"Kernel","value":$k,"inline":true},{"name":"Public IP","value":$ip,"inline":true},{"name":"Memory Usage","value":$mem,"inline":true},{"name":"Persistence","value":"ACTIVE","inline":true}],"footer":{"text":"ASTERIX OS Telemetry Core"}}]}')

    curl -s -H "Content-Type: application/json" -X POST -d "$payload" "$DISCORD_WEBHOOK_URL" >/dev/null
    echo -e "${C_GREEN}[✔] Telemetry report posted to Discord!${C_RESET}"
}

case "$1" in
    setup)
        cmd_setup
        ;;
    notify)
        shift
        cmd_notify "$*"
        ;;
    send)
        cmd_send "$2" "$3"
        ;;
    backup)
        cmd_backup
        ;;
    status)
        cmd_status
        ;;
    *)
        echo -e "${C_CYAN}${C_BOLD}ASTERIX OS - Discord Cloud Storage & Task Bridge${C_RESET}"
        echo "Usage:"
        echo "  as-discord setup                 » Configure Discord Webhook URL"
        echo "  as-discord notify <message>      » Post real-time alert embed"
        echo "  as-discord send <file> [note]    » Upload file/archive to Discord storage"
        echo "  as-discord backup                » Compress and upload persistent vault"
        echo "  as-discord status                » Post live node health telemetry"
        ;;
esac
