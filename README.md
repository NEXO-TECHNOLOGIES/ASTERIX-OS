# 🌌 ASTERIX OS
### Next-Generation Cybernetic Security Operating System & Mobile Engine

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

---

## ⚡ Core Features

* 🌌 **Master Command & Control Core (12 Subsystems in Pure Rust):**
  - Instant one-touch access to **Reconnaissance**, **Web Security**, **Exploitation**, **Password Auditing**, **Sniffing**, **Wireless Warfare**, **Forensics**, **Reverse Engineering**, **Developer Studio**, **Persistence Vault**, **Quad-Grid Tmux**, and **System Telemetry**.
* 🪟 **Ultimate Multi-Terminal Quad-Grid Multiplexer Studio:**
  - 4-way balanced cyber workspace (<kbd>Ctrl+A</kbd> <kbd>q</kbd> or `as-quad`) running Sniffer, Scanner, Shell, and Monitor simultaneously.
  - Mouse scroll up to **100,000 lines**, pane synchronization toggle (<kbd>Ctrl+A</kbd> <kbd>y</kbd>), and cyber neon telemetry status bar.
* ⚡ **Supercharged Cyber Shell Environment (`as-shell`):**
  - High-tech dynamic prompt for Bash & Zsh with Git branch, root badge, execution timer, and IP badge.
  - **FZF Fuzzy Search Suite:** <kbd>Ctrl+R</kbd> (history), <kbd>Ctrl+T</kbd> (files), <kbd>Alt+C</kbd> (directory jumping).
  - Fast domain aliases: `as-recon`, `as-web`, `as-sniff`, `as-crack`, `as-wifi`, `as-rev`, `as-forensic`, `as-dev`, `as-quad`.
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
├── desktop-env/                  # Linux Desktop Home Screen & HUD Environment
│   ├── applications/             # 12+ Linux .desktop application menu shortcuts
│   ├── conky/                    # Real-time desktop telemetry HUD overlay
│   ├── autostart/                # Auto-load wallpaper & HUD daemon
│   └── install-desktop.sh        # Desktop profile installer
├── engine/                       # Live ISO Build Engine (Debian live-build)
│   ├── build-iso.sh              # ISO compile script
│   ├── packages.list             # Master maximum-tier package manifest
│   ├── persistence-setup.sh      # USB persistence partition formatter
│   └── Dockerfile                # Isolated container build environment
├── ui-core/                      # Native Rust Cybernetic Visuals & Multiplexer
│   ├── asterix-loader/           # Pure Rust 12-subsystem master control hub
│   │   ├── Cargo.toml
│   │   ├── build.sh
│   │   └── src/main.rs
│   ├── asterix.tmux.conf         # Quad-Grid split & mouse scroll config
│   ├── asterix-shell-env.sh      # Cyber shell environment (FZF, aliases, prompts)
│   └── loading_screen.sh         # Pure bash fallback animation
├── termux-mobile/                # Android Mobile PRoot Environment
│   ├── install-termux.sh         # 1-command installer for Termux
│   ├── asterix-termux-init.sh    # Mobile session initializer
│   └── setup-persistence.sh      # Android /sdcard/ storage linker
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
bash <(curl -fsSL https://raw.githubusercontent.com/<YOUR_USER>/asterix-termux-mobile/main/install-termux.sh)
```
Once installed, type `ax` or `asterix` anytime to launch the cybernetic OS environment.

---

## 📚 Detailed Documentation
* 🌌 [Master Toolchain & Command Encyclopedia](docs/MASTER_TOOLCHAIN_MANUAL.md)
* 🛠️ [Developer Toolchain & Engineering Guide](docs/DEVELOPER_TOOLCHAIN_GUIDE.md)
* 📖 [Multi-Repository GitHub Deployment Guide](docs/MODULAR_GITHUB_GUIDE.md)
* 🖥️ [ASTERIX Terminal, Splitting & Scrolling Guide](docs/ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md)
* 📱 [Android Rooting & Architecture Guide](docs/ROOTING_AND_DEVICE_GUIDE.md)
* 🖼️ [Media & Asset Drop Instructions](assets/README.md)
