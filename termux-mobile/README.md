# ASTERIX OS - Termux Mobile Subsystem

High-Performance Rootless Cybernetic Defense & Security Engineering Suite for Android.

---

## 1. Executive Overview & Architecture

ASTERIX OS Mobile delivers a dual-tier rootless operating environment optimized for Android devices running Termux (Android 7.0 through Android 16+). It eliminates common mobile constraints such as random process terminations, battery-saving sleep interruptions, permission denials, and broken glibc dependencies.

```
+-------------------------------------------------------------------------+
|                       ANDROID HOST PLATFORM                             |
|           (Linux Kernel + Android Framework + Hardware Sensors)         |
+------------------------------------+------------------------------------+
                                     |
    +--------------------------------+--------------------------------+
    |                                                                 |
    v                                                                 v
+-----------------------------+                   +-----------------------------+
|    TIER 1: TERMUX NATIVE    |                   |   TIER 2: DEBIAN ROOTLESS   |
|   (Direct Bionic / ARM64)   |                   |    (PRoot Isolated Sandbox) |
+-----------------------------+                   +-----------------------------+
| * Zero-overhead CLI utils   |                   | * Full GNU glibc toolchain  |
| * Native Rust cyber engines | <--- Shared ----> | * Full APT package manager  |
| * Battery, thermal & net HUD|      Storage      | * Metapackages: asterix-core|
| * CPU Wake-Lock manager     |      Vault        | * Nmap, tshark, tcpdump     |
| * Dispatcher: `bin/ax`      |                   | * Multi-DNS failover resolver|
+-----------------------------+                   +-----------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                   TIER 3: RESILIENT PERSISTENT VAULT                    |
|                      (~/asterix_persistent/)                            |
|  projects/  scans/  loot/  captures/  reports/  notes/  scripts/  etc.  |
+-------------------------------------------------------------------------+
```

### Architectural Tiers

1. **Tier 1: Termux Native Execution**
   Direct execution on Android Bionic libc without emulation or container layers. Executes native Rust engines (`asterix-net-sentinel`, `asterix-bin-inspector`, `asterix-crypto-core`), low-level network audits, and mobile telemetry with zero latency.

2. **Tier 2: Debian Rootless PRoot Subsystem**
   Rootless GNU/Linux environment managed via `proot-distro`. Pre-configured with hardened multi-DNS resolvers, APT sandbox permission patches, daemon suppression, and ASTERIX metapackages.

3. **Tier 3: Resilient Persistent Vault**
   Located at `~/asterix_persistent/` with automated fallback to `~/.asterix_storage`. Houses 10 dedicated operational mission directories that persist across Termux sessions, updates, and environment re-installations.

---

## 2. Quick-Start & Installation

### Option A: 1-Line Automated Installer (Online)

Inside standard Termux (recommended from F-Droid, not Google Play):
```bash
curl -sSL https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/termux-mobile/install-termux.sh | bash
```

### Option B: Standalone Distribution Archive (Offline / Sideload)

For air-gapped devices or deployments without reliable connectivity:
```bash
# Transfer asterix-termux-v2.0.0-arm64-stable.tar.gz to device, then:
tar -xzf asterix-termux-v2.0.0-arm64-stable.tar.gz
cd asterix-termux
bash install-termux.sh
```

### Option C: Repository Checkout

```bash
git clone https://gitlab.com/nexo-technologies-group/asterix-os.git ~/ASTERIX-OS
cd ~/ASTERIX-OS/termux-mobile
bash install-termux.sh
```

---

## 3. Critical Mobile Hardening Features

### A. Android 12-16 Phantom Process Killer Mitigation
Android 12 and higher limits background child processes to 32 per app, terminating security tasks like port sweeps and AI indexing.

ASTERIX provides built-in diagnostics via `ax mobile phantom`. To permanently remove this limit:
```bash
# Run from PC via ADB:
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
adb shell "setprop persist.sys.fflag.override.settings_enable_monitor_phantom_procs false"

# Or on rooted devices inside Termux:
su -c '/system/bin/device_config put activity_manager max_phantom_processes 2147483647'
```

### B. Background Execution & CPU Wake-Lock
Android aggressively sleeps the CPU when the screen locks, interrupting network scans and listener daemons.

