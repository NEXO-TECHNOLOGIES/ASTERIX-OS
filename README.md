# 🌌 ASTERIX OS
### Next-Generation Cybernetic Security Operating System & Mobile Engine

> **🌐 Language / Idioma / Langue / Sprache / 语言 / لغة / Язык**: [English](README.md) | [Español](docs/locales/README.es.md) | [Français](docs/locales/README.fr.md) | [Deutsch](docs/locales/README.de.md) | [中文](docs/locales/README.zh.md) | [العربية](docs/locales/README.ar.md) | [Русский](docs/locales/README.ru.md)

```
    █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗ ███████╗
   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔═══██╗██╔════╝
   ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║   ██║███████╗
   ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║   ██║╚════██║
   ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╔╝███████║
   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝
                     >> NEXT-GEN CYBERNETIC PLATFORM <<
```

**ASTERIX OS** is a modular security environment and operating system designed for both **x86_64/ARM64 Live Bootable ISO systems (with Persistent USB storage)** and **Android Mobile devices via Termux PRoot**.

> [!NOTE]
> 🎯 **ASTERIX OS v2.0 "Phantom" Restructure**: Strategic architecture upgrade establishing **3 Product Tiers**, elevating the **8 Pure-Rust Security Engines** to center stage, adding formal [Threat Models](docs/THREAT_MODELS/), [Attack Playbooks](docs/ATTACK_PLAYBOOKS/), and [Performance Benchmarks](BENCHMARK_RESULTS.md). See [ASTERIX_OS_RESTRUCTURE_GUIDE.md](ASTERIX_OS_RESTRUCTURE_GUIDE.md) and [VERSION.toml](VERSION.toml).
> 🚀 **Latest Release Updates**: See [UPDATES.md](UPDATES.md) for full details on **ASTERIX Defender Core (Antivirus & Firewall)**, **APEX OVERDRIVE**, **LIGHTNING WAF & Web SOC**, and **Host Collaboration Bridge v3.0**.
> 🗺️ **Visual Architecture Diagram**: See [ASTERIX_OS_DIAGRAM.png](ASTERIX_OS_DIAGRAM.png) for the updated full-system layout diagram.

---

## 🎯 The 3 Product Tiers of ASTERIX OS v2.0

```
TIER 1: CORE OFFENSIVE & TELEMETRY ENGINES (Pure Rust, Ultra-Fast)
├── asterix-net-sentinel      → Parallel TCP/UDP scanner & port enumeration (3.75x faster than Nmap)
├── asterix-bin-inspector     → ELF/PE binary analysis, section entropy & obfuscation detector (6.7x faster)
├── asterix-log-hunter        → Real-time multi-pattern threat log forensics & brute-force detector (3.79x faster)
├── asterix-crypto-core       → Hash identification & cracking engine (182x faster than hashid)
├── asterix-dark-engine       → W^X violation scanner, memory page inspector & stealth radar HUD
├── asterix-defender-core     → Target hardening assessment, endpoint antivirus & host firewall
├── asterix-sys-mon           → Microsecond kernel & process telemetry surveillance HUD
├── asterix-code-repair       → Autonomous AST syntax defect repair & exploit payload healer
└── asterix-guard-engine      → Automated security compliance scoring & hardening benchmark

TIER 2: PLATFORM & DEPLOYMENT INFRASTRUCTURE
├── Live Bootable ISO         → Debian-based pentesting OS with persistent USB overlay
├── Termux Mobile             → Native Android offensive platform via PRoot Debian container
├── Quad-Grid Workspace       → 4-pane balanced terminal multiplexer (ax quad)
├── Cybernetic Desktop        → Minimal, fast desktop environment with live Conky HUD
├── AI Threat Hunter & SOC    → Conversational inference, threat modeling & hardware sensor bridge
├── Auto-Compiler Engine      → Autonomous self-healing compilation with automatic header resolution
└── Host Collaboration Bridge → Assimilates native Windows/Linux tools, telemetry & benchmark synergy

TIER 3: INTEGRATED SECURITY SUITES
├── THUNDER                   → Wireless reconnaissance, IP rotator (105 nodes) & MAC spoofer
├── LIGHTNING                 → Web SOC dashboard, WAF proxy & live threat interceptor
├── APEX OVERDRIVE            → Low-latency system optimization & real-time telemetry HUD
└── ANTI-NETWORK ATTACK       → ARP poisoning defense, TCP SYN shield & DNS lock
```

## ⚡ Core Features

* 🌌 **Master Command & Control Core (12 Subsystems in Pure Rust):**
  - Instant one-touch access to **Reconnaissance**, **Web Security**, **Exploitation**, **Password Auditing**, **Sniffing**, **Wireless Warfare**, **Forensics**, **Reverse Engineering**, **Developer Studio**, **Persistence Vault**, **Quad-Grid Tmux**, and **System Telemetry**.
