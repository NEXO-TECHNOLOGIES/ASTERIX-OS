# [ASTERIX] ASTERIX OS — New Updates & Architectural Enhancements
> **Next-Generation Cybernetic Operating System & High-Performance Security Platform**  
> *Latest Update Release | Web Code Structure Engine & Termux Max-Tier Upgrade*

---

##  Overview of Recent Upgrades

This update cycle introduces high-impact architectural enhancements:
1. **[ASTERIX] Peak Cognitive Neural AI & Supabase Cloud Memory (`ax ai` / `asterix-ai`)** — Upgraded from offline-only placeholder to a multi-tiered cognitive reasoning engine with persistent Supabase Cloud Memory, SQLite local caching, vector similarity search, and a deep offline knowledge matrix covering microkernels, assembly, C, and cybersecurity.
2. **[SEC] ASTERIX Cyber Microkernel in C and Assembly (`kernel/`)** — Freestanding bare-metal microkernel with Multiboot v1 bootstrap (`boot.asm`), CPU exception and IRQ interrupt stubs (`isr.asm`), memory-mapped VGA console driver (`vga.h`), 8259 PIC remapping and IDT (`idt.h`), physical frame memory allocator (`kernel.h`), round-robin scheduler, and `int 0x80` syscall gateway.
3. **[*] Stage 2 Bootloader & SIMD Crypto Assembly Engine (`boot-asm/`)** — Transitions 16-bit real mode to 32-bit protected mode and 64-bit long mode (`asterix-stage2-loader.asm`), INT 0x15 E820 system memory probe, dual A20 line gate, 4-level paging, and AVX2/SSE2 vectorized cryptographic accelerator (`asterix-simd-crypto.asm`).
4. ** Native C Standalone Cryptography & Raw Socket Packet Engine (`core-utils-c/`)** — Zero-dependency standalone implementations of ChaCha20-Poly1305 AEAD and AES-256 (`asterix-crypto-core.c`), plus raw socket packet decoder and stealth scan anomaly detector (`asterix-packet-engine.c`).
5. **[NET] Web Code Structure & Deep Source Extraction Engine (`ax web-structure` / `ax curl-tree` / `ax webdump`)** — Next-Gen `curl` alternative that parses full DOM trees, JavaScript bundles and extracted internal APIs, CSS stylesheets, form endpoints, tech stack and security posture, and exports the complete offline code structure with zero external pip dependencies.
6. **[MOBILE] Termux Mobile System Center & Toolbox (`ax mobile-sys` / `termux-toolbox`)** — Dedicated hardware HUD, battery health metrics, multi-DNS resolver latency benchmarking, storage cache purging, and Termux self-healing diagnostics.

---

## 0. [ASTERIX] Peak Cognitive Neural AI & Supabase Cloud Memory Bridge

The ASTERIX AI subsystem (`asterix-ai/`) has been upgraded to a resilient multi-tier cognitive architecture:

### Multi-Tier Inference Hierarchy:
- **Tier 1: Cloud & Local LLM Integration**: Automatically discovers and queries local Ollama models (`qwen2.5:3b-instruct` or custom models) or Cloud REST endpoints. Non-blocking health checks prevent socket hangs when offline.
- **Tier 2: Peak Embedded Cognitive Matrix (Zero Dependencies)**: When offline or Ollama is unavailable, the AI autonomously draws from a deep technical reasoning matrix covering:
  - Microkernel design (paging, GDT, IDT, system call gateways, PIC remapping)
  - x86_64 & ARM64 assembly (System V AMD64 ABI, registers, bootloaders, SIMD)
  - C systems programming (memory safety, stack canaries, ASLR, leak triage)
  - Hardware-accelerated cryptography (ChaCha20, Poly1305, AES-256)
  - Offensive cybersecurity & SOC triage (OWASP Top 10, SSRF guards, attack surfaces)
  - Android Termux resource governance & PRoot optimization

### Persistent Supabase Cloud Memory:
- **Persistent Local Cache**: Uses SQLite (`asterix-ai/cognitive_memory.db`) with automatic connection lifecycle management and zero platform file locks.
- **Supabase Cloud Bridge**: Seamless bidirectional synchronization with Supabase PostgREST backend. Configurable via `ax ai cloud-setup <URL> <KEY>` or environment variables `ASTERIX_SUPABASE_URL` / `ASTERIX_SUPABASE_KEY`.
- **Vector & Keyword Semantic Recall**: Token similarity scoring augments user prompts with recalled operational context and past dialogue turns.

