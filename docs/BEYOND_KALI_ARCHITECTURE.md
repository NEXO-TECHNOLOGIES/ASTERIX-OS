# [RUN] Beyond Kali: The ASTERIX OS Architecture Specification

> **Mission**: Building an operating system and mobile security environment that moves beyond traditional 2010s pentest distribution models (like Kali Linux) by engineering first-class architecture, security-first defaults, reproducibility, workflow automation, and mobile optimization.

---

## [BANK] Executive Architectural Overview

Traditional security distributions evolved from live CDs (Whoppix, BackTrack, Kali). While they aggregate hundreds of tools, their architecture remains rooted in legacy patterns:
- Flat `root` shell habits across the entire session.
- Mutable systems where broken package updates or sketchy tools corrupt the OS.
- Unpinned metapackages (`apt install and hope`) lacking reproducibility.
- Siloed output formats (every tool outputs a different raw text/XML format).
- Lack of scope/authorization enforcement (tools blindly attack whatever IP is typed).
- Desktop-centric design with mobile treated as an afterthought chroot.

**ASTERIX OS** eliminates these limitations across 7 architectural pillars:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ASTERIX OS OMNI-ARCHITECTURE                                   │
├───────────────────────────────┬──────────────────────────────────┬───────────────────────────────┤
│ 1. KERNEL & FOUNDATIONS       │ 2. SECURITY-FIRST DEFAULTS       │ 3. TOOLING & PACKAGING        │
│ • Immutable Base + OverlayFS  │ • Granular Privileges (No Root)  │ • Nix-Style Toolchain Lock    │
│ • TPM 2.0 Measured Attestation│ • Plausible Deniability Vaults   │ • CycloneDX / SPDX SBOMs      │
│ • Seccomp-BPF & Namespaces    │ • Lab vs. Engagement Modes       │ • Throwaway 'Try' Sandboxes   │
│ • Rust in Security Path       │ • Per-App Network Isolation      │ • Unified JSON Project Model  │
├───────────────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ 4. WORKFLOW & REPORTING       │ 5. MOBILE & ON-DEVICE ANGLE      │ 6. SUPPLY CHAIN & PERFORMANCE │
│ • Engagement-Centric Vaults   │ • Native ARM64 First-Class       │ • Cryptographic Verifier      │
│ • Built-in Terminal Recorder  │ • Battery/Thermal Governor       │ • Merkle Transparency Log     │
│ • Signed Scope Authorization  │ • Android Scoped Storage Match   │ • GPU Compute Profiling       │
│ • Automated Report Synthesis  │ • Mobile-to-Desktop Handoff      │ • MicroVM Container Isolation │
└───────────────────────────────┴──────────────────────────────────┴───────────────────────────────┘
```

---

## 1. Kernel & Architecture Foundations

### 1.1 Immutable Base with Instant OverlayFS Rollback (`ax overlay`)
ASTERIX OS decouples the base system from user modifications:
- **Lower Layer (`/lower`)**: Read-only, cryptographically verified base image.
- **Upper Layer (`/upper`)**: Mutable transactional directory mounted via OverlayFS.
- **Instant Rollback (`ax overlay rollback`)**: Purging the upper layer instantly restores the operating system to its bit-identical factory baseline. If a third-party tool corrupts dependencies or installs questionable files, a single command or reboot wipes all modifications without reinstalling.

### 1.2 TPM 2.0 Measured Boot & Chain-of-Custody Attestation (`ax attest`)
- Prior to launching an assessment, ASTERIX OS measures core kernels (`PCR 0`), bootloaders (`PCR 2`), master command dispatchers (`PCR 4`), and security policies (`PCR 7`).
- Emits a cryptographic composite measurement and chain-of-custody token (`AX-ATTEST-<HASH>`) suitable for legal court proceedings and client audit reports, proving the workstation was free of tampering before engagement commencement.

### 1.3 Kernel Seccomp-BPF Sandboxing & Namespaces (`ax isolate`)
- Risky or untrusted tools execute inside isolated user, mount, and PID namespaces with seccomp-bpf syscall filters, preventing rogue exploits or supply-chain payloads from accessing host files.

---

## 2. Security-First Defaults (Not Opt-In)

### 2.1 Dual Operational Modes: `Lab` vs. `Engagement` (`ax mode`)
- **`Lab Mode`**: Relaxed scope boundaries, verbose CTF/learning hints, and unrestricted experimental execution.
- **`Engagement Mode`**: Strict scope validation enabled. Every scan or exploit requires verification against a signed scope certificate. Destructive actions against unauthorized CIDRs are strictly blocked.

### 2.2 Granular Scope & Authorization Gating (`ax scope-check`)
- Pentesting tools verify target IPs against `scope.json`.
- Validates authorized CIDRs, domain wildcards, and explicit prohibited exclusions.
- Generates an immutable, timestamped entry in `audit_trail.log` recording operator ID, action, and scope compliance.

### 2.3 Plausible-Deniability Encrypted Persistence (`ax vault`)
- Full-volume cryptographic encryption supporting secondary decoy passes for high-risk border crossings or physical seizure threat models.

### 2.4 RAM Memory Hygiene & Sanitization (`ax mem-hygiene`)
- Flushes active Python process heaps, overwrites memory buffers with zeros, and purges kernel page caches (`/proc/sys/vm/drop_caches`) on shutdown to prevent cold-boot memory extraction of live credentials and loot.

---

## 3. Tooling & Package Ecosystem

### 3.1 Unified Project Data Model (`schemas/asterix_project_schema.json`)
Instead of each tool saving in its own siloed format:
- Hosts, ports, services, discovered credentials, and technical findings synchronize into a single JSON schema (`project.json`).
- High-level tools query the shared knowledge graph directly.

### 3.2 Automated SBOM Generation (`ax sbom`)
- Generates industry-standard **CycloneDX v1.5** and **SPDX v2.3** Software Bills of Materials on demand, satisfying modern enterprise compliance and supply-chain auditing mandates.

### 3.3 Throwaway Micro-Sandbox ('Try Before Install') (`ax try`)
- Executes community scripts or GitHub repositories inside an ephemeral throwaway directory. Once the command finishes, the entire sandbox is unlinked, leaving 0 bytes written to host persistence.

---

## 4. Workflow & UX Innovations

### 4.1 Engagement-Centric Workspaces (`ax engagement new`)
Workspaces are organized around clients and projects rather than generic home folders:
```
asterix_persistent/engagements/<job-id>/
├── project.json       # Unified data model
├── scope/             # Signed authorization certificate
├── scans/             # Output from nmap, web-structure, net-sentinel
├── evidence/          # Proof-of-concept logs & captures
├── loot/              # Discovered hashes, tokens, credentials
├── notes/             # Analyst documentation
├── reports/           # Synthesized client report markdown
└── timeline/          # Cryptographic audit_trail.log
```

### 4.2 Automated Client Report Pipeline (`ax report`)
- Automatically synthesizes Markdown assessment reports directly from `project.json` and `audit_trail.log`.
- Generates executive summaries, severity count matrices, scope validation proofs, host inventory tables, and remediation recommendations.

---

## 5. Mobile & On-Device Optimization

### 5.1 Dynamic Battery & Thermal Governor (`ax governor`)
- Continuously tracks CPU thermal zones (`/sys/class/thermal/`) and battery state.
- Automatically throttles high-concurrency tools (`hashcat`, `masscan`, `net-sentinel`) when battery < 20% or CPU temperature > 75°C, preventing device damage and unexpected shutdowns in the field.

### 5.2 Mobile-to-Desktop Handoff (`ax handoff`)
- Field operators can begin reconnaissance on an Android mobile phone (Termux / AVF) and export/sync the exact engagement workspace state to a desktop workstation with zero data loss.

---

## 6. Supply Chain Trust & Transparency Log

### 6.1 Cryptographic Transparency Log (`ax transparency`)
- Implements an in-toto / Sigstore style append-only Merkle hash chain (`TRANSPARENCY_LOG.jsonl`).
- Every package release is logged with index, builder identity, SHA-256 digest, and previous entry hash, allowing anyone to verify provenance and detect unauthorized package injection.

---

## 7. Master Command Quick Reference

| Command | Subsystem | Description |
| :--- | :--- | :--- |
| `ax engagement new <client> <job>` | Workflow | Initialize an engagement-centric workspace |
| `ax engagement report` | Reporting | Synthesize an executive & technical assessment report |
| `ax mode [lab\|engagement]` | Security Defaults | Toggle between relaxed Lab and strict Engagement mode |
| `ax scope <target>` | Scope Gating | Verify target authorization before scan/exploit |
| `ax overlay [status\|rollback]` | Foundations | Inspect or instantly revert mutable filesystem layer |
| `ax try <command>` | Sandboxing | Run an unfamiliar tool in an ephemeral throwaway sandbox |
| `ax attest` | Measured Boot | Generate TPM 2.0 chain-of-custody attestation token |
| `ax sbom` | Supply Chain | Generate CycloneDX v1.5 Software Bill of Materials |
| `ax transparency [log\|verify]`| Trust | Append or cryptographically audit package provenance |
| `ax governor` | Mobile Performance | Inspect battery/thermal throttling status & recommendations |
| `ax gpu` | Performance | Discover compute platforms and generate tuned hashcat profiles |
| `ax mem-hygiene` | Security Defaults | Purge RAM heap buffers and kernel page cache |
| `ax handoff [export\|import]` | Mobile Sync | Sync engagement state between phone and desktop |
