# Android Execution Architecture: Rootless vs. Hardware-Rooted
### Technical Analysis of the ASTERIX Mobile Subsystem

This document outlines the architecture for executing the ASTERIX OS security stack on mobile Android environments.

---

## 1. Architectural Models

ASTERIX OS supports two primary deployment strategies on Android hardware:

| Parameter | ASTERIX Rootless Sandbox (PRoot) | ASTERIX Hardware-Direct (Rooted) |
| :--- | :--- | :--- |
| **Prerequisites** | None (Runs in user space) | Unlocked bootloader, Magisk/KernelSU |
| **Integrity** | Device security remains intact | System partitions modified |
| **UID Emulation** | `ptrace` system call interception (UID 0 emulation) | Native Linux `su` execution |
| **Tool Support** | Nmap, Metasploit, Netcat, TShark, Python, Rust | All user-space tools + Raw Wi-Fi monitor mode |
| **Storage Bridge** | Direct bind mount to `/sdcard/ASTERIX_PERSISTENCE` | Native ext4/f2fs filesystem access |

---

## 2. ASTERIX Rootless PRoot Subsystem

The default ASTERIX mobile engine utilizes user-space `ptrace` hooking to provide full package management, networking tools, and runtime execution without modifying the host firmware:

```
┌───────────────────────────────────────────────────────────┐
│                      Android OS                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                   Termux Host                       │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │           ASTERIX PRoot Container             │  │  │
│  │  │  • Native Rust Loader (asterix-loader)        │  │  │
│  │  │  • Security Toolchain (MSF, Nmap, Netcat)     │  │  │
│  │  │  • Persistent Vault (/asterix_persistent)     │  │  │
│  │  │  • Multi-DNS Failover (1.1.1.1 / 8.8.8.8)     │  │  │
│  │  │  • Zero-Crash APT Sandbox (User 'root')       │  │  │
│  │  │  • Resilient Folder Engine (10 Stores)        │  │  │
│  │  └───────────────────────┬───────────────────────┘  │  │
│  └──────────────────────────┼──────────────────────────┘  │
│                             ▼                             │
│             /sdcard/ASTERIX_PERSISTENCE                   │
└───────────────────────────────────────────────────────────┘
```

### Capabilities & Hardening Features
* **Zero-Crash APT Sandbox**: Automatically enforces `APT::Sandbox::User "root"` to eliminate the common PRoot `_apt` permission denied error.
* **Resilient Multi-DNS Resolver**: Populates `/etc/resolv.conf` with multi-provider failover (Cloudflare, Google, Quad9) with query rotation.
* **Daemon Startup Blocker**: Deploys `/usr/sbin/policy-rc.d` returning `101`, preventing package upgrade crashes from missing systemd/init.
* **Shared Memory Emulation**: Configures `/dev/shm` and `/tmp` with mode `1777` for POSIX semaphores and multiprocessing.
* **Link2Symlink Hardlink Emulation**: Overcomes Android FAT/fuse filesystem limitations, ensuring directory creation and package operations succeed without hardlink permission errors.

### Resilient Folder Architecture
All mission data is organized across 10 persistent storage categories:
- `projects/`: User codebases, repositories, and tactical scripts.
- `scans/`: Network reconnaissance, Nmap, Nikto, and masscan logs.
- `loot/`: Captured hashes, credentials, and exfiltrated payloads.
- `captures/`: PCAP traffic logs and wireless captures.
- `reports/`: Audit findings, executive summaries, and compliance logs.
- `notes/`: Target tracking and engagement documentation.
- `scripts/`: Custom Python, Rust, and Bash tooling.
- `payloads/`: Compiled binaries, shellcodes, and exploit proofs.
- `wordlists/`: Password dictionaries, fuzzing lists, and wordlists.
- `workspace/`: Ephemeral workspace for active testing.

### Debian Rootless CLI Commands
```bash
ax debian                            # Launch hardened Debian rootless PRoot shell
ax debian run <command...>           # Execute command inside Debian rootless
ax debian folder create <name>       # Create new resilient folder with validation
ax debian folder template <n> <t>    # Create folder with template (recon, exploit, web, dev)
ax debian folder tree                # Display ASCII directory tree of persistent storage
ax debian folder fix-perms           # Recursively fix directory (0755) and file permissions
ax debian doctor                     # Run comprehensive diagnostic on Debian rootless
ax debian repair                     # Auto-heal all Debian rootless configs and directories
ax debian status                     # Display container status and storage telemetry
```

---

## 3. Hardware-Direct Kernel Considerations

Direct wireless frame injection (802.11 monitor mode) requires a kernel with patched wireless drivers (`mac80211`) and an external OTG-compatible network interface. For standard reconnaissance, auditing, network analysis, and exploit development, the rootless PRoot deployment provides complete operational parity.
