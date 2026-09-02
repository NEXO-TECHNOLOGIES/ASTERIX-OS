#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Native C Utilities Build Script
# Compiles all C tools with GCC or Clang and installs to /usr/local/bin
# =====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "\033[36m\033[1m[*] Compiling ASTERIX Native C Systems Utilities...\033[0m"

mkdir -p bin

COMPILER="gcc"
if ! command -v gcc >/dev/null 2>&1; then
    if command -v clang >/dev/null 2>&1; then
        COMPILER="clang"
    else
        echo -e "\033[31m[!] Neither gcc nor clang found. Install build-essential.\033[0m"
        exit 1
    fi
fi

$COMPILER -O3 -Wall -Wextra -D_GNU_SOURCE src/asterix-sysinfo.c -o bin/asterix-sysinfo
$COMPILER -O3 -Wall -Wextra -D_GNU_SOURCE src/asterix-memview.c -o bin/asterix-memview
$COMPILER -O3 -Wall -Wextra -D_GNU_SOURCE src/asterix-netprobe.c -o bin/asterix-netprobe
$COMPILER -O3 -Wall -Wextra -D_GNU_SOURCE src/asterix-hasher.c -o bin/asterix-hasher
$COMPILER -O3 -Wall -Wextra -D_GNU_SOURCE src/asterix-shredder.c -o bin/asterix-shredder

echo -e "\033[32m[✔] Successfully compiled all C binaries in ${SCRIPT_DIR}/bin/\033[0m"
ls -lh bin/

if [ "$EUID" -eq 0 ] || [ -w "/usr/local/bin" ]; then
    cp -f bin/* /usr/local/bin/
    chmod 755 /usr/local/bin/asterix-*
    echo -e "\033[32m[✔] Installed to /usr/local/bin/ globally!\033[0m"
fi
