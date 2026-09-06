# 📦 ASTERIX OS External Security Packages

This directory contains external security frameworks and defensive suites that are automatically cloned and synchronized by ASTERIX OS.

## 🚀 Managed Packages

| Package Name | Repository URL | Purpose |
| :--- | :--- | :--- |
| **`Asterix-Anti-Network-Attack`** | `https://github.com/alexhack235-code/Asterix-Anti-Network-Attack.git` | Active network defense countermeasures, ARP poisoning defense, TCP SYN flood protection, DNS hijacking shield, port scan traps, anti-reverse engineering sentinel, and email security auditing. |
| **`THUNDER`** | `https://github.com/alexhack235-code/THUNDER.git` | Enterprise Network & Device Defender: Wi-Fi deauthentication shield, anti-reverse shell monitor, ransomware honeypots, BadUSB mitigation, keylogger detection, encrypted DNS armor, ASR system hardening, malware scanner with cyberpunk HTML report visualizer, and 105-endpoint IP rotator. |
| **`ASTERISK-Web-Frality-scanner`** | `https://github.com/Alex-dot-dot/ASTERISK-Web-Frality-scanner.git` | WSCAN Web Weakness & Vulnerability Scanner: Crawls web targets, evaluates security headers, cookie flags, sensitive file leaks (.env, .git), SQL injection, reflected XSS, command injection, and open redirects. |
| **`LIGHTNING-`** | `https://github.com/alexhack235-code/LIGHTNING-.git` | LIGHTNING Autonomous WAF & Web SOC: Military-grade 16-module defense engine — WAF reverse-proxy, real-time Web SOC dashboard (port 8888), zero-day virtual patching, threat intelligence feeds, honeypot decoys, DLP, SSL/TLS manager, behavioral heuristic scoring, anti-bot PoW/CAPTCHA, and database security sentinel. |
| **`APEX-OVERDRIVE-`** | `https://github.com/alexhack235-code/APEX-OVERDRIVE-.git` | APEX OVERDRIVE eSports Performance Suite: Multi-platform system optimizer, sub-0.5ms ultra-low kernel timer resolution, RAM standby cache flush, TCP BBR network congestion anti-lag, process priority quantization, and 60 FPS glassmorphic HUD dashboard (port 4888). |

## 🛠️ Management Commands

You can manage all external packages using the master ASTERIX CLI:

```bash
# Check installation and sync status of all packages
ax pkg status

# Clone or pull latest updates for all packages and rebuild binaries
ax pkg sync

# List all available packages in the ASTERIX registry
ax pkg list

# Rebuild native components (e.g. Rust anti-reverse sentinel)
ax pkg build
```

Alternatively, running `./setup.sh` from the repository root will automatically fetch and compile all required packages.