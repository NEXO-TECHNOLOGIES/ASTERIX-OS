# 🧠 ASTERIX AI — Rule-Based Expert System & SOC Inference Engine

Welcome to **ASTERIX AI**, the native expert system and automated SOC (Security Operations Center) triage engine built specifically for ASTERIX OS.

ASTERIX AI operates on an **expert rule-based inference model** designed for air-gapped environments, lightweight edge nodes, Linux servers, and Termux mobile terminals. It requires **zero external cloud APIs**, **zero GPU overhead**, and operates completely offline using pure Python 3 or dependency-free native Bash.

---

## ⚡ Core Architecture

```
┌────────────────────────────────────────────────────────┐
│               ASTERIX AI INFERENCE ENGINE              │
├────────────────────────────────────────────────────────┤
│  CLI Entrypoint: ax ai [audit | ask "<query>" | rules] │
└───────────────────────────┬────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
    Python 3 Engine (engine.py)    Pure Bash Engine (engine.sh)
    [Full Heuristic Matching]     [Zero-Dependency Fallback]
              │                           │
              └─────────────┬─────────────┘
                            ▼
           Knowledge Base Directory (rules/)
       ├── security.json (ASLR, kptr, dmesg, SYN flood)
       ├── system.json   (swappiness, disk pressure, temp)
       └── network.json  (DNS leaks, promiscuous sniffing)
```

---

## 🛠️ Usage & Commands

### 1. Automated System & Security Audit
Evaluate all knowledge-base rules against the live operating system state and receive an instant resilience score and remediation plan:
```bash
ax ai audit
# or simply:
ax ai
```

### 2. Natural Language Expert Querying
Ask ASTERIX AI technical questions regarding troubleshooting, performance optimization, or exploit mitigations:
```bash
# Query memory and performance
ax ai ask "how do I fix memory swappiness and lag?"

# Query exploit mitigations
ax ai ask "check for aslr buffer overflow security"

# Query network attack defenses
ax ai ask "how to protect against syn flood ddos"
```

### 3. List Knowledge Base Rules
View all registered rules, their unique identifiers, severity ratings, and target kernel/system metrics:
```bash
ax ai rules
```

---

## 📋 Rule Definition Schema

All rules are defined in standard JSON format inside the `rules/` directory (`security.json`, `system.json`, `network.json`, or any custom `.json` file added).

```json
{
  "id": "SEC-001",
  "name": "Kernel ASLR Enforcement",
  "category": "security",
  "target": "/proc/sys/kernel/randomize_va_space",
  "expected": "2",
  "severity": "CRITICAL",
  "keywords": ["aslr", "memory", "buffer overflow", "randomization", "exploit"],
  "description": "Validates that Address Space Layout Randomization is locked at maximum entropy.",
  "pass_msg": "ASLR is fully enforced (Level 2).",
  "fail_msg": "ASLR is weakened or disabled.",
  "remediation": "sysctl -w kernel.randomize_va_space=2"
}
```

### Rule Fields:
- **`id`**: Unique identifier (e.g. `SEC-001`, `SYS-001`, `NET-001`).
- **`name`**: Short descriptive rule name.
- **`category`**: Category classification (`security`, `system`, `network`, `forensics`).
- **`target`**: Filesystem path (`/proc/...`, `/etc/...`) or dynamic metric key (`metric:disk_free_mb`, `metric:cpu_temp_c`, `metric:promisc_interfaces`).
- **`expected` / `expected_range`**: Anticipated value or acceptable range for compliance.
- **`severity`**: Incident priority (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
- **`keywords`**: Trigger terms for natural language query matching.
- **`description`**: Architectural context and risk explanation.
- **`pass_msg`**: Status statement when compliant.
- **`fail_msg`**: Threat indicator when non-compliant.
- **`remediation`**: Exact command required to resolve or harden the parameter.

---

## 🔒 Security & Performance Guarantee

1. **Deterministic Execution**: Pure rule evaluation with no probabilistic hallucinations or unpredictable behavior.
2. **Instant Response**: Under 5 milliseconds execution time on standard hardware.
3. **Dual Execution Runtime**: Automatically leverages `engine.py` when Python 3 is present; falls back seamlessly to `engine.sh` in minimal shell environments.
