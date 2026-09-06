# 🌌 ASTERIX OS — New Updates & Architectural Enhancements
> **Next-Generation Cybernetic Operating System & High-Performance Security Platform**  
> *Latest Update Release | Zero-Vulnerability Hardening & Windows Feature Parity*

---

## 📑 Overview of Recent Upgrades

This update cycle significantly elevates **ASTERIX OS** into a high-performance polyglot operating environment featuring:
1. **🛡️ Pure-Rust ASTERIX Defender Core** — Antivirus, Encrypted Quarantine Vault & Windows Security Center telemetry.
2. **⚡ LIGHTNING Autonomous WAF & Web SOC** — 16-module reverse proxy, real-time threat intelligence & SOC HUD.
3. **🎮 APEX OVERDRIVE & eSports Kernel Gaming Suite** — Windows Game Mode & DirectX HAGS parity with sub-0.5ms timers and 60 FPS HUD.
4. **🏢 Upgraded Windows Enterprise Feature Suite** — Native cryptographic ports of System Restore (VSS), Event Viewer, System File Checker (SFC), Task Manager EcoQoS, Local Security Policy (secpol), Sandbox, AppLocker, BitLocker, Credential Guard, and Exploit Guard.
5. **🐉 Kali Linux Live Tactical Features & Anti-Forensics** — Disguise engine (Undercover), cryptographic wipe (Nuke), system tweaks, forensic write-blocking, and RF spectrum audit.
6. **📦 Modular External Package Registry** — Unified GitHub auto-cloning and synchronization system.
7. **🔒 Zero-Vulnerability Security Hardening** — Kernel ASLR preservation, localhost loopback binding, and cryptographic file integrity seals.
8. **🗺️ Updated Visual Architecture Diagram** — High-resolution diagrammatic layout saved at the repository root.

---

## 1. 🛡️ ASTERIX Defender Core (Pure-Rust Antivirus & Host Firewall)

Located at `core-utils-rust/asterix-defender-core/`, this engine is built with **100% Pure Safe Rust (Zero External Crates)** for instant, zero-dependency compilation on Bare-Metal Linux, Debian Live ISOs, and Android Termux PRoot.

### Core Capabilities:
- **FIPS 180-4 SHA-256 Cryptographic Engine**: Native zero-crate implementation computing SHA-256 digests.
- **Antivirus & Threat Signature Scanner**: Detects known test patterns (EICAR), reverse shell invocations (`/dev/tcp`, `pty.spawn`, `nc -e`), PHP webshells (`c99`, `r57`, `b374k`, `eval(base64_decode)`), crypto-currency miners (`XMRig`, `stratum+tcp`), binary shellcode preambles, and high-entropy obfuscated droppers.
- **Encrypted Quarantine Vault**: Implements XOR stream neutralization (`ASTERIX_DEFENDER_CORE_QUARANTINE_ARMOR`), revokes execute permissions (`chmod 000`), and securely isolates infected files inside `~/.asterix/quarantine/`.
- **Host Firewall & Stealth Drop Rules**: Displays active packet filter status and 7-rule stealth drop policy.
- **Emergency Endpoint Network Isolation**: Instant network killswitch (`ax isolate` / `ax unisolate`) disconnecting all network interfaces to neutralize command-and-control (C2) during active incidents.
- **Windows Security Center Dashboard**: Real-time terminal health dashboard mirroring Windows Defender protection metrics.

### CLI Commands:
```bash
ax defender                  # Windows Security Center-style real-time health dashboard
ax defender scan [path]      # Scan directory or file for viruses, webshells & payloads
ax defender scan --quarantine # Scan and automatically neutralize & isolate threats
ax firewall                  # Inspect active host packet filter & stealth drop rules
ax isolate                   # Emergency network quarantine (disconnects external interfaces)
ax unisolate                 # Restore normal network routing
ax quarantine                # Inspect safely isolated threats in the quarantine vault
```

---

## 2. ⚡ LIGHTNING Autonomous WAF & Web SOC Command Center

Integrated into the package registry (`packages/LIGHTNING-/`), LIGHTNING delivers military-grade web defense:

### 16-Module Autonomous Defense Stack:
1. **WAF Reverse Proxy**: Intercepts, decodes, and inspects HTTP/HTTPS traffic.
2. **Real-Time Web SOC Dashboard**: Glassmorphic web console at `http://127.0.0.1:8888`.
3. **Zero-Day Dynamic Virtual Patching**: Neutralizes newly discovered exploit vectors before patches exist.
4. **Global Threat Intelligence Feeds**: Ingests malicious IP and botnet reputation blacklists.
5. **Decoy Honeypot Emulators**: Traps automated crawlers and adversary probes.
6. **Data Loss Prevention (DLP)**: Prevents accidental leaks of PII, API tokens, and credentials.
7. **Automated SSL/TLS Manager**: Manages certificates and enforces modern TLS ciphers.
8. **Behavioral Heuristic Scoring**: Evaluates visitor anomaly risk in real time.
9. **Anti-Bot Proof-of-Work (PoW) & CAPTCHA**: Halts Layer-7 DDoS and scraping attacks.
10. **Database Defense Sentinel**: Contextual SQL injection detection and blocking.
11. **Syslog Forwarder & SIEM Integration**: Ships structured CEF/JSON security events.
12. **Sliding-Window Token Bucket Rate Limiter**: Granular per-IP and per-URI traffic shaping.
13. **Multi-Tenant Access Control Lists (ACL)**: Whitelist and blacklist management.
14. **Unicode & Normalization Filter**: Eliminates path traversal and encoding smuggling bypasses.
15. **OpenAPI / Swagger Validator**: Restricts API calls to authorized endpoint schemas.
16. **High-Availability Sentinel**: Automated failover and health checking.

### CLI Commands:
```bash
ax lightning                 # Launch LIGHTNING WAF reverse proxy & Web SOC dashboard
ax waf                       # Alias for LIGHTNING WAF engine
ax soc                       # Alias for Web SOC control center
```

---

## 3. 🎮 APEX OVERDRIVE & eSports Kernel Gaming Suite

Engineered to match and surpass Windows Game Mode, DirectX Hardware-Accelerated GPU Scheduling (HAGS), and microsecond timer tuning for ultra-low latency eSports gaming.

### Key Performance Modules:
- **5-Stage Kernel Game Mode (`ax game boost`)**:
  1. **CPU Frequency Governor**: Locks all CPU cores to `performance` state.
  2. **Standby Memory Purge**: Flushes standby memory lists (`vm.drop_caches=3`) and compacts RAM for game textures.
  3. **Low-Latency Network Stack**: Activates TCP BBR congestion control, `tcp_low_latency=1`, `tcp_fastopen=3`, and `tcp_notsent_lowat=16384` to eliminate packet batching jitter.
  4. **Thread Priority**: Elevates audio and rendering threads to real-time priority (`rtprio 98`, `nice -20`).
  5. **Zero-Vulnerability Enforcement**: Verifies that ASLR, `kptr_restrict`, and `ptrace_scope` remain 100% active during gaming.
- **DirectX HAGS & Shader Cache Optimizer (`ax game hags`)**:
  - Purges fragmented or corrupt Mesa, Nvidia, and Vulkan shader caches.
  - Forces GPU power management clocks to maximum performance states.
- **Sub-0.5ms Kernel Timer Telemetry (`ax game timer`)**:
  - Inspects hardware clocksource (TSC/HPET) and optimizes scheduler quantum (`sched_migration_cost_ns`).
- **Safe Standby RAM Flush (`ax game clean`)**:
  - Releases cached standby memory without closing running games or applications.
- **APEX OVERDRIVE 60 FPS Telemetry HUD (`ax overdrive`)**:
  - Rust kernel accelerator + Express REST backend + HTML5 glassmorphic dashboard at `http://127.0.0.1:4888`.
  - **Zero LAN Exposure**: Hardened to bind strictly to localhost loopback (`127.0.0.1`).

### CLI Commands:
```bash
ax game                      # Inspect current gaming telemetry, CPU governor & memory state
ax game boost                # Engage 5-stage eSports low-latency optimization
ax game restore              # Revert to standard balanced power profile
ax game hags                 # Flush shader caches & set GPU to max clocks
ax game timer                # Telemetry of sub-0.5ms kernel hardware timers
ax game clean                # Purge standby RAM list safely
ax overdrive                 # Launch APEX OVERDRIVE 60 FPS glassmorphic HUD (port 4888)
```

