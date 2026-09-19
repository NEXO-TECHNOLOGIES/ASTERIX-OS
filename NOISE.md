# ASTERIX OS - Noise Elimination & De-bloat Log

This document records the cleanup, de-bloating, and discipline enforcement undertaken to transform ASTERIX OS from an unfocused concept bundle into a hardened, verifiable operating system project.

---

## 1. Noise Eliminated

### A. Environment Noise & Toolchain Drift (REMOVED)
* **Previous Noise**: Trying to bootstrap full Ubuntu environments, WSL wrappers, external Linux image downloads, and Dockerfiles.
* **Elimination**: Completely purged. All kernel compilation relies strictly on minimal, standalone native binaries:
  - `nasm` (32-bit ELF assembly)
  - `clang` (cross-compilation targeting `i386-unknown-none-elf`)
  - `lld` (direct ELF linking)
* **Result**: The host machine stays clean. Zero gigabytes of WSL/Ubuntu clutter.

### B. Visual Noise & Unicode Corruption (PURGED)
* **Previous Noise**: Emojis (`??`, `?`), em-dashes, and multi-byte UTF-8 sequences in kernel headers, source files, and terminal prints.
* **Why it was Noise**: Low-level x86 VGA text memory (`0x000B8000`) uses Code Page 437. UTF-8 multi-byte sequences result in corrupt screen characters and broken serial output.
* **Elimination**: Audited every single kernel source and build script. Replaced with pure, clean 7-bit ASCII.

### C. Linker Syntax Noise (FIXED)
* **Previous Noise**: Deprecated GNU ld directives (`BLOCK(4K)`) that prevented modern LLVM linkers (`ld.lld`) from completing builds.
* **Elimination**: Refactored `kernel/linker.ld` to use standard `: ALIGN(4K)` boundaries. Compatible with both LLVM and GNU toolchains.

### D. Silent Failure Noise (HARDENED)
* **Previous Noise**: The kernel ran in flat, unpaged protected mode with no memory isolation. Memory corruption resulted in silent CPU lockups.
* **Elimination**:
  - Activated hardware MMU Two-Tier Paging (`CR0.PG`, `CR3`).
  - Implemented Exception 14 Page Fault handler that dumps linear addresses from `CR2` and error flags to COM1 and VGA.

---

## 2. The Hard Rule of Discipline (Active)

Every component of ASTERIX OS is now held to three permanent standards:

1. **Bare-Metal Autonomy**:
   The microkernel must boot and execute on bare metal or hardware emulators (QEMU, Bochs, VirtualBox) without depending on a host operating system.
2. **Single Build Truth**:
   The canonical build path is `ax kernel` (or `.\kernel\build-kernel.ps1`). If a feature does not compile through this path, it does not ship.
3. **No Decorative Noise**:
   Keep code serious, technical, and clean. No emojis, no bloated dependencies, no unverified claims.

---

## 3. Project Separation & Boundary Line

To permanently prevent the "kitchen sink" repo problem identified in NOISE.md:
* **Core Kernel Tier (`kernel/`)**: Pure freestanding C, Assembly, Linker script, Hardware Drivers. Independent and isolated.
* **Distributed Compute Tier (`core-utils-rust/`, `os-computing/`)**: Native Rust/AVX2 cluster computing engine and symmetrical OS bridging.
* **Master Dispatcher (`bin/`)**: Lightweight orchestration CLI (`ax` / `ax.ps1`) providing single-command access to all subsystems.
