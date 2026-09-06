# 🌐 ASTERIX OS-Computing // Dual-Boot Collaboration & Host Bridge

The **ASTERIX OS-Computing Engine** (`os-computing/`) is a cross-platform symbiosis framework that detects the surrounding host Linux distribution (Kali Linux, Parrot Security, BlackArch, Ubuntu, Debian, Arch, or Termux) and mounted dual-boot installations.

Instead of duplicating gigabytes of security tools, wordlists, and databases, OS-Computing discovers co-existing installations and seamlessly creates a unified, weaponized bridge into the ASTERIX OS environment.

---

## ⚡ Key Features

1. **Host Environment & Dual-Boot Reconnaissance (`probe`)**:
   - Analyzes `/etc/os-release`, host kernel, and package managers.
   - Probes `/mnt/*` and `/media/*` for mounted dual-boot Linux systems.
   - Detects Kali, Parrot, BlackArch, and Arch partitions.

2. **Cross-OS Tool & Wordlist Assimilation (`collaborate`)**:
   - Searches host and dual-boot file paths for 30+ top-tier security tools (`nmap`, `msfconsole`, `wireshark`, `aircrack-ng`, `sqlmap`, `burpsuite`, `ghidra`, `radare2`).
   - Symlinks discovered executables into `~/.asterix_vault/host_arsenal/bin/`.
   - Bridges password lists (`rockyou.txt`, `seclists`) without duplicating disk space.
   - Automatically generates a sourceable shell configuration: `~/.asterix_vault/host_arsenal/env.sh`.

3. **OS Persona Mimicry & Adaptation (`imitate`)**:
   - Adapts ASTERIX shell prompt, themes, and shortcuts to synergize with the host OS.
   - **Kali Mode**: Unlocks Metasploit, BurpSuite, Undercover mode, and Dragon cyan color palette.
   - **BlackArch Mode**: Unlocks deep binary disassembly and multi-thousand package paths.
   - **Termux Mode**: Engages Android mobile persistence and low-power CPU governor.

---

## 🚀 CLI Commands

```bash
# Probe current host and scan mounted dual-boot partitions
ax os-computing probe

# Bridge host tools & wordlists into ASTERIX OS
ax os-computing collaborate

# Adapt ASTERIX UI and shortcuts to the host OS persona
ax os-computing imitate

# View complete cross-OS collaboration telemetry
ax os-computing status
```
