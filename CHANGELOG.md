# Changelog

All notable changes to the **ASTERIX OS** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-09-16

### Added
- **Kali-Style Debian Metapackages**: Pure-Python zero-dependency `.deb` package builder (`scripts-hub/ax-deb-builder.py`) capable of generating standard Debian binary packages on any platform without requiring `dpkg-deb`.
  - Curated metapackages: `asterix-core`, `asterix-tools-network`, `asterix-tools-web`, `asterix-tools-wireless`, `asterix-tools-re`, `asterix-tools-crypto`, and top-level `asterix-default`.
- **Zero-Dependency APT Repository Engine**: Automated repository builder (`scripts-hub/ax-apt-repo.py`) creating `pool/main/`, `Packages`, `Packages.gz`, and `Release` indexes with MD5, SHA-1, and SHA-256 digests.
- **Cryptographically Verified Installer**: Secure installer (`install.sh`) verifying SHA-256 release integrity and enforcing semantic release pinning instead of floating `curl | bash` HEAD.
- **Continuous Integration Pipeline**: Enhanced GitHub Actions workflow (`.github/workflows/ci.yml`) with ShellCheck script linting, Python test suite runs, and clean containerized Debian Bookworm install validation.
- **Desktop Docker Testing Environment**: `Dockerfile` and `docker-compose.yml` for non-root desktop testing with PRoot parity on x86_64 and arm64.
- **Android 15 Native Linux Terminal (AVF) Evaluation**: In-depth architectural assessment (`docs/ANDROID15_LINUX_TERMINAL_AVF.md`) analyzing hardware virtualization (KVM/crosvm) vs user-space PRoot.
- **1-Page-Per-Tool Documentation**: Modular documentation site layout (`docs/tools/`) covering all core commands and subsystems with static site config (`mkdocs.yml`).
- **Community Governance & Standards**: Added `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1), and structured GitHub issue and pull request templates.

### Fixed
- Fixed PRoot APT sandbox failure mode by enforcing `APT::Sandbox::User "root"` in `/etc/apt/apt.conf.d/99termux-rootless`.
- Fixed systemd daemon initialization hangs by deploying `/usr/sbin/policy-rc.d` (`exit 101`).
- Fixed missing `/opt/ASTERIX-OS` bind mount in `asterix-termux-init.sh`.
- Fixed DNS resolution failure modes inside rootless Debian via automated fallback to Cloudflare/Google DNS.

### Security
- Eliminated 5 unaudited external repository clones from `install-termux.sh` to eliminate supply chain exposure.
- Removed silent error swallowing (`|| true`) in favor of structured step exit-code logging and an end-of-install Health Summary table.
- Deployed `SECURITY.md` establishing responsible disclosure contacts and a mandatory Authorized Testing Only legal policy.

---

## [2.0.0] - 2026-09-08

### Added
- **Dual-OS Architecture**: Added OS collaboration and fusion bridge (`os-computing/os_bridge.py`) for host-container synergy.
- **Pure-Rust Security Engines**: 9 compiled crates in `core-utils-rust/` for high-throughput packet analysis and log auditing.
- **Microkernel Core**: C kernel stubs with Multiboot compliance (`kernel/`).
- **Release Integrity Verifier**: Initial release manifest (`BUILD_MANIFEST.json`) with SHA-256 checksum tracking.
- **AI Security Engine**: Local memory caching and rule-based diagnostic healer in `asterix-ai/`.

---

## [1.0.0] - 2026-09-01

### Added
- Initial proof-of-concept release.
- Termux mobile initialization script and PRoot Debian rootless container setup.
- Basic shell toolbox and persistence volume mounter.
