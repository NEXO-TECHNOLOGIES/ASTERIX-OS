# [ASTERIX] ASTERIX OS: 5 Breakthrough Differentiators Beyond Kali Linux

**Document Version**: 3.0.0  
**Scope**: Advanced Architectural Capabilities  
**Distribution Engine**: `ax` / `asterix`  
**Dependencies**: 100% Python Standard Library (Zero external pip wheels required)  

---

## Executive Summary

While legacy pentesting distributions (Kali Linux, Parrot OS, NetHunter) excel at packaging individual binary CLI tools (Nmap, Metasploit, Wireshark, Hashcat), they operate as **passive software repositories** rather than **integrated cybernetic operating systems**. Practitioners are forced to manually correlate scan outputs, resolve team collisions via chat messages, handle EDR egress detection alone, purchase specialized USB SDR dongles for RF counter-surveillance, and struggle to establish tamper-evident court admissibility for engagement evidence.

ASTERIX OS introduces **5 native breakthrough engines** directly into the operating system core to solve these fundamental operational limits:

| # | Breakthrough Capability | Legacy Offensive OS (Kali/Parrot) | ASTERIX OS Engine |
|---|---|---|---|
| 1 | ** Attack Path Pathfinder** | Disjoint terminal tool outputs; manual mental correlation | Autonomous DAG attack surface synthesis, Dijkstra hop/noise pathfinding, interactive HTML graph |
| 2 | ** Multiplayer Engagements** | Isolated single-operator terminals; risk of scan collision | Real-time P2P encrypted squad synchronization, UDP discovery, logical vector clocks, target locking |
| 3 | ** Ghost Egress & Decoy** | Static IP egress; immediately fingerprinted by EDR/WAF | Dynamic egress traffic shaping, Gaussian jitter, enterprise background decoy blending |
| 4 | ** Mobile RF Sentinel** | Requires external Alfa/HackRF dongles and driver compilation | Native passive BLE tracker detection (AirTags/SmartTags), Evil Twin rogue AP hunter, ultrasonic probe |
| 5 | ** Tamper-Proof Vault** | Unsigned flat text logs, easily challenged in litigation | Cryptographic RFC 3161 timestamping, Ed25519/HMAC digital signatures, verifiable `.axproof` envelopes |

---

## 1.  Attack Path Pathfinder (`ax pathfinder` / `ax graph`)

### Purpose & Architecture
Instead of reading thousands of lines of raw Nmap XML or tool logs, `ax-pathfinder` automatically ingests the unified engagement data model (`schemas/asterix_project_schema.json`) and builds a **Directed Acyclic Graph (DAG)** mapping:
- **Perimeter Entry Nodes**: Exposed external web, SSH, VPN, and mail interfaces.
- **Service Bridges**: Running services, protocol versions, and banners.
- **Vulnerability Bridges**: Discovered CVEs and misconfigurations linking entry nodes to internal segments.
- **Credential Pivots**: Harvested credentials and private keys enabling lateral movement without alerts.
- **Crown Jewels**: Automatically identifies Domain Controllers, Active Directory LDAP nodes, and database vaults.

### Optimization Algorithms
- **[*] Shortest Path**: Uses Dijkstra's algorithm to compute the minimal hop sequence between an external entry vector and high-value target assets.
- ** Lowest-Noise (Stealth) Path**: Weights each traversal edge by its probability of triggering EDR/SIEM detection. Exploitation of loud services incurs high noise penalties, whereas authenticating via harvested credentials has minimal noise weight.
- **[SEC] Chokepoints & Blast Radius**: Calculates graph centrality to reveal which single host or service, if secured by defenders or compromised by attackers, controls access to the largest radius of downstream assets.

### Usage
```bash
# Run demonstration on high-fidelity enterprise topology
ax pathfinder demo

# Ingest active engagement project.json and analyze attack surface
ax pathfinder analyze --project project.json

# Calculate shortest & lowest-noise paths to a specific asset
ax pathfinder paths --crown-jewel "10.0.20.5"

# Export self-contained, dark-mode interactive HTML/SVG graph
ax pathfinder export-html -o reports/attack_path.html
```

