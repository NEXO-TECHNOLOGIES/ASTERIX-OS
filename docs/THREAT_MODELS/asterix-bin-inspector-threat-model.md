# 🛡️ Threat Model: `asterix-bin-inspector`
## Binary Inspection, Format Analysis & Section Entropy Engine

### 1. Component Overview
- **Binary**: `asterix-bin-inspector`
- **Language**: 100% Native Safe Rust (Zero Dependencies)
- **Role**: Tier-1 Static Binary Analysis, Header & Section Validation, Entropy Measurement.
- **Supported Formats**: ELF (32/64-bit, Little/Big Endian), PE32 / PE32+ (Windows), Mach-O (macOS).

---

### 2. Detection Capabilities (What It Identifies)
- **Packed / Encrypted Payloads**: Computes Shannon entropy per binary section; sections with entropy values > 7.2 are flagged as packed, encrypted, or compressed.
- **Known Packer Signatures**: Detects common packing signatures including UPX, ASPack, Petite, and customized stub markers.
- **Section Anomaly Warnings**: Identifies anomalous section flags, such as executable plus writable flags (W^X violations), zero raw size with large virtual size, or non-standard entry points.
- **Compiler & Toolchain Signatures**: Extracts build artifacts, import tables, exported functions, and debug paths without executing target code.

---

### 3. Limitations & Non-Detection Scenarios
- **Dynamic Unpacking**: As a static analysis tool, it does not dynamically execute code in an instrumented VM; multi-stage self-modifying payloads cannot be observed post-unpacking.
- **Custom High-Entropy Data**: Legitimate compressed assets (JPEG, embedded zlib data) inside a binary will exhibit elevated entropy and may produce benign false positives.
- **Polymorphic Encoders**: Custom multi-byte XOR or rotational ciphers without standardized stub structures require manual disassembly verification.

---

### 4. Operational Security & Safety
- **Memory Safety**: Written completely in safe Rust, preventing memory corruption vulnerabilities (buffer overflows, use-after-free) even when parsing maliciously crafted or corrupted headers.
- **Isolation**: Operates strictly read-only on target files; zero temporary file creation or execution hooks.
