# 🛡️ Threat Model: `asterix-sys-mon`
## Real-Time Microsecond Kernel & Process Telemetry Engine

### 1. Component Overview
- **Binary**: `asterix-sys-mon`
- **Language**: 100% Native Safe Rust
- **Role**: Tier-1 Microsecond Kernel Telemetry, Real-time Process Surveillance, Host Reconnaissance HUD.
- **Latency**: Sub-millisecond polling cycles utilizing direct `/proc` kernel interfaces.

---

### 2. Detection & Surveillance Capabilities
- **Ephemeral Process Detection**: Captures short-lived helper processes and fork storms that evade traditional 1-second interval monitors.
- **Kernel Patch & Architecture Enumeration**: Discovers kernel release string, compile flags, microcode revision, and CPU hardware features (AES-NI, AVX, SGX, virtualization).
- **Process Hierarchy Analysis**: Identifies suspicious parent-child relationships (e.g., web server spawning interactive shells, cron launching compilers).

---

### 3. Limitations & Non-Detection Scenarios
- **Direct Syscall Unregistered Threads**: Threads executing completely in memory without registering with the task scheduler (hypothetical microkernel injection) are invisible to `/proc`.
- **High Polling Overhead at Scale**: Polling at microsecond frequencies on systems with > 10,000 active processes can consume measurable CPU cycles if thread throttling is disabled.

---

### 4. Operational Security
- **Passive Querying**: Read-only access to system telemetry interfaces; creates no sockets and triggers no host security log events.
