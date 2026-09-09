$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "[ASTERIX] Starting Ollama server..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
    Start-Sleep -Seconds 3
}

Write-Host "[ASTERIX] Launching ASTERIX AI..."
python .\ax_ai.py --security