```bash
ax ai ask "how do syscalls work in the kernel?"       # Ask Peak AI with cognitive memory recall
ax ai chat                                            # Interactive conversational cyber session
ax ai cloud-setup <SUPABASE_URL> <SUPABASE_ANON_KEY>  # Link AI to Supabase cloud memory
ax ai cloud-sync                                      # Force bidirectional memory sync
ax ai cloud-memory                                    # Inspect total and synced memory count
```

---

## 0.1 [SEC] ASTERIX Cyber Microkernel in C and Assembly (`kernel/`)

Located in `kernel/`, the ASTERIX Cyber Microkernel provides a freestanding Ring 0 bare-metal kernel foundation:

- **Multiboot v1 Bootstrap (`kernel/src/boot.asm`)**:
  - Aligned Multiboot header (Magic: `0x1BADB002`, Flags: `0x03`, Checksum: `-0x1BADB005`) compatible with GNU GRUB and QEMU.
  - Initial 32 KB kernel stack and GDT initialization before transitioning control to `kmain`.
- **CPU Exception & Hardware IRQ Stubs (`kernel/src/isr.asm`)**:
  - Dedicated assembly ISR entry points for CPU exceptions 0–31 (Divide-by-zero, Page Fault, GPF, etc.).
  - Hardware IRQ stubs 0–15 remapped via 8259 PIC to interrupts 32–47.
  - Software interrupt `int 0x80` syscall gate.
- **C Microkernel Core (`kernel/src/kernel.c`)**:
  - Freestanding memory-mapped VGA video driver at `0xB8000` (80x25 text grid, 16 hardware colors, automatic scrolling).
  - 8259 PIC master/slave remapping (`0x20` and `0xA0` ports).
  - Physical Memory Frame Allocator (PMM) managing up to 128 MB of RAM in 4 KB physical pages with bitmap tracking.
  - Process Control Block (`pcb_t`) structures and Round-Robin scheduler stub.
  - Syscall dispatcher handling `SYS_WRITE (1)`, `SYS_READ (2)`, `SYS_YIELD (3)`, `SYS_GETPID (4)`, and `SYS_AUDIT (5)`.

Build and run in QEMU:
```bash
cd kernel && make
make qemu
```

---

## 0.2 [*] Bare-Metal Assembly Systems Expansion (`boot-asm/`)

- **Stage 2 Loader (`boot-asm/asterix-stage2-loader.asm`)**:
  - Probes available physical memory using BIOS INT 0x15 AX=0xE820 and stores the memory map at physical address `0x9000`.
  - Enables the A20 address line via Fast A20 (port `0x92`) and 8042 Keyboard Controller fallback.
  - Verifies CPUID support and checks for 64-bit Long Mode capability (`EDX bit 29`).
  - Sets up 4-level identity paging (PML4 at `0x1000`, PDPT at `0x2000`, PD at `0x3000` with 2MB huge pages).
  - Enables PAE in `CR4`, enables `EFER.LME` (MSR `0xC0000080`), activates paging in `CR0`, and executes a 64-bit far jump into Long Mode.
- **AVX2 / SSE Vectorized Cryptographic Engine (`boot-asm/asterix-simd-crypto.asm`)**:
  - `asterix_simd_xor_stream`: AVX2 256-bit vectorized stream encryption processing 32 bytes per instruction with SSE2 fallback.
  - `asterix_simd_entropy_scan`: Hardware vectorized byte frequency histogram counter for packed malware analysis and entropy calculation.
  - `asterix_simd_chacha_qr`: Vectorized ChaCha20 quarter-round (ARX) execution in registers.

---

## 0.3  Standalone Native C Cryptographic Core & Packet Engine (`core-utils-c/`)

- **Standalone Cryptographic Core (`core-utils-c/src/asterix-crypto-core.c`)**:
  - **Zero External Dependencies**: Standard C99 implementation without OpenSSL or libsodium.
  - **ChaCha20 Stream Cipher**: RFC 8439 compliant 256-bit key and 96-bit nonce stream cipher.
  - **Poly1305 Authenticator**: Constant-time polynomial evaluation modulo $2^{130} - 5$.
  - **AEAD Construction**: ChaCha20-Poly1305 authenticated encryption with associated data.
  - **AES-256 Block Cipher**: Rijndael S-Box substitution and 14-round key expansion.
  - Includes `--test` self-test suite (validating against official RFC 8439 and NIST SP 800-38A vectors) and `--bench` throughput benchmark.