---

## 2.  Multiplayer Engagements (`ax team` / `ax collab-sync`)

### Purpose & Architecture
In multi-operator red teams and penetration tests, two operators often scan or exploit the same IP address simultaneously, causing defensive EDR alert spikes or CTF flags to be overwritten. 

`ax-team` establishes an ad-hoc, zero-infrastructure **Peer-to-Peer (P2P) mesh network** over local Wi-Fi, mobile hotspot tethering, or WireGuard VPN.

### Key Capabilities
- **Target Lock Collision Avoidance**: An operator can acquire an atomic lock on an IP or subnet (`ax team lock 192.168.1.50`). Other operators' terminals will flag the lock with operator identity, reason, and TTL to prevent duplicated noise.
- **Logical Vector Clocks**: Conflict-free distributed causality tracking ensures delta updates merge cleanly across mobile Termux and desktop instances without centralized database servers.
- **Cryptographic Packet Verification**: All UDP discovery beacons and HTTP delta synchronizations are signed and verified using HMAC-SHA256 with a shared team secret passphrase.

### Usage
```bash
# Initialize a new squad mesh with custom callsign
ax team init "red-squad" --callsign "vanguard_lead" --passphrase "SecureSecretKey"

# Lock an IP address to prevent squad collision
ax team lock 10.0.20.5 --reason "Active Kerberos ticket harvesting" --ttl 1800

# Inspect active target locks held across the team
ax team locks

# Release lock when operation completes
ax team unlock 10.0.20.5

# Broadcast presence on local Wi-Fi mesh & listen for peers
ax team beacon
ax team listen
```

---

## 3.  Ghost Egress & Decoy Blending (`ax ghost` / `ax decoy`)

### Purpose & Architecture
Modern enterprise security centers (SOCs) and Web Application Firewalls (WAFs) detect offensive security testing through **behavioral heuristic scoring**: bursts of high-frequency requests, abnormal User-Agents, and non-standard egress traffic patterns.

`ax-ghost` provides active egress auditing and a background decoy traffic engine that blends testing activity into typical enterprise workstation traffic.

### Key Capabilities
- **Benign Decoy Blending**: Sends legitimate, benign background HTTP/DNS queries to high-reputation domain endpoints (`cloudflare.com`, `wikipedia.org`, `microsoft.com`, `kernel.org`, `apple.com`).
- **Statistical Timing Jitter**: Applies Gaussian/Poisson delay jitter between transactions, defeating frequency-threshold and burst-detection heuristics.
- **Client Footprint Morphing**: Dynamically rotates authentic Windows Chrome, macOS Safari, Linux Firefox, and Android Chrome HTTP headers.
- **Multi-Egress Routing Advice**: Audits local IPv4/IPv6 dual-stack posture and recommends interface rotation (Wi-Fi, 5G cellular tether, WireGuard) and IPv6 SLAAC privacy addressing.

### Usage
```bash
# Audit egress interfaces and public IP posture
ax ghost audit

# Run 10 benign decoy requests with randomized Gaussian jitter
ax ghost decoy --count 10 --interval 1.5 --jitter 0.8

# Simulate decoy traffic generation without firing live network packets
ax ghost decoy --count 5 --dry-run

# Inspect browser and client User-Agent morphing profiles
ax ghost morph
```

---

## 4.  Mobile RF & Sensor Sentinel (`ax radio` / `ax ble`)

### Purpose & Architecture
Conventional security distributions require external USB software-defined radios (HackRF, RTL-SDR) or Alfa Wi-Fi dongles to perform wireless auditing. `ax-radio` utilizes **built-in hardware interfaces** across Windows (`netsh`), Linux (`nmcli`/`iw`), and Android Termux (`termux-wifi-scaninfo`) for 100% passive, zero-transmission counter-surveillance.

