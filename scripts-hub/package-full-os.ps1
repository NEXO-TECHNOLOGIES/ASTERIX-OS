<#
.SYNOPSIS
    ASTERIX OS - Full System Archive & Cloud Packaging Tool
.DESCRIPTION
    Creates a complete, uncompressed or ZIP archive of the entire 189+ MB ASTERIX OS
    source code, wallpapers, media assets, compilers, and toolchains for direct
    upload to Google Drive, GitHub Releases, or GitLab.
#>

[CmdletBinding()]
param(
    [string]$OutputDir = "$HOME\Desktop",
    [string]$ArchiveName = "ASTERIX-OS-FULL-PACKAGE.zip"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$C_CYAN    = "$([char]27)[38;5;51m"
$C_GREEN   = "$([char]27)[38;5;46m"
$C_YELLOW  = "$([char]27)[38;5;220m"
$C_WHITE   = "$([char]27)[38;5;231m"
$C_RESET   = "$([char]27)[0m"
$C_BOLD    = "$([char]27)[1m"

Write-Host "`n$C_CYAN$C_BOLD[ ASTERIX OS // FULL SYSTEM PACKAGING & CLOUD UPLOAD UTILITY ]$C_RESET`n"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$AsterixRoot = Split-Path -Parent $ScriptDir
$DestinationPath = Join-Path $OutputDir $ArchiveName

Write-Host "  • Source Directory:      $C_WHITE$AsterixRoot$C_RESET"
Write-Host "  • Target Archive:       $C_YELLOW$DestinationPath$C_RESET"

# Calculate Total Uncompressed Size
$fileCount = (Get-ChildItem -Path $AsterixRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object).Count
$totalBytes = (Get-ChildItem -Path $AsterixRoot -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
$totalMB = [math]::Round($totalBytes / 1MB, 2)

Write-Host "  • Total System Payload:  $C_GREEN$totalMB MB ($fileCount files)$C_RESET`n"
Write-Host "  [*] Packaging entire OS workspace into ZIP... (please wait a few moments)" -ForegroundColor Cyan

if (Test-Path $DestinationPath) {
    Remove-Item -Force $DestinationPath
}

# Compress into ZIP
Compress-Archive -Path "$AsterixRoot\*" -DestinationPath $DestinationPath -CompressionLevel Optimal

$zipBytes = (Get-Item $DestinationPath).Length
$zipMB = [math]::Round($zipBytes / 1MB, 2)
$sha256 = (Get-FileHash -Path $DestinationPath -Algorithm SHA256).Hash

Write-Host "`n  $C_GREEN$C_BOLD[✔] FULL ASTERIX OS PACKAGE READY FOR CLOUD UPLOAD!$C_RESET"
Write-Host "  • Package Path:   $C_WHITE$DestinationPath$C_RESET"
Write-Host "  • Package Size:   $C_GREEN$zipMB MB$C_RESET (Compressed from $totalMB MB)"
Write-Host "  • SHA-256 Hash:   $C_CYAN$sha256$C_RESET`n"

Write-Host "$C_YELLOW$C_BOLD--- UPLOAD OPTIONS ---$C_RESET"
Write-Host "1. $C_WHITE$C_BOLD Google Drive (Recommended for easy sharing):$C_RESET"
Write-Host "   - Open drive.google.com and upload '$DestinationPath' (or upload the uncompressed '$AsterixRoot' folder)."
Write-Host "   - Right-click the file/folder -> Share -> Change to 'Anyone with the link can view'."
Write-Host "   - Copy the link and paste it into README.md under the Download section."
Write-Host ""
Write-Host "2. $C_WHITE$C_BOLD GitHub Releases (Official distribution up to 2 GB per file):$C_RESET"
Write-Host "   - Go to your repository on GitHub -> Releases -> 'Draft a new release'."
Write-Host "   - Drag and drop '$DestinationPath' into the 'Attach binaries' section."
Write-Host "   - Publish the release! Everyone can download the full package directly from GitHub."
Write-Host ""