- **Raw Socket Packet Engine (`core-utils-c/src/asterix-packet-engine.c`)**:
  - Live wire capture and protocol parsing for Ethernet, IPv4, TCP, UDP, and ICMP.
  - Autonomous stealth scan detection: flags NULL scans (no flags), XMAS tree scans (FIN+PSH+URG), SYN-FIN illegal scans, and Land attack loopback exploits.
  - Synthetic threat pattern audit mode (`--test`) for automated protocol validation.

---

## 0. [NET] Web Code Structure & Deep Source Extraction Engine (`ax web-structure` / `ax curl-tree`)

Built with **100% Python Standard Library (Zero Pip Dependencies)**, this engine transforms basic `curl <url>` into a full architectural code analyzer and offline code structure dumper.

### Core Capabilities:
- **Intelligent URL Resolver**: Automatically normalizes bare domains (`target.com` -> `https://target.com`), follows redirects, and handles TLS gracefully.
- **Architectural DOM Hierarchy Tree**: Renders a clean visual ASCII/ANSI tree diagram (`├──`, `└──`) of `<head>`, `<nav>`, `<main>`, `<section>`, forms, and components.
- **JavaScript & Module Extraction**: Extracts external scripts, inline script blocks, ES6 modules, and parses code to discover internal REST/GraphQL/WebSocket endpoints and AJAX calls (`fetch`, `axios`, etc.).
- **CSS & Styling Architecture**: Maps stylesheets, `@import` rules, fonts, and inline styles.
- **API & Endpoint Scanner**: Catalogs all discovered API routes, forms, methods, and parameters.
- **Technology Stack & Security Fingerprinting**: Automatically fingerprints CMS, frontend frameworks (React, Next.js, Vue, Nuxt, Angular, Tailwind, Bootstrap), web servers (Nginx, Cloudflare, Apache), and audits security headers (CSP, HSTS, X-Frame-Options, CORS).
- **Offline Code Structure Reconstructor (`--dump <dir>`)**: Downloads, prettifies, de-minifies, and organizes the complete codebase into an offline project folder (`index.html`, `js/`, `css/`, `manifest.json`, `endpoints.json`, `structure_tree.txt`).

### CLI Usage:
```bash
ax web-structure https://example.com          # Interactive architectural code structure tree
ax curl-tree example.com                      # Visual ASCII tree alternative to plain curl
ax web-structure example.com --source         # Beautified, syntax-highlighted code with line numbers
ax web-structure example.com --endpoints      # Extract all internal API routes and forms
ax web-structure example.com --dump ./dump    # Full offline code structure downloader & beautifier
ax mobile-sys battery                         # Mobile battery and hardware telemetry
ax mobile-sys dns                             # Mobile DNS latency benchmark (1.1.1.1, 8.8.8.8, 9.9.9.9)
```

---

## 1. [SEC] ASTERIX Defender Core (Pure-Rust Antivirus & Host Firewall)

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

## 2. [*] LIGHTNING Autonomous WAF & Web SOC Command Center

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

## 3.  APEX OVERDRIVE & eSports Kernel Gaming Suite

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

## 4.  Upgraded Windows Enterprise Feature Suite (Zero-Vulnerability Architecture)

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

## 5. [SEC] ASTERIX OS Tactical Stealth, Anti-Forensics & System Hardening Suite

Engineered natively for tactical field operations, cyber defense, and live incident response, these native subsystems integrate operational stealth, anti-forensics, forensic data preservation, and radio frequency reconnaissance directly into the ASTERIX OS platform:

### 1. `ax undercover` — Tactical Terminal Camouflage Engine
- **Architecture**: Native Python/Shell Disguise Engine
- **Functionality**: Instantly disguises the active terminal session as Windows 10/11 PowerShell / Command Prompt (`PS C:\Users\Administrator>`).
- **Tactical Utility**: Provides instant operational security when operating in public or monitored environments, wiping tactical terminal banners and spoofing Windows prompt semantics.

### 2. `ax nuke` — Cryptographic Emergency Wipe & Anti-Forensics
- **Architecture**: Native DOD-Standard Secure Storage Eradication
- **Functionality**: Performs emergency DOD-standard cryptographic sanitization (`shred -u -z -n 3`) of temporary caches, command history (`.bash_history`), session tokens, swap buffers, and sensitive workspace logs.
- **Safety**: Includes dry-run verification mode (`ax nuke dry-run`) and mandatory confirmation prompts to prevent accidental execution.

