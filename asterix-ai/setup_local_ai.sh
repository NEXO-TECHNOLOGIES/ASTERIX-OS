#!/usr/bin/env bash
# Termux/Android setup for local Ollama + ASTERIX AI

set -e

echo "[ASTERIX] Checking Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
    echo "[ASTERIX] Ollama is not installed."
    echo "[ASTERIX] Install it first, then rerun this script."
    echo "[ASTERIX] Example: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

echo "[ASTERIX] Starting Ollama server in background..."
ollama serve >/tmp/asterix-ollama.log 2>&1 &

sleep 3

echo "[ASTERIX] Pulling qwen2:0.5b model..."
ollama pull qwen2:0.5b

echo "[ASTERIX] Setup complete. Run: python ax_ai.py"
