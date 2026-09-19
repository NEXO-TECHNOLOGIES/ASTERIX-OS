# ASTERIX OS - Project Rechange Specification

This project is locked to a clean, custom, source-first bare-metal approach.

## 1. Core Mandate (Enforced)

- No Ubuntu dependencies
- No WSL imitation
- No copied Linux distributions
- No heavy host installer clutter
- No forced dependency on a giant host OS setup
- Build from a minimal custom kernel structure and our own project layout

## 2. Realized Architecture

The kernel build is self-contained and builds from source:

- Native source files:
  - `kernel/src/boot.asm` (Multiboot bootstrap)
  - `kernel/src/isr.asm` (Interrupt service stubs)
  - `kernel/src/serial.c` (16550 UART driver)
  - `kernel/src/paging.c` (Hardware MMU two-tier paging)
  - `kernel/src/kernel.c` (Core coordinator, PMM, and scheduler)
- Minimal linker script: `kernel/linker.ld` (1MB load, 4KB page alignment)
- Independent build scripts: `kernel/build-kernel.ps1` and `kernel/build-kernel.sh`
- Lean standalone toolchain: `clang`, `nasm`, and `lld`

## 3. Verified Build Verification

The build produces a clean, freestanding 32-bit ELF executable:
- Artifact: `kernel/bin/asterix-microkernel.elf`
- Master CLI: `ax kernel` or `.\kernel\build-kernel.ps1`

## 4. Governing Rule for All Future Development

Any future work must respect this requirement:
The project must be developed as a clean custom OS from scratch, not as a copied Ubuntu/WSL environment or a bloated Windows-heavy setup.
