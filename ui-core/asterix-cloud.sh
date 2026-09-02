#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Cloud Compute & Remote Storage Client
# Offloads heavy calculations, compiles, and files to your cloud panel
# =====================================================================

set -e

CONFIG_DIR="${HOME}/.config/asterix"
CONFIG_FILE="${CONFIG_DIR}/cloud.env"
PERSIST_CONFIG="/asterix_persistent/cloud.env"

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_MAGENTA='\033[38;5;201m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

mkdir -p "${CONFIG_DIR}"

load_config() {
    if [ -f "${PERSIST_CONFIG}" ]; then
        source "${PERSIST_CONFIG}"
    elif [ -f "${CONFIG_FILE}" ]; then
        source "${CONFIG_FILE}"
    fi

    if [ -z "${ASTERIX_CLOUD_URL}" ]; then
        echo -e "${C_RED}[!] Cloud panel not linked.${C_RESET}"
        echo -e "${C_YELLOW}[*] Run: as-cloud link <panel_url> [auth_key]${C_RESET}"
        echo -e "    Example: as-cloud link http://123.45.67.89:8080 asterix-sec-key-2026"
        exit 1
    fi
    ASTERIX_CLOUD_KEY="${ASTERIX_CLOUD_KEY:-asterix-sec-key-2026}"
}

cmd_link() {
    local url="$1"
    local key="${2:-asterix-sec-key-2026}"

    if [ -z "$url" ]; then
        echo -e "${C_CYAN}${C_BOLD}"
        cat << 'EOF'
    ___   _____ ______ ______ ____     ____  __    ____  __  ______
   /   | / ___//_  __// ____// __ \   / __ \/ /   / __ \/ / / / __ \
  / /| | \__ \  / /  / __/  / /_/ /  / / / / /   / / / / / / / / / /
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /___/ /_/ / /_/ / /_/ / 
/_/  |_/____/ /_/  /_____//_/ |_|   \____/_____/\____/\____/_____/  
       LINK 50-COINS PANEL / CLOUD COMPUTE WORKER NODE
EOF
        echo -e "${C_RESET}"
        read -r -p "Enter Panel / VPS URL (e.g. http://123.45.67.89:8080) > " url
        read -r -p "Enter Auth Key [default: asterix-sec-key-2026] > " key
        key="${key:-asterix-sec-key-2026}"
    fi

    url="${url%/}"

    echo -e "${C_CYAN}[*] Testing connection to ${url}...${C_RESET}"
    if curl -s --max-time 5 "${url}/health" | grep -q "ONLINE"; then
        echo -e "${C_GREEN}[✔] Cloud Node responded ONLINE!${C_RESET}"
    else
        echo -e "${C_YELLOW}[!] Warning: Node could not be verified, saving configuration anyway...${C_RESET}"
    fi

    echo "ASTERIX_CLOUD_URL=\"${url}\"" > "${CONFIG_FILE}"
    echo "ASTERIX_CLOUD_KEY=\"${key}\"" >> "${CONFIG_FILE}"
    chmod 600 "${CONFIG_FILE}"

    if [ -d "/asterix_persistent" ]; then
        cp "${CONFIG_FILE}" "${PERSIST_CONFIG}"
    fi

    echo -e "${C_GREEN}[✔] Cloud Compute Node linked successfully!${C_RESET}"
}

cmd_status() {
    load_config
    echo -e "${C_CYAN}[*] Fetching Cloud Node Telemetry from ${ASTERIX_CLOUD_URL}...${C_RESET}\n"
    local res
    res=$(curl -s -H "X-Asterix-Key: ${ASTERIX_CLOUD_KEY}" "${ASTERIX_CLOUD_URL}/status")

    if command -v jq >/dev/null 2>&1; then
        echo "$res" | jq .
    else
        echo "$res"
    fi
}