### Key Capabilities
- **Evil Twin / Rogue AP Hunter**: Passively analyzes the surrounding 2.4 GHz and 5 GHz spectrum. Detects BSSID MAC OUI conflicts (e.g., enterprise Cisco SSID suddenly broadcast from a low-cost Espressif ESP32/ESP8266) and flags Wi-Fi encryption downgrade attacks (open network masquerading as WPA2/WPA3).
- **Passive RF Jamming & Interference Sentinel (`ax radio jamming-audit`)**: Audits ambient spectrum for intentional carrier interference, channel noise floor spikes, and anomalous multi-BSSID blackout conditions, providing DFS and band-steering mitigation advice.
- **802.11 Deauthentication Flood & PMF Auditor (`ax radio deauth-alert`)**: Evaluates network vulnerability to unauthenticated 802.11 management frame spoofing and verifies 802.11w Protected Management Frames (PMF) enforcement.
- **Passive BLE Tracker Sentinel**: Audits Bluetooth Low Energy advertisement frames. Detects Apple AirTag / Find My beacons (`0x004C`), Samsung SmartTags, Tile Mate devices, and Flipper Zero broadcast profiles.
- **Ultrasonic Beacon Probe**: Audits microphone subsystem sample rates (44.1 kHz, 48 kHz, 96 kHz) to determine Nyquist coverage for near-ultrasonic cross-device attribution beacons (18 kHz - 22 kHz).

### Usage
```bash
# Comprehensive radio and sensor posture audit
ax radio status

# Passively scan surrounding Wi-Fi APs and BSSIDs
ax radio wifi-sentinel

# Audit for Evil Twin rogue access points and encryption downgrades
ax radio evil-twin-audit

# Passively audit spectrum for RF jamming & carrier interference
ax radio jamming-audit

# Audit 802.11w PMF protection & deauth flood vulnerability
ax radio deauth-alert

# Scan for stalking AirTags and nearby BLE tracker beacons
ax radio ble-scan

# Audit microphone frequency coverage for ultrasonic tracking
ax radio ultrasonic-audit
```

---

## 5.  Tamper-Proof Evidence Vault (`ax proof` / `ax evidence`)

### Purpose & Architecture
In penetration testing and incident response engagements, captured artifacts (pcaps, terminal sessions, loot databases, and vulnerability evidence) are frequently challenged in legal proceedings or by client IT management on grounds of potential tampering or unverified timestamps.

`ax-evidence` implements a cryptographic chain-of-custody sealing and verification architecture that produces immutable `.axproof` forensic envelopes.

### Key Capabilities
- **Dual-Algorithm Hashing**: Computes SHA-256 and SHA-512 digests for bit-for-bit file verification.
- **RFC 3161 Compliant Timestamping**: Generates microsecond-resolution UTC timestamps bound to hardware monotonic clock ticks and cryptographic nonces.
- **Hardware & Machine Binding**: Incorporates the machine fingerprint, operating system kernel, hostname, and operator callsign into an HMAC-SHA256 digital signature.
- **Forensic Verification Engine**: Instantly validates whether a file has remained untouched or flags exact byte-level corruption and tampering.
- **Audit Ledger**: Chronologically logs every sealed artifact into `~/.asterix/evidence/evidence_ledger.json`.

### Usage
```bash
# Cryptographically seal an evidence file into an immutable .axproof envelope
ax evidence seal nmap_full_audit.txt --operator "lead_auditor" --engagement-id "ENG-2026-001"

# Verify evidence integrity against its proof envelope
ax evidence verify nmap_full_audit.txt

# Inspect detailed metadata within an .axproof envelope
ax evidence inspect nmap_full_audit.txt.axproof

# View chronological chain-of-custody ledger across engagements
ax evidence ledger
```

---

## Verification & Architecture Verification

All 5 breakthrough engines are covered by automated unit and integration tests located in `python-lab/test_breakthrough_features.py`:

```bash
# Execute the complete breakthrough test suite
python python-lab/test_breakthrough_features.py

# Execute the entire ASTERIX OS test matrix
python python-lab/test_beyond_kali.py
python python-lab/test_packaging_and_repo.py
python python-lab/test_debian_rootless.py
python scripts-hub/ax-release-verify.py
```