* 🪟 **Ultimate Multi-Terminal Quad-Grid Multiplexer Studio:**
  - 4-way balanced cyber workspace (<kbd>Ctrl+A</kbd> <kbd>q</kbd>, `ax-quad`, or `asterix-quad`) running Sniffer, Scanner, Shell, and Monitor simultaneously.
  - Mouse scroll up to **100,000 lines**, pane synchronization toggle (<kbd>Ctrl+A</kbd> <kbd>y</kbd>), and cyber neon telemetry status bar.
* ⚡ **Supercharged Cyber Shell Environment (`ax-shell` / `asterix-shell`):**
  - High-tech dynamic prompt for Bash & Zsh with Git branch, root badge, execution timer, and IP badge.
  - **FZF Fuzzy Search Suite:** <kbd>Ctrl+R</kbd> (history), <kbd>Ctrl+T</kbd> (files), <kbd>Alt+C</kbd> (directory jumping).
  - Fast domain shortcuts (`ax-*` & `asterix-*`): `ax-recon`, `ax-web`, `ax-sniff`, `ax-crack`, `ax-wifi`, `ax-rev`, `ax-forensic`, `ax-dev`, `ax-quad`, `ax-cipher`, `ax-crypto`, `ax-sysmon`, `ax-guard`, `ax-bininspect`.
* 🦈 **BlackArch & Kali Grade Master Security Toolchain:**
  - **Recon & OSINT:** Nmap, Masscan, Amass, TheHarvester, DnsRecon, Whois, Netdiscover.
  - **Web Application Auditing:** SQLMap, Gobuster, Nikto, FFUF, WPScan, Commix, WhatWeb, Wafw00f.
  - **Exploitation & Payloads:** Metasploit Framework (`msfconsole`), SearchSploit, Socat, Netcat.
  - **Password & Hash Cracking:** Hashcat, John The Ripper, Hydra, Medusa, Ncrack, Crunch, HashID.
  - **Traffic Sniffing & Spoofing:** Wireshark, TShark, Tcpdump, Bettercap, Ettercap, MITMProxy, MacChanger.
  - **Wireless & Radio Warfare:** Aircrack-ng, Wifite, Reaver, Kismet, PixieWPS, Bully.
  - **Forensics & Steganography:** Binwalk, Foremost, Scalpel, Steghide, Exiftool, Chkrootkit.
  - **Reverse Engineering & Disassembly:** Radare2 / R2, GDB, Valgrind, Strace, Hexedit, XXD.
* 🛠️ **Full-Stack Developer & Build Toolchain:**
  - Rust (`rustc`, `cargo`), Go (`golang-go`), C/C++ (`gcc`, `clang`, `cmake`, `make`), Python 3 (`python3-dev`, `pip`, `ipython`), Node.js (`npm`), LazyGit, SQLite3, PostgreSQL, Redis-cli, HTTPie.
* 💾 **Dual-Layer Data Persistence (`ASTERIX PERSISTENCE`):**
  - **Live USB Mode:** Dedicated `persistence.conf` partition overlay preserving all user files across reboots.
  - **Termux Mobile Mode:** Automated bridge binding `$HOME/asterix_persistent` directly to Android internal storage `/sdcard/ASTERIX_PERSISTENCE`.

---

## 📁 Repository Layout

