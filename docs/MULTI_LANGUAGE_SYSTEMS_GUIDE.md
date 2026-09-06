# 🌐 ASTERIX OS — Multi-Language Deep Systems Architecture & Toolchain Guide

ASTERIX OS features a multi-tiered polyglot systems architecture spanning **x86-64 Assembly**, **Pure C11**, **C++17**, **Rust**, and **Go**. Every language was chosen for its distinct architectural strengths:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                      ASTERIX OS POLYGLOT MATRIX                          │
├───────────────────┬───────────────────┬──────────────────────────────────┤
│ LANGUAGE          │ COMPONENT         │ PURPOSE                          │
├───────────────────┼───────────────────┼──────────────────────────────────┤
│ x86-64 Assembly   │ boot-asm/         │ MBR Boot Sector & Raw Syscalls   │
│ Pure C (C11)      │ core-utils-c/     │ Deep Kernel, Rootkit, /proc      │
│ Modern C++ (C++17)│ core-utils-cpp/   │ Raw Packets, Vuln Scanner, Logs  │
│ Pure Rust (2021)  │ core-utils-rust/  │ Binary Inspection, Sentinel, etc │
│ Rust UI Core      │ ui-core/loader    │ Memory-Safe TUI & Master Hub     │
│ Go (Golang)       │ core-utils-go/    │ High-Concurrency Network Recon   │
│ POSIX Shell       │ scripts-hub/      │ Automation & Maintenance Chains  │
└───────────────────┴───────────────────┴──────────────────────────────────┘
```

---

## ⚡ 1. One-Click Master Build Pipeline (`./build-all.sh`)

To compile the entire multi-language ecosystem in one step:

```bash
chmod +x build-all.sh
sudo ./build-all.sh
```

This compiles:
1. **C Suite** (`gcc -O3 -Wall -Wextra -D_GNU_SOURCE`)
2. **C++ Suite** (`g++ -std=c++17 -O2 -pthread`)
3. **Assembly Suite** (`nasm -f bin`, `nasm -f elf64` + `ld`)
4. **Go Suite** (`go build -ldflags="-s -w"`)

All resulting binaries are automatically installed into `/usr/local/bin/`.

---

## 🔬 2. Deep Kernel & OS-Level C Suite (`core-utils-c/`)

### A. Rootkit & Stealth Process Detector (`asterix-rootkit-detect` / `as-rootkit`)
Cross-references the virtual `/proc/` filesystem with kernel scheduler task queues (`/proc/sched_debug`) to expose hidden processes, inspects `/proc/modules` for rogue rootkit drivers, and audits `/etc/passwd` for unauthorized UID-0 backdoor accounts.

```bash
as-rootkit
```

### B. Live Syscall & I/O Port Monitor (`asterix-syscall-mon` / `as-syscall`)
Monitors live kernel system calls for any PID via `/proc/<PID>/syscall`, resolves syscall numbers to human-readable names with arguments and stack pointers, and maps hardware I/O ports (`/proc/ioports`) and physical RAM maps (`/proc/iomem`).

```bash
# Monitor live syscalls executed by a process
as-syscall --pid 1337

# Display kernel hardware I/O port assignments
as-syscall --ioports

# Display physical RAM memory mapping
as-syscall --iomem
```

### C. Deep Process Environment & FD Dumper (`asterix-env-dump` / `as-envdump`)
Parses null-delimited process memory to extract environment variables, command-line arguments, open file descriptors (sockets, pipes, devices), and virtual memory regions.

```bash
as-envdump <PID>
as-envdump <PID> --env-only
as-envdump <PID> --fd-only
as-envdump <PID> --maps
```

### D. Core C System Utilities
* `as-sysinfo`: Probes CPU registers, memory layout, thermal sensors, and system load.
* `as-memview`: Interactive colorized hex dump and `/proc/<PID>/maps` inspector.
* `as-netprobe`: Non-blocking multi-port TCP connectivity and latency benchmark.
* `as-hasher`: Standalone SHA-256 + CRC-32 file integrity calculator (zero external libs).
* `as-shredder`: DoD 5220.22-M compliant multi-pass secure file wiper and zero-fill sanitizer.

---

## 📡 3. Native C++ Cyber Suite (`core-utils-cpp/`)

### A. Raw Packet Crafter & Layer-3 Sniffer (`asterix-packetcraft` / `as-packetcraft`)
Builds and sends raw ICMP echo request packets with sub-millisecond precision, and operates an AF_PACKET raw socket sniffer that parses IPv4 headers, TCP control flags (SYN, ACK, FIN, RST, PSH), and UDP ports in real time.

```bash
# Send raw ICMP echo requests
sudo as-packetcraft --ping 8.8.8.8 --count 5