---

## 4. 🏢 Upgraded Windows Enterprise Feature Suite (Zero-Vulnerability Architecture)

We ported core Windows administrative and reliability subsystems into native, hardened ASTERIX OS tools:

| Windows Feature | ASTERIX OS Command | Upgrades Over Windows Equivalent |
| :--- | :--- | :--- |
| **System Restore / VSS** | `ax snapshot` | Atomic configuration snapshots (`/etc`, shell configs, package manifests) with cryptographic SHA-256 verification seals. Verifies hash tree **before** executing any rollback; aborts if tampering is detected. Automatically creates pre-rollback safeguard snapshots. |
| **Event Viewer & Reliability Monitor** | `ax event-log` | Analyzes `/var/log/auth.log`, `dmesg`, and `journalctl`. Maps Windows Event IDs 4625 (Auth Fail), 4624 (Logins), 4672 (Sudo), Kernel Panics, and OOM kills. Calculates live **ASTERIX System Reliability Index (0–100%)** with live streaming support. |
| **System File Checker & DISM** | `ax sfc` | Verifies cryptographic SHA-256 integrity, permissions, and ELF binary headers of all core OS utilities. Automatically triggers clean source recompilation via `ax sfc repair` if discrepancies exist. |
| **Task Manager Priority & EcoQoS** | `ax taskmgr` | Sets Realtime (`nice -20`, `ionice -c 1`) vs Windows EcoQoS Efficiency Mode (`nice 19`, `ionice -c 3`). Includes process security auditor detecting hidden binaries, anomalous parent PIDs, and scripts executing from `/tmp`. |
| **Local Security Policy (secpol.msc)** | `ax secpol` | Audits and enforces 11 NSA/CIS Linux kernel baseline parameters (ASLR, kptr_restrict, ptrace_scope, protected symlinks/hardlinks, no core dumps, TCP SYN cookies, reverse path filtering, martian logging). |
| **Windows Sandbox** | `ax sandbox` | Ephemeral, disposable isolated container using Linux namespaces / bubblewrap / firejail. Read-only rootfs with volatile RAM overlay; self-destructs and wipes all artifacts on session exit. |
| **AppLocker / App Identity** | `ax applocker` | Enforces `noexec` on `/tmp`, `/dev/shm`, and `/var/tmp`. Scans for unauthorized binaries in writable directories and verifies against a cryptographic SHA-256 binary whitelist ledger. |
| **BitLocker Drive Encryption** | `ax bitlocker` | LUKS2 AES-256-XTS volume encryption manager with Argon2id PBKDF. Audits encrypted swap partitions to prevent cold-boot memory dump leaks to disk. |
| **Credential Guard & Key Isolation** | `ax cred-guard` | Enforces `prctl(PR_SET_DUMPABLE, 0)` anti-dumping memory shield (blocks Mimikatz/ProcDump), locks `/etc/shadow` to `0600`, and hardens kernel keyring. |
| **Exploit Guard & ASR** | `ax exploit-guard` | Audits Hardware DEP/NX, ASLR, and enforces Attack Surface Reduction (ASR) rules: blocks unprivileged eBPF, blacklists legacy protocols (DCCP, SCTP, RDS, TIPC), and verifies module signatures. |

