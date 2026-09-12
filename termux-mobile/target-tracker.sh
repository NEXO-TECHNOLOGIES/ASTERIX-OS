#!/usr/bin/env bash
# ASTERIX OS Target IP Tracker for Termux
# Features: history, sweep, geo-style metadata, JSON output, local logging
# Usage: target-tracker.sh <ip-or-host> [--save] [--json] [--history] [--geo] [--sweep]

set -u

TARGET=""
SAVE_LOG=0
SHOW_JSON=0
SHOW_HISTORY=0
SHOW_GEO=0
SWEEP_MODE=0
THEME="matrix"

for arg in "$@"; do
    case "$arg" in
        --save) SAVE_LOG=1 ;;
        --json) SHOW_JSON=1 ;;
        --history) SHOW_HISTORY=1 ;;
        --geo) SHOW_GEO=1 ;;
        --sweep) SWEEP_MODE=1 ;;
        --theme=*) THEME="${arg#*=}" ;;
        --theme) THEME="next" ;;
        -h|--help|help) TARGET="" ;;
        *) if [ -z "$TARGET" ]; then TARGET="$arg"; fi ;;
    esac
done

LOG_DIR="${HOME}/.asterix_storage"
LOG_FILE="${LOG_DIR}/target_tracker.log"
mkdir -p "$LOG_DIR" 2>/dev/null || true

trim_target() {
    echo "$1" | tr -d '\r' | sed 's#^https\?://##; s#/$##'
}

resolve_ip() {
    local value="$1"
    if [[ "$value" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "$value"
        return 0
    fi

    if command -v getent >/dev/null 2>&1; then
        local resolved
        resolved=$(getent ahostsv4 "$value" 2>/dev/null | awk 'NR==1 {print $1}' | head -n 1)
        if [ -n "$resolved" ]; then
            echo "$resolved"
            return 0
        fi
    fi

    if command -v ping >/dev/null 2>&1; then
        local ping_ip
        ping_ip=$(ping -c 1 -W 1 "$value" 2>/dev/null | awk '/from/ {print $3}' | sed 's/(//; s/)//' | head -n 1)
        if [ -n "$ping_ip" ]; then
            echo "$ping_ip"
            return 0
        fi
    fi

    return 1
}

resolve_latency_ms() {
    local host="$1"
    if command -v ping >/dev/null 2>&1; then
        local out
        out=$(ping -c 1 -W 1 "$host" 2>/dev/null | tail -n 1 | grep -Eo '[0-9]+\.[0-9]+ ms' | head -n 1 | grep -Eo '[0-9]+\.[0-9]+' | head -n 1)
        if [ -n "$out" ]; then
            echo "$out"
            return 0
        fi
    fi
    echo "n/a"
}

is_private_ip() {
    local ip="$1"
    case "$ip" in
        10.*|192.168.*|172.1[6789].*|172.2[0-9].*|172.3[01].*) return 0 ;;
        *) return 1 ;;
    esac
}

geo_style() {
    local ip="$1"
    if [ "$ip" = "UNKNOWN" ]; then
        echo "region=unresolved; network=unknown; signal=none"
        return 0
    fi

    if is_private_ip "$ip"; then
        echo "region=local-private; network=internal-lan; signal=strong"
    else
        echo "region=public-internet; network=external-route; signal=stable"
    fi
}

generate_sweep_targets() {
    local value="$1"
    if [[ "$value" == *"/"* ]]; then
        local base="${value%/*}"
        local prefix="${value#*/}"
        local octet="${base##*.}"
        local base_prefix="${base%.*}"
        if [[ "$prefix" == "24" ]] || [[ "$prefix" == "16" ]] || [[ "$prefix" == "8" ]]; then
            for n in 1 2 3 4 5 6 7 8 9 10 20 30 40 50 60 70 80 90 100 110 120 130 140 150 160 170 180 190 200 210 220 230 240 250; do
                echo "${base_prefix}.${n}"
            done
        fi
        return 0
    fi

    if [[ "$value" == *"-"* ]]; then
        local start="${value%-*}"
        local stop="${value#*-}"
        local s_oct="${start##*.}"
        local e_oct="${stop##*.}"
        for n in $(seq "$s_oct" "$e_oct" 2>/dev/null || echo "$s_oct"); do
            echo "${start%.*}.${n}"
        done
        return 0
    fi

    echo "$value"
}

if [ -z "$TARGET" ] && [ "$SHOW_HISTORY" -eq 0 ]; then
    echo "Usage: target-tracker.sh <ip-or-host> [--save] [--json] [--history] [--geo] [--sweep]"
    echo "Example: target-tracker.sh 8.8.8.8"
    echo "Example: target-tracker.sh example.com --save --geo"
    echo "Example: target-tracker.sh 192.168.1.0/24 --sweep"
    exit 1
fi

