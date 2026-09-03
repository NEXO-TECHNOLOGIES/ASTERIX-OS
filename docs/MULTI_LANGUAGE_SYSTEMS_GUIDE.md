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
│ Rust              │ ui-core/loader    │ Memory-Safe TUI & Master Hub     │
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

---

## ⚡ Quick Reference Table: All New Terminal Shortcuts

| Shortcut | Language | Binary | Description |
| :--- | :--- | :--- | :--- |
| `as-rootkit` | Pure C | `asterix-rootkit-detect` | Scheduler vs /proc hidden process & rootkit detector |
| `as-syscall` | Pure C | `asterix-syscall-mon` | Real-time syscall argument watcher & I/O port mapper |
| `as-envdump` | Pure C | `asterix-env-dump` | Full process environment, FDs, and memory dumper |
| `as-sysinfo` | Pure C | `asterix-sysinfo` | Low-level CPU, RAM, thermal, and kernel probe |
| `as-memview` | Pure C | `asterix-memview` | Colorized binary hex visualizer and memory map inspector |
| `as-netprobe` | Pure C | `asterix-netprobe` | High-speed asynchronous socket latency & port prober |
| `as-hasher` | Pure C | `asterix-hasher` | Zero-dependency SHA-256 and CRC-32 file digest verifier |
| `as-shredder` | Pure C | `asterix-shredder` | DoD 5220.22-M compliant secure storage & file sanitizer |
| `as-packetcraft`| C++17 | `asterix-packetcraft` | Raw socket ICMP generator and Layer-3 network sniffer |
| `as-vulnscan` | C++17 | `asterix-vulnscan` | Multi-threaded CVE signature and banner matcher |
| `as-logwatch` | C++17 | `asterix-logwatch` | Live system log watcher with regex threat alerting |
| `as-rawinfo` | Assembly | `asterix-raw-info` | Zero-libc direct x86-64 Linux syscall engine |
| `as-webrecon` | Go | `asterix-webrecon` | Concurrent DNS enumerator and HTTP header fingerprinter |
| `as-netrecon` | Bash | `net-recon.sh` | Automated subnet discovery and diagnostic reporter |
| `as-cleanup` | Bash | `secure-cleanup.sh` | RAM cache purge and artifact wiper |
| `as-backup` | Bash | `backup-cloud.sh` | Automated persistent vault sync to Discord/Panel |
| `as-scaffold` | Bash | `dev-bootstrap.sh` | 1-click project scaffolder (Rust, C, Go, Python, Node) |