### CLI Usage:
```bash
# System Restore (VSS)
ax snapshot create [name]    # Create cryptographically sealed restore point
ax snapshot list             # View all saved restore points with integrity status
ax snapshot restore <ID>     # Safely rollback system configurations to snapshot
ax snapshot delete <ID>      # Remove a snapshot from storage

# Event Viewer & Reliability Monitor
ax event-log                 # Display security event scorecard & System Reliability Index
ax event-log stream          # Real-time streaming log monitor (Ctrl+C to exit)

# System File Checker (SFC)
ax sfc                       # Scan all core ASTERIX binaries for corruption or tampering
ax sfc repair                # Automatically recompile & repair corrupted components

# Task Manager & Efficiency Mode
ax taskmgr                   # Launch cyber resource monitor (btop/htop/ps)
ax taskmgr priority <PID> <realtime|high|normal|eco> # Set process priority
ax taskmgr eco <PID>         # Place process into Windows EcoQoS Efficiency Mode
ax taskmgr audit             # Audit running processes for /tmp malware or hidden PIDs
ax taskmgr kill <PID>        # Terminate process cleanly

# Local Security Policy (secpol.msc)
ax secpol audit              # Audit kernel parameters against 11 NSA/CIS baselines
ax secpol enforce            # Enforce 100% compliance via /etc/sysctl.d/99-asterix-hardening.conf

# Windows Sandbox Equivalent
ax sandbox                   # Launch disposable ephemeral rootless sandbox shell
ax sandbox run <command...>  # Execute command in temporary RAM sandbox and destroy on exit

# AppLocker Equivalent
ax applocker audit           # Audit mount execution policies and running binaries
ax applocker lockdown        # Remount /tmp and /dev/shm with noexec flag
ax applocker whitelist <path> # Add trusted binary to cryptographic ledger

# BitLocker Equivalent
ax bitlocker status          # Check LUKS2 volume encryption and encrypted vault status
ax bitlocker audit           # Audit system disk and swap encryption state

# Credential Guard Equivalent
ax cred-guard audit          # Audit memory dump protection, shadow permissions & SSH keys
ax cred-guard lockdown       # Lock memory dumping, secure /etc/shadow to 0600

# Exploit Guard & Attack Surface Reduction
ax exploit-guard audit       # Verify Hardware DEP/NX, ASLR, and eBPF hardening
ax exploit-guard asr         # Apply Attack Surface Reduction rules (disable unprivileged eBPF & legacy protocols)
```

---

## 5. 🐉 Kali Linux Live Tactical Features & Anti-Forensics Suite

