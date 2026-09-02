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

* 🛠️ **Full-Stack Developer & Reverse Engineering Arsenal:**
  - **Languages & Compilers:** Rust (`rustc`, `cargo`), Go (`golang-go`), C/C++ (`gcc`, `g++`, `clang`, `llvm`, `cmake`, `make`), Python 3 (`python3-dev`, `pip`, `ipython`), Node.js (`npm`), GDB, Valgrind, Strace.
  - **Binary & Firmware Analysis:** Radare2 / R2, Binwalk, Hexedit, XXD.
  - **Databases & API Debuggers:** SQLite3, PostgreSQL client, Redis-tools, HTTPie, Socat.
  - **Modern Productivity CLI:** Ripgrep (`rg`), Fd-find (`fd`), Bat (`batcat`), Eza, FZF, Zoxide, LazyGit, JQ, YQ, TLDR, NCDU.
* 💾 **Dual-Layer Data Persistence (`ASTERIX PERSISTENCE`):**
  - **Live USB Mode:** Dedicated `persistence.conf` partition overlay preserving all user files across reboots.
  - **Termux Mobile Mode:** Automated bridge binding `$HOME/asterix_persistent` directly to Android internal storage `/sdcard/ASTERIX_PERSISTENCE`.
* 🦈 **Pre-Configured Security Toolchain:**
  - **Network & Sniffing:** Wireshark, TShark, Tcpdump, Nmap, Masscan, Netcat / Ncat, MacChanger, Socat.
  - **Auditing & Exploitation:** Metasploit Framework (`msfconsole`), SearchSploit, Sqlmap, Hydra, John, Hashcat, Nikto, Gobuster.
* 🪟 **Multi-Terminal Studio & Mouse Scrolling:**
  - Integrated Tmux engine with mouse scroll support, vertical/horizontal splits (<kbd>Ctrl+A</kbd> <kbd>|</kbd> and <kbd>Ctrl+A</kbd> <kbd>-</kbd>), and cyber status bar.
* 🖼️ **Custom Visuals & Media Asset Vault:**
  - Dedicated asset folders (`assets/wallpapers/`, `assets/animations/`, `assets/iso-branding/`) for custom ISO backgrounds and boot videos.

---

## 📁 Repository Layout

```
ASTERIX OS/
├── assets/                       # User Media Vault (Wallpapers, GRUB themes & Boot Videos)
│   ├── wallpapers/               # Desktop & Terminal Backgrounds
│   ├── animations/               # Boot Animation Videos / GIFs
│   └── iso-branding/             # GRUB splash & OS logos
├── desktop-env/                  # Linux Desktop Home Screen & HUD Environment
│   ├── applications/             # Linux .desktop application menu shortcuts
│   ├── conky/                    # Real-time desktop telemetry HUD overlay
│   ├── autostart/                # Auto-load wallpaper & HUD daemon
│   └── install-desktop.sh        # Desktop profile installer
├── engine/                       # Live ISO Build Engine (Debian live-build)
│   ├── build-iso.sh              # ISO compile script
│   ├── packages.list             # Master developer & security package manifest
│   ├── persistence-setup.sh      # USB persistence partition formatter
│   └── Dockerfile                # Isolated container build environment
├── ui-core/                      # Native Rust Cybernetic Visuals & Multiplexer
│   ├── asterix-loader/           # Pure Rust bootloader & control hub
│   │   ├── Cargo.toml
│   │   ├── build.sh
│   │   └── src/main.rs
│   ├── asterix.tmux.conf         # Multi-terminal split & mouse scroll config
│   └── loading_screen.sh         # Pure bash fallback animation
├── termux-mobile/                # Android Mobile PRoot Environment
│   ├── install-termux.sh         # 1-command installer for Termux
│   ├── asterix-termux-init.sh    # Mobile session initializer
│   └── setup-persistence.sh      # Android /sdcard/ storage linker
└── docs/                         # Master Documentation & Architecture Guides
    ├── DEVELOPER_TOOLCHAIN_GUIDE.md # Compilers, Runtimes, R2, GDB & DBs
    ├── MODULAR_GITHUB_GUIDE.md   # Splitting across multiple GitHub accounts
    ├── ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md # Terminal tabs, splits & scrolling
    └── ROOTING_AND_DEVICE_GUIDE.md # Mobile PRoot vs. Hardware Rooted
```

---

## 🚀 Quick Start Guide

### 1. Running the Rust Boot Loader Locally
```bash
cd "ui-core/asterix-loader"
./build.sh
./asterix-loader
```

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
* 🛠️ [Developer Toolchain & Engineering Guide](docs/DEVELOPER_TOOLCHAIN_GUIDE.md)
* 📖 [Multi-Repository GitHub Deployment Guide](docs/MODULAR_GITHUB_GUIDE.md)
* 🖥️ [ASTERIX Terminal, Splitting & Scrolling Guide](docs/ASTERIX_TERMINAL_AND_WORKFLOW_GUIDE.md)
* 📱 [Android Rooting & Architecture Guide](docs/ROOTING_AND_DEVICE_GUIDE.md)
* 🖼️ [Media & Asset Drop Instructions](assets/README.md)
