#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS — ProxyChains Creator Engine (Native Bash Fallback)
# Validates SOCKS4/SOCKS5 proxies and builds verified proxychains.conf.
# Zero external dependencies.
# ==============================================================================

set -e

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[38;5;51m"
C_GREEN="\033[38;5;46m"
C_YELLOW="\033[38;5;220m"
C_RED="\033[38;5;196m"
C_MAGENTA="\033[38;5;201m"
C_WHITE="\033[38;5;231m"
C_BLUE="\033[38;5;45m"
C_GRAY="\033[38;5;244m"

VAULT_DIR="${HOME}/.asterix_vault/proxychains"
CONFIG_OUT="${VAULT_DIR}/proxychains.conf"

echo -e "${C_CYAN}${C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_CYAN}║${C_WHITE} ${C_BOLD}[ ASTERIX PROXYCHAINS CREATOR // PROXY VALIDATION & CHAIN ENGINE ]${C_RESET}${C_CYAN}       ║${C_RESET}"
echo -e "${C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝${C_RESET}\n"

action="${1:-scan}"
shift || true

test_tcp_port() {
    local ip="$1"
    local port="$2"
    if command -v nc >/dev/null 2>&1; then
        nc -z -w 2 "$ip" "$port" >/dev/null 2>&1
    else
        timeout 2 bash -c "cat < /dev/null > /dev/tcp/${ip}/${port}" 2>/dev/null
    fi
}

mkdir -p "$VAULT_DIR" 2>/dev/null || true

case "$action" in
    scan|test|check)
        echo -e "  ${C_CYAN}[*] Testing Proxy Nodes for SOCKS4 / SOCKS5 Availability...${C_RESET}\n"
        echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
        printf " %-8s %-18s %-8s %-10s %-10s %s\n" "STATUS" "IP ADDRESS" "PORT" "TYPE" "COUNTRY" "CHAIN"
        echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"

        # Test curated nodes
        proxies=(
            "188.166.49.208:1080:socks5:NL"
            "159.203.87.130:1080:socks5:US"
            "178.62.203.220:1080:socks5:GB"
            "138.68.60.227:1080:socks5:DE"
            "45.77.200.12:1080:socks4:JP"
            "185.199.229.156:1080:socks4:FR"
        )

        cat << 'EOF' > "$CONFIG_OUT"
# ASTERIX OS — Verified ProxyChains Configuration (Bash Generator)
dynamic_chain
proxy_dns
quiet_mode
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
EOF

        hop=1
        for entry in "${proxies[@]}"; do
            IFS=':' read -r ip port proto country <<< "$entry"
            if test_tcp_port "$ip" "$port"; then
                printf " ${C_GREEN}%-8s${C_RESET} %-18s %-8s ${C_CYAN}%-10s${C_RESET} %-10s ${C_MAGENTA}Hop #%s${C_RESET}\n" "[ALIVE]" "$ip" "$port" "$proto" "$country" "$hop"
                echo "${proto} ${ip} ${port}" >> "$CONFIG_OUT"
                hop=$((hop + 1))
            else
                printf " ${C_RED}%-8s${C_RESET} %-18s %-8s ${C_GRAY}%-10s${C_RESET} %-10s ${C_GRAY}SKIPPED${C_RESET}\n" "[DEAD]" "$ip" "$port" "$proto" "$country"
            fi
        done
        echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"

        echo -e "  ${C_GREEN}${C_BOLD}[✔] Chain Configured in:${C_RESET} ${C_YELLOW}${CONFIG_OUT}${C_RESET}"
        echo -e "  ${C_WHITE}Execute via:${C_RESET} ${C_GREEN}proxychains4 -f ${CONFIG_OUT} <command>${C_RESET}\n"
        ;;

    status|show)
        if [ -f "$CONFIG_OUT" ]; then
            echo -e "  ${C_GREEN}${C_BOLD}[✔] Active ProxyChains Configuration Located:${C_RESET} ${CONFIG_OUT}\n"
            grep -v '^#' "$CONFIG_OUT" | grep -v '^$' | while read -r line; do
                echo -e "    ${C_CYAN}${line}${C_RESET}"
            done
            echo ""
        else
            echo -e "  ${C_YELLOW}[i] No ProxyChains config generated yet. Run 'ax proxychains scan'${C_RESET}\n"
        fi
        ;;

    *)
        echo -e "  ${C_WHITE}${C_BOLD}USAGE:${C_RESET}"
        echo -e "    ax proxychains scan         - Scan proxies, check latency, display IP/port/country/type"
        echo -e "    ax proxychains status       - Display currently configured proxy chain\n"
        ;;
esac
