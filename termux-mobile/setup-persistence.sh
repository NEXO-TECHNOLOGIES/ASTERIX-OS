#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Resilient Persistent Storage Subsystem v3.2
# Creates zero-crash directory hierarchy on Android internal storage
# and bridges to Debian Rootless PRoot.
# =====================================================================

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}[*] Setting up ASTERIX Resilient Persistence Architecture...${NC}"

# Request Android storage permission safely (does not abort if denied)
termux-setup-storage 2>/dev/null || true

LOCAL_VAULT="$HOME/asterix_persistent"
LEGACY_VAULT="$HOME/.asterix_storage"
SDCARD_VAULT="/sdcard/ASTERIX_PERSISTENCE"

# Create all standard persistent mission folders
FOLDERS=(
    "projects"
    "scans"
    "loot"
    "captures"
    "reports"
    "notes"
    "scripts"
    "payloads"
    "wordlists"
    "workspace"
)

for v in "$LOCAL_VAULT" "$LEGACY_VAULT"; do
    for f in "${FOLDERS[@]}"; do
        mkdir -p "$v/$f" 2>/dev/null || true
        [ ! -f "$v/$f/.keep" ] && printf "# ASTERIX OS Persistent Store: %s\n" "$f" > "$v/$f/.keep" 2>/dev/null || true
    done
    chmod -R 755 "$v" 2>/dev/null || true
done

# Gracefully link external Android SDCard storage if writable
if [ -d "/sdcard" ] && [ -w "/sdcard" ]; then
    mkdir -p "$SDCARD_VAULT" 2>/dev/null || true
    ln -sf "$SDCARD_VAULT" "$LOCAL_VAULT/sdcard_bridge" 2>/dev/null || true
    ln -sf "$SDCARD_VAULT" "$LEGACY_VAULT/sdcard_link" 2>/dev/null || true
    echo -e "${GREEN}[[OK]] Linked Android external storage: ${SDCARD_VAULT}${NC}"
else
    echo -e "${CYAN}[i] Using resilient Termux private storage (100% stable, zero permissions needed).${NC}"
fi

# Create workspace readme
cat << 'EOF' > "$LOCAL_VAULT/README.md"
# ASTERIX OS Persistent Storage Vault
All data placed inside this directory survives container reboots and package upgrades.
• `projects/`  - User codebases, repositories, and tactical tools
• `scans/`     - Nmap, Nikto, masscan, and network recon logs
• `loot/`      - Hashes, retrieved credentials, and extracted data
• `captures/`  - PCAP packet captures and wireless traffic dumps
• `reports/`   - Security assessment and audit documentation
• `notes/`     - Target tracking and engagement notes
• `scripts/`   - Custom attack and automation scripts
• `payloads/`  - Compiled binaries, shellcodes, and payloads
• `wordlists/` - Dictionaries and credential lists
• `workspace/` - Ephemeral and scratch workspace
EOF

echo -e "${GREEN}${BOLD}[[OK]] ASTERIX Persistence is ready and hardened at: ${YELLOW}${LOCAL_VAULT}${NC}"
