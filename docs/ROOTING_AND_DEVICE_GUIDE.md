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
│  │  └───────────────────────┬───────────────────────┘  │  │
│  └──────────────────────────┼──────────────────────────┘  │
│                             ▼                             │
│             /sdcard/ASTERIX_PERSISTENCE                   │
└───────────────────────────────────────────────────────────┘
```

### Capabilities
* Full access to TCP/UDP socket creation and network analysis.
* Automated persistent data synchronization with Android shared storage.
* Zero risk of device bricking or warranty invalidation.

---

## 3. Hardware-Direct Kernel Considerations

Direct wireless frame injection (802.11 monitor mode) requires a kernel with patched wireless drivers (`mac80211`) and an external OTG-compatible network interface. For standard reconnaissance, auditing, network analysis, and exploit development, the rootless PRoot deployment provides complete operational parity.