### 3. `ax tweaks` — Tactical Privacy & Network Obfuscation
- **Architecture**: Kernel & Network Layer Hardening Interface
- **Functionality**: Hardens network privacy by managing MAC address randomization (`macchanger` / `ip link`), enabling IPv6 temporary privacy addresses (`net.ipv6.conf.*.use_tempaddr=2`), and enforcing encrypted zero-log DNS resolvers (Quad9 / Cloudflare).

### 4. `ax forensic-mode` — Cryptographic Forensic Write-Blocker
- **Architecture**: Non-Invasive Digital Evidence Integrity Subsystem
- **Functionality**: Enforces digital evidence preservation rules: remounts all external drives and partitions strictly read-only (`mount -o remount,ro`), audits and disables active swap spaces to prevent evidence spilling, and suppresses background auto-mounting daemons.

### 5. `ax rf-audit` — Wireless RF Spectrum & Hardware Reconnaissance
- **Architecture**: Native Subsystem Radio Transceiver Monitor
- **Functionality**: Audits the host's wireless spectrum capabilities across Wi-Fi (802.11), Bluetooth, Ultra-Wideband (UWB), and Software-Defined Radio (SDR) USB peripherals. Reports hardware/software block status, monitor-mode support, packet injection readiness, and active RF killswitch state.

### 6. `ax hashdeep` — Recursive Cryptographic Binary Integrity Auditor
- **Architecture**: Multi-Algorithm File Hash Engine (MD5/SHA-1/SHA-256/SHA-512)
- **Functionality**: Creates recursive SHA-256 integrity baselines for all system and application binaries (`$PREFIX/bin`, `/bin`, `/usr/bin`). Audits live files against the baseline to immediately detect unauthorized binary modification, rootkits, or tampering. Also provides multi-algorithm hash checks (MD5, SHA-1, SHA-256, SHA-512).

### 7. `ax yara-scan` — Rule-Based Threat & Malware Heuristic Scanner
- **Architecture**: Deep Heuristic & Shannon Entropy Analyzer
- **Functionality**: Deep signature and pattern analyzer scanning directories for obfuscated webshells (`eval`, `base64_decode`), interactive reverse shell / C2 beacons (`/dev/tcp/`, `pty.spawn`), shellcode injection byte-sequences, and high Shannon entropy anomalies (>7.2 bits/byte).

### 8. `ax mac-guard` — Mandatory Access Control & Security Confinement
- **Architecture**: Kernel Mandatory Access Control Interface (AppArmor / SELinux)
- **Functionality**: Audits kernel-level Mandatory Access Control (AppArmor / SELinux), reports active profile confinement, and identifies unconfined network-listening daemons.

### 9. `ax timeline` — Digital Forensics MACB Activity Reconstructor
- **Architecture**: Chronological Filesystem Artifact Reconstruction Engine
- **Functionality**: Reconstructs chronological file activity (Modified, Accessed, Changed) within an incident window (e.g. last 1h, 24h, 7d). Features anti-forensic timestomp detection to flag files with future timestamps or suspicious metadata alterations.

### 10. `ax trash` — Cryptographic Recycle Bin & Deleted Media Vault
- **Architecture**: Cryptographically Audited Quarantine & Staging Store
- **Functionality**: Replaces destructive `rm -rf` by moving files to `~/.asterix_vault/trash/` with a cryptographic manifest containing timestamp, original absolute path, file size, and SHA-256 hash. Allows 1-click restore (`ax trash restore <ID>`) or permanent 3-pass DOD wipe (`ax trash empty`).

### 11. `ax carve` — Forensic Signature File Carver (Deleted Media Recovery)
- **Architecture**: Native Magic-Byte Header/Footer Pattern Carver
- **Functionality**: Scans disk devices, image dumps, or folders to carve and recover lost or deleted media using file magic headers and footers (JPEGs, PNGs, MP4/MOV videos, PDFs, and Office ZIP archives). Automatically leverages accelerated binary carving if helper libraries are installed.

### 12. `ax cam-hunter` — Hotel & Privacy Counter-Surveillance Subsystem (TSCM)
- **Architecture**: Pure Python Safe Surveillance Detector & Passive RF Sweeper
- **Functionality**: Protects user privacy when staying in hotels, Airbnbs, or sensitive meeting rooms. Replaces illegal and ineffective RF jamming with true Technical Surveillance Counter-Measures (TSCM): sweeps local Wi-Fi for hidden streaming cameras (RTSP 554, ONVIF 8000/8899, HTTP/MJPEG 8081), flags known spy-camera hardware MAC OUIs (Espressif ESP32-CAM, Tuya, Xiongmai, Dahua), detects covert ad-hoc wireless SSIDs (`CAM_*`, `IPCAM_*`), and provides an optical retro-reflection & infrared night-vision inspection field guide.

