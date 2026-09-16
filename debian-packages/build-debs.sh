#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS — Debian Metapackage Build & Repository Pipeline
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUT_DIR="${1:-$REPO_ROOT/packages/debs}"
REPO_DIR="${2:-$REPO_ROOT/apt-repo}"
VERSION="${3:-2.1.0}"

echo "=== ASTERIX OS Debian Packaging Pipeline ==="
echo "[*] Output Directory: $OUT_DIR"
echo "[*] APT Repo Root:   $REPO_DIR"
echo "[*] Target Version:  $VERSION"

mkdir -p "$OUT_DIR" "$REPO_DIR"

if command -v python3 >/dev/null 2>&1; then
    python3 "$REPO_ROOT/scripts-hub/ax-deb-builder.py" build-all -o "$OUT_DIR" -v "$VERSION"
    python3 "$REPO_ROOT/scripts-hub/ax-apt-repo.py" build -s "$OUT_DIR" -o "$REPO_DIR"
else
    echo "[!] Error: python3 is required to build Debian packages."
    exit 1
fi

echo "=== Packaging & APT Indexing Complete ==="
