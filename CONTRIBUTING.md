# Contributing to ASTERIX OS

Thank you for your interest in contributing to **ASTERIX OS**! We welcome contributions from systems engineers, cybersecurity professionals, and mobile developers who share our vision of building the most **transparent, hardened, and reproducible mobile rootless security environment**.

---

##  Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) and uphold the [Authorized Testing Only](SECURITY.md) guidelines.

---

##  Development Setup & Standards

### 1. Zero External Dependency Policy for Core Scripts
To guarantee instant execution across mobile Android Termux, embedded systems, and minimal Linux containers:
- **Core helper scripts (`scripts-hub/`) must use 100% Python Standard Library**.
- Do not introduce external `pip` dependencies into foundational dispatchers or installer scripts without maintainer review.

### 2. POSIX Compatibility & Shell Standards
- All shell scripts in `termux-mobile/`, `bin/`, and `debian-packages/` must pass [ShellCheck](https://www.shellcheck.net/) with zero critical warnings.
- Avoid Bash-isms in portable scripts that may run under `sh` or `dash`.
- Never use blanket `|| true` to suppress exit codes on critical operations. Use structured logging and exit code validation.

### 3. Cryptographic Verification Integrity
Whenever you modify files tracked in [`BUILD_MANIFEST.json`](BUILD_MANIFEST.json):
```bash
# Verify integrity
python scripts-hub/ax-release-verify.py

# Update manifest after deliberate, verified modifications
python scripts-hub/ax-release-verify.py --update
```

---

## [TEST] Testing Your Changes

Before submitting a pull request, you must run the local automated test suite:

```bash
# 1. Test Debian Rootless & Folder Management Subsystems
python python-lab/test_debian_rootless.py

# 2. Test Debian Packaging & APT Repository Generator
python python-lab/test_packaging_and_repo.py

# 3. Test Cryptographic Manifest
python scripts-hub/ax-release-verify.py
```

All tests must pass (`OK`).

---

## [TWIST] Submitting a Pull Request

1. Fork the repository and create a descriptive branch: `git checkout -b feat/your-feature-name`.
2. Follow Conventional Commits format:
   - `feat(subsystem): add new capability`
   - `fix(proot): resolve permissions bug`
   - `docs(tools): update command documentation`
3. Push to your fork and submit a PR against `main`.
4. Ensure all CI checks (ShellCheck, Python Test Suite, Clean Debian Container Test) pass.