Extracted and adapted directly from the live Kali Linux 2025.2 filesystem (`D:\` Live USB), these 5 tactical tools integrate stealth, evasion, forensic integrity, and radio frequency reconnaissance into ASTERIX OS:

### 1. `ax undercover` — Kali Undercover Disguise Engine
- **Origin**: `kali-undercover`
- **Functionality**: Instantly disguises the active terminal session as Windows 10 PowerShell / Command Prompt (`PS C:\Users\Administrator>`).
- **Tactical Utility**: Provides instant operational security when operating in public or monitored environments, wiping tactical terminal banners and spoofing Windows prompt semantics.

### 2. `ax nuke` — Cryptographic Emergency Wipe & Anti-Forensics
- **Origin**: `cryptsetup-nuke-password`
- **Functionality**: Performs emergency DOD-standard cryptographic sanitization (`shred -u -z -n 3`) of temporary caches, command history (`.bash_history`), session tokens, swap buffers, and sensitive workspace logs.
- **Safety**: Includes dry-run verification mode (`ax nuke dry-run`) and mandatory confirmation prompts to prevent accidental execution.

### 3. `ax tweaks` — Tactical Privacy & Network Obfuscation
- **Origin**: `kali-tweaks`
- **Functionality**: Hardens network privacy by managing MAC address randomization (`macchanger` / `ip link`), enabling IPv6 temporary privacy addresses (`net.ipv6.conf.*.use_tempaddr=2`), and enforcing encrypted zero-log DNS resolvers (Quad9 / Cloudflare).

### 4. `ax forensic-mode` — Cryptographic Forensic Write-Blocker
- **Origin**: Kali Live Forensics boot option (`noswap noautomount`)
- **Functionality**: Enforces digital evidence preservation rules: remounts all external drives and partitions strictly read-only (`mount -o remount,ro`), audits and disables active swap spaces to prevent evidence spilling, and suppresses background auto-mounting daemons.

### 5. `ax rf-audit` — Wireless RF Spectrum & Hardware Reconnaissance
- **Origin**: Kali wireless reconnaissance stack (`rfkill`, `kismet`, multi-device capture)
- **Functionality**: Audits the host's wireless spectrum capabilities across Wi-Fi (802.11), Bluetooth, Ultra-Wideband (UWB), and Software-Defined Radio (SDR) USB peripherals. Reports hardware/software block status, monitor-mode support, packet injection readiness, and active RF killswitch state.

### Tactical CLI Commands:
```bash
ax undercover                   # Engage or disengage Windows PowerShell disguise shell
ax nuke dry-run                 # Preview files marked for cryptographic destruction
ax nuke shred                   # Execute 3-pass zeroization on logs and volatile caches
ax tweaks                       # Inspect and configure MAC randomization & IPv6 privacy
ax forensic-mode audit          # Verify write-blocker, swap state & automount status
ax forensic-mode engage         # Remount partitions read-only & lock automount
ax rf-audit                     # Audit Wi-Fi, Bluetooth, NFC & SDR radio transceivers
```

---

## 6. 📦 Modular External Package Registry Architecture

To prevent repository bloat, third-party security tools are managed via automated synchronization:

```
ASTERIX-OS/
├── setup.sh                         # 1-command bootstrap
├── bin/ax                           # Universal omni-dispatcher with auto-fetch
├── packages/                        # Git-ignored local package storage
│   ├── README.md                    # Package directory documentation
│   ├── Asterix-Anti-Network-Attack/ # ARP, SYN flood, DNS hijack, sentinel
│   ├── THUNDER/                     # Enterprise defender, BadUSB, IP rotator
│   ├── ASTERISK-Web-Frality-scanner/# WSCAN Web weakness scanner
│   ├── LIGHTNING-/                  # Autonomous WAF & Web SOC
│   └── APEX-OVERDRIVE-/             # eSports performance suite & 60 FPS HUD
└── scripts-hub/
    └── ax-pkg-sync.sh               # Master package synchronization engine
```

### Management Commands:
```bash
ax pkg status                # Check git commits, branch & sync state of all packages
ax pkg sync [all|<name>]     # Auto-clone or pull latest tools and compile binaries
ax pkg list                  # View all registered external packages in catalog
ax pkg build                 # Rebuild native Rust/C components across all packages
```

---

## 7. 🔒 Zero-Vulnerability Security Verification Matrix

| Component | Security Control Applied | Verification Result |
| :--- | :--- | :--- |
| **APEX OVERDRIVE Server** | Bound strictly to `127.0.0.1` (`HOST = '127.0.0.1'`); no external LAN listening | **PASS (Zero remote attack surface)** |
| **Kernel Game Mode** | ASLR (`va_space=2`), `kptr_restrict=2`, `ptrace_scope=2` never lowered or disabled | **PASS (Defense intact during boost)** |
| **Snapshot Rollback Engine** | Computes SHA-256 hash tree comparison before restoration; aborts on mismatch | **PASS (Anti-tampering enforced)** |
| **Snapshot Vault Directory** | Permissions restricted to `chmod 700` (directory) and `chmod 600` (manifests/metadata) | **PASS (Unauthorized read blocked)** |
| **Process Security Auditor** | Identifies unlinked `/proc/*/exe` files and execution from `/tmp` or `/dev/shm` | **PASS (Malware stealth detected)** |
| **Kernel Hardening Baseline** | Enforces 11 NSA/CIS sysctl rules via `/etc/sysctl.d/99-asterix-hardening.conf` | **PASS (Kernel attack surface closed)** |
| **Compiler Verification** | `asterix-loader` and `asterix-defender-core` compiled via cargo with 0 errors | **PASS (0 errors, 0 warnings)** |

---

## 8. 🗺️ ASTERIX OS Visual Architecture Diagram

The architectural filesystem layout diagram has been refreshed with all recent additions:
- **Filesystem Root**: Saved directly in the root directory (not in subfolders):
  - `ASTERIX_OS_DIAGRAM.png` (High-resolution PNG)
  - `ASTERIX_OS_DIAGRAM.jpg` (JPEG copy)
  - `ASTERIX_OS_LAYOUT.png` (Layout reference)
  - `ASTERIX_OS_LAYOUT.jpg` (Layout reference)
- **Visual Features**:
  - Cyan 3D wireframe **A** logo centered on a dark cybernetic grid.
  - Multi-tier structured boxes showing `bin/`, `ui-core/`, `engine/`, `termux-mobile/`, `boot-asm/`, `core-utils-rust/` (including `asterix-defender-core`), `packages/` (including `APEX-OVERDRIVE-` and `LIGHTNING-`), and Tier 5 Windows Enterprise Subsystems (`snapshot`, `event-log`, `sfc`, `taskmgr`, `secpol`).
