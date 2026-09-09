#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS — Termux Stable ARM64 Bundle Generator v1.0
# Author: NEXO TECHNOLOGIES GROUP
#
# Packages the complete ASTERIX OS Termux deployment (~312 MB stable)
# into a distributable .tar.gz archive suitable for:
#   - Direct GitHub/GitLab Release upload
#   - Manual sideloading on any Android device with Termux
#   - F-Droid/IzzyOnDroid distribution
#
# Bundle Contents (~312 MB):
#   ├── asterix-termux-init.sh          (Main ASTERIX Termux bootstrap)
#   ├── install-termux.sh               (Rootless Debian PRoot installer)
#   ├── bin/ax                          (ASTERIX master command dispatcher)
#   ├── asterix-ai/                     (Full AI engine + self-evolution)
#   ├── scripts-hub/                    (All Python tools & scripts)
#   ├── os-computing/                   (Host OS bridge)
#   ├── docs/                           (Documentation & manuals)
#   └── TERMUX_INSTALL_GUIDE.md         (Step-by-step install guide)
# =====================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
     TERMUX ARM64 BUNDLE PACKAGER v1.0 (312 MB Stable)
EOF
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASTERIX_ROOT="$(dirname "$SCRIPT_DIR")"
BUNDLE_NAME="asterix-termux-v2.0.0-arm64-stable.tar.gz"
OUT_DIR="${ASTERIX_ROOT}/releases"
BUNDLE_PATH="${OUT_DIR}/${BUNDLE_NAME}"
STAGING_DIR="${ASTERIX_ROOT}/.termux-staging"

mkdir -p "$OUT_DIR"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR/asterix-termux"

echo -e "${YELLOW}[*] Step 1: Staging ASTERIX Termux deployment files...${NC}"

# Core files
cp "${ASTERIX_ROOT}/termux-mobile/asterix-termux-init.sh" "$STAGING_DIR/asterix-termux/"
cp "${ASTERIX_ROOT}/termux-mobile/install-termux.sh"      "$STAGING_DIR/asterix-termux/"

# Master command dispatcher
mkdir -p "$STAGING_DIR/asterix-termux/bin"
cp "${ASTERIX_ROOT}/bin/ax" "$STAGING_DIR/asterix-termux/bin/"
chmod +x "$STAGING_DIR/asterix-termux/bin/ax"

# AI Engine (entire directory, excluding __pycache__ and .pyc)
mkdir -p "$STAGING_DIR/asterix-termux/asterix-ai"
rsync -av --exclude="__pycache__" --exclude="*.pyc" \
  "${ASTERIX_ROOT}/asterix-ai/" \
  "$STAGING_DIR/asterix-termux/asterix-ai/" 2>/dev/null || \
  cp -r "${ASTERIX_ROOT}/asterix-ai/." "$STAGING_DIR/asterix-termux/asterix-ai/"

# Scripts hub (Python tools)
mkdir -p "$STAGING_DIR/asterix-termux/scripts-hub"
for pyfile in ax-arsenal.py ax-boot-tool.py ax-cam-hunter.py ax-undercover.py ax-privacy.py ax-doctor.py ax-shield.py ax-scratch.py ax-bounty.py ax-cartographer.py ax-intel-defense.py ax-cloud-defense.py; do
    [ -f "${ASTERIX_ROOT}/scripts-hub/${pyfile}" ] && \
        cp "${ASTERIX_ROOT}/scripts-hub/${pyfile}" "$STAGING_DIR/asterix-termux/scripts-hub/"
done

# OS Computing bridge
mkdir -p "$STAGING_DIR/asterix-termux/os-computing"
for f in os_bridge.py os_bridge.sh README.md; do
    [ -f "${ASTERIX_ROOT}/os-computing/${f}" ] && \
        cp "${ASTERIX_ROOT}/os-computing/${f}" "$STAGING_DIR/asterix-termux/os-computing/"
done

# Core documentation
mkdir -p "$STAGING_DIR/asterix-termux/docs"
for doc in MASTER_TOOLCHAIN_MANUAL.md TOOLS_REGISTRY.md AX_COMMAND_GUIDE.md; do
    [ -f "${ASTERIX_ROOT}/docs/${doc}" ] && \
        cp "${ASTERIX_ROOT}/docs/${doc}" "$STAGING_DIR/asterix-termux/docs/"
done
[ -f "${ASTERIX_ROOT}/README.md" ] && cp "${ASTERIX_ROOT}/README.md" "$STAGING_DIR/asterix-termux/"

# Auto-generated Termux install guide
cat > "$STAGING_DIR/asterix-termux/TERMUX_INSTALL_GUIDE.md" << 'GUIDE_EOF'
# 📱 ASTERIX OS v2.0 'Phantom' — Termux ARM64 Install Guide

## Requirements
- Android 7.0 or later
- Termux (latest from F-Droid — NOT from Google Play Store)
- ~1.5 GB free storage (for Debian PRoot + tools)