ASTERIX automatically acquires a CPU wake-lock during setup and provides manual controls:
```bash
ax mobile wake on       # Acquire CPU wake-lock (keeps background scans running)
ax mobile wake off      # Release CPU wake-lock to conserve battery
```

### C. Flash Storage Pre-Flight Check
The installer queries available storage before launching heavy tasks:
- If free storage is **<600 MB**, ASTERIX automatically engages **Lightweight Native Mode**, skipping the ~400 MB Debian PRoot container download while providing the full suite of native tools.
- Prevents out-of-disk crashes and corrupted package databases.

### D. Zero-Crash Debian PRoot Hardening
The Debian subsystem applies automatic configuration fixes:
1. **Multi-DNS Resolver**: Writes Quad9, Cloudflare, and Google DNS into `/etc/resolv.conf` with 2-second timeout and retry rotation.
2. **APT Sandbox Patch**: Adds `APT::Sandbox::User "root"` to eliminate the common `_apt` privilege drop crash in PRoot.
3. **Daemon Suppressor**: Installs `/usr/sbin/policy-rc.d` with return code 101 to prevent services (systemd/init scripts) from failing during `apt install`.
4. **Shared Memory Permissions**: Hardens `/dev/shm` and `/tmp` with mode 1777.

---

## 4. Command & Workflow Reference

All capabilities are accessible via `ax mobile` or direct tool aliases.

### Hardware & Mobile Telemetry
```bash
ax mobile hud               # Battery percentage, health, temperature, charging current, RAM & CPU load
ax mobile-sys battery       # Detailed battery diagnostics
ax mobile-sys dns           # Benchmark latency against Cloudflare, Google, Quad9, OpenDNS
```

### Network Recon & Analysis
```bash
ax mobile scan 192.168.1.1       # Native port scan via asterix-net-sentinel
ax mobile tracker 1.1.1.1        # Target IP lookup, ping latency, and route class
ax mobile sweep 192.168.1.0/24   # Local subnet ping sweep
```

### Binary & Cryptographic Inspection
```bash
ax mobile inspect sample.elf     # ELF header analysis, sections, and embedded strings
ax mobile crypto file.iso        # SHA-256 and BLAKE3 integrity verification
```

### Web Structure Intelligence
```bash
ax mobile web-structure https://example.com --tree       # Extract visual site hierarchy
ax mobile web-structure https://example.com --endpoints  # Scrape API endpoints and scripts
ax mobile webdump https://example.com ./output           # Offline asset clone
```

### Debian Rootless Subsystem Control
```bash
ax mobile debian shell           # Enter Debian rootless PRoot shell
ax mobile debian doctor          # Verify PRoot container integrity
ax mobile debian repair          # Re-apply DNS, APT sandbox, and permission patches
```

### Mission Directory & Persistent Storage
```bash
ax mobile folder list            # List all persistent mission vaults
ax mobile folder create target_alpha --template=recon  # Scaffold engagement directories
```

### Cache & Space Management
```bash
ax mobile clean                  # Purge apt cache, temporary sockets, and reclaim flash storage
```

---

## 5. Persistent Storage Layout

All mission data is preserved inside `~/asterix_persistent/` (mirrored inside Debian PRoot at `/asterix_persistent`):

```
~/asterix_persistent/
|-- projects/      User source trees, git repositories, and build artifacts
|-- scans/         Nmap XML/nmap logs, masscan results, and port records
|-- loot/          Extracted credentials, API keys, and hashes
|-- captures/      PCAP network packet traces and wireless captures
|-- reports/       Audit findings, vulnerability dossiers, and executive summaries
|-- notes/         Target notes and scope checklists
|-- scripts/       Custom Python/bash scripts developed on mobile
|-- payloads/      Compiled test payloads and security testing fixtures
|-- wordlists/     Custom dictionaries and password evaluation lists
`-- workspace/     Scratchpad for temporary unpacking and edits
```

---

## 6. Engineering Standards

- **Strict Zero Emojis**: 100% 7-bit ASCII and standard ANSI escape sequences across all mobile scripts, logs, and documentation to guarantee compatibility with minimal serial consoles, ADB shells, and terminal emulators.
- **Fail-Safe Fallbacks**: Every command checks for native Rust binaries first, falls back to Python 3 engines second, and falls back to core POSIX/Linux utilities third.
- **Non-Interactive Resilience**: All automated scripts check `[ -t 0 ]` before invoking interactive prompts, preventing headless stalls during scripting and automation.
