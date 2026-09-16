#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WRAPPER="${SCRIPT_DIR}/web-structure.sh"

if [ ! -f "$WRAPPER" ]; then
    echo "FAIL: web-structure.sh is missing"
    exit 1
fi

chmod +x "$WRAPPER" 2>/dev/null || true

# Test help output
HELP_OUT="$(bash "$WRAPPER" --help 2>&1 || true)"
if ! echo "$HELP_OUT" | grep -qi "web code structure"; then
    echo "FAIL: web-structure.sh --help did not return expected banner/usage"
    exit 1
fi

echo "PASS: web-structure.sh CLI wrapper operational"
