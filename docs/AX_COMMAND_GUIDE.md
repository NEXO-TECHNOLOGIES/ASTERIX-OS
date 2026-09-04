# 🌌 ASTERIX OS: Master `ax` / `asterix` Command Architecture & Operational Guide
### Comprehensive Reference for the Cybernetic Operating Engine & Omni-Dispatcher

---

## 📑 Table of Contents
1. [Architectural Overview](#1-architectural-overview)
2. [Dual-Core Execution Pipeline](#2-dual-core-execution-pipeline)
3. [Multi-Environment Awareness (Live ISO, Desktop & Termux)](#3-multi-environment-awareness)
4. [The Universal Omni-Dispatcher (Infinite System Commands)](#4-the-universal-omni-dispatcher)
5. [Complete Command Encyclopedia & Usage Patterns](#5-complete-command-encyclopedia--usage-patterns)
   - [Tactical Cyber Warfare, Deception & Anti-Forensics](#51-tactical-cyber-warfare-deception--anti-forensics)
   - [Network & OSINT Reconnaissance](#52-network--osint-reconnaissance)
   - [Security, Cryptography & Forensics](#53-security-cryptography--forensics)
   - [Deep Core Root & Kernel Hardening](#54-deep-core-root--kernel-hardening)
   - [System Hardware, Workspace & Desktop HUD](#55-system-hardware-workspace--desktop-hud)
   - [Direct Subsystem Jumpers & Interactive Hub](#56-direct-subsystem-jumpers--interactive-hub)
6. [Shell Integration & Velocity Shortcuts (`ax-*`)](#6-shell-integration--velocity-shortcuts)
7. [Diagnostics, Health Audits & Troubleshooting](#7-diagnostics-health-audits--troubleshooting)

---

## 1. Architectural Overview

The **`ax`** (and its canonical alias **`asterix`**) command interface is the central nervous system of ASTERIX OS. It unifies:
* **Interactive Rust TUI Command Center**: High-velocity terminal menus, ANSI telemetry HUDs, quad-split tmux studio triggers, and system maintenance.
* **POSIX Master Shell Engine**: High-velocity command execution, tactical cyber tools, anti-forensics routines, encryption, and system controls.
* **Universal Omni-Dispatcher**: A dynamic fallback engine that transparently wraps, executes, and audits **any installed Linux utility** (Nmap, Hydra, Curl, Git, etc.).

```
                         ┌──────────────────────────────────┐
                         │   User invokes `ax` / `asterix`  │
                         └─────────────────┬────────────────┘
                                           │
                        Is there an argument passed?
                                  /         \
                             [No]             [Yes]
                              /                 \
            ┌──────────────────────┐        ┌──────────────────────────────────┐
            │ Launch Rust TUI Hub  │        │ Match Built-In CLI Subcommand    │
            │  (`asterix-loader`)  │        │ (`bin/ax` + `main.rs`)           │
            └──────────────────────┘        └─────────────────┬────────────────┘
                                                              │
                                                   Is command recognized?
                                                     /              \
                                                [Yes]                [No]
                                                 /                     \
                             ┌───────────────────────┐       ┌───────────────────────┐
                             │ Execute Native Subcmd │       │ Universal Omni-       │
                             │ (C/C++/Go/Rust/Shell) │       │ Dispatcher (`$PATH`)  │
                             └───────────────────────┘       └───────────────────────┘
```

Both `ax` and `asterix` are symlinked to each other (`/usr/local/bin/ax` -> `/usr/local/bin/asterix`), ensuring identical syntax and behavior across all environments.

---

## 2. Dual-Core Execution Pipeline

ASTERIX OS utilizes a bidirectional bridge between its compiled Rust core and POSIX shell scripts:

### A. The Compiled Rust Hub (`ui-core/asterix-loader/src/main.rs`)
* When executed with **no arguments** (`ax` or `asterix`), the Rust core runs the boot sequence and presents the primary 16-item Command & Control matrix.
* When executed with **subsystem flags** (e.g. `ax recon` or `ax --recon`), the Rust core instantly bypasses the main menu and launches the targeted domain-specific sub-menu.
* For all other subcommands, Rust uses `dispatch_ax_tool(&args[1..])` to route the execution to the POSIX engine.

### B. The POSIX Master Script (`bin/ax`)
* Serves as the primary execution engine.
* Parses arguments with a high-performance `case "$SUBCOMMAND" in` dispatcher.
* Implements specialized native routines for cyber warfare, anti-forensics, crypto, hardware telemetry, and file manipulation.
* Contains path resolvers (`find_asterix_root`, `find_helper_script`, `run_native_bin`) to locate compiled C/C++/Go binaries and helper scripts whether installed in `/etc/asterix`, run from repository source, or executing in a live chroot.

---

## 3. Multi-Environment Awareness

The command automatically probes and adapts to its runtime environment:

### Package Manager Auto-Detection (`detect_pkg_manager`)
```bash
detect_pkg_manager() {
    if [ -n "$PREFIX" ] && command -v pkg >/dev/null 2>&1; then
        echo "termux"
    elif command -v apt-get >/dev/null 2>&1; then
        echo "apt"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v apk >/dev/null 2>&1; then
        echo "apk"
    fi
}
```
* On Debian/Ubuntu/Kali/Live ISO: Uses `apt-get`.
* On Android Termux: Uses `pkg`.
* On Arch Linux: Uses `pacman`.
* On Fedora: Uses `dnf`.

### Intelligent Privilege Elevation (`run_as_root`)
* Automatically checks `id -u`.
* If running as non-root, it routes through `sudo` (Desktop/Live ISO) or `tsu` (Rooted Android Termux).
* If running inside a PRoot container or already root, it executes directly without overhead.

---

## 4. The Universal Omni-Dispatcher

The **Omni-Dispatcher** (`dynamic_system_exec`) is the mechanism that gives `ax` the power of **thousands of commands**:

```bash
dynamic_system_exec() {
    local cmd="$1"
    shift || true
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "${C_CYAN}[*] ASTERIX Omni-Exec: ${C_WHITE}${cmd} ${*}${C_RESET}"
        "$cmd" "$@"
        local rc=$?
        if [ $rc -eq 0 ]; then
            echo -e "\n${C_GREEN}[✔] ${cmd} finished successfully.${C_RESET}"
        else
            echo -e "\n${C_YELLOW}[!] ${cmd} exited with status ${rc}.${C_RESET}"
        fi
        return $rc
    else
        echo -e "${C_RED}[!] Command '${cmd}' not recognized in ASTERIX OS.${C_RESET}"
        echo -e "${C_YELLOW}[*] Try installing it via: ${C_WHITE}ax install ${cmd}${C_RESET}"
        return 127
    fi
}
```

### How to use the Omni-Dispatcher
You can prepend `ax` to **any system command**. For example:
* `ax nmap -sV -sC 192.168.1.1`
* `ax curl -IL https://target.internal`
* `ax git log -n 5 --oneline`
* `ax hydra -l admin -P /usr/share/wordlists/rockyou.txt 10.0.0.1 ssh`
* `ax tcpdump -i eth0 -nn -c 20`

**Benefits:**
1. **Unified Command Identity**: All system interaction stems from `ax`.
2. **Audit & Status Telemetry**: Shows execution start banner, command line arguments, and return code status.
3. **Smart Suggestions**: If the tool is missing, `ax` prompts you with the exact command to install it (`ax install <tool>`).

---

## 5. Complete Command Encyclopedia & Usage Patterns

### 5.1 Tactical Cyber Warfare, Deception & Anti-Forensics

#### `ax matrix`
* **Purpose**: Terminal animated digital rain visualizer streaming Katakana and ASCII glyphs with phosphor heads and fading trails.
* **Usage**: `ax matrix`
* **Controls**: Press `q` or `Ctrl+C` to cleanly restore terminal cursor and exit.

#### `ax stealth` (alias: `ax ghost`)
* **Purpose**: Full anti-forensics lockdown.
* **Actions Performed**:
  1. Purges volatile directories: `/tmp/*`, `/var/tmp/*`, `/dev/shm/*`.
  2. Cryptographically shreds `~/.bash_history`, `~/.zsh_history`, and sets `HISTFILE=/dev/null`.
  3. Vacuums and purges `journalctl` logs.
  4. Flushes system DNS caches (`resolvectl` / `systemd-resolve`).
  5. Clears X11 / Wayland clipboard buffers (`xclip`).
  6. Drops Linux RAM pagecaches (`echo 3 > /proc/sys/vm/drop_caches`).
* **Usage**: `ax stealth`

#### `ax killswitch [restore]` (alias: `ax lockdown`)
* **Purpose**: Emergency physical and network isolation.
* **Actions**:
  * Shuts down all non-loopback network interfaces (`ip link set <iface> down`, `nmcli networking off`).
  * Drops all incoming, forwarding, and outgoing packets (`iptables -P INPUT/FORWARD/OUTPUT DROP`).
  * Terminates active remote SSH sessions.
* **Usage**:
  * Engage lockdown: `ax killswitch`
  * Restore network stack: `ax killswitch restore`

#### `ax decoy [port]` (alias: `ax honeypot`)
* **Purpose**: Instant intrusion detection listener.
* **Mechanism**: Binds an active TCP socket (default: 8080, or 22, 80, 445). Traps incoming scans or exploits, returns realistic server banners, logs the remote IP, timestamp, and payload to `./loot/decoy-<port>.log`, and alerts the terminal in bold red.
* **Usage**: `ax decoy 22` or `ax decoy 8080`

#### `ax payload <ip> <port>` (alias: `ax revshell`)
* **Purpose**: Generates copy-paste reverse shell one-liners across 9 target languages.
* **Supported Runtimes**: Bash (Interactive & /dev/tcp), Python3 (PTY spawned), Netcat (traditional & OpenBSD mkfifo), Socat (TTY interactive), PowerShell (Windows target), PHP, and Node.js.
* **Usage**: `ax payload 10.10.14.5 4444`

#### `ax malware-scan [dir]` (alias: `ax webshell`)
* **Purpose**: Rapid tactical scanner for webshells and persistence.
* **Checks**:
  1. Base64 eval loaders (`eval(base64_decode(...))`).
  2. Raw execution entry points (`system($_POST)`, `shell_exec`).
  3. World-writable hidden binaries.
  4. Local user and system crontabs.
* **Usage**: `ax malware-scan /var/www/html`

#### `ax tor-status` (alias: `ax tor`, `ax onion`)
* **Purpose**: Audits Tor daemon state and routes a test request through the local SOCKS5 proxy (`127.0.0.1:9050`) to `check.torproject.org`. Flags whether traffic is successfully onion-routed or if direct IP leaks exist.
* **Usage**: `ax tor-status`

#### `ax quote` (alias: `ax ethos`)
* **Purpose**: Displays hacker philosophy and cyberpunk literary quotes (William Gibson, Neal Stephenson, Phrack).
* **Usage**: `ax quote`

---

### 5.2 Network & OSINT Reconnaissance

| Command | Usage | Description |
| :--- | :--- | :--- |
| **`ax ip`** | `ax ip` | Shows LAN IP, default gateway, public IP (via API), and interfaces. |
| **`ax ports`** | `ax ports` | Audits open listening sockets (`ss -tulpn` or `netstat`). |
| **`ax ping <host>`** | `ax ping 1.1.1.1` | Cybernetic ICMP latency probe with round-trip metrics. |
| **`ax scan <target>`** | `ax scan 192.168.1.50` | Port and service version scan via Nmap or native netprobe. |
| **`ax netrecon [subnet]`** | `ax netrecon 192.168.1.0/24` | Network discovery, ARP sweeps, and diagnostic report. |
| **`ax subdomains <domain>`**| `ax subdomains site.com` | Queries Certificate Transparency (`crt.sh`) for subdomains and resolves IPs. |
| **`ax banner-grab <host> [port]`** | `ax banner-grab 10.0.0.1 22` | Raw socket daemon banner grabber. |
| **`ax wifi-scan`** | `ax wifi-scan` | Scans wireless spectrum, SSIDs, BSSIDs, dBm signal, and encryption. |
| **`ax sniff-live [iface]`**| `ax sniff-live wlan0` | Terminal packet sniffer capturing live frames with TCPDump. |
| **`ax speedtest`** | `ax speedtest` | Benchmarks downstream throughput and round-trip ping latency. |
| **`ax mac [iface]`** | `ax mac eth0` | Inspects MAC address or randomizes it via `macchanger`. |
| **`ax webrecon <url>`** | `ax webrecon target.com` | High-speed Go-based web reconnaissance engine. |
| **`ax dns <domain>`** | `ax dns google.com` | Resolves A, MX, and TXT records with timing stats. |
| **`ax whois <domain>`** | `ax whois target.com` | Queries registrar and ASN allocation details. |
| **`ax traceroute <ip>`** | `ax traceroute 8.8.8.8` | Maps network routing hops and latency. |
| **`ax arp`** | `ax arp` | Dumps local ARP table. |
| **`ax connections`** | `ax connections` | Lists active established connections and socket endpoints. |
| **`ax traffic`** | `ax traffic` | Real-time network interface RX/TX bytes and packet telemetry. |

---

### 5.3 Security, Cryptography & Forensics

#### `ax encrypt <file>` / `ax decrypt <file>`
* **Algorithm**: AES-256-CBC with PBKDF2 salted key derivation via OpenSSL.
* **Output**: Produces `<file>.axenc` on encryption, extracts back to original file on decryption.
* **Usage**:
  * Encrypt: `ax encrypt confidential.pdf`
  * Decrypt: `ax decrypt confidential.pdf.axenc`

#### `ax exif <file> [--strip]` (alias: `ax metadata`)
* **Purpose**: Forensics metadata extraction and privacy sanitization.
* **Inspection**: Extracts camera models, GPS latitude/longitude, software versions, creation timestamps.
* **Sanitization**: Passing `--strip` permanently removes all metadata from the file.
* **Usage**:
  * Inspect: `ax exif photo.jpg`
  * Sanitize: `ax exif photo.jpg --strip`

#### `ax hash <file|string>`
* **Algorithms**: Computes MD5, SHA-1, SHA-256, and SHA-512 simultaneously.
* **Usage**: `ax hash binary.bin` or `ax hash "cybernetic-password"`

#### `ax shred <file>`
* **Purpose**: Cryptographic multi-pass secure file obliteration (overwriting with random patterns before unlinking).
* **Usage**: `ax shred secret_keys.txt`

#### `ax docker-audit` (alias: `ax container`)
* **Purpose**: Inspects Docker/Podman engines, checks for exposed `/var/run/docker.sock` privilege escalation risks, lists active containers, and verifies whether the current session is executing inside a container.
* **Usage**: `ax docker-audit`

#### `ax firewall` (alias: `ax ufw`, `ax iptables`)
* **Purpose**: Displays active iptables and ufw filtering rules, NAT policies, and open ports.
* **Usage**: `ax firewall`

#### `ax audit` (alias: `ax hardening`)
* **Purpose**: Automated Linux security audit. Checks file permissions, open ports, SSH root login policies, and password hashing configurations.
* **Usage**: `ax audit`

#### `ax suid`
* **Purpose**: Scans the filesystem for binaries with the SUID (`-perm -4000`) or SGID bit set, identifying potential local privilege escalation vectors.
* **Usage**: `ax suid`

#### `ax certs <host>` (alias: `ax ssl`)
* **Purpose**: Connects to remote TLS endpoints, dumps the SSL certificate chain, issuer, validity period, and SAN (Subject Alternative Names).
* **Usage**: `ax certs api.github.com`

#### `ax genpass [len]`
* **Purpose**: Generates high-entropy cryptographic passwords with letters, numbers, and symbols (default: 24 characters).
* **Usage**: `ax genpass 32`

#### `ax entropy <file>`
* **Purpose**: Calculates Shannon entropy (0.0 to 8.0) of a file to detect packed binaries, obfuscated shellcode, or encrypted ransomware payloads.
* **Usage**: `ax entropy suspect.exe`

#### `ax qr <text|url>` (alias: `ax qrcode`)
* **Purpose**: Renders a high-contrast UTF-8 ASCII QR code in the terminal.
* **Usage**: `ax qr "WIFI:S:MySecretNet;T:WPA;P:Pass1234;;"` or `ax qr "https://asterix-os.org"`

#### `ax kernel-hardening` (alias: `ax sysctl-check`)
* **Purpose**: Deep Linux kernel security parameter audit. Checks ASLR (`kernel.randomize_va_space`), ptrace scope restriction, SYN flood cookies, ICMP redirect prevention, IP spoof filtering (`rp_filter`), and dmesg/kptr restrictions. Computes a percentage security score.
* **Usage**: `ax kernel-hardening`

#### `ax fim-init` & `ax fim-check` (File Integrity Monitoring Core)
* **Purpose**: Cryptographic baseline snapshot and tamper detection for `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`, `/etc/pam.d/`, `/bin/bash`, and critical binaries.
* **Usage**:
  * Take baseline: `ax fim-init`
  * Verify system integrity: `ax fim-check`

#### `ax auth-audit`
* **Purpose**: Authentication and intrusion anomaly correlator. Scans `/var/log/auth.log` or systemd journal for top attacking IP addresses, failed passwords, and sudo elevation events.
* **Usage**: `ax auth-audit`

#### `ax git-secrets` (alias: `ax secrets`)
* **Purpose**: Scans code repositories for committed private keys, AWS access keys, API tokens, and `.env` credential files.
* **Usage**: `ax git-secrets [dir]`

#### `ax cis-audit` (alias: `ax compliance`)
* **Purpose**: Validates system configuration against CIS Linux benchmarks (/etc/shadow permissions, empty passwords, SSH root login policies, legacy plaintext daemons).
* **Usage**: `ax cis-audit`

#### `ax tls-audit <host> [port]` (alias: `ax cert-check`)
* **Purpose**: Deep TLS certificate audit: extracts subject, issuer, SAN domains, and expiration countdown.
* **Usage**: `ax tls-audit github.com 443`

---

### 5.4 Deep Core Root & Kernel Hardening

| Command | Usage | Description |
| :--- | :--- | :--- |
| **`ax kmod-audit`** | `ax kmod-audit` | Decodes kernel taint bitmask, checks module loading locks & unindexed LKMs. |
| **`ax deleted-procs`** | `ax deleted-procs` | Detects stealth ghost processes executing from unlinked binaries (`/proc/*/exe`). |
| **`ax cap-audit`** | `ax cap-audit` | Audits high-privilege file capabilities (`cap_setuid`, `cap_sys_admin`) and process bounding sets. |
| **`ax ebpf-audit`** | `ax ebpf-audit` | Audits loaded eBPF programs, maps, and unprivileged BPF disable state. |
| **`ax root-persistence`** | `ax root-persistence` | Scans `/etc/ld.so.preload`, systemd generators, cron hooks, and PAM triggers. |
| **`ax seccomp-audit`** | `ax seccomp-audit` | Audits Seccomp-BPF sandbox isolation across all running processes. |
| **`ax tty-snoop`** | `ax tty-snoop` | Checks TIOCSTI ioctl injection prevention and audits active pseudo-terminals. |
| **`ax kexec-lockdown`** | `ax kexec-lockdown` | Audits Linux kernel lockdown mode (`integrity`/`confidentiality`) and kexec status. |
| **`ax mem-protect`** | `ax mem-protect` | Verifies hardware exploit mitigations: SMEP, SMAP, NX/XD, PTI, and sysfs vulnerabilities. |
| **`ax mount-hardening`** | `ax mount-hardening` | Checks `/tmp`, `/dev/shm`, and `/var/tmp` for `nosuid`, `nodev`, and `noexec` flags. |
| **`ax ipc-audit`** | `ax ipc-audit` | Audits shared memory segments, message queues, and semaphores (`ipcs`). |
| **`ax dmesg-exploit`** | `ax dmesg-exploit` | Scans kernel ring buffer for general protection faults, stack canaries, and ROP/slab corruptions. |
| **`ax root-jail`** | `ax root-jail` | Instantly spawns an ephemeral zero-privilege namespace isolation sandbox via `unshare`. |
| **`ax core-dump-audit`** | `ax core-dump-audit` | Audits `core_pattern` handlers and `fs.suid_dumpable` memory leakage risks. |

---

### 5.5 System Hardware, Workspace & Desktop HUD

| Command | Usage | Description |
| :--- | :--- | :--- |
| **`ax sysfetch`** | `ax sysfetch` | Cyberpunk ASCII system information display (Kernel, Host, Memory, Uptime, Shell). |
| **`ax cpu`** | `ax cpu` | Inspects CPU model, core architecture, frequencies, and load averages. |
| **`ax disk`** | `ax disk` | Shows partition mounts, total capacity, used space, and free sectors. |
| **`ax mem`** | `ax mem` | Displays total/used/free RAM and swap buffers. |
| **`ax ps`** | `ax ps` | Lists active processes sorted by CPU and memory consumption. |
| **`ax benchmark`** | `ax benchmark` | Runs native CPU mathematics benchmark. |
| **`ax service <name> <action>`** | `ax service ssh restart` | System service manager wrapper (`systemctl`). |
| **`ax backup`** | `ax backup` | Syncs and compresses persistent vault data to Discord and Cloud Panel. |
| **`ax loot`** | `ax loot` | Explores captured credentials, scan reports, and exfiltrated files. |
| **`ax scaffold <lang> <name>`** | `ax scaffold rust cyber_app` | Instantly scaffolds a project in Rust, C, C++, Go, Python, or Node.js. |
| **`ax wallpaper [random]`** | `ax wallpaper` | Cycles desktop wallpaper from the assets vault. |
| **`ax hud [on\|off\|restart]`** | `ax hud restart` | Toggles or restarts the Conky real-time desktop HUD overlay. |
| **`ax top`** | `ax top` | Launches Btop / Htop cyber resource monitor. |
| **`ax compress <target>`** | `ax compress project/` | Archives a directory into `.tar.gz`. |
| **`ax extract <archive>`** | `ax extract data.tar.gz` | Universal archive extractor (`tar.gz`, `tar.bz2`, `tar.xz`, `zip`). |
| **`ax find-large [dir]`** | `ax find-large /var` | Identifies the top 15 largest disk-consuming files. |
| **`ax pstree`** | `ax pstree` | Process hierarchy and execution anomaly tree. |
| **`ax env-audit`** | `ax env-audit` | Runtime PATH hygiene and sensitive environment variable audit. |

---

### 5.5 Direct Subsystem Jumpers & Interactive Hub

Executing `ax` with a subsystem name instantly launches that specialized operational environment:

* **`ax recon`**: 01. Reconnaissance & OSINT (Nmap, Masscan, Whois, Netdiscover)
* **`ax web`**: 02. Web Application Warfare (SQLMap, Gobuster, Nikto, FFUF)
* **`ax exploit`**: 03. Exploitation & Payloads (Metasploit, SearchSploit, Socat)
* **`ax crack`**: 04. Password & Hash Auditing (Hashcat, John The Ripper, Hydra)
* **`ax sniff`**: 05. Sniffing & Traffic Control (Wireshark, TShark, Tcpdump)
* **`ax wifi`**: 06. Wireless Attacks (Aircrack-ng, Wifite, Reaver)
* **`ax forensics`**: 07. Digital Forensics & Stego (Binwalk, Foremost, Steghide)
* **`ax rev`**: 08. Reverse Engineering (Radare2, GDB, Hexedit)
* **`ax dev`**: 09. Full-Stack Developer Studio (Rust, Go, C/C++, Python)
* **`ax quad`**: 11. Instant 4-Way Tmux Quad-Grid Cyber Studio
* **`ax portal`**: 12. Web Operations Media Portal (port 7777)
* **`ax discord`**: Discord Remote Vault Bridge & Notifications
* **`ax cloud`**: Cloud Compute Worker Daemon
* **`ax vault`**: Jump directly into `/asterix_persistent` encrypted vault
* **`ax shell`**: Spawns an enhanced cyber shell with full ASTERIX environment

**Executing `ax` without arguments launches the full interactive Rust Command Center.**

---

## 6. Shell Integration & Velocity Shortcuts

ASTERIX OS defines one-touch aliases inside `ui-core/asterix-shell-env.sh`:

```bash
# Tactical Cyber
alias ax-matrix='ax matrix'
alias ax-stealth='ax stealth'
alias ax-killswitch='ax killswitch'
alias ax-decoy='ax decoy'
alias ax-payload='ax payload'
alias ax-malware='ax malware-scan'
alias ax-tor='ax tor-status'

# Network & OSINT
alias ax-ip='ax ip'
alias ax-ports='ax ports'
alias ax-subdomains='ax subdomains'
alias ax-banner='ax banner-grab'
alias ax-wifi='ax wifi-scan'
alias ax-sniff='ax sniff-live'
alias ax-speedtest='ax speedtest'

# Security & Crypto
alias ax-encrypt='ax encrypt'
alias ax-decrypt='ax decrypt'
alias ax-docker='ax docker-audit'
alias ax-exif='ax exif'
alias ax-qr='ax qr'

# System
alias ax-sysfetch='ax sysfetch'
alias ax-doctor='ax doctor'
alias ax-update='ax update'
alias ax-upgrade='ax upgrade'
```

---

## 7. Diagnostics, Health Audits & Troubleshooting

### Running System Diagnostics
To verify your toolchains, compilers, pentesting utilities, and storage mounts:
```bash
ax doctor
```
Checks:
* Compiler toolchains: `rustc`, `cargo`, `gcc`, `g++`, `go`, `python3`, `nasm`.
* Security tools: `nmap`, `radare2`, `gdb`, `tmux`, `curl`, `tcpdump`.
* Persistence mount status: checks `/asterix_persistent`.

### Refreshing Packages & Toolchains
```bash
ax update     # Pulls new security rules, Exploit-DB, and git repositories
ax upgrade    # Upgrades packages and recompiles all native C/C++/Go/Rust suites
```

### Cache & Artifact Purging
```bash
ax clean      # Frees disk space by removing unused packages and build artifacts
```
