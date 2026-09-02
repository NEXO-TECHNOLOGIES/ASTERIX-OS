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

## 🚀 Quick Start Guide

### 1. Running the Rust Boot Loader & Master Matrix
```bash
cd "ui-core/asterix-loader"
./build.sh
./asterix-loader
```
Direct Subsystem Launchers:
* `asterix --recon` » Jump to Recon & OSINT
* `asterix --web-audit` » Jump to Web Security
* `asterix --exploit` » Jump to Exploitation
* `asterix --passwords` » Jump to Password Cracking
* `asterix --sniffing` » Jump to Sniffing & Traffic
* `asterix --wireless` » Jump to Wireless Attacks
* `asterix --forensics` » Jump to Digital Forensics
* `asterix --reverse` » Jump to Reverse Engineering (Radare2)
* `asterix --dev` » Jump to Full-Stack Developer Studio
* `asterix --quad` » Launch Instant 4-Way Quad-Grid Workspace

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
Once installed, type `asterix` anytime to launch the cybernetic OS environment.

---

## 📚 Detailed Documentation
* 🌌 [Master Toolchain & Command Encyclopedia](docs/MASTER_TOOLCHAIN_MANUAL.md)
* 🛠️ [Developer Toolchain & Engineering Guide](docs/DEVELOPER_TOOLCHAIN_GUIDE.md)
* 📖 [Multi-Repository GitHub Deployment Guide](docs/MODULAR_GITHUB_GUIDE.md)
* 🖥️ [ASTERIX Terminal, Splitting & Scrolling Guide](docs/ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md)
* 📱 [Android Rooting & Architecture Guide](docs/ROOTING_AND_DEVICE_GUIDE.md)
* 🖼️ [Media & Asset Drop Instructions](assets/README.md)
