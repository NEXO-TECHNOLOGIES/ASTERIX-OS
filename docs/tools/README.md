# 🛠️ ASTERIX OS Tool Catalog & Reference Documentation

Welcome to the official, audited documentation for ASTERIX OS tools and subsystems. Every tool included in the distribution is documented with its operational purpose, usage syntax, supported platforms, and security boundaries.

---

## 📂 Core CLI & Subsystem Managers

| Tool / Subsystem | Binary / Script | Description | Platform Support |
| :--- | :--- | :--- | :--- |
| [**`ax` Master Dispatcher**](ax.md) | `bin/ax`, `bin/ax.ps1` | Unified entrypoint for all ASTERIX OS commands and tools. | Linux, Termux, Windows |
| [**Debian Rootless Manager**](ax-debian-manager.md) | `scripts-hub/ax-debian-manager.py` | PRoot container diagnostics, 10-tier folder vault, and self-healing. | Linux, Termux, Windows |
| [**System Doctor**](ax-doctor.md) | `scripts-hub/ax-doctor.py` | Environment diagnostics, zombie port unblocking, and secret scans. | Linux, Termux, Windows |
| [**Release Verifier**](ax-release-verify.md) | `scripts-hub/ax-release-verify.py` | SHA-256 supply chain integrity auditor against `BUILD_MANIFEST.json`.| Linux, Termux, Windows |

---

## 🌐 Network & Web Security

| Tool | Binary / Script | Description | Platform Support |
| :--- | :--- | :--- | :--- |
| [**Web Code Structure**](web-structure.md) | `scripts-hub/ax-web-structure.py` | Deep DOM hierarchy, script/style mapper, and offline site reconstructor.| Linux, Termux, Windows |
| [**Net Sentinel**](net-sentinel.md) | `core-utils-rust/asterix-net-sentinel` | Zero-copy packet engine and high-throughput multi-threaded port prober. | Linux, Termux |
| [**Black Hole**](black-hole.md) | `scripts-hub/black_hole.py` | Privacy sinkhole, tracking blocker, and local telemetry interceptor. | Linux, Termux, Windows |

---

## 🛡️ Counter-Surveillance & Defensive Utilities

| Tool | Binary / Script | Description | Platform Support |
| :--- | :--- | :--- | :--- |
| [**Undercover Mode**](undercover.md) | `scripts-hub/ax-undercover.py` | Disguises terminal as Windows PowerShell or macOS Terminal. | Linux, Termux, Windows |
| [**Shadowcam Discovery**](shadowcam.md) | `scripts-hub/shadowcam_discover.py` | Local network RTSP / ONVIF IP camera stream auditor. | Linux, Termux, Windows |
| [**Cam Hunter**](cam-hunter.md) | `scripts-hub/ax-cam-hunter.py` | Hotel counter-surveillance and Wi-Fi camera transmitter probe. | Linux, Termux, Windows |
| [**Threat Feed Collector**](self-evolve.md) | `asterix-ai/ax-self-evolve.py` | Autonomous security feed aggregator for CVE and threat intel updates. | Linux, Termux, Windows |

---

## 📋 Security Policy & Auditing

For ethical usage guidelines and independent code review findings, consult:
- [**Vulnerability Disclosure & Legal Notice**](../../SECURITY.md)
- [**Tool Audit & Safety Boundary Report**](../AUDIT_REPORT_TOOLS.md)