### Tactical CLI Commands:
```bash
ax undercover                   # Engage or disengage Windows PowerShell disguise shell
ax nuke dry-run                 # Preview files marked for cryptographic destruction
ax nuke shred                   # Execute 3-pass zeroization on logs and volatile caches
ax tweaks                       # Inspect and configure MAC randomization & IPv6 privacy
ax forensic-mode audit          # Verify write-blocker, swap state & automount status
ax forensic-mode engage         # Remount partitions read-only & lock automount
ax rf-audit                     # Audit Wi-Fi, Bluetooth, NFC & SDR radio transceivers
ax cam-hunter hotel             # Full hotel room privacy sweep: IoT cameras, ad-hoc APs & optical guide
ax cam-hunter scan              # Scan local Wi-Fi for hidden video streams (RTSP/ONVIF)
ax cam-hunter guide             # Optical pinhole reflection & infrared camera detection field guide
ax hashdeep baseline [dir]      # Generate SHA-256 baseline of system binaries
ax hashdeep audit [dir]         # Verify live binaries against baseline to detect tampering
ax yara-scan [dir]              # Scan directory for webshells, C2 beacons & shellcode
ax mac-guard                    # Audit AppArmor/SELinux confinement on listening services
ax timeline [dir] [mins]        # Digital forensics chronological activity & timestomp audit
ax trash [list|restore|empty]   # Secure recycle bin & quarantined media storage
ax carve <target> [out_dir]     # Foremost & Scalpel digital forensics deleted media recovery
```

---

## 6. [*] Performance, Storage & Network Diagnostics Subsystem

Engineered for high-efficiency operation across both Android Termux mobile devices and Bare-Metal Linux servers:

### 1. `ax power` — Hardware Power, Thermal & CPU Governor Controller
- **CPU Scaling Governors**: Dynamically switches CPU cores between `performance` (eSports/high compute) and `powersave` (battery preservation).
- **Battery Health Telemetry**: Live readout of battery capacity percentage, health status, charging wattage, and real-time millidegree temperature.
- **Thermal Sensors**: Streams temperature readings across all sysfs thermal zones with high-temperature color alerts (>60°C Yellow, >75°C Red).

### 2. `ax clean-pro` — Zero-Crash Storage Deduplication & Cache Optimizer
- **Package Cache Purge**: Automatically cleans `apt` archives and Termux `pkg` caches to eliminate "out of disk space" errors.
- **Volatile Artifact Eviction**: Purges aged temporary files, dead `.cache` entries, and lingering session artifacts.
- **SSD & Flash Wear-Leveling**: Invokes kernel TRIM (`fstrim -v /`) on supported SSD, NVMe, and UFS flash storage.

### 3. `ax flow` — Real-Time Network Flow & Socket Telemetry
- **Socket States**: Live protocol analysis across `ESTABLISHED`, `SYN_SENT`, `LISTEN`, and `TIME_WAIT` sockets.
- **DNS Speed Benchmark**: Benchmarks round-trip latency in milliseconds across Cloudflare (1.1.1.1), Google (8.8.8.8), Quad9 (9.9.9.9), and OpenDNS.
- **Interface Bandwidth**: Real-time cumulative RX/TX megabytes counter.

### 4. `ax ssl-audit` — Deep SSL/TLS Certificate & Expiry Tracker
- **Expiration Warnings**: Computes days remaining until expiry with color-coded alerts (<30 days Yellow, <7 days Critical Red).
- **Cipher & Protocol**: Inspects negotiated TLS version (TLS 1.2/1.3) and active cryptographic cipher suite.
- **Identity & SANs**: Extracts full Subject Alternative Names (SANs) and certificate authority chain.

### Subsystem Commands:
```bash
ax power [status|boost|save]    # Mobile/Linux CPU scaling governor, thermal & battery controller
ax clean-pro                    # Zero-crash cache purge, temporary file cleanup & SSD TRIM
ax flow                         # Real-time socket states, DNS latency benchmark & flow monitor
ax ssl-audit <domain>           # Deep SSL/TLS cipher auditor, expiry tracker & SAN inspector
```

---

## 7. [PKG] Modular External Package Registry Architecture

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

## 8. [LOCK] Zero-Vulnerability Security Verification Matrix

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

