# 🔧 ASTERIX OS — Native C Systems Utilities Manual

A comprehensive guide to all native C utilities compiled and shipped with ASTERIX OS.

---

## 🧱 Building the Native C Suite

```bash
# Compile all utilities (requires gcc or clang)
cd core-utils-c/
./build.sh

# Or use Make directly
make all
sudo make install      # Installs to /usr/local/bin/
```

---

## 🖥️ 1. `asterix-sysinfo` — Hardware & Kernel Telemetry Probe

Reads low-level kernel registers and system files to display CPU model, memory layout, thermal zones, and uptime.

```bash
asterix-sysinfo
```

**Output:** CPU architecture, core count, clock speed, RAM usage, swap allocation, kernel identity, and thermal zone temperature.

---

## 🔬 2. `asterix-memview` — Memory & Binary Hex Inspector

Displays colorized hex dumps of any binary file or live process memory mappings from `/proc/<pid>/maps`.

```bash
# Hex dump a binary file (first 512 bytes)
asterix-memview /bin/ls

# Inspect first 4096 bytes of a file
asterix-memview /boot/vmlinuz 4096

# Inspect virtual memory map of a running process
asterix-memview -p <PID>
```

**Output columns:** Offset (yellow), byte value color-coded (green = printable, gray = null, magenta = binary), ASCII matrix.

---

## 📡 3. `asterix-netprobe` — Non-Blocking Network & Port Prober

Asynchronous multi-port TCP connection tester with live latency measurements.

```bash
# Probe a single port
asterix-netprobe 192.168.1.1 80

# Probe a range of ports (20 to 1024) with 300ms timeout
asterix-netprobe 10.0.0.1 20 1024 300

# Probe the top web ports on a remote target
asterix-netprobe target.htb 80 443 500
```

**Output:** Open ports, response latency in milliseconds, total discovered port count.

---

## 🔑 4. `asterix-hasher` — Cryptographic Integrity Verifier

Zero-dependency, standalone CRC-32 and SHA-256 file checksum calculator.

```bash
# Calculate SHA-256 + CRC32 of any file
asterix-hasher /etc/passwd
asterix-hasher /boot/vmlinuz
asterix-hasher /asterix_persistent/loot.tar.gz
```

**Output:** File size, CRC-32 hex, SHA-256 hex digest. No OpenSSL dependency.

---

## 🗑️ 5. `asterix-shredder` — DoD Secure Storage Wiper

Multi-pass cryptographic random overwrite + zero-fill sanitizer. File is truncated and unlinked after shredding.

```bash
# 3-pass secure wipe (default)
asterix-shredder /tmp/sensitive.txt

# 7-pass DoD 5220.22-M wipe
asterix-shredder /asterix_persistent/loot.tar.gz 7

# Maximum 35-pass overwrite
asterix-shredder /dev/sdb 35
```

**Passes:** Odd = cryptographic random noise, Even = `0xFF` inversion, Final = `0x00` zero-fill + fsync.

---

## 🔍 6. `asterix-proctrace` — Real-Time Process & Memory Tracer

Live top-30 process monitor sorted by RAM usage, refreshing every second.

```bash
# Monitor all processes (top 30 by RAM)
asterix-proctrace

# Monitor a specific PID
asterix-proctrace --pid 1234
```

**Output table:** PID, process name, state (RUNNING/SLEEP/ZOMBIE), RAM (kB), CPU time.

---

## 🤖 7. `scripts-hub/` Automation Suite

| Script | Usage | Description |
|:---|:---|:---|
| `net-recon.sh` | `./net-recon.sh 192.168.1.0/24` | Full subnet recon & HTML report |
| `dev-bootstrap.sh` | `./dev-bootstrap.sh rust my-project` | Scaffold Rust/C/Go/Python/Node workspace |
| `secure-cleanup.sh` | `./secure-cleanup.sh` | Wipe RAM cache, temp files, bash history |
| `backup-cloud.sh` | `./backup-cloud.sh` | Auto-compress and sync vault to Discord/Panel |

---

## ⚡ ASTERIX Shell Aliases

```bash
as-sysinfo      # Launch asterix-sysinfo
as-memview      # Launch asterix-memview
as-netprobe     # Launch asterix-netprobe
as-hasher       # Launch asterix-hasher
as-shredder     # Launch asterix-shredder
as-proctrace    # Launch asterix-proctrace
```