cmd_compute() {
    load_config
    local command_str="$*"

    if [ -z "$command_str" ]; then
        echo -e "${C_RED}Usage: as-cloud compute \"<command to run in cloud>\"${C_RESET}"
        echo -e "Example: as-cloud compute \"gcc -O3 -march=native code.c -o code && ./code\""
        exit 1
    fi

    echo -e "${C_CYAN}[*] Offloading computation to Cloud Panel...${C_RESET}"
    echo -e "${C_GRAY}Task: ${command_str}${C_RESET}\n"

    local payload
    if command -v jq >/dev/null 2>&1; then
        payload=$(jq -n --arg cmd "$command_str" '{"command": $cmd, "timeout": 180}')
    else
        payload="{\"command\":\"${command_str}\",\"timeout\":180}"
    fi

    local res
    res=$(curl -s -H "Content-Type: application/json" \
                 -H "X-Asterix-Key: ${ASTERIX_CLOUD_KEY}" \
                 -X POST \
                 -d "$payload" \
                 "${ASTERIX_CLOUD_URL}/compute")

    if command -v jq >/dev/null 2>&1; then
        local stdout
        local stderr
        local time_sec
        local success
        stdout=$(echo "$res" | jq -r '.stdout // ""')
        stderr=$(echo "$res" | jq -r '.stderr // ""')
        time_sec=$(echo "$res" | jq -r '.execution_time_sec // "N/A"')
        success=$(echo "$res" | jq -r '.success // false')

        if [ "$success" = "true" ]; then
            echo -e "${C_GREEN}${C_BOLD}[✔] Cloud Task Completed Successfully in ${time_sec}s:${C_RESET}"
            echo -e "${stdout}"
        else
            echo -e "${C_RED}[!] Cloud Task Failed in ${time_sec}s:${C_RESET}"
            [ -n "$stdout" ] && echo -e "${stdout}"
            [ -n "$stderr" ] && echo -e "${C_RED}${stderr}${C_RESET}"
        fi
    else
        echo "$res"
    fi
}

cmd_push() {
    load_config
    local file_path="$1"

    if [ ! -f "$file_path" ]; then
        echo -e "${C_RED}[!] File not found: ${file_path}${C_RESET}"
        exit 1
    fi

    local filename
    filename=$(basename "$file_path")
    echo -e "${C_CYAN}[*] Uploading ${filename} to Cloud Vault...${C_RESET}"

    local res
    res=$(curl -s -H "X-Asterix-Key: ${ASTERIX_CLOUD_KEY}" \
                 --data-binary "@${file_path}" \
                 "${ASTERIX_CLOUD_URL}/upload?file=${filename}")

    echo -e "${C_GREEN}[✔] Upload response: ${res}${C_RESET}"
}

cmd_pull() {
    load_config
    local remote_filename="$1"
    local output_path="${2:-./${remote_filename}}"

    if [ -z "$remote_filename" ]; then
        echo -e "${C_RED}Usage: as-cloud pull <remote_filename> [destination_path]${C_RESET}"
        exit 1
    fi

    echo -e "${C_CYAN}[*] Downloading ${remote_filename} from Cloud Vault...${C_RESET}"
    curl -s -H "X-Asterix-Key: ${ASTERIX_CLOUD_KEY}" \
         -o "${output_path}" \
         "${ASTERIX_CLOUD_URL}/download?file=${remote_filename}"

    if [ -f "${output_path}" ] && [ -s "${output_path}" ]; then
        echo -e "${C_GREEN}[✔] File saved to ${output_path} (${remote_filename})${C_RESET}"
    else
        echo -e "${C_RED}[!] Download failed or remote file not found.${C_RESET}"
        rm -f "${output_path}" 2>/dev/null || true
    fi
}

cmd_list() {
    load_config
    echo -e "${C_CYAN}[*] Remote Cloud Vault Files:${C_RESET}"
    curl -s -H "X-Asterix-Key: ${ASTERIX_CLOUD_KEY}" "${ASTERIX_CLOUD_URL}/status" | \
        jq -r '.file_list[]' 2>/dev/null || echo -e "${C_YELLOW}(Install jq for formatted file lists)${C_RESET}"
}

case "$1" in
    link)
        cmd_link "$2" "$3"
        ;;
    status)
        cmd_status
        ;;
    compute|exec)
        shift
        cmd_compute "$@"
        ;;
    push|upload)
        cmd_push "$2"
        ;;
    pull|download)
        cmd_pull "$2" "$3"
        ;;
    list|ls)
        cmd_list
        ;;
    *)
        echo -e "${C_CYAN}${C_BOLD}ASTERIX OS - Cloud Compute & Storage Client${C_RESET}"
        echo "Usage:"
        echo "  as-cloud link <url> [key]      » Link ASTERIX to your 50-coins panel / VPS"
        echo "  as-cloud status                » Check cloud compute CPU, RAM, and storage"
        echo "  as-cloud compute \"<command>\"   » Offload heavy computation to the cloud"
        echo "  as-cloud push <local_file>     » Store file in remote cloud vault"
        echo "  as-cloud pull <remote_file>    » Retrieve file from remote cloud vault"
        echo "  as-cloud list                  » List all files stored in cloud vault"
        ;;
esac