## 9.  ASTERIX OS Visual Architecture Diagram

The architectural filesystem layout diagram has been refreshed with all recent additions:
- **Filesystem Root**: Saved directly in the root directory (not in subfolders):
  - `ASTERIX_OS_DIAGRAM.png` (High-resolution PNG)
  - `ASTERIX_OS_DIAGRAM.jpg` (JPEG copy)
  - `ASTERIX_OS_LAYOUT.png` (Layout reference)
  - `ASTERIX_OS_LAYOUT.jpg` (Layout reference)
- **Visual Features**:
  - Cyan 3D wireframe **A** logo centered on a dark cybernetic grid.
  - Multi-tier structured boxes representing the full v3.0 "Beyond Kali" architecture:
    - **Tier 1: [CORE CLI & TUI]**: `bin/` (ax Master CLI, multi-subsystem routers) and `ui-core/` (asterix-loader Rust TUI, shell environment).
    - **Tier 2: [CONTAINER & MOBILE KERNEL]**: `engine/` (build-iso.sh, live persistence) and `termux-mobile/` (PRoot Debian Rootless, hardware HUD).
    - **Tier 3: [NATIVE MULTI-LANGUAGE UTILITIES]**: `boot-asm/` (16-bit MBR bootloader, ASM ciphers) and `core-utils-rust/` (asterix-defender-core, crypto-core, net-sentinel, log-hunter).
    - **Tier 4: [BREAKTHROUGH BEYOND-KALI ENGINES]**: `scripts-hub/` (`ax pathfinder` DAG, `ax team` P2P mesh, `ax ghost` decoy egress, `ax radio` RF sentinel, `ax evidence` vault).
    - **Tier 5: [PACKAGING & REPO ARCHITECTURE]**: `packages/debs/` (7 Kali-style metapackages), `apt-repo/` (Release/Packages APT repo), `Dockerfile` (Docker desktop sandbox).
    - **Tier 6: [ENTERPRISE SCOPE & FORENSICS]**: `ax engagement` (scope gating, client workspaces), `ax attest` (vTPM attestation & SBOM), and `ax sandbox` (OverlayFS rollback).

---

## 10.  ASTERIX AI — Rule-Based Expert System & SOC Inference Engine

Located in `asterix-ai/`, this is an offline expert triage system operating with **zero cloud dependencies** and **zero GPU requirements**:
- **Dual Runtime Architecture**:
  - `engine.py`: Pure Python 3 standard library heuristic inference and natural language query matching.
  - `engine.sh`: Pure native Bash fallback for minimal environments where Python is not available.
- **Knowledge Base Categories (`rules/`)**:
  - `security.json`: ASLR Level 2 validation, `kptr_restrict`, unprivileged `dmesg` restrictions, TCP SYN flood defense, and ICMP redirect mitigation.
  - `system.json`: Memory swappiness latency optimization, partition storage pressure thresholds, and CPU thermal throttling detection.
  - `network.json`: Localhost DNS privacy checks and promiscuous interface packet-sniffing detection.
- **Resilience Scoring & Actionable Remediations**:
  - Computes a comprehensive 0–100 Cyber Resilience Score.
  - Generates immediate terminal remediation commands for any non-compliant rules.
- **Natural Language Triage**:
  - Query via `ax ai ask "<question>"` for instant root-cause analysis and configuration fixes.

### CLI Commands:
```bash
ax ai [audit]                    # Evaluate live system state and generate resilience score
ax ai ask "<query>"              # Natural language question triage (e.g. "how do I fix memory swappiness?")
ax ai rules                      # Display active knowledge base rules, severity, and categories
```

---

## 11. [*] ASTERIX Auto-Compiler // Autonomous Self-Healing Build Engine

Located in `auto-compiler/`, this engine automates the entire compilation, linting, and bug-healing process with zero manual intervention:
- **Zero-Manual Error Healing**:
  - **Implicit Function Resolution**: Intercepts compiler errors and automatically injects missing standard library headers (`<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<unistd.h>`).
  - **Semicolon Insertion**: Parses line-and-column compiler diagnostics, automatically inserts missing `;` terminators, and preserves a `.bak` backup copy.
  - **Dynamic Linker Flag Injection**: When code triggers undefined references, dynamically adds `-lpthread`, `-lm`, `-lssl`, `-lcrypto`, or `-lpcap`.
  - **Header-to-Package Mapping**: Employs `recipes/headers.json` to resolve missing library headers to Linux packages (`libssl-dev`, `libpcap-dev`).
  - **Symbol Stripping**: Automatically invokes `strip --strip-unneeded` to produce compact, production-ready binaries.

