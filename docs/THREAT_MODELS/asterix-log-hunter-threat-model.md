# 🛡️ Threat Model: `asterix-log-hunter`
## High-Throughput Threat Log Forensics & Anomaly Analysis Engine

### 1. Component Overview
- **Binary**: `asterix-log-hunter`
- **Language**: 100% Native Safe Rust (Zero Dependencies)
- **Role**: Tier-1 Post-Exploitation Forensics, Threat Hunting, Auth Log Auditing & Syslog Stream Inspection.
- **Engine**: Single-pass multi-pattern automaton with zero allocations on hot paths.

---

### 2. Detection Capabilities (What It Identifies)
- **Authentication Anomalies**: Repeated failed SSH logins, brute-force patterns, password spraying, and root privilege escalations (`sudo`, `su`, PAM failures).
- **Web Application Injections**: Common attack signatures in access logs (SQL injection attempts, path traversal `../`, command injection patterns, XSS probes).
- **Persistence & Task Manipulation**: Cron modifications, systemd service tampering, and unusual shell spawning logged in system security facilities.
- **Anti-Forensics Markers**: Detects log gaps, truncation, zero-byte fills, and timestamp reordering indicative of forensic tampering.

---

### 3. Limitations & Non-Detection Scenarios
- **Encrypted Channels**: Only inspects text-based system logs and exported server logs; network-layer encrypted traffic must be logged by an endpoint agent first.
- **Low-and-Slow Attacks**: Single attempts distributed over days or weeks below burst thresholds will not trigger rate-based anomaly counters.
- **Log Forgery**: Attackers with root privileges who carefully edit existing lines without breaking format continuity cannot be distinguished purely from syntax without cryptographic log forwarders.

---

### 4. Operational Security
- **Read-Only Operation**: Never alters, writes to, or deletes source log files.
- **Output Formats**: Colorized incident matrix in terminal or structured JSON lines for ingest into external SIEM/SOC platforms.