```
ASTERIX OS/
├── assets/                       # User Media Vault (Wallpapers, GRUB themes & Boot Videos)
│   ├── wallpapers/               # Desktop & Terminal Backgrounds
│   ├── animations/               # Boot Animation Videos / GIFs
│   └── iso-branding/             # GRUB splash & OS logos
├── core-utils-c/                 # Deep Kernel & System Analysis C Utilities (8 Native Tools)
├── core-utils-cpp/               # High-Performance C++ Cyber Tools (PacketCraft, VulnScan, LogWatch)
├── core-utils-go/                # High-Concurrency Go Reconnaissance Engine (asterix-webrecon)
├── core-utils-rust/              # Native Pure-Rust Security & Systems Engines Suite (7 Engines)
│   ├── asterix-bin-inspector/    # Binary analysis, ELF/PE/Mach-O parsing & section entropy
│   ├── asterix-net-sentinel/     # Thread-pooled TCP scanner, banner grabber & CIDR engine
│   ├── asterix-crypto-core/      # SHA256/512/MD5 hash engine, identifier & manifest suite
│   ├── asterix-sys-mon/          # Real-time microsecond kernel & process telemetry HUD
│   ├── asterix-guard-engine/     # Automated security hardening audit & compliance score
│   ├── asterix-dark-engine/      # Shannon entropy, W^X memory page inspector & stealth radar HUD
│   └── asterix-log-hunter/       # Multi-signature threat log analyzer & real-time log streamer
├── boot-asm/                     # x86-64 Assembly Bootloader (MBR Sector Chainloader & Telemetry)
├── desktop-env/                  # Linux Desktop Home Screen & HUD Environment
│   ├── applications/             # 12+ Linux .desktop application menu shortcuts
│   ├── conky/                    # Real-time desktop telemetry HUD overlay
│   ├── autostart/                # Auto-load wallpaper & HUD daemon
│   └── install-desktop.sh        # Desktop profile installer
├── engine/                       # Live ISO Build Engine (Debian live-build, UEFI+BIOS Hybrid)
│   ├── build-iso.sh              # ISO compile script with dual bootloaders & chroot hooks
│   ├── grub-theme/               # Multi-profile GRUB menu (Live, Persistence, LUKS, Forensic, Fail-safe)
│   ├── isolinux/                 # Legacy BIOS isolinux bootloader menus
│   ├── packages.list             # Master maximum-tier package manifest
│   ├── persistence-setup.sh      # Dual-mode USB persistence provisioner (Standard & LUKS Encrypted)
│   └── Dockerfile                # Isolated container build environment
├── ui-core/                      # Native Rust Cybernetic Visuals & Multiplexer
│   ├── asterix-loader/           # Pure Rust 12-subsystem master control hub
│   │   ├── Cargo.toml
│   │   ├── build.sh
│   │   └── src/main.rs
│   ├── asterix.tmux.conf         # Quad-Grid split & mouse scroll config
│   ├── asterix-shell-env.sh      # Cyber shell environment (FZF, aliases, prompts)
├── termux-mobile/            # Android Mobile PRoot Environment
│   ├── install-termux.sh     # 1-command installer for Termux (with auto-packages)
│   ├── asterix-termux-init.sh# Cybernetic mobile session initializer
│   └── setup-persistence.sh  # Android /sdcard/ storage bridge
├── asterix-ai/               # Rule-Based Expert System & SOC Inference Engine
│   ├── engine.py             # Pure Python 3 heuristic inference runner
│   ├── engine.sh             # Zero-dependency native Bash fallback engine
│   └── rules/                # Knowledge base rules (security, system, network, exploit JSON)
├── auto-compiler/            # Autonomous Self-Healing Compilation Engine
│   ├── autocompile.py        # Python 3 heuristic diagnostic and source repair loop
│   ├── autocompile.sh        # Pure Bash fallback auto-compiler
│   └── recipes/              # Missing header to package and linker flags mapping
├── os-computing/             # Dual-Boot & Host OS Collaboration Bridge
│   ├── os_bridge.py          # Host OS discovery, partition probe & tool assimilation
│   └── os_bridge.sh          # Pure Bash fallback cross-OS bridge
├── proxychains-creator/       # Proxy Discovery, SOCKS4/5 Validation & Chain Generator
│   ├── proxy_manager.py      # Python 3 socket handshake, geo lookup & chain generator
│   └── proxy_manager.sh      # Pure Bash fallback proxy tester
├── auto-updater/              # F-Droid-Style Live Repository Sync Daemon
│   ├── update_daemon.py      # Python 3 GitHub API poller & git-pull daemon (zero deps)
│   ├── update_daemon.sh      # Pure Bash fallback daemon (curl/wget + git)
│   ├── asterix-updater.service # systemd unit for Linux system-wide install
│   └── README.md             # Auto-updater documentation
├── secure-chat/               # Military-Grade Localhost E2EE Chat Vault
│   ├── server.py             # Pure Python 3 multi-threaded zero-knowledge server
│   ├── server.sh             # Bash launcher & status checker
│   ├── client.py             # Interactive CLI terminal chat client
│   ├── web/
│   │   └── index.html        # Web Crypto API (AES-256-GCM + PBKDF2), Burn & Panic UI
│   └── README.md             # E2EE architecture & security threat model
├── setup.sh                  # 1-command bootstrap: clones packages & compiles engines
├── packages/                 # Auto-synchronized external security suites
│   ├── README.md             # Package registry documentation
│   ├── Asterix-Anti-Network-Attack/ # Auto-cloned (ARP, SYN, DNS, Sentinel, Email)
│   ├── THUNDER/              # Auto-cloned (Wi-Fi deauth, IP Rotator, ASR, Defender)
│   ├── ASTERISK-Web-Frality-scanner/ # Auto-cloned (WSCAN Web Weakness Scanner)
│   ├── LIGHTNING-/            # Auto-cloned (WAF Proxy, Web SOC Dashboard & IDS)
│   └── APEX-OVERDRIVE-/       # Auto-cloned (eSports Gaming Optimizer & 60 FPS HUD)
└── docs/                         # Master Documentation & Architecture Guides
    ├── MASTER_TOOLCHAIN_MANUAL.md # Complete toolchain command encyclopedia
    ├── DEVELOPER_TOOLCHAIN_GUIDE.md # Compilers, Runtimes, R2, GDB & DBs
    ├── MODULAR_GITHUB_GUIDE.md   # Splitting across multiple GitHub accounts
    ├── ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md # Terminal tabs, splits & scrolling
    └── ROOTING_AND_DEVICE_GUIDE.md # Mobile PRoot vs. Hardware Rooted
```

