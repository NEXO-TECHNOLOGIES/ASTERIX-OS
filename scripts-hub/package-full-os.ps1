<#
.SYNOPSIS
    ASTERIX OS - Full System Archive & Cloud Packaging Tool
.DESCRIPTION
    Creates a complete distribution ZIP archive of ASTERIX OS
    source code, compilers, AI engines, and toolchains for direct
    upload to Google Drive, GitHub Releases, or GitLab.
    Supports -ExcludeMedia to produce a lightweight, code-only distribution.
#>

[CmdletBinding()]
param(
    [string]$OutputDir = "$HOME\Desktop",
    [string]$ArchiveName = "ASTERIX-OS-FULL-PACKAGE.zip",
    [switch]$ExcludeMedia,
    [switch]$NoMedia
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$C_CYAN    = "$([char]27)[38;5;51m"
$C_GREEN   = "$([char]27)[38;5;46m"
$C_YELLOW  = "$([char]27)[38;5;220m"
$C_WHITE   = "$([char]27)[38;5;231m"
$C_RESET   = "$([char]27)[0m"
$C_BOLD    = "$([char]27)[1m"

$SkipMedia = $ExcludeMedia -or $NoMedia

Write-Host ""
Write-Host "$C_CYAN$C_BOLD[ ASTERIX OS // FULL SYSTEM PACKAGING & CLOUD UPLOAD UTILITY ]$C_RESET"
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$AsterixRoot = Split-Path -Parent $ScriptDir
$DestinationPath = Join-Path $OutputDir $ArchiveName

Write-Host "  * Source Directory:      $C_WHITE$AsterixRoot$C_RESET"
Write-Host "  * Target Archive:        $C_YELLOW$DestinationPath$C_RESET"
if ($SkipMedia) {
    Write-Host "  * Media Filter:          $C_GREEN[EXCLUDED] (Skipping wallpapers, animations & media)$C_RESET"
} else {
    Write-Host "  * Media Filter:          $C_YELLOW[INCLUDED] (Full media payload included)$C_RESET"
}

# Ignored items
$IgnoreDirs = @(".git", ".github", "node_modules", "venv", ".venv", "__pycache__", "target", "dist", "build", ".asterix_vault")
$MediaExts  = @(".jpg", ".jpeg", ".png", ".gif", ".ico", ".mp4", ".webp", ".svg", ".bmp")

# Gather files
Write-Host "  [*] Scanning workspace files..." -ForegroundColor DarkGray
$allFiles = Get-ChildItem -Path $AsterixRoot -Recurse -File -ErrorAction SilentlyContinue | Where-Object {
    $rel = $_.FullName.Substring($AsterixRoot.Length).TrimStart("\/")
    $parts = $rel.Split([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    
    # Check ignored directories
    foreach ($p in $parts) {
        if ($IgnoreDirs -contains $p) {
            return $false
        }
    }

    # Check media exclusion
    if ($SkipMedia) {
        if ($parts[0] -eq "assets") { return $false }
        if ($parts -contains "frames") { return $false }
        if ($MediaExts -contains $_.Extension.ToLower()) { return $false }
    }
    
    return $true
}

$fileCount = $allFiles.Count
$totalBytes = ($allFiles | Measure-Object -Property Length -Sum).Sum
$totalMB = [math]::Round($totalBytes / 1MB, 2)

Write-Host "  * Total System Payload:  $C_GREEN$totalMB MB ($fileCount files)$C_RESET"
Write-Host ""
Write-Host "  [*] Packaging workspace into ZIP archive... (please wait)" -ForegroundColor Cyan

if (Test-Path $DestinationPath) {
    Remove-Item -Force $DestinationPath
}

# Fast .NET ZIP Compression
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zipStream = [System.IO.File]::Create($DestinationPath)
$archive = New-Object System.IO.Compression.ZipArchive($zipStream, [System.IO.Compression.ZipArchiveMode]::Create)

try {
    foreach ($file in $allFiles) {
        $relPath = $file.FullName.Substring($AsterixRoot.Length).TrimStart("\/").Replace("\", "/")
        $entry = $archive.CreateEntry($relPath, [System.IO.Compression.CompressionLevel]::Optimal)
        $entryStream = $entry.Open()
        $fileStream = [System.IO.File]::OpenRead($file.FullName)
        $fileStream.CopyTo($entryStream)
        $fileStream.Close()
        $entryStream.Close()
    }
} finally {
    $archive.Dispose()
    $zipStream.Dispose()
}

$zipBytes = (Get-Item $DestinationPath).Length
$zipMB = [math]::Round($zipBytes / 1MB, 2)
$sha256 = (Get-FileHash -Path $DestinationPath -Algorithm SHA256).Hash

Write-Host ""
Write-Host "  $C_GREEN$C_BOLD[+] FULL ASTERIX OS PACKAGE READY FOR CLOUD UPLOAD!$C_RESET"
Write-Host "  * Package Path:   $C_WHITE$DestinationPath$C_RESET"
Write-Host "  * Package Size:   $C_GREEN$zipMB MB$C_RESET (Compressed from $totalMB MB)"
Write-Host "  * SHA-256 Hash:   $C_CYAN$sha256$C_RESET"
Write-Host ""

Write-Host "$C_YELLOW$C_BOLD--- UPLOAD OPTIONS ---$C_RESET"
Write-Host "1. $C_WHITE$C_BOLD Google Drive (Recommended for easy sharing):$C_RESET"
Write-Host "   - Open drive.google.com and upload '$DestinationPath'."
Write-Host "   - Right-click the file -> Share -> Change to 'Anyone with the link can view'."
Write-Host "   - Copy the link and paste it into README.md under the Download section."
Write-Host ""
Write-Host "2. $C_WHITE$C_BOLD GitHub Releases (Official distribution up to 2 GB per file):$C_RESET"
Write-Host "   - Go to your repository on GitHub -> Releases -> 'Draft a new release'."
Write-Host "   - Drag and drop '$DestinationPath' into the 'Attach binaries' section."
Write-Host "   - Publish the release! Everyone can download the package directly from GitHub."
Write-Host ""
