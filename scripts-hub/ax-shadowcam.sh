#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ASTERIX OS — ax-shadowcam  (Dark Stream & Camera Security Auditor)     ║
# ║  RTSP / ONVIF stream security auditing · exposed endpoint detector       ║
# ║  100% defensive / forensic — audits network camera posture & encryption  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# Usage:
#   ax shadowcam audit <ip_or_host> [port]
#   ax shadowcam scan <subnet>           (e.g. 192.168.1.0/24)
#   ax shadowcam onvif [broadcast_ip]    (defaults to 239.255.255.250)
#   ax shadowcam paths <ip_or_host>      (test common RTSP channel paths)
#   ax shadowcam report <ip_or_host>     (generate full audit report)

R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
FG_DARKGRAY='\033[38;5;237m'; FG_GRAY='\033[38;5;243m'
FG_GREEN='\033[38;5;46m';     FG_DKGREEN='\033[38;5;22m'
FG_CYAN='\033[38;5;51m'
FG_MAGENTA='\033[38;5;201m';  FG_PURPLE='\033[38;5;141m'
FG_RED='\033[38;5;196m';      FG_ORANGE='\033[38;5;208m'
FG_YELLOW='\033[38;5;220m';   FG_WHITE='\033[38;5;231m'

hrule() {
    local c="${1:-─}" col="${2:-$FG_CYAN}"
    local w; w=$(tput cols 2>/dev/null || echo 72)
    echo -e "${col}$(printf "%${w}s" | tr ' ' "$c")${R}"
}
header() {
    clear
    hrule "═" "$FG_MAGENTA"
    echo -e " ${FG_MAGENTA}${BOLD}[ ASTERIX SHADOWCAM — STREAM & CAMERA SECURITY AUDITOR ]${R}"
    echo -e " ${FG_GRAY}RTSP · ONVIF · Video Surveillance Security Posture · Defensive Audit${R}"
    hrule "═" "$FG_MAGENTA"
    echo ""
}
ok()   { echo -e "  ${FG_GREEN}[✔]${R} $*"; }
warn() { echo -e "  ${FG_YELLOW}[!]${R} $*"; }
crit() { echo -e "  ${FG_RED}[✖]${R} $*"; }
info() { echo -e "  ${FG_CYAN}[*]${R} $*"; }

COMMON_RTSP_PATHS=(
    "/live/ch0"
    "/live/ch1"
    "/h264"
    "/h264Preview_01_main"
    "/h264Preview_01_sub"
    "/Streaming/Channels/101"
    "/Streaming/Channels/102"
    "/cam/realmonitor?channel=1&subtype=0"
    "/cam/realmonitor?channel=1&subtype=1"
    "/onvif1"
    "/media/video1"
    "/axis-media/media.amp"
    "/video.mjpg"
    "/mjpg/video.mjpg"
    "/1/stream1"
    "/live.sdp"
    "/mpeg4"
    "/ch01.264"
)

# Audit single host RTSP endpoint
audit_target() {
    local host="$1"
    local port="${2:-554}"
    header
    info "Target Host: ${FG_WHITE}${host}:${port}${R}"
    info "Sending RTSP OPTIONS probe..."

    local probe="OPTIONS rtsp://${host}:${port} RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: ASTERIX-ShadowCam/1.0\r\n\r\n"
    local response=""

    if command -v nc &>/dev/null; then
        response=$(printf "$probe" | nc -w 3 "$host" "$port" 2>/dev/null || true)
    elif command -v socat &>/dev/null; then
        response=$(printf "$probe" | socat -t 3 - "TCP:${host}:${port}" 2>/dev/null || true)
    fi

    if [[ -z "$response" ]]; then
        warn "No RTSP response received on port ${port} (port may be closed or filtered)."
        return 1
    fi

    echo ""
    info "RTSP Banner / Handshake Response:"
    echo -e "${FG_DARKGRAY}${response}${R}"
    echo ""

    # Check authentication
    if echo "$response" | grep -qi "401 Unauthorized"; then
        ok "RTSP authentication REQUIRED (Status: 401 Unauthorized)"
        if echo "$response" | grep -qi "Digest"; then
            ok "Authentication scheme: ${FG_GREEN}Digest Auth (Secure)${R}"
        elif echo "$response" | grep -qi "Basic"; then
            crit "Authentication scheme: ${FG_RED}Basic Auth (Insecure plaintext)${R}"
        fi
    elif echo "$response" | grep -qi "200 OK"; then
        crit "RTSP endpoint allows UNAUTHENTICATED OPTIONS (200 OK) — Potential Exposure!"
    fi

    # Check Server header
    local server
    server=$(echo "$response" | grep -i "Server:" | head -1)
    if [[ -n "$server" ]]; then
        info "Camera Device Banner: ${FG_YELLOW}${server}${R}"
    fi

    # Check Public supported methods
    local methods
    methods=$(echo "$response" | grep -i "Public:" | head -1)
    if [[ -n "$methods" ]]; then
        info "Supported RTSP Methods: ${FG_CYAN}${methods}${R}"
    fi
}

# Scan subnet for exposed camera ports (554, 8554, 80, 8080, 8000, 3702)
scan_subnet() {
    local subnet="$1"
    header
    info "Scanning subnet for camera/surveillance interfaces: ${FG_WHITE}${subnet}${R}"
    echo ""

    if command -v nmap &>/dev/null; then
        info "Running Nmap camera profile (ports 554,8554,8000,3702)..."
        nmap -sT -p 554,8554,8000,3702 --open -T4 "$subnet" -oG - 2>/dev/null | \
            grep "Ports:" | while IFS= read -r line; do
                local host; host=$(echo "$line" | awk '{print $2}')
                local ports; ports=$(echo "$line" | grep -oP 'Ports:.*')
                echo -e "  ${FG_GREEN}[HOST DETECTED]${R} ${FG_WHITE}${host}${R}  ${FG_YELLOW}${ports}${R}"
            done
    else
        warn "nmap not available. Using native TCP socket probe..."
        local prefix; prefix=$(echo "$subnet" | cut -d/ -f1 | cut -d. -f1-3)
        for i in {1..20}; do
            local test_ip="${prefix}.${i}"
            (echo >"/dev/tcp/${test_ip}/554") 2>/dev/null && \
                ok "RTSP Port 554 OPEN on ${test_ip}"
        done
    fi
}