---

## ⚡ Master Unified CLI: `ax` & `asterix`

ASTERIX OS features a unified command interface accessible interchangeably as **`ax`** or **`asterix`**:

```bash
# System & Arsenal Operations
ax update               # Refresh package repos, git core & security databases
ax upgrade              # Upgrade system packages & rebuild all native toolchains
ax install <pkg...>     # Automatically install packages via system package manager
ax remove <pkg...>      # Uninstall packages
ax search <keyword>     # Search package repositories
ax clean                # Purge unused packages, build artifacts & system cache
ax build                # Compile native C, C++, Go, Assembly, and Rust suites
ax doctor               # Comprehensive diagnostics on compilers, tools & storage
ax status               # Real-time telemetry HUD (Node, IP, Storage, Kernel)
ax sysfetch             # Cyberpunk ASCII system information fetch display
ax list                 # Browse all 80+ native specialized commands
ax version              # Show ASTERIX OS release information

# Active Anti-Network Attack & Account Defense
ax anti-net             # Master Anti-Network Attack interactive defense dashboard
ax anti-email <audit|breach> # Defensive email/account security (SPF/DMARC/breach check)
ax anti-arp <status|lock>    # ARP poisoning detection & permanent gateway locking
ax anti-syn <enable|status>  # TCP SYN flood shield & embryonic rate limiter
ax anti-dns <check|lock>     # DNS poisoning detector & immutable resolver lock
ax anti-scan <status|enable> # Port scan detector & dynamic 30-min auto-quarantine
ax anti-rev <audit|watch>    # Process anti-debugging, dumpable lock & anti-tampering

# THUNDER Enterprise Defender & Privacy Armor
ax thunder [args]            # THUNDER Enterprise Network & Device Defender
ax thunder --shield-all      # Arm all defensive shields simultaneously
ax thunder --scan <dir>      # Directory malware scan & interactive cyberpunk HTML report
ax ip-rotator [args]         # 105-endpoint IP rotator & network MAC randomizer

# WSCAN Web Weakness & Vulnerability Scanner
ax wscan [url]               # Interactive / automated web vulnerability audit
ax wscan <url> --sensitive   # Probe for exposed .env, .git, and config leaks
ax wscan <url> --method sql,xss # Active injection testing on target endpoints

# LIGHTNING WAF & Web SOC Command Center
ax lightning                 # Launch the full 16-module autonomous defense engine
ax waf                       # Alias — starts WAF reverse-proxy + Web SOC dashboard
ax soc                       # Alias — same as above (Web SOC entry point)

# ASTERIX DEFENDER CORE (Pure-Rust Antivirus & Host Firewall)
ax defender                  # Windows Security Center-style real-time status dashboard
ax defender scan [path]      # Real-time antivirus scanner (EICAR, Webshells, Reverse Shells, Miners)
ax defender scan --quarantine # Automatically neutralize and isolate detected threats
ax firewall                  # Inspect active host packet filter and stealth drop rules
ax isolate                   # Emergency endpoint network isolation (quarantines device from network)
ax unisolate                 # Restore normal external network connectivity
ax quarantine                # Inspect safely isolated threats in the encrypted quarantine vault

# Gaming Optimization & APEX OVERDRIVE Suite
ax game                      # Inspect gaming mode status, CPU scheduler, RAM, and TCP tuning
ax game boost                # Activate 5-stage eSports low-latency gaming engine
ax game hags                 # Flush GPU shader caches & trigger maximum hardware clocks
ax overdrive                 # Launch APEX OVERDRIVE 60 FPS glassmorphic HUD dashboard (port 4888)

# Upgraded Windows Enterprise Features (Zero-Vulnerability Architecture)
ax snapshot [create|list|restore] # System Restore & Volume Shadow Copy (VSS) cryptographic rollback
ax event-log [audit|stream]       # Windows Event Viewer & System Reliability Monitor (Events 4624/4625/4672)
ax sfc [scan|repair]              # Windows System File Checker & DISM component store verification
ax taskmgr [priority|eco|audit]   # Task Manager process priority & Windows EcoQoS Efficiency Mode
ax secpol [audit|enforce]         # Local Security Policy (secpol.msc) 11-rule kernel hardening baseline
ax sandbox [launch|run]           # Disposable ephemeral sandbox container (Windows Sandbox equivalent)
ax applocker [audit|lockdown]     # Application Identity & binary whitelisting (AppLocker equivalent)
ax bitlocker [status|audit]       # LUKS2 AES-256-XTS volume & swap encryption (BitLocker equivalent)
ax cred-guard [audit|lockdown]    # Process memory anti-dumping & credential shield (Credential Guard)
ax exploit-guard [audit|asr]      # Hardware DEP/NX & Attack Surface Reduction (Exploit Guard / ASR)

# Kali Linux Live Tactical Features & Anti-Forensics
ax undercover                   # Kali Undercover mode: Disguise shell as Windows PowerShell
ax nuke [dry-run|shred]         # Cryptographic emergency nuke: Multi-pass DOD wipe of keys, vaults & logs
ax tweaks                       # Kali Tweaks: MAC address randomization, IPv6 privacy, DNS resolver
ax forensic-mode [audit|engage] # Kali Forensic Mode: Hardware write-blocker, no-swap, no automount
ax rf-audit                     # Full wireless RF spectrum audit: Wi-Fi, Bluetooth, NFC, SDR hardware
ax hashdeep [baseline|audit]    # Kali Hashdeep: Recursive cryptographic binary integrity & tampering auditor
ax yara-scan [dir]              # Kali YARA heuristics: Webshell, reverse shell & memory shellcode scanner
ax mac-guard                    # Kali AppArmor & SELinux: Mandatory Access Control & process confinement audit
ax timeline [dir] [mins]        # Kali Sleuthkit: Digital forensics MACB timeline & timestomp anomaly detector
ax trash [list|restore|empty]   # Secure recycle bin: Preserves deleted files and media with recovery manifest
ax carve <target> [out_dir]     # Kali Forensics file carver: Recovers deleted photos, videos, PDFs & ZIPs

# ASTERIX AI — Rule-Based Expert System & SOC Inference Engine
ax ai [audit]                    # Autonomous rule evaluation across live kernel, sysfs, and host state
ax ai ask "<query>"              # Natural language technical triage, troubleshooting & remediation
ax ai rules                      # Browse active knowledge base rules, severity ratings & metrics

# Autonomous Code Repair, Debugging & Developer Accelerators
ax -fix <file|snippet>           # Universal Autonomous Code Healer (Python, C, C++, Rust, Go, JS, TS, Bash, JSON, SQL, HTML/CSS)
ax debug <command>               # Runtime Crash Interceptor: captures tracebacks & shows AI fix hints
ax bounty <domain>               # Automated Bug Bounty Recon: CT logs, port sweep, WAF & secrets dossier
ax scratch <lang> [--watch]      # Developer Scratchpad Studio with sub-millisecond hot-reload execution
ax map [path] [--tree|audit]     # Autonomous Codebase Cartographer: AST topology, cycles, bottlenecks & AI context
ax scaffold <type> <name>        # Architecture Synthesizer: auto-generate boilerplate (route, service, model)
ax unblock <port>                # Socket Unblocker: free occupied ports & kill zombie background processes
ax secrets [path]                # Credential Sentinel: audit codebase for leaked API keys, tokens & certs
ax doctor [--fix]                # System Doctor: diagnose online connectivity, DNS health & dev toolchains

# Performance, Power & Network Health Subsystem
ax power [status|boost|save]    # Mobile/Linux CPU scaling governor, thermal sensors & battery health
ax clean-pro                    # Zero-crash package archive purge, cache evictor & SSD/UFS TRIM
ax flow                         # Real-time TCP/UDP socket states, interface I/O & DNS latency benchmark
ax ssl-audit <domain>           # Deep SSL/TLS cipher auditor, expiry tracker & SAN certificate inspector

# Package Management & GitHub Synchronization
ax pkg status                # Check status and git commits of all security packages
ax pkg sync [all|<name>]     # Auto-clone or pull latest tools and compile binaries
ax pkg list                  # View all registered external packages

# Dark Cyber Security & Forensic Analysis
ax darktrace [mod]      # Stealth memory triage, entropy scan, log anomaly & net telemetry
ax shadowcam <target>   # RTSP / ONVIF stream & network camera security auditor
ax dark-engine <subcmd> # Pure-Rust Shannon entropy & W^X process memory page scanner
ax log-hunter <subcmd>  # Pure-Rust security log threat hunter & live threat stream monitor

# Tactical Cyber Warfare, Deception & Anti-Forensics
ax matrix               # Stream cyberpunk animated digital rain visualizer
ax stealth              # Engage Ghost Mode: Shreds bash history, logs, caches & RAM
ax killswitch [restore] # Sever all RF/ethernet, drop iptables & isolate system
ax decoy [port]         # Deploy honeypot listener to detect & log adversary probes
ax payload <ip> <port>  # Generate multi-language reverse shell one-liners
ax malware-scan [dir]   # Audit directory for webshells, base64 evals & persistence
ax tor-status           # Verify Tor onion routing, SOCKS5 proxy & identity leaks
ax quote                # Display cybernetic hacker ethos inspiration

# Network & OSINT Reconnaissance
ax ip                   # Display LAN IP, WAN public IP, interfaces & gateway
ax ports                # Audit open listening TCP/UDP sockets and processes
ax ping <target>        # Cybernetic ICMP latency probe
ax scan <target>        # Rapid port and service scanner
ax netrecon [subnet]    # Automated network discovery & diagnostic reporter
ax subdomains <domain>  # Passive CT subdomain enumeration (crt.sh)
ax banner-grab <host>   # Raw TCP socket daemon banner grabber
ax wifi-scan            # Scan wireless spectrum, SSIDs, BSSIDs & channels
ax sniff-live [iface]   # Live terminal packet sniffer radar
ax speedtest            # Benchmark network throughput and ICMP latency
ax mac [iface]          # Inspect or randomize/spoof interface MAC address
ax webrecon <url>       # High-performance Go web reconnaissance engine
ax dns <domain>         # Resolve DNS records (A, MX, TXT) with latency
ax whois <domain>       # Query registrar and ASN allocation details
ax traceroute <ip>      # Map network routing hops

# Security, Crypto & Forensics
ax encrypt <file>       # AES-256-CBC cryptographic file encryption
ax decrypt <file>       # AES-256-CBC cryptographic file decryption
ax hash <file|str>      # Multi-hash calculator (MD5, SHA-1, SHA-256, SHA-512)
ax shred <file>         # Cryptographic multi-pass secure file obliteration
ax exif <file> [--strip]# Forensic metadata inspection & sanitization
ax rootkit              # Scan for anomalous kernel modules and hidden procs
ax docker-audit         # Inspect Docker containers, sockets & escape risks
ax trace [pid]          # Live syscall monitor and process tracer
ax vuln [target]        # Cyber vulnerability assessment scanner
ax packet               # Interactive raw packet crafting and injection
ax logwatch             # Real-time security log and auth anomaly watcher
ax firewall             # Inspect active packet filter and firewall rules
ax audit                # Automated Linux security & hardening audit
ax suid                 # Scan filesystem for suspicious SUID binaries
ax certs <host>         # Inspect remote SSL/TLS certificate chain
ax genpass [len]        # Generate high-entropy cryptographic password
ax entropy <file>       # Detect packed, encrypted or obfuscated binaries
ax qr <text|url>        # Generate terminal ASCII QR code

# Deep Core Root & Kernel Hardening
ax kmod-audit           # Deep kernel module analysis, taint bitmask & unlinked LKM check
ax deleted-procs        # Ghost process detection: running binaries unlinked from disk
ax cap-audit            # Linux file capabilities & ambient process bounding set audit
ax ebpf-audit           # Inspect loaded eBPF programs, maps & unprivileged BPF state
ax root-persistence     # Scan ld.so.preload, systemd generators & PAM backdoor hooks
ax seccomp-audit        # Audit Seccomp-BPF filter isolation status across all processes
ax tty-snoop            # Detect TIOCSTI ioctl injection & audit pseudo-terminals
ax kexec-lockdown       # Kernel lockdown level & kexec hot-swap disable state check
ax mem-protect          # Verify CPU hardware exploit mitigations (SMEP, SMAP, NX)
ax mount-hardening      # Inspect /tmp & /dev/shm for nosuid, noexec, nodev flags
ax ipc-audit            # Audit shared memory segments, message queues & semaphores
ax dmesg-exploit        # Scan dmesg for slab corruption, ROP or stack canary crashes
ax root-jail            # Spawn ephemeral zero-privilege namespace isolation sandbox
ax core-dump-audit      # Inspect core_pattern handler & suid_dumpable memory policy

# Vault, Workspace & Desktop HUD
ax backup               # Sync and compress vault to Discord and Cloud Panel
ax loot                 # Browse captured hashes, scan reports & intelligence
ax scaffold <lang> <name># Scaffolds Rust, C, C++, Go, Python, or Node project
ax mem                  # Physical memory and ring buffer inspector
ax cpu                  # Inspect CPU microarchitecture and load average
ax disk                 # View disk partition mounts and capacity
ax ps                   # List active processes sorted by utilization
ax benchmark            # Run native CPU mathematics benchmark
ax wallpaper [random]   # Instantly cycle desktop cyberpunk wallpaper
ax hud [on|off|restart] # Toggle Conky desktop telemetry overlay
ax top                  # Launch Btop / Htop cyber resource monitor
ax compress <target>    # Create compressed tar archive
ax extract <archive>    # Automatically extract any archive format
ax find-large [dir]     # Find top 15 largest files on disk

# Direct Cyber Subsystem Launchers (no flags required)
ax recon                # 01. Reconnaissance & OSINT (Nmap, Masscan, Whois)
ax web                  # 02. Web Application Warfare (SQLMap, Gobuster, Nikto)
ax exploit              # 03. Exploitation & Payloads (Metasploit, Socat)
ax crack                # 04. Password & Hash Auditing (Hashcat, John, Hydra)
ax sniff                # 05. Sniffing & Traffic Control (Wireshark, TShark)
ax wifi                 # 06. Wireless Attacks (Aircrack-ng, Wifite)
ax forensics            # 07. Digital Forensics (Binwalk, Foremost, Steghide)
ax rev                  # 08. Reverse Engineering (Radare2, GDB, Hexedit)
ax dev                  # 09. Full-Stack Developer Studio (Rust, Go, C, Python)
ax quad                 # 11. Instant 4-Way Tmux Quad-Grid Cyber Studio
ax portal               # 12. Web Operations Media Portal (port 7777)
ax discord              # Discord Remote Vault Bridge & Notifications
ax cloud                # Cloud Compute Worker Daemon
ax vault                # Quick jump to /asterix_persistent storage
ax shell                # Launch enhanced cyber shell
```
> [!TIP]
> **⚡ Universal Omni-Dispatcher (Thousands of Tools):** Any Linux tool (e.g., `ax nmap -sV target`, `ax curl`, `ax git status`, `ax hydra`, `ax aircrack-ng`) is dynamically wrapped, executed, and monitored with status telemetry! Both `ax` and `asterix` work identically everywhere: Live USB, Linux Desktop, PRoot sandbox, and Android Termux!

