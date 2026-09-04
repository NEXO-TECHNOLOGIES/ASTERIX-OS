# 🌌 ASTERIX OS Master Toolchain & Command Encyclopedia
### Maximum-Tier Reference for Penetration Testing, Reverse Engineering, and Systems Development

**ASTERIX OS** is engineered as an elite Linux distribution unifying the offensive capabilities of BlackArch and Kali with a modern Rust command core, dual-layer persistent storage, and full-stack software development environments.

---

## ⚡ Universal Command Core: `ax` & `asterix`

ASTERIX OS provides a unified command line tool accessible interchangeably via **`ax`** or **`asterix`**:

### System & Package Management Commands
| Command | Alternate | Description |
| :--- | :--- | :--- |
| `ax update` | `asterix update` | Refresh package indexes, pull git core updates & sync security signatures |
| `ax upgrade` | `asterix upgrade` | Upgrade all OS packages & recompile native C/C++/Go/Asm/Rust toolchains |
| `ax install <pkg>` | `asterix install <pkg>` | Automatically install packages using underlying package manager (apt/pkg) |
| `ax remove <pkg>` | `asterix remove <pkg>` | Uninstall specified packages from the system |
| `ax search <term>` | `asterix search <term>` | Search repository package manifests |
| `ax clean` | `asterix clean` | Purge obsolete dependencies, package cache & temporary build artifacts |
| `ax build` | `asterix build` | Execute master multi-language compilation engine (`build-all.sh`) |
| `ax doctor` | `asterix doctor` | Deep health diagnostics: verify compilers, runtimes, security tools & vault |
| `ax status` | `asterix status` | Display real-time telemetry HUD (Node, IP, Memory, Uptime, Persistence) |
| `ax sysfetch` | `ax neofetch` | High-tech cyberpunk ASCII system architecture and kernel display |
| `ax list` | `asterix list` | Browse the complete repertoire of 80+ specialized commands |
| `ax version` | `asterix version` | Show ASTERIX OS release information and architecture |
| `ax help` | `asterix help` | Display cybernetic command manual |

### Tactical Cyber Warfare, Deception & Anti-Forensics
| Command | Alternate | Description |
| :--- | :--- | :--- |
| `ax matrix` | `asterix matrix` | Stream interactive animated digital rain visualizer (press 'q' to exit) |
| `ax stealth` | `ax ghost` | Ghost Mode: Shreds bash/zsh history, journald, temp files, DNS cache & RAM |
| `ax killswitch` | `ax lockdown` | Emergency network severance: drops all interfaces & sets iptables to DROP |
| `ax killswitch restore` | `ax lockdown off` | Restores standard network connectivity and iptables policies |
| `ax decoy [port]` | `ax honeypot` | Spins up deception listener to catch and log intruder payloads |
| `ax payload <ip> <port>` | `ax revshell` | Generates copy-paste reverse shell one-liners across 9 languages |
| `ax malware-scan [dir]` | `ax webshell` | Scans for obfuscated PHP evals, webshells, hidden binaries & cron persistence |
| `ax tor-status` | `ax tor` | Audits Tor onion routing, verifies SOCKS5 proxy & tests for leaks |
| `ax quote` | `ax ethos` | Dispenses classic hacker philosophy and cyberpunk literature ethos |

### Network & OSINT Reconnaissance Commands
| Command | Alternate | Description |
| :--- | :--- | :--- |
| `ax ip` | `ax myip` | Display LAN IP, WAN public IP, interface statuses, and default gateway |
| `ax ports` | `ax listen` | Audit open listening TCP/UDP sockets and associated processes |
| `ax ping <host>` | `asterix ping <host>` | Cybernetic ICMP latency probe with round-trip metrics |
| `ax scan <target>`| `asterix scan <target>` | Rapid Nmap / netprobe port and service version detector |
| `ax netrecon` | `asterix netrecon` | Automated network discovery, subnet mapping & diagnostic reporter |
| `ax subdomains <domain>` | `ax subenum` | Passive Certificate Transparency subdomain discovery via crt.sh |
| `ax banner-grab <host>` | `ax grab` | Grabs raw daemon banners via direct TCP socket probes |
| `ax wifi-scan` | `ax airmon` | Scans wireless spectrum, SSIDs, BSSIDs, signal power & security modes |
| `ax sniff-live [iface]` | `ax pcap` | Live terminal packet sniffer and protocol radar |
| `ax speedtest` | `ax bandwidth` | Tests downstream bandwidth and round-trip ping latency |
| `ax mac [iface]` | `asterix mac` | Inspect or randomize/spoof interface MAC address with macchanger |
| `ax webrecon <url>` | `asterix webrecon` | High-performance Go-based web reconnaissance engine |
| `ax dns <domain>` | `ax dig` | Resolves DNS records (A, MX, TXT) with latency profiling |
| `ax whois <domain>` | `asterix whois` | Queries domain registrar and ASN allocation details |
| `ax traceroute <ip>`| `ax tracepath` | Maps internet routing hops |