# Live Layer-3 raw packet sniffer
sudo as-packetcraft --sniff --count 200
```

### B. Vulnerability Scanner & Banner Grabber (`asterix-vulnscan` / `as-vulnscan`)
Multi-threaded banner grabber that connects across port ranges and executes regex pattern matching against known CVE signatures (OpenSSH, Apache, vsftpd, Samba, IIS, OpenSSL Heartbleed, etc.).

```bash
# Scan target across ports 1-1024 with 32 threads
as-vulnscan 192.168.1.1 1 1024 32
```

### C. Real-Time Threat Log Watcher (`asterix-logwatch` / `as-logwatch`)
Tails system and authentication logs in real time, colorizing and alerting on SSH brute force, privilege escalations, port scans, kernel panics, UFW firewall drops, and custom regex signatures.

```bash
# Watch syslog for threats
sudo as-logwatch /var/log/syslog

# Watch auth log with a custom regex pattern
sudo as-logwatch /var/log/auth.log "malicious_user"
```

---

## ⚙️ 4. x86-64 Pure Assembly Engine (`boot-asm/`)

### A. Custom MBR Bootloader Sector (`asterix-mbr.asm`)
Pure 16-bit real-mode x86 assembly bootloader that sets 80x25 text mode, renders the electric cyan ASTERIX boot banner, executes a hardware delay loop, and includes the `0xAA55` boot sector signature.

```bash
# Assemble MBR binary (512 bytes)
cd boot-asm
make bin/asterix-mbr.bin

# Test in QEMU emulator:
qemu-system-x86_64 -drive format=raw,file=bin/asterix-mbr.bin
```

### B. Zero-Libc Linux Syscall Utility (`asterix-raw-info` / `as-rawinfo`)
Pure 64-bit assembly (`SYS_write`, `SYS_gethostname`, `SYS_getuid`, `SYS_exit`) that executes directly against the Linux kernel without linking against `libc` or any external dynamic runtime.

```bash
as-rawinfo
```

---

## 🚀 5. High-Concurrency Go Cyber Engine (`core-utils-go/`)

### Concurrent DNS Enumerator & Web Fingerprinter (`asterix-webrecon` / `as-webrecon`)
Leverages Go goroutines and worker pools to concurrently brute-force subdomains, resolve IP addresses, probe HTTP/HTTPS endpoints, extract HTML page titles, and audit security response headers.

```bash
# Subdomain brute-force with 30 concurrent workers
as-webrecon --enum target.com 30

