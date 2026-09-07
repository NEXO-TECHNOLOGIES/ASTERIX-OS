# 🌐 ASTERIX OS-Computing // Universal Host Collaboration & Bridge v3.0

The **ASTERIX OS-Computing Engine** (`os-computing/`) is a next-generation cross-platform symbiosis framework that runs on **Windows (10/11/Server)**, **Linux (Kali Linux, Parrot Security, BlackArch, Ubuntu, Debian, Arch)**, **macOS**, **WSL (Windows Subsystem for Linux)**, and **Termux (Android)**.

Instead of duplicating gigabytes of security tools, wordlists, and compilers, OS-Computing discovers co-existing host installations, detects hardware compute topology, and seamlessly creates a unified, weaponized bridge into the ASTERIX OS environment.

---

## ⚡ Key Capabilities (v3.0)

1. **Host Environment & Deep Hardware Reconnaissance (`probe`)**:
   - **Multi-OS Detection**: Inspects Windows NT release/build/edition, Linux `/etc/os-release`, macOS `sw_vers`, or Termux prefixes.
   - **Hardware Profiling**: Identifies CPU microarchitecture, clock frequencies, physical cores, and logical concurrency threads.
   - **Memory & Paging**: Measures physical RAM pool, available RAM, memory commit load %, and pagefile/swap allocations.
   - **GPU & Hardware Acceleration**: Detects NVIDIA CUDA GPUs, AMD ROCm, Intel HD/Iris/Arc graphics, DirectX 12 / Direct3D, and Vulkan runtimes.
   - **Storage Topology**: Analyzes all drive partitions (C:\, D:\, `/`, `/mnt/*`, `/media/*`), storage capacities, and free disk space.
   - **Native Security Controls**: Inspects Windows Defender Real-Time Protection, Antivirus status, and virtualization isolations.
   - **Subsystems & Virtualization**: Probes Windows Subsystem for Linux (WSL1/WSL2) distributions, Hyper-V, and mounted dual-boot partitions.

2. **Cross-OS Tool & Wordlist Assimilation (`collaborate`)**:
   - Searches host paths, `Program Files`, Chocolatey, Scoop, and dual-boot file paths for 120+ top-tier security & systems tools (`nmap`, `masscan`, `msfconsole`, `wireshark`, `sqlmap`, `burpsuite`, `ghidra`, `radare2`, `hashcat`, `john`, `rustc`, `python3`, `node`, `git`).
   - Generates executable command wrappers (`.cmd` for Windows CMD/PowerShell, symlinks for POSIX Linux/macOS) into `~/.asterix_vault/host_arsenal/bin/`.
   - Bridges wordlists (`rockyou.txt`, `SecLists`) into `~/.asterix_vault/host_arsenal/wordlists/`.
   - Generates sourceable environment configurations:
     - `~/.asterix_vault/host_arsenal/env.ps1` (PowerShell)
     - `~/.asterix_vault/host_arsenal/env.bat` (Windows Command Prompt)
     - `~/.asterix_vault/host_arsenal/env.sh` (Bash / Zsh)

3. **Live Hardware Compute Synergy Benchmark (`compute`)**:
   - Engages concurrent multi-core floating-point and cryptographic hashing benchmark across all CPU threads.
   - Measures operations per second (MegaOps/Sec) and validates hardware acceleration pipelines.

4. **OS Persona Mimicry & Adaptation (`imitate`)**:
   - Adapts ASTERIX shell prompt, themes, and shortcuts to synergize with the host OS.
   - **Windows Mode**: `[PERSONA: CYBERNETIC WINDOWS SENTINEL]` — Native Win32 API, PowerShell Core, WSL2, Defender telemetry.
   - **Kali Mode**: `[PERSONA: KALI DRAGON TOTAL SYNERGY]` — Metasploit, BurpSuite, Undercover mode, Dragon cyan colorway.
   - **BlackArch Mode**: `[PERSONA: BLACKARCH TOTAL WARFARE]` — Deep binary disassembly and multi-thousand package paths.
   - **Termux Mode**: `[PERSONA: TERMUX MOBILE WARRIOR]` — Android mobile persistence and low-power CPU governor.

5. **Telemetry & Feature Export (`features`)**:
   - Dumps full structured system telemetry to `~/.asterix_vault/host_arsenal/host_features.json`.

---

## 🚀 CLI Commands

### In Windows PowerShell:
```powershell
# Using Master Launcher:
.\bin\ax.ps1 os-computing probe
.\bin\ax.ps1 os-computing collaborate
.\bin\ax.ps1 os-computing compute
.\bin\ax.ps1 os-computing features
.\bin\ax.ps1 os-computing status

# Or Native PowerShell Script:
powershell -ExecutionPolicy Bypass -File .\os-computing\os_bridge.ps1 probe
powershell -ExecutionPolicy Bypass -File .\os-computing\os_bridge.ps1 collaborate
powershell -ExecutionPolicy Bypass -File .\os-computing\os_bridge.ps1 status
```

### In Windows CMD / Command Prompt:
```cmd
bin\ax.cmd os-computing probe
bin\ax.cmd os-computing collaborate
bin\ax.cmd os-computing status
```

### In Linux / macOS / WSL / Git Bash:
```bash
ax os-computing probe
ax os-computing collaborate
ax os-computing compute
ax os-computing status
```