### Security, Cryptography & Forensics Commands
| Command | Alternate | Description |
| :--- | :--- | :--- |
| `ax encrypt <file>` | `ax enc` | Encrypts file using AES-256-CBC with PBKDF2 key derivation |
| `ax decrypt <file>` | `ax dec` | Decrypts AES-256-CBC encrypted `.axenc` files |
| `ax hash <file>` | `asterix hash <file>` | Multi-algorithm checksum engine (MD5, SHA-1, SHA-256, SHA-512) |
| `ax shred <file>`| `asterix shred <file>` | Military-grade cryptographic multi-pass secure file obliteration |
| `ax exif <file> [--strip]` | `ax metadata` | Forensics metadata viewer and instant privacy metadata wiper |
| `ax rootkit` | `asterix rootkit` | Scan for anomalous kernel modules, stealth hooks, and hidden procs |
| `ax docker-audit` | `ax container` | Audits Docker daemon, container escapes, socket permissions & privileges |
| `ax trace [pid]` | `ax proctrace` | Live syscall monitor and process execution tracer |
| `ax vuln [target]`| `asterix vuln` | Cyber vulnerability assessment and service exposure scanner |
| `ax packet` | `asterix packet` | Raw packet crafting, protocol fuzzing, and injection studio |
| `ax logwatch` | `asterix logwatch` | Real-time security log and auth anomaly watcher |
| `ax firewall` | `ax ufw` | Inspects active iptables / nftables packet filtering rules |
| `ax audit` | `ax hardening` | Automated system security posture and hardening audit |
| `ax suid` | `asterix suid` | Scans filesystem for suspicious SUID/SGID root binaries |
| `ax certs <host>` | `ax ssl` | Displays remote SSL/TLS certificate chain and expiration dates |
| `ax genpass [len]`| `ax password` | Generates cryptographically secure high-entropy passwords |
| `ax entropy <file>`| `asterix entropy`| Measures Shannon entropy to detect packed or encrypted malware |
| `ax qr <text|url>` | `ax qrcode` | Renders terminal ASCII QR code for payloads, URLs or configs |

### Vault, Workspace & Desktop HUD Commands
| Command | Alternate | Description |
| :--- | :--- | :--- |
| `ax backup` | `asterix backup` | Sync and compress persistent vault to Discord and Cloud Panel |
| `ax loot` | `asterix loot` | Browse captured hashes, scan reports, PCAP captures & loot files |
| `ax scaffold <lang> <name>` | `ax new` | Scaffolds Rust, C, C++, Go, Python, or Node developer workspace |
| `ax mem` | `ax ram` | Physical memory profile and ring buffer inspector |
| `ax cpu` | `ax cpuinfo` | Inspects CPU architecture, core count and load averages |
| `ax disk` | `ax df` | Displays disk partition mounts and free storage capacity |
| `ax ps` | `ax procs` | Lists active processes sorted by CPU and memory utilization |
| `ax benchmark` | `ax bench` | Native CPU mathematics and memory benchmarking |
| `ax wallpaper` | `ax wp` | Instantly cycle desktop cyberpunk wallpaper from assets vault |
| `ax hud [on\|off\|restart]` | `asterix hud` | Control Conky real-time desktop telemetry HUD overlay |
| `ax top` | `asterix top` | Launch Btop / Htop high-tech terminal resource monitor |
| `ax compress <target>` | `ax tar` | Creates compressed `.tar.gz` archive |
| `ax extract <archive>` | `ax untar` | Universal archive extractor (tar.gz, tar.bz2, zip, tar.xz) |
| `ax find-large [dir]` | `ax bigfiles` | Identifies top 15 largest disk-consuming files |

### ⚡ Universal Omni-Dispatcher (Thousands of System Tools)
Any command not in the table above is automatically passed through the **Omni-Dispatcher** (`dynamic_system_exec`). If the command exists on the operating system, it is executed within the cybernetic environment with timing, status codes, and security telemetry! Examples:
* `ax nmap -sV -sC 192.168.1.1`
* `ax curl -IL https://example.com`
* `ax git status`
* `ax hydra -l admin -P wordlist.txt 192.168.1.50 ssh`
* `ax john --wordlist=rockyou.txt hashes.txt`

