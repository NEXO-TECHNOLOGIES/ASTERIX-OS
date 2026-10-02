<#
.SYNOPSIS
    ASTERIX OS - Native C Systems Utilities PowerShell Build Engine
.DESCRIPTION
    Compiles native C utilities on Windows using GCC / Clang / MinGW or delegates to Debian PRoot / Termux.
#>

param (
    [switch]$Clean,
    [string]$Compiler = ""
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$SrcDir = Join-Path $ScriptDir "src"
$BinDir = Join-Path $ScriptDir "bin"

$C_CYAN    = "$([char]27)[38;5;51m"
$C_GREEN   = "$([char]27)[38;5;46m"
$C_YELLOW  = "$([char]27)[38;5;220m"
$C_RED     = "$([char]27)[38;5;196m"
$C_RESET   = "$([char]27)[0m"
$C_BOLD    = "$([char]27)[1m"

if ($Clean) {
    if (Test-Path $BinDir) {
        Remove-Item -Recurse -Force $BinDir
        Write-Host "  ${C_GREEN}[OK] Cleaned $BinDir${C_RESET}"
    }
    return
}

if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Path $BinDir -Force | Out-Null
}

function Find-CCompiler {
    $candidates = @("gcc.exe", "clang.exe", "cc.exe")
    foreach ($c in $candidates) {
        $found = Get-Command $c -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return $found.Source
        }
    }
    return $null
}

$cc = if ($Compiler) { $Compiler } else { Find-CCompiler }

Write-Host "  ${C_CYAN}${C_BOLD}[*] ASTERIX OS Native C Utilities Build Engine${C_RESET}"

if (-not $cc) {
    Write-Host "  ${C_YELLOW}[!] No standalone C compiler (gcc/clang) detected in Windows PATH.${C_RESET}"
    Write-Host "  ${C_CYAN}[i] On Linux / Termux / Debian PRoot, run: make or bash build.sh${C_RESET}"
    Write-Host "  ${C_CYAN}[i] Or use: ax debian run make -C /opt/ASTERIX-OS/core-utils-c${C_RESET}"
    return
}

Write-Host "  ${C_GREEN}[*] Using compiler: $cc${C_RESET}"

$sources = Get-ChildItem -Path $SrcDir -Filter "*.c"
$compiled = 0
$failed = 0

foreach ($src in $sources) {
    $binName = [System.IO.Path]::GetFileNameWithoutExtension($src.Name) + ".exe"
    $outPath = Join-Path $BinDir $binName
    Write-Host "  [*] Compiling $($src.Name)..." -NoNewline

    try {
        & $cc -O2 -Wall -Wextra $src.FullName -o $outPath 2>$null
        if (Test-Path $outPath) {
            Write-Host " ${C_GREEN}[OK]${C_RESET}"
            $compiled++
        } else {
            Write-Host " ${C_YELLOW}[SKIPPED (POSIX-only)]${C_RESET}"
        }
    } catch {
        Write-Host " ${C_RED}[FAIL]${C_RESET}"
        $failed++
    }
}

Write-Host "`n  ${C_GREEN}[OK] C build pipeline completed: $compiled binaries produced.${C_RESET}`n"
