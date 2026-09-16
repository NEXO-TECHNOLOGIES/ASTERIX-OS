# Security Policy & Governance

## 1. Authorized Testing & Ethical Use Notice

> [!IMPORTANT]
> **STRICTLY FOR AUTHORIZED SECURITY RESEARCH & DEFENSIVE TELEMETRY ONLY**
>
> ASTERIX OS bundles defensive telemetry, network auditing, forensic tools, and packet analysis utilities (such as `nmap`, `tcpdump`, and `tshark`). These tools are provided exclusively for authorized penetration testing, vulnerability assessment, defensive telemetry, systems administration, and security education on infrastructure you own or have explicit, documented, written authorization to examine.
>
> Unauthorized scanning, packet interception, network disruption, or exploitation of computer systems without prior mutual written consent is illegal across most jurisdictions and strictly prohibited by the ASTERIX OS project policy. Users are individually and solely responsible for verifying and complying with all applicable local, national, and international laws before running any tool bundled with this platform.

---

## 2. Supply Chain & Packaging Integrity

ASTERIX OS strictly adheres to verifiable software supply chain standards:
* **No Unaudited Third-Party Cloning**: The installer does not auto-clone, execute, or grant arbitrary execution permissions to third-party repositories.
* **Cryptographic Release Verification**: Official release tarballs and images are checksummed with SHA-256 signatures published in `BUILD_MANIFEST.json`.
* **Standard Distribution Repositories**: All runtime packages in the Debian rootless subsystem are pulled directly from official Debian and Termux upstream mirrors via signed repositories.
* **Least Privilege Permissions**: Scripts and utilities are deployed with minimal necessary permissions (avoiding blanket executable marks on unknown files).

---

## 3. Reporting a Security Vulnerability

The ASTERIX OS engineering team takes security reports seriously. If you discover a vulnerability, security defect, or supply chain exposure within ASTERIX OS or its subcomponents, please report it through private responsible disclosure:

### Preferred Disclosure Method
- **GitHub Security Advisory**: Submit a private report via the [Security Advisories](https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS/security/advisories) tab.
- **Direct Security Email**: Send details and proof-of-concept to `security@nexo-tech.internal` (or repository maintainers).

### Please Include
1. A clear description of the vulnerability and affected components (`termux-mobile/`, `core-utils-*`, `bin/ax`, etc.).
2. Step-by-step reproduction instructions or a minimal proof-of-concept.
3. The potential impact (e.g., local privilege escalation, arbitrary code execution, unintended data exposure).
4. Any proposed remediations or patches if available.

### Disclosure Response Timeline
* **Initial Acknowledgement**: Within 48 hours of receipt.
* **Severity Assessment & Triage**: Within 5 business days.
* **Remediation & Patch Release**: Typically within 14–30 business days depending on complexity.
* **Public Disclosure**: Coordinated following the release of the remediation patch.

---

## 4. Supported Versions

Security updates are prioritized for the current active release line:

| Version | Status | Security Support |
| :--- | :--- | :--- |
| **v2.x (Current / Main)** | Active | Supported (Full patches and bug fixes) |
| **v1.x (Legacy)** | End-of-Life | Not supported (Upgrade recommended) |
