#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS - Termux Session Initializer
# Starts the native Rust boot animation and binds persistent storage
# =====================================================================

PERSIST_DIR="$HOME/asterix_persistent"
mkdir -p "$PERSIST_DIR"

if [ -x "$PREFIX/bin/asterix-loader" ]; then
    "$PREFIX/bin/asterix-loader"
fi

# Enter PRoot Debian container with persistent storage bound
exec proot-distro login --bind "$PERSIST_DIR":/asterix_persistent debian
