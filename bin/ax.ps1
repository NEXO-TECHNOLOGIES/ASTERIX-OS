<#
.SYNOPSIS
    ASTERIX OS Master Omni-Command System (Windows PowerShell Dispatcher: ax / asterix)
.DESCRIPTION
    Native Windows PowerShell entrypoint for ASTERIX OS commands and subsystems.
#>

param(
    [Parameter(Position = 0)]
    [string]$Command = "status",
    [switch]$fix,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

if ($fix) {
    if ($Command -and $Command -ne "status") {
        $RemainingArgs = @($Command) + $RemainingArgs
    }
    $Command = "-fix"
}

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$C_CYAN    = "$([char]27)[38;5;51m"
$C_GREEN   = "$([char]27)[38;5;46m"
$C_YELLOW  = "$([char]27)[38;5;220m"
$C_RED     = "$([char]27)[38;5;196m"
$C_MAGENTA = "$([char]27)[38;5;201m"
$C_WHITE   = "$([char]27)[38;5;231m"
$C_RESET   = "$([char]27)[0m"
$C_BOLD    = "$([char]27)[1m"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$AsterixRoot = Split-Path -Parent $ScriptDir

# Locate real Python interpreter (preferring Python 3.14 / local / uv over WindowsApp store alias)
function Get-RealPython {
    $candidates = @(
        "$HOME\.local\bin\python3.14.exe",
        "$HOME\AppData\Roaming\uv\python\cpython-3.14-windows-x86_64-none\python.exe",
        "python3.14",
        "py",
        "python3",
        "python"
    )
    foreach ($cand in $candidates) {
        $path = $null
        if (Test-Path $cand) {
            $path = $cand
        } else {
            $found = Get-Command $cand -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($found -and $found.Source -notmatch "WindowsApps") {
                $path = $found.Source
            }
        }
        if ($path) {
            # Test that it can execute
            try {
                $test = & $path --version 2>&1
                if ($test -match "Python 3") {
                    return $path
                }
            } catch {}
        }
    }
    return $null
}

$RealPython = Get-RealPython

switch ($Command.ToLower()) {
    { $_ -in @("os-computing", "os-collaborate", "host-sync", "os-bridge", "collab", "host-collab") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge $RemainingArgs
        } elseif (Test-Path $psBridge) {
            & $psBridge @RemainingArgs
        } else {
            Write-Host "  ${C_RED}[!] Error: Neither os_bridge.py nor os_bridge.ps1 found.${C_RESET}"
        }
    }

    { $_ -in @("ai", "asterix-ai", "ask-ai") } {
        $aiScript = Join-Path $AsterixRoot "asterix-ai\engine.py"
        if ($RealPython -and (Test-Path $aiScript)) {
            & $RealPython $aiScript $RemainingArgs
        } else {
            Write-Host "  ${C_YELLOW}[!] Python runtime not ready or engine.py not found.${C_RESET}"
        }
    }

    { $_ -in @("sysfetch", "fetch") } {
        $fetchScript = Join-Path $AsterixRoot "scripts-hub\ax-sysfetch.sh"
        $gitBash = "C:\Program Files\Git\bin\bash.exe"
        if (Test-Path $gitBash) {
            & $gitBash $fetchScript
        } else {
            Write-Host "  ${C_CYAN}[*] ASTERIX OS v2.0 - Windows Host Engine${C_RESET}"
            Get-CimInstance Win32_OperatingSystem | Format-List Caption, Version, OSArchitecture, TotalVisibleMemorySize
        }
    }

    { $_ -in @("status", "info") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge status
        } else {
            $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
            & $psBridge status
        }
    }

    { $_ -in @("probe", "detect") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge probe
        } else {
            $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
            & $psBridge probe
        }
    }

    { $_ -in @("collaborate", "bridge", "sync") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge collaborate
        } else {
            $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
            & $psBridge collaborate
        }
    }

    { $_ -in @("compute", "benchmark", "synergy") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge compute
        } else {
            $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
            & $psBridge compute
        }
    }

    { $_ -in @("features", "export") } {
        $pyBridge = Join-Path $AsterixRoot "os-computing\os_bridge.py"
        if ($RealPython -and (Test-Path $pyBridge)) {
            & $RealPython $pyBridge features
        } else {
            $psBridge = Join-Path $AsterixRoot "os-computing\os_bridge.ps1"
            & $psBridge features
        }
    }

    { $_ -in @("version", "-v", "--version") } {
        $versionFile = Join-Path $AsterixRoot "VERSION.toml"
        Write-Host "  ======================================================================" -ForegroundColor Cyan
        Write-Host "  [ ASTERIX OS v2.0 // MASTER VERSION SPECIFICATION // PHANTOM ]" -ForegroundColor White
        Write-Host "  ======================================================================" -ForegroundColor Cyan
        if (Test-Path $versionFile) {
            Get-Content $versionFile | ForEach-Object {
                if ($_ -match "^\[") {
                    Write-Host "  $_" -ForegroundColor Magenta
                } elseif ($_ -match "=") {
                    $parts = $_ -split "=", 2
                    Write-Host "    $($parts[0].Trim())" -ForegroundColor Cyan -NoNewline
                    Write-Host " = " -ForegroundColor White -NoNewline
                    Write-Host "$($parts[1].Trim())" -ForegroundColor Green
                } else {
                    Write-Host "  $_" -ForegroundColor DarkGray
                }
            }
        } else {
            Write-Host "  ASTERIX OS v2.0.0 (Phantom)" -ForegroundColor Green
        }
    }

    { $_ -in @("bench", "benchmarks", "speed") } {
        Write-Host "  ======================================================================" -ForegroundColor Cyan
        Write-Host "  [ ASTERIX OS v2.0 // BENCHMARKS vs TRADITIONAL LINUX TOOLS ]" -ForegroundColor White
        Write-Host "  ======================================================================" -ForegroundColor Cyan
        Write-Host "  * Net Sentinel vs Nmap (1000 ports):  " -ForegroundColor White -NoNewline
        Write-Host "3.74x FASTER (12.1s vs 45.2s) | 7.2x LESS RAM (11.8MB vs 85MB)" -ForegroundColor Green
        Write-Host "  * Bin Inspector vs readelf/strings:  " -ForegroundColor White -NoNewline
        Write-Host "6.72x FASTER (1.21s vs 8.14s) | Single zero-copy buffer" -ForegroundColor Green
        Write-Host "  * Log Hunter vs grep/awk (500MB log): " -ForegroundColor White -NoNewline
        Write-Host "3.79x FASTER (3.9s vs 14.8s)  | 16 parallel signatures" -ForegroundColor Green
        Write-Host "  * Crypto Core vs sha256sum/hashid:   " -ForegroundColor White -NoNewline
        Write-Host "182x FASTER hash identification (82k vs 450/sec)" -ForegroundColor Green
        Write-Host "  Detailed benchmarks documented in BENCHMARK_RESULTS.md" -ForegroundColor DarkGray
    }

    { $_ -in @("-fix", "fix", "code-fix", "heal") } {
        $healerScript = Join-Path $AsterixRoot "asterix-ai\code_healer.py"
        if ($RealPython -and (Test-Path $healerScript)) {
            & $RealPython $healerScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or code_healer.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("debug", "trace-bug", "crash-report") } {
        $debugScript = Join-Path $AsterixRoot "asterix-ai\runtime_debugger.py"
        if ($RealPython -and (Test-Path $debugScript)) {
            & $RealPython $debugScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or runtime_debugger.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("bounty", "bug-bounty", "recon-bounty") } {
        $bountyScript = Join-Path $AsterixRoot "scripts-hub\ax-bounty.py"
        if ($RealPython -and (Test-Path $bountyScript)) {
            & $RealPython $bountyScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-bounty.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("scratch", "playground") } {
        $scratchScript = Join-Path $AsterixRoot "scripts-hub\ax-scratch.py"
        if ($RealPython -and (Test-Path $scratchScript)) {
            & $RealPython $scratchScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-scratch.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("map", "cartographer", "arch", "topology") } {
        $cartographerScript = Join-Path $AsterixRoot "scripts-hub\ax-cartographer.py"
        if ($RealPython -and (Test-Path $cartographerScript)) {
            & $RealPython $cartographerScript "map" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cartographer.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("scaffold", "synth") } {
        $cartographerScript = Join-Path $AsterixRoot "scripts-hub\ax-cartographer.py"
        if ($RealPython -and (Test-Path $cartographerScript)) {
            & $RealPython $cartographerScript "scaffold" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cartographer.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("unblock", "port-kill", "kill-port") } {
        $doctorScript = Join-Path $AsterixRoot "scripts-hub\ax-doctor.py"
        if ($RealPython -and (Test-Path $doctorScript)) {
            & $RealPython $doctorScript "unblock" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-doctor.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("secrets", "secret-scan", "vault-scan") } {
        $doctorScript = Join-Path $AsterixRoot "scripts-hub\ax-doctor.py"
        if ($RealPython -and (Test-Path $doctorScript)) {
            & $RealPython $doctorScript "secrets" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-doctor.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("doctor", "net-doctor", "sys-doctor", "diagnose") } {
        $doctorScript = Join-Path $AsterixRoot "scripts-hub\ax-doctor.py"
        if ($RealPython -and (Test-Path $doctorScript)) {
            & $RealPython $doctorScript "doctor" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-doctor.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("canary", "ransomware-guard", "anti-ransomware") } {
        $shieldScript = Join-Path $AsterixRoot "scripts-hub\ax-shield.py"
        if ($RealPython -and (Test-Path $shieldScript)) {
            & $RealPython $shieldScript "canary" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-shield.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("supply-chain", "dep-audit", "audit-deps") } {
        $shieldScript = Join-Path $AsterixRoot "scripts-hub\ax-shield.py"
        if ($RealPython -and (Test-Path $shieldScript)) {
            & $RealPython $shieldScript "supply-chain" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-shield.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("phish-shield", "phish-check", "homoglyph") } {
        $shieldScript = Join-Path $AsterixRoot "scripts-hub\ax-shield.py"
        if ($RealPython -and (Test-Path $shieldScript)) {
            & $RealPython $shieldScript "phish-shield" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-shield.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("takeover", "subdomain-takeover", "cname-audit") } {
        $cloudScript = Join-Path $AsterixRoot "scripts-hub\ax-cloud-defense.py"
        if ($RealPython -and (Test-Path $cloudScript)) {
            & $RealPython $cloudScript "takeover" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cloud-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("ssrf-guard", "ssrf", "metadata-guard") } {
        $cloudScript = Join-Path $AsterixRoot "scripts-hub\ax-cloud-defense.py"
        if ($RealPython -and (Test-Path $cloudScript)) {
            & $RealPython $cloudScript "ssrf-guard" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cloud-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("api-sentinel", "api-audit", "api-guard") } {
        $cloudScript = Join-Path $AsterixRoot "scripts-hub\ax-cloud-defense.py"
        if ($RealPython -and (Test-Path $cloudScript)) {
            & $RealPython $cloudScript "api-sentinel" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cloud-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("scrub", "exif-strip", "anon-media") } {
        $privScript = Join-Path $AsterixRoot "scripts-hub\ax-privacy.py"
        if ($RealPython -and (Test-Path $privScript)) {
            & $RealPython $privScript "scrub" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-privacy.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("dns-shield", "doh", "dns-crypt") } {
        $privScript = Join-Path $AsterixRoot "scripts-hub\ax-privacy.py"
        if ($RealPython -and (Test-Path $privScript)) {
            & $RealPython $privScript "dns-shield" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-privacy.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("ip-shield", "webrtc-leak", "privacy-audit") } {
        $privScript = Join-Path $AsterixRoot "scripts-hub\ax-privacy.py"
        if ($RealPython -and (Test-Path $privScript)) {
            & $RealPython $privScript "ip-shield" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-privacy.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("call-shield", "voip-guard", "acoustic-scan") } {
        $intelScript = Join-Path $AsterixRoot "scripts-hub\ax-intel-defense.py"
        if ($RealPython -and (Test-Path $intelScript)) {
            & $RealPython $intelScript "call-shield" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-intel-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("vision-shield", "stego-guard", "face-cloak") } {
        $intelScript = Join-Path $AsterixRoot "scripts-hub\ax-intel-defense.py"
        if ($RealPython -and (Test-Path $intelScript)) {
            & $RealPython $intelScript "vision-shield" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-intel-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("stealth-trace", "anti-fingerprint", "ja3-scan") } {
        $intelScript = Join-Path $AsterixRoot "scripts-hub\ax-intel-defense.py"
        if ($RealPython -and (Test-Path $intelScript)) {
            & $RealPython $intelScript "stealth-trace" @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-intel-defense.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("undercover", "stealth", "camouflage", "stealth-shell") } {
        $underScript = Join-Path $AsterixRoot "scripts-hub\ax-undercover.py"
        if ($RealPython -and (Test-Path $underScript)) {
            & $RealPython $underScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-undercover.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("boot-tool", "live-boot", "usb-boot", "rufus-prep", "downloads", "iso") } {
        $bootScript = Join-Path $AsterixRoot "scripts-hub\ax-boot-tool.py"
        if ($RealPython -and (Test-Path $bootScript)) {
            & $RealPython $bootScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-boot-tool.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("arsenal", "tools", "tool-registry", "packages-all") } {
        $arsenalScript = Join-Path $AsterixRoot "scripts-hub\ax-arsenal.py"
        if ($RealPython -and (Test-Path $arsenalScript)) {
            & $RealPython $arsenalScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-arsenal.py not found." -ForegroundColor Red
        }
    }

    { $_ -in @("cam-hunter", "hotel-guard", "tscm", "spycam-scan", "privacy-sweep") } {
        $camScript = Join-Path $AsterixRoot "scripts-hub\ax-cam-hunter.py"
        if ($RealPython -and (Test-Path $camScript)) {
            & $RealPython $camScript @RemainingArgs
        } else {
            Write-Host "  [ERROR] Python runtime or ax-cam-hunter.py not found." -ForegroundColor Red
        }
    }

    default {
        # Fallback to Git Bash ax if available
        $gitBash = "C:\Program Files\Git\bin\bash.exe"
        $bashAx = Join-Path $AsterixRoot "bin\ax"
        if ((Test-Path $gitBash) -and (Test-Path $bashAx)) {
            & $gitBash $bashAx $Command $RemainingArgs
        } else {
            Write-Host "  ${C_CYAN}ASTERIX OS Master Command Dispatcher (Windows)${C_RESET}"
            Write-Host "  Usage: ax <command> [args...]"
            Write-Host "  Commands:"
            Write-Host "    ax os-computing [probe|collaborate|compute|imitate|features|status]"
            Write-Host "    ax status"
            Write-Host "    ax probe"
            Write-Host "    ax collaborate"
            Write-Host "    ax compute"
            Write-Host "    ax ai [chat|ask|audit]"
            Write-Host "    ax sysfetch"
            Write-Host "    ax -fix <file|snippet>       Auto-repair code syntax (Python, C, Rust, Bash, JS)"
            Write-Host "    ax debug <command>           Intercept runtime crashes & get AI root-cause hints"
            Write-Host "    ax bounty <domain>           Autonomous bug bounty recon & attack surface probe"
            Write-Host "    ax scratch <lang> [--watch]  Instant scratchpad studio with live hot-reload"
            Write-Host "    ax map [path] [--tree|audit] Autonomous codebase cartographer & architecture map"
            Write-Host "    ax scaffold <type> <name>    Auto-generate architecture boilerplate (route/service/model)"
            Write-Host "    ax unblock <port>            Instantly free blocked port & terminate zombie process"
            Write-Host "    ax secrets [path]            Audit codebase for leaked API keys, tokens & credentials"
            Write-Host "    ax doctor [--fix]            Diagnose online connectivity & developer environment"
            Write-Host "    ax canary [deploy|check]     Deploy & monitor anti-ransomware canary tripwires"
            Write-Host "    ax supply-chain [path]       Audit dependencies for typosquatting & malicious hooks"
            Write-Host "    ax phish-shield <domain>     Detect homoglyphs, Punycode tricks & phishing spoofing"
            Write-Host "    ax takeover <domain>         Audit dangling CNAMEs & cloud service subdomain takeovers"
            Write-Host "    ax ssrf-guard <url>          Block SSRF, cloud metadata (169.254.169.254) & rebinding"
            Write-Host "    ax api-sentinel <url>        Audit API defense headers, CORS, shadow OpenAPI schemas"
            Write-Host "    ax scrub <file|folder>       Lossless metadata anonymizer: strip GPS & EXIF from media"
            Write-Host "    ax dns-shield                Encrypted DNS (DoH) auditor: block ISP cleartext snooping"
            Write-Host "    ax ip-shield                 Audit WebRTC STUN leaks, IPv6 bypasses & public IP risk"
            Write-Host "    ax call-shield [audit|scan]  VoIP wiretap defense, ultrasonic beacon hunter & mic monitor"
            Write-Host "    ax vision-shield [stego|cloak] Image steganography scanner & adversarial biometric cloaker"
            Write-Host "    ax stealth-trace [fingerprint] Hardware/browser entropy auditor, JA3 sentinel & packet padding"
            Write-Host "    ax undercover [on|off|boot]  Terminal disguise mode & stealth bootloader camouflage"
            Write-Host "    ax boot-tool [guide|rufus|list] Live USB creator, Rufus/Ventoy profiles & drive scanner"
            Write-Host "    ax cam-hunter [hotel|scan|rf|guide] Hotel privacy counter-surveillance & hidden camera detector"
        }
    }
}