if [ "$SHOW_HISTORY" -eq 1 ]; then
    if [ -f "$LOG_FILE" ]; then
        echo "ASTERIX tracker history"
        tail -n 12 "$LOG_FILE" 2>/dev/null || true
    else
        echo "No tracker history yet. Run: target-tracker 8.8.8.8 --save"
    fi
    exit 0
fi

TARGET_CLEAN=$(trim_target "$TARGET")
TARGET_IP=""
TARGET_IP=$(resolve_ip "$TARGET_CLEAN" || true)
if [ -z "$TARGET_IP" ]; then
    TARGET_IP="UNKNOWN"
fi

TARGET_HOST="${TARGET_CLEAN}"
STATUS="UNKNOWN"
LATENCY="n/a"
if [ "$TARGET_IP" != "UNKNOWN" ]; then
    if command -v ping >/dev/null 2>&1; then
        if ping -c 1 -W 1 "$TARGET_IP" >/dev/null 2>&1; then
            STATUS="ONLINE"
            LATENCY=$(resolve_latency_ms "$TARGET_IP")
        else
            STATUS="UNREACHABLE"
        fi
    else
        STATUS="RESOLVED"
    fi
fi

NOW=$(date '+%Y-%m-%d %H:%M:%S %Z')
if [ "$SAVE_LOG" -eq 1 ]; then
    printf '%s | target=%s | ip=%s | status=%s | latency=%s\n' "$NOW" "$TARGET_CLEAN" "$TARGET_IP" "$STATUS" "$LATENCY" >> "$LOG_FILE" 2>/dev/null || true
fi

if [ "$SHOW_JSON" -eq 1 ]; then
    printf '{"target":"%s","ip":"%s","status":"%s","latency":"%s","timestamp":"%s"}\n' \
        "$TARGET_CLEAN" "$TARGET_IP" "$STATUS" "$LATENCY" "$NOW"
    exit 0
fi

if [ "$SWEEP_MODE" -eq 1 ]; then
    echo "ASTERIX sweep mode: ${TARGET_CLEAN}"
    for ip in $(generate_sweep_targets "$TARGET_CLEAN"); do
        if command -v ping >/dev/null 2>&1; then
            if ping -c 1 -W 1 "$ip" >/dev/null 2>&1; then
                echo "[ONLINE] ${ip} $(resolve_latency_ms "$ip") ms"
            else
                echo "[DOWN]   ${ip}"
            fi
        else
            echo "[SKIP]   ${ip} (ping unavailable)"
        fi
    done
    exit 0
fi

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

case "$STATUS" in
    ONLINE) STATUS_COLOR="$GREEN" ;;
    RESOLVED|UNREACHABLE) STATUS_COLOR="$YELLOW" ;;
    *) STATUS_COLOR="$RED" ;;
esac

GEO_INFO=$(geo_style "$TARGET_IP")

if [ "$SHOW_GEO" -eq 1 ]; then
    echo -e "${CYAN}${BOLD}╔═══════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║${NC} ${YELLOW}ASTERIX GEO STYLE TRACKER${NC} ${CYAN}${BOLD}║${NC}"
    echo -e "${CYAN}${BOLD}╚═══════════════════════════════╝${NC}"
    echo ""
    echo -e "${BOLD}TARGET:${NC} ${TARGET_CLEAN}"
    echo -e "${BOLD}IP:${NC}    ${TARGET_IP}"
    echo -e "${BOLD}ROUTE:${NC} ${GEO_INFO}"
    echo -e "${BOLD}LATENCY:${NC} ${LATENCY}"
    echo -e "${BOLD}STATUS:${NC} ${STATUS_COLOR}${STATUS}${NC}"
    echo -e "${BOLD}TIME:${NC}   ${NOW}"
    echo ""
    exit 0
fi

echo -e "${CYAN}${BOLD}╔═══════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║${NC} ${YELLOW}ASTERIX TARGET TRACKER${NC} ${CYAN}${BOLD}║${NC}"
echo -e "${CYAN}${BOLD}╚═══════════════════════════════╝${NC}"
echo ""
echo -e "${BOLD}TARGET:${NC} ${TARGET_CLEAN}"
echo -e "${BOLD}IP:${NC}    ${TARGET_IP}"
echo -e "${BOLD}STATUS:${NC} ${STATUS_COLOR}${STATUS}${NC}"
echo -e "${BOLD}LATENCY:${NC} ${LATENCY}"
echo -e "${BOLD}TIME:${NC}   ${NOW}"
echo ""

if [ "$SAVE_LOG" -eq 1 ]; then
    echo -e "${GREEN}[+] Saved to: ${LOG_FILE}${NC}"
fi

if [ -f "$LOG_FILE" ]; then
    echo -e "${YELLOW}Recent entries:${NC}"
    tail -n 5 "$LOG_FILE" 2>/dev/null || true
fi