### CLI Commands:
```bash
ax auto-compile <source>         # Compile C, C++, Rust, Go, or Assembly with auto-healing
ax auto-compile <dir>            # Auto-detect and build Makefile, Cargo.toml, or go.mod projects
```

---

## 12. [NET] ASTERIX OS-Computing // Universal Host Collaboration & Bridge v3.0

Located in `os-computing/`, this framework fuses ASTERIX OS with the host operating system (Windows 10/11, Linux, macOS, Termux) and mounted dual-boot systems (Debian, Ubuntu, Arch, Fedora, and companion security partitions):
- **Cross-OS Discovery (`ax os-computing probe`)**:
  - Detects host distribution, NT build/Linux release, kernel, architecture, and compute cores.
  - Probes CPU microarchitecture, RAM pools, GPU hardware accelerators (Intel HD/Arc, NVIDIA CUDA, AMD ROCm, Direct3D 12, Vulkan).
  - Inspects storage partitions, Windows Defender real-time protection, and Windows Subsystem for Linux (WSL1/WSL2).
- **Weaponized Arsenal Symbiosis (`ax os-computing collaborate`)**:
  - Searches for 120+ elite security tools across both operating systems and bridges them into `~/.asterix_vault/host_arsenal/bin/`.
  - Generates cross-platform environment hooks (`env.ps1`, `env.bat`, and `env.sh`).
  - Bridges wordlists (`rockyou.txt`, `seclists`) without duplicating disk space.
- **Compute & Hardware Synergy (`ax os-computing compute`)**:
  - Fuses available CPU cores, RAM, and GPU accelerators with live multi-core benchmark measuring throughput in MegaOps/Sec.
- **OS Persona Mimicry (`ax os-computing imitate`)**:
  - Adapts ASTERIX shell prompt, themes, and shortcuts to match host persona (Cybernetic Windows Sentinel, Sovereign Dragon, Crimson Warfare, Termux Mobile).
- **Telemetry Export (`ax os-computing features`)**:
  - Dumps complete machine telemetry to `~/.asterix_vault/host_arsenal/host_features.json`.

### CLI Commands:
```bash
ax os-computing probe            # Scan host OS, hardware topology, and dual-boot partitions
ax os-computing collaborate      # Bridge and fuse companion OS tools and wordlists into ASTERIX
ax os-computing compute          # Maximize CPU, RAM, and GPU compute synergy with live benchmark
ax os-computing imitate          # Adapt ASTERIX UI persona to host distribution
ax os-computing features         # Export complete telemetry to host_features.json
ax os-computing status           # Display complete cross-OS collaboration telemetry
```

---

## 13. [TOOL] ASTERIX Code-Repair Engine (Native Rust & C Self-Healing)

Located in `core-utils-rust/asterix-code-repair/` and `core-utils-c/src/asterix-code-repair.c`:
- **Dual-Tier Native Performance**: Tier 1 in pure Rust with zero-cost abstractions; Tier 2 in POSIX C for minimal embedded footprints.
- **Defect Detection & Auto-Healing**:
  - Traverses directory trees recursively (skipping `.git`, `target`, `node_modules`).
  - Balances `{}` braces, `()` parentheses, and `[]` brackets.
  - Injects missing semicolons `;` in C/C++ statements.
  - Injects missing colons `:` in Python control blocks.
  - Normalizes Windows CRLF line endings to Linux LF.
  - Creates `.bak` safety backups before applying any modification.

```bash
ax code-repair scan <dir>        # Inspect codebase for syntax and formatting defects
ax code-repair fix <dir>         # Recursively heal all defects with safety backups
```

---

## 14.  Conversational ASTERIX AI v3.0 (ChatGPT-Style Copilot)

Located in `asterix-ai/`:
- **Interactive Conversational Shell (`ax ai chat`)**: Provides an offline, zero-dependency natural language dialogue interface without sending queries to the cloud.
- **Expansive Dialogue & Threat Matrix**:
  - Conversational intents (`asterix-ai/rules/conversational_ai.json`): Greetings, identity, hacker philosophy, and career roadmaps.
  - Cyber Encyclopedia (`asterix-ai/rules/cyber_encyclopedia.json`): Deep multi-paragraph explanations on Buffer Overflows, ROP, SQLi, XSS, SUID privilege escalation, ARP spoofing, and Zero Trust.
