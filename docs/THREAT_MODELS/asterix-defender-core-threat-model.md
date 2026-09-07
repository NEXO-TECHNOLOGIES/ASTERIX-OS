# 🛡️ Threat Model: `asterix-defender-core`
## Target Hardening Assessment & Active Endpoint Defense Engine

### 1. Component Overview
- **Binary**: `asterix-defender-core`
- **Language**: 100% Native Safe Rust (Zero Dependencies)
- **Role**: Tier-1 Target Hardening Assessment, Endpoint Antivirus Scanning, Quarantine Vault & Host Firewall Management.
- **Subsystems**: Heuristic file pattern scanner, XOR-neutralized quarantine vault, packet filter interface, network killswitch.

---

### 2. Assessment Capabilities (What It Identifies & Enforces)
- **Target Hardening Assessment**: Audits endpoint defenses including ASLR configuration, DEP/NX enforcement, firewall active state, and listening service exposure.
- **Malware & Webshell Signatures**: Fast multi-pattern search identifying webshells (`c99`, `r57`, b374k stubs), reverse shell invocation strings (`pty.spawn`, bash `/dev/tcp`, netcat exec stubs), and known testing strings (EICAR).
- **Endpoint Isolation**: Implements an instant network isolation mode (`ax defender isolate`) that flushes active socket connections and restricts routing to loopback.
- **XOR Neutralization Quarantine**: Safely neutralizes flagged payloads using single-byte XOR transformations and revocable filesystem permissions (`chmod 000`) within `~/.asterix_vault/quarantine`.

---

### 3. Limitations & Non-Detection Scenarios
- **Novel Zero-Day Payloads**: Does not detect completely novel, uncompiled or uniquely obfuscated binaries that exhibit zero known heuristic patterns or entropy spikes.
- **Encrypted Archives**: Cannot inspect the contents of password-protected ZIP, RAR, or 7z archives without key extraction.
- **Kernel-Level Rootkits**: Userspace scanning cannot detect rootkits intercepting `sys_getdents` or hooking kernel syscall tables to hide files.

---

### 4. Operational Security
- **Safe Neutralization**: Quarantined files are made non-executable and XOR-obfuscated to prevent accidental execution by users or indexers.
- **Reversible Action**: Quarantined files can be reviewed, verified, or restored (`ax defender unquarantine`) with zero data loss.