# Test standard channel paths on a camera host
test_paths() {
    local host="$1"
    local port="${2:-554}"
    header
    info "Testing common RTSP stream endpoints on ${FG_WHITE}${host}:${port}${R}..."
    echo ""

    local exposed=0
    for path in "${COMMON_RTSP_PATHS[@]}"; do
        local uri="rtsp://${host}:${port}${path}"
        local probe="DESCRIBE ${uri} RTSP/1.0\r\nCSeq: 2\r\nUser-Agent: ASTERIX-ShadowCam/1.0\r\nAccept: application/sdp\r\n\r\n"
        local resp=""
        if command -v nc &>/dev/null; then
            resp=$(printf "$probe" | nc -w 2 "$host" "$port" 2>/dev/null || true)
        fi

        if echo "$resp" | grep -qi "200 OK"; then
            crit "EXPOSED UNPROTECTED STREAM: ${FG_RED}${uri}${R} (200 OK)"
            exposed=$(( exposed + 1 ))
        elif echo "$resp" | grep -qi "401 Unauthorized"; then
            ok "Protected (401 Auth): ${FG_CYAN}${path}${R}"
        elif echo "$resp" | grep -qi "404 Not Found"; then
            echo -e "  ${FG_DARKGRAY}[-] Not Found: ${path}${R}"
        fi
    done

    echo ""
    if (( exposed > 0 )); then
        crit "SECURITY RISK: Found ${exposed} unauthenticated stream path(s)!"
    else
        ok "All tested stream paths require authentication or are disabled."
    fi
}

# ONVIF WS-Discovery probe
probe_onvif() {
    local bcast="${1:-239.255.255.250}"
    header
    info "Probing ONVIF WS-Discovery on UDP 3702 (${bcast})..."
    echo ""

    local onvif_xml='<?xml version="1.0" encoding="utf-8"?><Envelope xmlns:tds="http://www.onvif.org/ver10/device/wsdl" xmlns="http://www.w3.org/2003/05/soap-envelope"><Header><wsa:MessageID xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">uuid:asterix-probe</wsa:MessageID><wsa:To xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To><wsa:Action xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action></Header><Body><Probe xmlns="http://schemas.xmlsoap.org/ws/2005/04/discovery"><Types>tds:Device</Types></Probe></Body></Envelope>'

    if command -v socat &>/dev/null; then
        echo "$onvif_xml" | socat -t 3 - "UDP-DATAGRAM:${bcast}:3702,broadcast" 2>/dev/null | \
            grep -oP '(?<=<d:XAddrs>)[^<]+' | while IFS= read -r xaddr; do
                ok "ONVIF Device Endpoint Found: ${FG_GREEN}${xaddr}${R}"
            done
    else
        warn "socat required for ONVIF WS-Discovery UDP broadcast."
        info "Install via: sudo apt install socat  or  pkg install socat"
    fi
}

CMD="${1:-}"
TARGET="${2:-}"
PORT="${3:-554}"

case "$CMD" in
    audit)
        [[ -z "$TARGET" ]] && { echo "Usage: ax shadowcam audit <ip_or_host> [port]"; exit 1; }
        audit_target "$TARGET" "$PORT"
        ;;
    scan)
        [[ -z "$TARGET" ]] && { echo "Usage: ax shadowcam scan <subnet>  (e.g. 192.168.1.0/24)"; exit 1; }
        scan_subnet "$TARGET"
        ;;
    paths)
        [[ -z "$TARGET" ]] && { echo "Usage: ax shadowcam paths <ip_or_host> [port]"; exit 1; }
        test_paths "$TARGET" "$PORT"
        ;;
    onvif)
        probe_onvif "$TARGET"
        ;;
    report)
        [[ -z "$TARGET" ]] && { echo "Usage: ax shadowcam report <ip_or_host> [port]"; exit 1; }
        local rpt="$HOME/asterix_persistent/shadowcam-${TARGET}-$(date +%Y%m%d).report"
        mkdir -p "$(dirname "$rpt")" 2>/dev/null
        {
            audit_target "$TARGET" "$PORT"
            test_paths "$TARGET" "$PORT"
        } | tee "$rpt"
        ok "Report saved: $rpt"
        ;;
    help|--help|-h|"")
        header
        echo -e " ${FG_WHITE}USAGE:${R}"
        echo -e "   ${FG_CYAN}ax shadowcam audit <host> [port]${R}  Audit RTSP banner, methods & auth enforcement"
        echo -e "   ${FG_CYAN}ax shadowcam scan <subnet>${R}       Scan network for exposed camera ports (554, 8554)"
        echo -e "   ${FG_CYAN}ax shadowcam paths <host> [port]${R}  Test 18 standard industrial RTSP channels"
        echo -e "   ${FG_CYAN}ax shadowcam onvif [ip]${R}          WS-Discovery probe for ONVIF surveillance hardware"
        echo -e "   ${FG_CYAN}ax shadowcam report <host>${R}        Comprehensive camera security report"
        echo ""
        ;;
    *)
        echo -e "${FG_RED}[!] Unknown command: $CMD${R}  (use: ax shadowcam help)"
        exit 1
        ;;
esac