### Subsystem Direct Launchers
| Fast Alias | Direct CLI Command | Subsystem Domain | Primary Tools Included |
| :--- | :--- | :--- | :--- |
| `as-hub` | `ax` or `asterix` | **Master Command Matrix** | All 12 subsystems & live telemetry |
| `as-recon` | `ax recon` | **01. Recon & OSINT** | Nmap, Masscan, DnsRecon, Whois, Netdiscover |
| `as-web` | `ax web` | **02. Web App Warfare** | SQLMap, Gobuster, Nikto, FFUF, Wafw00f |
| `as-exploit`| `ax exploit` | **03. Exploitation & Payloads** | Metasploit, SearchSploit, Socat, Netcat |
| `as-crack` | `ax crack` | **04. Password & Hash Auditing** | Hashcat, John The Ripper, Hydra, Crunch |
| `as-sniff` | `ax sniff` | **05. Sniffing & Traffic Control**| Wireshark, TShark, Tcpdump, MacChanger |
| `as-wifi` | `ax wifi` | **06. Wireless & Radio Attacks** | Aircrack-ng, Wifite, Reaver, Kismet |
| `as-forensic`| `ax forensics` | **07. Forensics & Stego** | Binwalk, Foremost, Steghide, Exiftool |
| `as-rev` | `ax rev` | **08. Reverse Engineering** | Radare2 (R2), GDB, Hexedit, XXD |
| `as-dev` | `ax dev` | **09. Full-Stack Dev Studio** | Rust, Go, C/C++, Python, Node, LazyGit |
| `as-quad` | `ax quad` | **11. Quad-Grid Tmux Studio** | 4-way balanced cyber split workspace |
| `vault` | `ax vault` | **10. Persistent Storage** | Access encrypted live USB / SDCard storage |
| `as-update` | `ax update` | **System Maintenance** | Synchronize package indexes and rules |
| `as-upgrade`| `ax upgrade` | **System Maintenance** | Upgrade system packages and tool suites |

---

## 🪟 Ultimate Terminal & Tmux Quad-Grid Workflow

```
┌───────────────────────────────────────┬───────────────────────────────────────┐
│ [1] PACKET SNIFFER (TShark / Tcpdump) │ [2] RECON / SCANNER (Nmap / Masscan)  │
├───────────────────────────────────────┼───────────────────────────────────────┤
│ [3] SUPERUSER SHELL (Zsh / Bash Prompt)│ [4] RESOURCE MONITOR (Btop / Sensors) │
└───────────────────────────────────────┴───────────────────────────────────────┘
```

### Essential Keybindings:
* **Prefix Key:** <kbd>Ctrl+A</kbd>
* **Launch 4-Way Quad Grid:** Type `as-quad` or press <kbd>Ctrl+A</kbd> <kbd>q</kbd>
* **Mouse Scroll:** Enabled up to **100,000 lines** (scroll wheel anywhere)
* **Vertical Split:** <kbd>Ctrl+A</kbd> <kbd>|</kbd>
* **Horizontal Split:** <kbd>Ctrl+A</kbd> <kbd>-</kbd>
* **Broadcast Typing to All Panes (Sync):** <kbd>Ctrl+A</kbd> <kbd>y</kbd>
* **Switch Panes Fast:** <kbd>Alt+Arrow Keys</kbd> (No prefix needed) or click pane
* **New Tab / Window:** <kbd>Ctrl+A</kbd> <kbd>c</kbd>

---

## ⚡ Supercharged Cyber Shell Environment

Both Bash and Zsh are pre-configured with:
* **FZF Fuzzy History Search:** Press <kbd>Ctrl+R</kbd> to interactively search command history.
* **FZF Fuzzy File Search:** Press <kbd>Ctrl+T</kbd> to locate any file in the filesystem.
* **FZF Directory Jumper:** Press <kbd>Alt+C</kbd> to fuzzy jump into subdirectories.
* **Smart Directory Jump:** `z <directory_keyword>` (powered by `zoxide`).
* **Modern File Listings:** `ls` uses `eza` with icons and git integration; `cat` uses `batcat` with line numbers and syntax highlighting.
* **One-Step Compilers:**
  - `run-rs <file.rs>`: Instant Rust compilation and execution
  - `run-c <file.c>`: Instant C/C++ compilation and execution
  - `run-py <file.py>`: Python 3 execution

---

## 💾 Persistent Storage Architecture

All data, custom scripts, and tool repos saved in `/asterix_persistent/` remain permanent:
* **On Live USB (PC/VM):** Stored directly on the encrypted ext4 partition labeled `persistence`.
* **On Mobile (Android Termux):** Bridged directly to `/sdcard/ASTERIX_PERSISTENCE`.
