# 🌌 ASTERIX OS Master Toolchain & Command Encyclopedia
### Maximum-Tier Reference for Penetration Testing, Reverse Engineering, and Systems Development

**ASTERIX OS** is engineered as an elite Linux distribution unifying the offensive capabilities of BlackArch and Kali with a modern Rust command core, dual-layer persistent storage, and full-stack software development environments.

---

## 🧭 Master Navigation & Fast Aliases

ASTERIX OS provides one-touch CLI aliases to jump directly into any security domain:

| Fast Alias | Direct Command | Domain / Subsystem | Primary Tools Included |
| :--- | :--- | :--- | :--- |
| `as-hub` | `asterix` | **Master Command Matrix** | All 12 subsystems & live telemetry |
| `as-recon` | `asterix --recon` | **01. Recon & OSINT** | Nmap, Masscan, DnsRecon, Whois, Netdiscover |
| `as-web` | `asterix --web-audit` | **02. Web App Warfare** | SQLMap, Gobuster, Nikto, FFUF, Wafw00f |
| `as-exploit`| `asterix --exploit` | **03. Exploitation & Payloads** | Metasploit, SearchSploit, Socat, Netcat |
| `as-crack` | `asterix --passwords` | **04. Password & Hash Auditing** | Hashcat, John The Ripper, Hydra, Crunch |
| `as-sniff` | `asterix --sniffing` | **05. Sniffing & Traffic Control**| Wireshark, TShark, Tcpdump, MacChanger |
| `as-wifi` | `asterix --wireless` | **06. Wireless & Radio Attacks** | Aircrack-ng, Wifite, Reaver, Kismet |
| `as-forensic`| `asterix --forensics` | **07. Forensics & Stego** | Binwalk, Foremost, Steghide, Exiftool |
| `as-rev` | `asterix --reverse` | **08. Reverse Engineering** | Radare2 (R2), GDB, Hexedit, XXD |
| `as-dev` | `asterix --dev` | **09. Full-Stack Dev Studio** | Rust, Go, C/C++, Python, Node, LazyGit |
| `as-quad` | `asterix --quad` | **11. Quad-Grid Tmux Studio** | 4-way balanced cyber split workspace |
| `vault` | `cd /asterix_persistent` | **10. Persistent Storage** | Access encrypted live USB / SDCard storage |

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