---

## 🚀 Quick Start Guide

### 1. Launching the Cyber Command Center
Type `ax` or `asterix` anywhere in the terminal to launch the interactive Rust Command & Control Hub.

To run direct subsystems or flags:
* `ax recon` or `asterix --recon` » Jump to Recon & OSINT
* `ax web` or `asterix --web-audit` » Jump to Web Security
* `ax exploit` or `asterix --exploit` » Jump to Exploitation
* `ax crack` or `asterix --passwords` » Jump to Password Cracking
* `ax sniff` or `asterix --sniffing` » Jump to Sniffing & Traffic
* `ax wifi` or `asterix --wireless` » Jump to Wireless Attacks
* `ax forensics` or `asterix --forensics` » Jump to Digital Forensics
* `ax rev` or `asterix --reverse` » Jump to Reverse Engineering (Radare2)
* `ax dev` or `asterix --dev` » Jump to Full-Stack Developer Studio
* `ax quad` or `asterix --quad` » Launch Instant 4-Way Quad-Grid Workspace

### 2. Building the Bootable Live ISO (with Persistence)
```bash
cd engine
sudo ./build-iso.sh
```
To prepare a USB flash drive with live data persistence:
```bash
sudo ./persistence-setup.sh /dev/sdX
```

### 3. Installing on Android via Termux (Rootless)
Open Termux on Android and run:
```bash
curl -sSL https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/termux-mobile/install-termux.sh | bash
```
*(Alternative via GitLab: `curl -sSL https://gitlab.com/nexo-technologies-group/asterix-os/-/raw/main/termux-mobile/install-termux.sh | bash`)*

