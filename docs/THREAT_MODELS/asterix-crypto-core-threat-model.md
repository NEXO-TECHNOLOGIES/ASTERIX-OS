# 🛡️ Threat Model: `asterix-crypto-core`
## Cryptographic Identification, Hash Auditing & Verification Engine

### 1. Component Overview
- **Binary**: `asterix-crypto-core`
- **Language**: 100% Native Safe Rust (Zero External Crates)
- **Role**: Tier-1 Hash Format Identification, Integrity Verification, Dictionary Auditing & Cryptographic Analysis.
- **Supported Algorithms**: MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, NTLM, and UNIX crypt hashes.

---

### 2. Detection Capabilities (What It Identifies)
- **Hash Type Identification**: Automatically determines hash type based on bit length, encoding format (hex, base64, modular crypt format), and salt prefixes across 40+ hash classifications.
- **Known Weak Hashes**: Flags collisions and vulnerable algorithms (e.g., MD5 and SHA-1 in cryptographic certificates or signatures).
- **Integrity Validation**: Computes microsecond-accurate SHA-256/SHA-512 manifests across directories to detect unauthorized modification or file tampering.

---

### 3. Limitations & Non-Detection Scenarios
- **Memory-Hard KDFs**: Verification speed on memory-hard key derivation functions (Argon2id, scrypt) is intentionally constrained by the target function parameters; GPU offloading is not supported natively within the lightweight zero-dependency binary.
- **Salts Unknown**: Hashes with unknown or dynamic per-record salts without format headers cannot be classified by length alone.

---

### 4. Operational Security
- **Side-Channel Protections**: Uses constant-time comparison routines for password and token matching to prevent timing side-channel attacks.
- **Zero Heap Spilling**: Zeroizes sensitive candidate buffers in memory upon routine completion.
