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

# Keep compiler warnings visible but tolerate the project's mixed source style.
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-sysinfo.c -o bin/asterix-sysinfo
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-memview.c -o bin/asterix-memview
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-netprobe.c -o bin/asterix-netprobe
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-hasher.c -o bin/asterix-hasher
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-shredder.c -o bin/asterix-shredder
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-rootkit-detect.c -o bin/asterix-rootkit-detect
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-syscall-mon.c -o bin/asterix-syscall-mon
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-env-dump.c -o bin/asterix-env-dump
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-code-repair.c -o bin/asterix-code-repair
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-crypto-core.c -o bin/asterix-crypto-core
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-packet-engine.c -o bin/asterix-packet-engine
$COMPILER -O2 -Wall -Wextra -D_GNU_SOURCE src/asterix-hardware-bridge.c -o bin/asterix-hardware-bridge

echo -e "\033[32m[OK] Successfully compiled all C binaries in ${SCRIPT_DIR}/bin/\033[0m"
ls -lh bin/

if [ "$EUID" -eq 0 ] || [ -w "/usr/local/bin" ]; then
    cp -f bin/* /usr/local/bin/
    chmod 755 /usr/local/bin/asterix-*
    echo -e "\033[32m[OK] Installed to /usr/local/bin/ globally!\033[0m"
fi