## Step 1: Install Termux
Download from **F-Droid** (recommended):
> https://f-droid.org/packages/com.termux/

## Step 2: Transfer & Extract this Bundle
```bash
# Copy the bundle to your device, then inside Termux:
tar -xzf asterix-termux-v2.0.0-arm64-stable.tar.gz
cd asterix-termux/
```

## Step 3: Run the Installer
```bash
bash install-termux.sh
```
This automatically:
- Installs Debian PRoot rootless Linux environment
- Compiles the native Rust boot engine on your device
- Deploys the full ASTERIX OS inside Termux
- Sets up the `ax` master command dispatcher

## Step 4: Initialize ASTERIX
```bash
bash asterix-termux-init.sh
```

## Quick Commands After Install
```bash
ax help                      # Show all available commands
ax ai chat                   # Start conversational AI session
ax cam-hunter hotel          # Hotel privacy counter-surveillance sweep
ax self-evolve evolve        # Update AI knowledge from threat feeds
ax arsenal list              # Browse 180+ security tools
ax boot-tool dualboot 4      # Generate dual-boot USB files
```

## Default Credentials
- **User:** `asterix`
- **Password:** `asterix`

## Bundle Size
~312 MB compressed (core system)
~1.5 GB expanded (with Debian PRoot)
GUIDE_EOF

echo -e "${GREEN}  [✔] Staging complete: $(find "$STAGING_DIR" -type f | wc -l) files staged${NC}"

echo -e "${YELLOW}[*] Step 2: Computing staging directory size...${NC}"
STAGING_SIZE_BYTES=$(find "$STAGING_DIR" -type f -exec wc -c {} + 2>/dev/null | tail -1 | awk '{print $1}')
STAGING_SIZE_MB=$(echo "$STAGING_SIZE_BYTES" | awk '{printf "%.1f", $1/1048576}')
echo -e "${GREEN}  [✔] Pre-compression payload: ${STAGING_SIZE_MB} MB${NC}"

echo -e "${YELLOW}[*] Step 3: Creating compressed .tar.gz bundle...${NC}"
cd "$STAGING_DIR"
tar -czf "$BUNDLE_PATH" asterix-termux/ 2>/dev/null

BUNDLE_BYTES=$(wc -c < "$BUNDLE_PATH")
BUNDLE_MB=$(echo "$BUNDLE_BYTES" | awk '{printf "%.1f", $1/1048576}')

echo -e "${GREEN}  [✔] Bundle created: ${BUNDLE_PATH}${NC}"
echo -e "${GREEN}  [✔] Compressed size: ${BUNDLE_MB} MB${NC}"

echo -e "${YELLOW}[*] Step 4: Computing SHA-256 & SHA-512 checksums...${NC}"
if command -v sha256sum > /dev/null 2>&1; then
    SHA256=$(sha256sum "$BUNDLE_PATH" | awk '{print $1}')
    SHA512=$(sha512sum "$BUNDLE_PATH" 2>/dev/null | awk '{print $1}' || echo "N/A")
elif command -v shasum > /dev/null 2>&1; then
    SHA256=$(shasum -a 256 "$BUNDLE_PATH" | awk '{print $1}')
    SHA512=$(shasum -a 512 "$BUNDLE_PATH" | awk '{print $1}')
else
    SHA256="(sha256sum not available on this system)"
    SHA512="N/A"
fi

echo -e "${GREEN}  SHA-256: ${SHA256}${NC}"

# Append to releases/SHA256SUMS
echo "${SHA256}  ${BUNDLE_NAME}" >> "${OUT_DIR}/SHA256SUMS"
[ "$SHA512" != "N/A" ] && echo "${SHA512}  ${BUNDLE_NAME}" >> "${OUT_DIR}/SHA512SUMS"

echo -e "${YELLOW}[*] Step 5: Cleaning up staging directory...${NC}"
rm -rf "$STAGING_DIR"

echo ""
echo -e "${CYAN}${BOLD}══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✔ ASTERIX OS TERMUX ARM64 BUNDLE READY FOR DISTRIBUTION!${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════════════${NC}"
echo -e "  • Bundle:    ${YELLOW}${BUNDLE_PATH}${NC}"
echo -e "  • Size:      ${YELLOW}${BUNDLE_MB} MB${NC}"
echo -e "  • SHA-256:   ${YELLOW}${SHA256:0:48}...${NC}"
echo -e ""
echo -e "  ${BOLD}Upload Options:${NC}"
echo -e "    GitHub Release:  gh release upload v2.0.0 ${BUNDLE_PATH}"
echo -e "    GitLab Upload:   Use GitLab Releases UI or API"
echo -e ""
echo -e "  ${BOLD}Termux Install Command for End Users:${NC}"
echo -e "    ${CYAN}curl -L https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases/download/v2.0.0/${BUNDLE_NAME} | tar -xzf -${NC}"
echo -e "    ${CYAN}cd asterix-termux && bash install-termux.sh${NC}"
echo ""
