# PowerShell installer for local Ollama + ASTERIX AI
# Usage: powershell -ExecutionPolicy Bypass -File .\setup_local_ai.ps1

$ErrorActionPreference = "Stop"

Write-Host "[ASTERIX] Checking for Ollama..."
$ollama = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollama) {
    Write-Host "[ASTERIX] Ollama is not installed. Please install it from: https://ollama.com/download/windows"
    Write-Host "[ASTERIX] Then rerun this script."
    exit 1
}

Write-Host "[ASTERIX] Starting Ollama server..."
Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
Start-Sleep -Seconds 3

Write-Host "[ASTERIX] Pulling qwen2:0.5b model..."
& ollama pull qwen2:0.5b

Write-Host "[ASTERIX] Done. You can now run: python .\ax_ai.py"
