# 🚀 `ax` — Master CLI Dispatcher

The master command dispatcher for ASTERIX OS, providing a unified CLI interface across Linux, Android Termux, and Windows PowerShell.

---

## 📌 Usage

```bash
ax <command> [arguments...]
```

On Windows:
```powershell
ax <command> [arguments...]
# or
powershell -ExecutionPolicy Bypass -File bin/ax.ps1 <command>
```

---

## ⚙️ Core Subcommands

### System & Diagnostics
- `ax status`: Display live system telemetry (hostname, kernel, uptime, persistence status).
- `ax doctor [--fix]`: Comprehensive environment, port, and security audit.
- `ax verify`: Cryptographically audit codebase against `BUILD_MANIFEST.json`.

### Debian PRoot & Containers
- `ax debian [doctor|repair|shell]`: Inspect and self-heal the Debian rootless container.
- `ax folder [new|template|ls|tree|fix-perms]`: Mission folder creation and permission repair.
- `ax docker [run|build|compose]`: Launch the desktop container environment.

### Packaging & Distribution
- `ax deb build-all`: Build all 7 Kali-style Debian metapackages.
- `ax repo [build|serve]`: Generate or locally host an APT repository.

---

## 🔒 Security Constraints
- All command executions are unprivileged by default.
- Commands requiring elevated networking capabilities (raw sockets) gracefully detect environment limits and provide fallback implementations.
