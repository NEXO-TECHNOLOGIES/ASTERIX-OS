#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Master Web Operations Portal Launcher
# Hosts the interactive local dashboard on port 7777
# =====================================================================

PORT=7777
PORTAL_DIR=""

if [ -d "/etc/asterix/web-dashboard" ]; then
    PORTAL_DIR="/etc/asterix/web-dashboard"
elif [ -d "web-dashboard" ]; then
    PORTAL_DIR="web-dashboard"
elif [ -d "$(dirname "$0")/../web-dashboard" ]; then
    PORTAL_DIR="$(dirname "$0")/../web-dashboard"
fi

if [ -z "$PORTAL_DIR" ] || [ ! -d "$PORTAL_DIR" ]; then
    echo -e "\033[31m[!] Error: web-dashboard directory not found.\033[0m"
    exit 1
fi

echo -e "\033[36m\033[1m"
cat << 'EOF'
    ___   _____ ______ ______ ____     ____  ____  ____  ______ ___    __ 
   /   | / ___//_  __// ____// __ \   / __ \/ __ \/ __ \/_  __//   |  / / 
  / /| | \__ \  / /  / __/  / /_/ /  / /_/ / / / / /_/ / / /  / /| | / /  
 / ___ |___/ / / /  / /___ / _, _/  / ____/ /_/ / _, _/ / /  / ___ |/ /___
/_/  |_/____/ /_/  /_____//_/ |_|  /_/    \____/_/ |_| /_/  /_/  |_/_____/
        MASTER WEB PORTAL & MEDIA OPERATIONS MATRIX
EOF
echo -e "\033[0m"

echo -e "\033[32m[✔] Starting ASTERIX OS Web Portal...\033[0m"
echo -e "\033[33m[*] Local URL:    \033[1mhttp://localhost:${PORT}\033[0m"
echo -e "\033[33m[*] Web Directory: ${PORTAL_DIR}\033[0m"
echo -e "\033[35m[*] Features:      Wallpaper Gallery, 12 Subsystems Catalog, Discord Bridge\033[0m"
echo -e "\033[0m"

# Open browser if DISPLAY is present
if [ -n "$DISPLAY" ]; then
    (sleep 1 && (xdg-open "http://localhost:${PORT}" || sensible-browser "http://localhost:${PORT}" || firefox "http://localhost:${PORT}") 2>/dev/null) &
fi

cd "$PORTAL_DIR"

if command -v python3 >/dev/null 2>&1; then
    python3 -m http.server "$PORT" --bind 0.0.0.0
elif command -v node >/dev/null 2>&1 && command -v npx >/dev/null 2>&1; then
    npx serve -l "$PORT" .
else
    echo -e "\033[31m[!] Neither Python3 nor Node.js detected. Please install python3.\033[0m"
fi
