<#
.SYNOPSIS
    ASTERIX OS Master Build Engine for Windows (PowerShell)
    Compiles the Freestanding x86 Microkernel and All Native Rust Cyber Engines.
#>
[CmdletBinding()]
param(
    [switch]$SkipKernel,
    [switch]$SkipRust,
    [switch]$RunMicrokernel
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$C_CYAN    = "$([char]27)[38;5;51m"
$C_GREEN   = "$([char]27)[38;5;46m"
$C_YELLOW  = "$([char]27)[38;5;220m"
$C_RED     = "$([char]27)[38;5;196m"
$C_WHITE   = "$([char]27)[38;5;231m"
$C_RESET   = "$([char]27)[0m"
$C_BOLD    = "$([char]27)[1m"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BinDir = Join-Path $ScriptDir "bin"

Write-Host "${C_CYAN}${C_BOLD}"
Write-Host "    ___   _____ ______ ______ ____     ____  __  __"
Write-Host "   /   | / ___//_  __// ____// __ \   / __ \/ / / /"
Write-Host "  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / "
Write-Host " / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  "
Write-Host "/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   "
Write-Host "     MASTER BUILD ENGINE (WINDOWS & CROSS-PLATFORM)"
Write-Host "${C_RESET}"

# Ensure output bin directory exists
if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

# 1. Freestanding x86 Multiboot Microkernel
if (-not $SkipKernel) {
    Write-Host "${C_YELLOW}[1/2] Building Freestanding x86 Multiboot Microkernel...${C_RESET}"
    $kernelBuild = Join-Path $ScriptDir "kernel\build-kernel.ps1"
    if (Test-Path $kernelBuild) {
        $kernelArgs = @()
        if ($RunMicrokernel) { $kernelArgs += "-Run" }
        & powershell.exe -ExecutionPolicy Bypass -File $kernelBuild @kernelArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ${C_GREEN}[OK] Microkernel ELF compiled & verified.${C_RESET}"
        } else {
            Write-Host "  ${C_RED}[!] Microkernel build returned exit code $LASTEXITCODE.${C_RESET}"
        }
    } else {
        Write-Host "  ${C_RED}[!] kernel\build-kernel.ps1 not found.${C_RESET}"
    }
} else {
    Write-Host "  ${C_CYAN}[i] Skipping microkernel build (-SkipKernel specified).${C_RESET}"
}

# 2. Native Rust Cyber Engines
if (-not $SkipRust) {
    Write-Host "${C_YELLOW}[2/2] Compiling Native Rust Cyber & Systems Suite (core-utils-rust)...${C_RESET}"
    $rustDir = Join-Path $ScriptDir "core-utils-rust"
    if (Test-Path $rustDir) {
        Push-Location $rustDir
        try {
            # Use stable-x86_64-pc-windows-gnu if available to avoid missing MSVC link.exe
            cargo build --release
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ${C_GREEN}[OK] Rust release binaries built successfully.${C_RESET}"
                $builtExes = Get-ChildItem "target\release\*.exe"
                foreach ($exe in $builtExes) {
                    Copy-Item $exe.FullName $BinDir -Force
                    Write-Host "  ${C_GREEN}  + Installed: bin\$($exe.Name) ($([math]::Round($exe.Length / 1KB, 1)) KB)${C_RESET}"
                }
            } else {
                Write-Host "  ${C_RED}[!] Cargo build returned exit code $LASTEXITCODE.${C_RESET}"
            }
        } finally {
            Pop-Location
        }
    } else {
        Write-Host "  ${C_RED}[!] core-utils-rust directory not found.${C_RESET}"
    }
} else {
    Write-Host "  ${C_CYAN}[i] Skipping Rust tools build (-SkipRust specified).${C_RESET}"
}

Write-Host ""
Write-Host "${C_GREEN}${C_BOLD}=== ASTERIX OS BUILD COMPLETE ===${C_RESET}"
Write-Host "All binaries deployed to: ${BinDir}"
Write-Host "Run 'bin\ax.ps1' or 'bin\ax' to launch the suite."
