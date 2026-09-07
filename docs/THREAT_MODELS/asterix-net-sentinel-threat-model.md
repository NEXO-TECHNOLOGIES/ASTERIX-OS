# 🛡️ Threat Model: `asterix-net-sentinel`
## High-Performance Network Scanner & Port Enumeration Engine

### 1. Component Overview
- **Binary**: `asterix-net-sentinel`
- **Language**: 100% Native Safe Rust (Zero External Crate Dependencies)
- **Role**: Tier-1 Network Discovery, Port Enumeration, Banner Grabbing & CIDR Sweeping.
- **Architectural Design**: Lock-free asynchronous thread-pooled connection dispatching with microsecond timing.

---

### 2. Detection Capabilities (What It Identifies)
- **TCP Open Ports**: Identifies listening socket endpoints across IPv4 subnets using full and half-open TCP handshakes.
- **Banner Information**: Extracts initial application greeting banners (HTTP, SSH, FTP, SMTP, MySQL, etc.) for service version identification.
- **Host Availability**: Discovers active network hosts across `/24`, `/16`, or arbitrary CIDR prefixes.
- **Firewall Filtering Responses**: Distinguishes between explicitly closed ports (RST response) and filtered/dropped ports (timeout/ICMP unreachable).

---

### 3. Limitations & Non-Detection Scenarios (What It Misses)
- **Stateful Deep Packet Inspection (DPI)**: If an intermediate firewall silently drops SYN packets or performs TCP SYN proxying with delayed binding, response latency may miscategorize filtered ports.
- **UDP Port Verification**: UDP probing is subject to rate-limiting by operating system ICMP rate throttles (RFC 1812), potentially generating false negatives on high-speed sweeps.
- **Application-Layer Emulation**: Does not execute protocol-specific fuzzing or deep SSL certificate chain verification during baseline reconnaissance.

---

### 4. Operational Security & Network Footprint
- **IDS/IPS Alert Potential**: Rapid port sweeps generate sequential SYN spikes that readily trigger network intrusion detection signatures (e.g., Snort SID 1000001, Suricata stream-events).
- **Stealth Profiles**:
  - *Standard Mode*: Fast scanning prioritizing completion speed (higher visibility).
  - *Stealth Mode*: Introduces jitter and distributed port sequences to reduce heuristic signature triggers.
- **Resource Footprint**: Consumes under 12 MB of memory with zero runtime disk writes unless explicitly instructed to output JSON telemetry.
