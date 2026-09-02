#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Automated Network Reconnaissance & Diagnostic Reporter
# Runs a full network scan and generates a structured report
# =====================================================================

set -e

C_CYAN='\033[38;5;51m'
C_GREEN='\033[38;5;46m'
C_YELLOW='\033[38;5;220m'
C_RED='\033[38;5;196m'
C_BOLD='\033[1m'
C_RESET='\033[0m'

REPORT_DIR="${HOME}/asterix_reports"
mkdir -p "$REPORT_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="${REPORT_DIR}/net_recon_${TIMESTAMP}.txt"

TARGET="${1:-192.168.1.0/24}"

echo -e "${C_CYAN}${C_BOLD}"
cat << 'EOF'
    ___   _____ ______ ______ ____     ____  ____________  ____  _   __
   /   | / ___//_  __// ____// __ \   / __ \/ ____/ ____/ / __ \/ | / /
  / /| | \__ \  / /  / __/  / /_/ /  / /_/ / __/ / /     / / / /  |/ / 
 / ___ |___/ / / /  / /___ / _, _/  / _, _/ /___/ /___  / /_/ / /|  /  
/_/  |_/____/ /_/  /_____//_/ |_|  /_/ |_/_____/\____/  \____/_/ |_/   
        AUTOMATED NETWORK RECON & DIAGNOSTIC ENGINE
EOF
echo -e "${C_RESET}"

{
    echo "======================================"
    echo " ASTERIX OS Network Reconnaissance Report"
    echo " Generated: $(date)"
    echo " Target: $TARGET"
    echo "======================================"
    echo ""
} > "$REPORT_FILE"

echo -e "${C_YELLOW}[*] Target: ${TARGET}${C_RESET}"
echo -e "${C_YELLOW}[*] Report: ${REPORT_FILE}${C_RESET}\n"

echo -e "${C_CYAN}[1/5] Network Interface Discovery...${C_RESET}"
{
    echo "=== NETWORK INTERFACES ==="
    ip addr show 2>/dev/null || ifconfig 2>/dev/null || echo "ip/ifconfig not found"
    echo ""
} | tee -a "$REPORT_FILE"

echo -e "${C_CYAN}[2/5] Routing Table Analysis...${C_RESET}"
{
    echo "=== ROUTING TABLE ==="
    ip route show 2>/dev/null || route -n 2>/dev/null || echo "Not available"
    echo ""
} | tee -a "$REPORT_FILE"

echo -e "${C_CYAN}[3/5] ARP Cache Inspection...${C_RESET}"
{
    echo "=== ARP CACHE ==="
    arp -n 2>/dev/null || ip neigh show 2>/dev/null || echo "Not available"
    echo ""
} | tee -a "$REPORT_FILE"

if command -v nmap >/dev/null 2>&1; then
    echo -e "${C_CYAN}[4/5] Host Discovery (Nmap)...${C_RESET}"
    {
        echo "=== HOST DISCOVERY (Nmap -sn) ==="
        nmap -sn "$TARGET" 2>/dev/null
        echo ""
    } | tee -a "$REPORT_FILE"

    echo -e "${C_CYAN}[5/5] Port & Service Fingerprint (Common Ports)...${C_RESET}"
    {
        echo "=== PORT & SERVICE SCAN (Top 100) ==="
        nmap -sV --top-ports 100 "$TARGET" 2>/dev/null
        echo ""
    } | tee -a "$REPORT_FILE"
else
    echo -e "${C_YELLOW}[!] Nmap not installed. Skipping deep scan.${C_RESET}"
fi

echo -e "${C_GREEN}[✔] Recon Complete! Report saved to: ${REPORT_FILE}${C_RESET}"
