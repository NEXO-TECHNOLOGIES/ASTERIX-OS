# 📦 `ax-debian-manager` — Debian Rootless Subsystem & Folder Engine

A zero-dependency Python engine that manages the Debian rootless (`proot-distro`) container, manages the 10-tier mission folder architecture, and eliminates PRoot failure modes.

---

## 📌 Usage

```bash
ax debian [doctor|repair|enter]
ax folder [new|template|ls|tree|fix-perms]
```

Direct script invocation:
```bash
python scripts-hub/ax-debian-manager.py <command> [args...]
```

---

## ⚙️ Key Capabilities

### 1. Rootless Failure Self-Healing (`ax debian repair`)
Remediates common PRoot and Termux issues:
- Configures `/etc/apt/apt.conf.d/99termux-rootless` (`APT::Sandbox::User "root";`) to fix `_apt` permission denied errors.
- Deploys `/usr/sbin/policy-rc.d` (`exit 101`) to prevent daemons from crashing container updates.
- Injects reliable DNS resolvers into `/etc/resolv.conf`.
- Mounts `/dev/shm` and restores `/tmp` permissions.

### 2. Mission Folder Architecture (`ax folder`)
Maintains 10 persistent, isolated mission folders across `/asterix_persistent`:
- `projects/`, `scans/`, `loot/`, `captures/`, `reports/`, `notes/`, `scripts/`, `payloads/`, `wordlists/`, `workspace/`

### 3. Template Generation (`ax folder new <path> --template <type>`)
Generates structured mission templates:
- `web`: Scope, target URLs, authentication notes, vulnerability checklist.
- `recon`: Subdomain discovery checklists, IP blocks, DNS enum targets.
- `re`: Binary metadata, disassembler notes, decompiled function logs.
- `exploit`: Proof-of-concept scripts, payloads, execution notes.

### 4. Permission Self-Repair (`ax folder fix-perms`)
Removes stale package manager lockfiles (`apt.lock`, `.dpkg-lock`) and restores `755` read/write permissions.