# Rapid HTTP/HTTPS service fingerprinting
as-webrecon --finger 192.168.1.1
```

## 🦀 6. Native Rust Security & Systems Engines (`core-utils-rust/`)

ASTERIX OS features 5 high-velocity pure-Rust engines engineered with **Zero External Crate Dependencies** for 100% standalone reliability across bare-metal Linux, Debian Live ISOs, and Android Termux PRoot:

### A. Binary Forensics & Section Entropy Analyzer (`asterix-bin-inspector`)
Decodes ELF (Linux), PE (Windows), and Mach-O headers without external libraries. Parses entry points, architectures (x86_64, ARM, AArch64, RISC-V), calculates Shannon entropy per section to detect packers and crypters, extracts filtered strings (URLs, IPs, sensitive keys), and renders color-coded hex dumps.
```bash
ax bin-inspect /bin/ls --all
ax bin-inspect sample.bin --hex --offset 0x100 --len 64
```

### B. High-Concurrency Network Sentinel (`asterix-net-sentinel`)
Thread-pooled asynchronous TCP port scanner and service prober with polite banner grabbing, socket RTT latency/jitter benchmarking, and IPv4 CIDR subnet calculation.
```bash
ax sentinel 127.0.0.1 -p top100 --threads 50 --banner
ax sentinel --ping 1.1.1.1
ax sentinel --subnet 192.168.1.50/24
```

### C. Cryptographic Analysis & Manifest Suite (`asterix-crypto-core`)
Pure standard Rust cryptographic implementations of SHA-256 (FIPS 180-4), SHA-512 (FIPS 180-4), and MD5 (RFC 1321). Features an intelligent hash identifier, file entropy tester, directory `.axsum` integrity manifest generator/verifier, and microsecond hashing throughput benchmarks.
```bash
ax crypto hash /bin/bash --algo sha256
ax crypto identify "5d41402abc4b2a76b9719d911017c592"
ax crypto manifest /etc/asterix -o asterix-core.axsum
ax crypto bench
```

### D. Real-Time Microsecond Kernel & Process HUD (`asterix-sys-mon`)
Microsecond telemetry visualizer rendering real-time cyberpunk ANSI gauges of CPU per-core utilization, RAM/Swap allocation, disk I/O, process states, and virtualization environment classification (Docker, LXC, Termux PRoot, Bare-Metal).
```bash
ax sysmon              # Interactive live-updating telemetry HUD
ax sysmon --snapshot   # Single snapshot for scripts
ax sysmon --json       # Machine-readable telemetry
```

### E. Automated Security Hardening & Compliance Engine (`asterix-guard-engine`)
Audits Linux kernel sysctl hardening (`ASLR`, `kptr_restrict`, `dmesg_restrict`, `yama/ptrace_scope`, `fs.protected_symlinks`), audits `/etc/shadow`, `/etc/passwd`, `/etc/sudoers`, detects rogue UID-0 accounts, audits SSH configuration, computes an Asterix Cyber Compliance Score (0-100), and auto-generates bash remediation scripts.
```bash
ax guard
ax guard --generate-fix -o apply-hardening.sh
```

---

## ⚡ Quick Reference Table: All Native Toolchain Commands (`ax-*` & `asterix-*`)

| Primary Shortcut | Full Command Form | Language | Binary Target | Description |
| :--- | :--- | :--- | :--- | :--- |
| `ax-rootkit` | `asterix-rootkit` | Pure C | `asterix-rootkit-detect` | Scheduler vs /proc hidden process & rootkit detector |
| `ax-syscall` | `asterix-syscall` | Pure C | `asterix-syscall-mon` | Real-time syscall argument watcher & I/O port mapper |
| `ax-envdump` | `asterix-envdump` | Pure C | `asterix-env-dump` | Full process environment, FDs, and memory dumper |
| `ax-sysinfo` | `asterix-sysinfo` | Pure C | `asterix-sysinfo` | Low-level CPU, RAM, thermal, and kernel probe |
| `ax-memview` | `asterix-memview` | Pure C | `asterix-memview` | Colorized binary hex visualizer and memory map inspector |
| `ax-netprobe` | `asterix-netprobe` | Pure C | `asterix-netprobe` | High-speed asynchronous socket latency & port prober |
| `ax-hasher` | `asterix-hasher` | Pure C | `asterix-hasher` | Zero-dependency SHA-256 and CRC-32 file digest verifier |
| `ax-shredder` | `asterix-shredder` | Pure C | `asterix-shredder` | DoD 5220.22-M compliant secure storage & file sanitizer |
| `ax-packetcraft`| `asterix-packetcraft`| C++17 | `asterix-packetcraft` | Raw socket ICMP generator and Layer-3 network sniffer |
| `ax-vulnscan` | `asterix-vulnscan` | C++17 | `asterix-vulnscan` | Multi-threaded CVE signature and banner matcher |
| `ax-logwatch` | `asterix-logwatch` | C++17 | `asterix-logwatch` | Live system log watcher with regex threat alerting |
| `ax-rawinfo` | `asterix-rawinfo` | Assembly | `asterix-raw-info` | Zero-libc direct x86-64 Linux syscall engine |
| `ax-cipher` | `asterix-cipher` | Assembly | `asterix-cipher-asm` | 512-bit ARX multi-round cipher & AXCIPH02 binary container |
| `ax-webrecon` | `asterix-webrecon` | Go | `asterix-webrecon` | Concurrent DNS enumerator and HTTP header fingerprinter |
| `ax-bininspect`| `asterix-bininspect`| Pure Rust | `asterix-bin-inspector` | ELF/PE/Mach-O binary header parser, container & entropy |
| `ax-sentinel` | `asterix-sentinel` | Pure Rust | `asterix-net-sentinel` | Multi-threaded port telemetry, banner grabber & CIDR |
| `ax-crypto` | `asterix-crypto` | Pure Rust | `asterix-crypto-core` | SHA256/512/MD5, ChaCha20 cipher & manifest suite |
| `ax-sysmon` | `asterix-sysmon` | Pure Rust | `asterix-sys-mon` | Real-time CPU, RAM, process HUD & telemetry visualizer |
| `ax-guard` | `asterix-guard` | Pure Rust | `asterix-guard-engine` | Automated security hardening audit & compliance score |
| `ax-netrecon` | `asterix-netrecon` | Bash | `net-recon.sh` | Automated subnet discovery and diagnostic reporter |
| `ax-cleanup` | `asterix-cleanup` | Bash | `secure-cleanup.sh` | RAM cache purge and artifact wiper |
| `ax-backup` | `asterix-backup` | Bash | `backup-cloud.sh` | Automated persistent vault sync to Discord/Panel |
| `ax-scaffold` | `asterix-scaffold` | Bash | `dev-bootstrap.sh` | 1-click project scaffolder (Rust, C, Go, Python, Node) |
