# ⚡ ASTERIX Auto-Compiler // Autonomous Self-Healing Build Engine

The **ASTERIX Auto-Compiler** (`auto-compiler/`) is an autonomous multi-language compilation and heuristic source repair system built directly into ASTERIX OS.

It intercepts compiler diagnostics and syntax errors in real-time, automatically repairs broken code without manual intervention, injects missing standard headers and library flags, and repeatedly recompiles until a hardened binary is produced.

---

## 🛠️ Key Capabilities

- **Zero-Manual Code Healing**:
  - **Implicit Function Resolution**: Automatically identifies undeclared standard library functions (`printf`, `malloc`, `strlen`, `fork`, `close`) and injects the corresponding `#include` statements (`<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<unistd.h>`).
  - **Missing Semicolon Correction**: Uses compiler line-and-column diagnostic tokens to locate missing `;` terminators, creates a `.bak` backup, and inserts the missing token.
  - **Linker Flag Auto-Resolution**: When code triggers `undefined reference` for math, threads, networking, or cryptography, the compiler dynamically adds `-lm`, `-lpthread`, `-lssl`, `-lcrypto`, `-lpcap`, `-lcurl`, or `-lz`.
  - **Header-to-Package Mapping**: Uses `recipes/headers.json` to resolve missing library headers to native Linux distribution packages (`libssl-dev`, `libpcap-dev`, `libcurl4-openssl-dev`).
  - **Symbol Stripping**: Automatically strips debug symbols using `strip --strip-unneeded` to reduce final binary footprint by up to 70%.

---

## 💻 Supported Languages & Tools

| Language | Primary Compiler | Heuristic Auto-Fixes Supported |
| :--- | :--- | :--- |
| **C (`.c`)** | `gcc` / `clang` | Missing headers, semicolons, linker flags (`-lm`, `-lpthread`, `-lssl`), `-Werror` relaxation |
| **C++ (`.cpp`, `.cc`)** | `g++` / `clang++` | Missing STL includes, library flags, symbol resolution |
| **Rust (`.rs`)** | `rustc` / `cargo` | Auto-release profile (`-O`), workspace build detection |
| **Go (`.go`)** | `go build` | Automated package builds, output naming |
| **Assembly (`.asm`, `.s`)** | `nasm` + `ld` | ELF64 object generation & executable linking |
| **Project Trees** | `make` / `cargo` / `go` | Automatic root build manifest detection (`Makefile`, `Cargo.toml`, `go.mod`) |

---

## 🚀 CLI Usage

```bash
# Auto-compile a C source file with self-repair
ax auto-compile exploit_tester.c

# Compile with custom flags
ax auto-compile network_radar.cpp -Wall

# Auto-compile an entire Rust or C project directory
ax auto-compile ./core-utils-rust/asterix-crypto-core
```
