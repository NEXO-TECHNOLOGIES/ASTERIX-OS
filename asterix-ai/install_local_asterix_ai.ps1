$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

Write-Host "[ASTERIX] Checking Python..."
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ASTERIX] Python not found. Installing Python 3.12..."
    winget install --id Python.Python.3.12 --exact --accept-source-agreements --accept-package-agreements
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        throw "Python still not available after install. Please restart PowerShell and rerun this script."
    }
}

Write-Host "[ASTERIX] Checking Ollama..."
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCmd) {
    Write-Host "[ASTERIX] Ollama not found. Installing Ollama..."
    winget install --id Ollama.Ollama --exact --accept-source-agreements --accept-package-agreements
    $ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollamaCmd) {
        throw "Ollama still not available after install. Please restart PowerShell and rerun this script."
    }
}

Write-Host "[ASTERIX] Starting Ollama server..."
$ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
}

Write-Host "[ASTERIX] Waiting for Ollama to become ready..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 3 | Out-String
        if ($response -match "models") {
            $ready = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    throw "Ollama server did not become ready in time."
}

Write-Host "[ASTERIX] Pulling local model qwen2.5:3b-instruct..."
& ollama pull qwen2.5:3b-instruct

Write-Host "[ASTERIX] Creating local memory files if needed..."
if (-not (Test-Path "memory.log")) {
    New-Item -ItemType File -Path "memory.log" -Force | Out-Null
}

Write-Host "[ASTERIX] Installation complete."
Write-Host "[ASTERIX] Run: python .\ax_ai.py --security"