- **Multilingual Support**: Real-time localized overviews in English, Spanish, French, German, Chinese, Arabic, and Russian (`ax ai about <lang>`).

```bash
ax ai chat                       # Launch interactive conversational AI session
ax ai ask "<query>"              # Natural language threat breakdown and remediation
ax ai audit                      # Evaluate system resilience against CIS benchmarks (0-100 score)
ax ai about [es|fr|de|zh|ar|ru]  # Display multilingual ASTERIX overview
```

---

## 15. [NET] ProxyChains Creator & Dynamic Routing Engine

Located in `proxychains-creator/`:
- **Protocol Handshake Probing**: Probes SOCKS5 (RFC 1928) and SOCKS4 sockets to ensure genuine proxy availability, not just open ports.
- **Detailed IP Telemetry**: Displays `STATUS`, `IP ADDRESS`, `PORT`, `TYPE (SOCKS4/5)`, `COUNTRY`, and `LATENCY (ms)`.
- **Dynamic Configuration Synthesis**: Automatically generates verified `~/.asterix_vault/proxychains/proxychains.conf` using `dynamic_chain` and `proxy_dns` to prevent DNS leakage.

```bash
ax proxychains scan              # Test SOCKS proxies and generate dynamic chain
ax proxychains add <ip> <port>   # Test and add a single proxy endpoint
ax proxychains status            # Display current active proxy chains configuration
```




## UPDATE 16 — AI Cognitive Adaptation Engine

- NEW: `asterix-ai/user_input_learner.py` — Full cognitive profile engine
- Persistent memory at `~/.asterix_vault/ai_memory/user_profile.json`
- Tracks 6 interest domains, infers technical level, detects preferred languages
- `ax ai teach "fact"` — store custom rules permanently into AI memory
- `ax ai profile` — rich color-coded memory HUD
- Every query auto-ingests and recalls relevant learned facts
- New aliases: `ax-memory`, `ax-teach`, `ai-memory`, `ax-learn`

## UPDATE 17 — Live Auto-Update Daemon (F-Droid Style)

- NEW: `auto-updater/update_daemon.py` — Python background daemon
- NEW: `auto-updater/update_daemon.sh` — Bash fallback daemon
- NEW: `auto-updater/asterix-updater.service` — systemd unit
- Polls GitHub API every 60s for new commits, auto-pulls on change
- `ax auto-update start|stop|status|check|log`
- State + log stored in `~/.asterix_vault/auto-updater/`
- New alias: `auto-update`

## UPDATE 18 — Auto-Updater ON / OFF Toggling
- Added `ax auto-update on` / `ax auto-update off` controls
- Toggles persistent `"enabled"` state in `~/.asterix_vault/auto-updater/state.json`
- Automatic daemon lifecycle management (stops on OFF, starts on ON)
- New aliases: `auto-update-on`, `auto-update-off`

## UPDATE 19 — Secure Localhost Chatting Vault (Zero-Knowledge E2EE)
- NEW: `secure-chat/` ecosystem
  - `server.py` — Python 3 multi-threaded zero-knowledge server (zero pip deps)
  - `web/index.html` — Cyber-dark glassmorphism UI with native Web Crypto API (AES-256-GCM + PBKDF2)
  - `client.py` — CLI terminal client
  - `server.sh` — Bash launcher
- Strict 2-party limit ("u and the person")
- 100% In-memory ephemeral storage (zero disk logs)
- Message self-destruct timers (5s, 15s, 30s, 60s)
-  1-click Emergency Panic Killswitch
- Cryptographic safety numbers / fingerprint
- Synthesized Web Audio API sound effects
- New aliases: `ax-chat`, `ax-secure-chat`, `secure-chat`, `chat-room`

## UPDATE 20 — Secure Chat v2.0: Group Vaults, Admin Controls & 3-Strike IDS
- Added **Group Vault** multi-user architecture alongside Direct 1-on-1 mode
- Custom password creation on room setup with PBKDF2 verification
- **[ALERT] 3-Strike Intrusion Detection System (IDS):**
  - Triggers OS terminal alert: `[ALERT] ASTERIX CAUGHT A THIEF SNOOPING INTO THE PRIVATE CHAT!`
  - Logs intruder IP and Port + counter-attack tool recommendations (`ax nmap`, `ax killswitch`, `ax decoy`)
  - Real-time intrusion alarm broadcast to connected web vault users
- ** Group Admin Suite:** Kick members, mute/unmute, purge chat history
- Full CLI client integration with `/kick`, `/mute`, `/purge`, `/members`
