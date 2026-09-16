#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS — Termux Web Code Structure & Deep Source Extractor
# Wrapper for ax-web-structure.py
# Usage:
#   web-structure <url> [--tree|--source|--endpoints|--scripts|--tech|--dump <dir>|--json]
#   curl-tree <url>
#   webdump <url> <dir>
# =====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASTERIX_ROOT="$(dirname "$SCRIPT_DIR")"
find_python() {
    for cand in python3 python py \
        "/data/data/com.termux/files/usr/bin/python3" \
        "/usr/bin/python3" \
        "/usr/local/bin/python3" \
        "$HOME/.local/bin/python3.14.exe" \
        "$HOME/AppData/Local/Programs/Python/Python312/python.exe"; do
        if command -v "$cand" >/dev/null 2>&1; then
            # Verify it runs and is not the WindowsApps alias
            if "$cand" -c "import sys; print(sys.version_info[0])" 2>/dev/null | grep -q "3"; then
                echo "$cand"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_BIN="$(find_python || true)"
ENGINE="${ASTERIX_ROOT}/scripts-hub/ax-web-structure.py"

if [ ! -f "$ENGINE" ]; then
    if [ -f "$HOME/ASTERIX-OS/scripts-hub/ax-web-structure.py" ]; then
        ENGINE="$HOME/ASTERIX-OS/scripts-hub/ax-web-structure.py"
    elif [ -f "/etc/asterix/scripts-hub/ax-web-structure.py" ]; then
        ENGINE="/etc/asterix/scripts-hub/ax-web-structure.py"
    else
        echo "Error: ax-web-structure.py not found in ASTERIX OS."
        exit 1
    fi
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3 is required to run web-structure."
    exit 1
fi

exec "$PYTHON_BIN" "$ENGINE" "$@"