Once installed, type `ax` or `asterix` anytime to launch the cybernetic OS environment.

### 4. 1-Line Universal Bootstrap (Linux / Bare-Metal / Debian)
```bash
curl -sSL https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/setup.sh | bash
```

### 5. Termux Troubleshooting & Instant Fixes

* **Commands showing `Error: shell '/bin/sh' is not available in container 'debian'`?**  
  Connect `ax` directly to native Termux for 100% native execution:
  ```bash
  ln -sf ~/ASTERIX-OS/bin/ax $PREFIX/bin/ax && ln -sf ~/ASTERIX-OS/bin/ax $PREFIX/bin/asterix
  ```
* **Corrupted or half-downloaded Debian PRoot container?**  
  Cleanly reinstall the container:
  ```bash
  proot-distro reset debian
  ```
* **Termux out of disk space (`E: You don't have enough free space`)?**  
  Purge package cache:
  ```bash
  apt clean && pkg clean
  ```

---

## 💾 Full OS Distribution & Downloads (Resolving the 33 MB GitHub Issue)

> [!TIP]
> **Why does GitHub's "Download ZIP" only give ~33 MB when the repo is 188+ MB?**
> GitHub automatically applies maximum zip compression (which shrinks text, code, and scripts by 75–85%) and excludes untracked build caches (such as `core-utils-rust/target/`, which is ~71 MB). **All source files and media are intact.**
>
> To download or distribute the complete, unstripped ASTERIX OS workspace with pre-compiled artifacts and full media:

### Option 1: Official GitHub Releases (Up to 2.0 GB per file)
Download the full pre-packaged release archive directly from our GitHub Releases page:
- 📦 **GitHub Releases Download**: `https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/releases` (or your fork's `/releases/latest`)

### Option 2: Full Package via Google Drive
- ☁️ **Google Drive Direct Download**: `[Download ASTERIX-OS-FULL-PACKAGE.zip from Google Drive]` *(Paste your shared Google Drive link here after uploading)*

### Option 3: Package the Entire OS Locally (1-Click PowerShell)
To bundle the complete repository into a distribution ZIP on your machine:
```powershell
# Standard distribution package (pass -ExcludeMedia for lean code-only package)
powershell -ExecutionPolicy Bypass -File "scripts-hub\package-full-os.ps1" -ExcludeMedia
```
*This generates `ASTERIX-OS-FULL-PACKAGE.zip` directly on your Desktop with an automatic SHA-256 integrity checksum ready for Google Drive or GitHub Releases.*

---

## 📚 Detailed Documentation & Restructure Roadmap
* 🎯 [ASTERIX OS v2.0 Restructure Guide](ASTERIX_OS_RESTRUCTURE_GUIDE.md) — Architectural roadmap & toolchain optimization
* 📋 [Single Source of Truth Versioning](VERSION.toml) — Official semantic version matrix (Phantom)
* ⚡ [Official Performance Benchmarks](BENCHMARK_RESULTS.md) — Rust vs Nmap, readelf & GNU tools (3-7x speedup)
* 🛡️ [Threat Models & Detection Analysis](docs/THREAT_MODELS/) — Detection limits, stealth & operational security
* 🏹 [Offensive Security Playbooks](docs/ATTACK_PLAYBOOKS/) — Reconnaissance, web, binary & mobile workflows
* 🚀 [New Updates & Releases Guide (Defender, APEX, Windows Features)](UPDATES.md)
* 🗺️ [Master Visual Architecture Diagram](ASTERIX_OS_DIAGRAM.png)
* 🌌 [Master Toolchain & Command Encyclopedia](docs/MASTER_TOOLCHAIN_MANUAL.md)
* 🛠️ [Developer Toolchain & Engineering Guide](docs/DEVELOPER_TOOLCHAIN_GUIDE.md)
* 📖 [Multi-Repository GitHub Deployment Guide](docs/MODULAR_GITHUB_GUIDE.md)
* 🖥️ [ASTERIX Terminal, Splitting & Scrolling Guide](docs/ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md)
* 📱 [Android Rooting & Architecture Guide](docs/ROOTING_AND_DEVICE_GUIDE.md)
* 🖼️ [Media & Asset Drop Instructions](assets/README.md)

---

## ⚖️ License & Software Freedom

ASTERIX OS is developed by **NEXO TECHNOLOGIES GROUP** and dual-licensed under:

- **[Apache License, Version 2.0](LICENSE)**
- **[MIT License](LICENSE)**

at your option.

This dual-licensing structure follows the standard convention of the **Rust ecosystem** (used by the Rust Foundation, Tokio, Serde, and Axum), ensuring explicit patent grants and corporate indemnification under Apache-2.0 alongside total permissive freedom under MIT.

### Multi-Language SPDX Identifier Conventions

Source files across the codebase adhere to standardized SPDX header conventions:

| Language | SPDX License Header |
|---|---|
| **Rust** | `// SPDX-License-Identifier: MIT OR Apache-2.0` |
| **Python** | `# SPDX-License-Identifier: MIT OR Apache-2.0` |
| **C / C++** | `/* SPDX-License-Identifier: MIT OR Apache-2.0 */` |
| **Go** | `// SPDX-License-Identifier: MIT OR Apache-2.0` |
| **JavaScript / TypeScript** | `// SPDX-License-Identifier: MIT OR Apache-2.0` |
| **Shell / Bash** | `# SPDX-License-Identifier: MIT OR Apache-2.0` |
| **Assembly** | `; SPDX-License-Identifier: MIT OR Apache-2.0` |

Copyright (c) 2026 NEXO TECHNOLOGIES GROUP. All rights reserved.
