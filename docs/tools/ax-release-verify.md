# 🔐 `ax-release-verify` — Cryptographic Release & Supply Chain Verifier

Audits files against `BUILD_MANIFEST.json` to detect tampering, corruption, or unverified supply chain alterations.

---

## 📌 Usage

```bash
ax verify [--manifest <path>] [--update]
```

Direct script invocation:
```bash
python scripts-hub/ax-release-verify.py
```

---

## ⚙️ Key Capabilities

- Computes SHA-256 digests across all system kernels, binaries, Rust crates, and scripts.
- Flags modified, missing, or mismatched artifacts with exit code `1` (suitable for CI/CD gates).
- Allows project maintainers to recalculate signed hashes using `--update` when releasing new versions.
