#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS - Custom Microkernel Build Script (Source-First, Zero-Host-Bloat)
# Assembles boot.asm & isr.asm and compiles kernel.c using minimal freestanding toolchain
# Conforms to RECHANGE.md: No Ubuntu, No WSL, No apt-get, No external Linux downloads
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
BIN_DIR="${SCRIPT_DIR}/bin"
SRC_DIR="${SCRIPT_DIR}/src"
INC_DIR="${SCRIPT_DIR}/include"

mkdir -p "${BUILD_DIR}" "${BIN_DIR}"

NASM="${NASM:-nasm}"
CC="${CC:-clang}"
if ! command -v "$CC" >/dev/null 2>&1; then
    CC="gcc"
fi

echo "[ASTERIX KERNEL] Building custom microkernel from local sources..."

# 1. Assemble Multiboot Bootstrap Stub
echo "[ASTERIX KERNEL] Assembling bootloader: ${SRC_DIR}/boot.asm"
"$NASM" -f elf32 "${SRC_DIR}/boot.asm" -o "${BUILD_DIR}/boot.o"

# 2. Assemble Interrupt Service Routines & IRQ Stubs
echo "[ASTERIX KERNEL] Assembling ISR stubs: ${SRC_DIR}/isr.asm"
"$NASM" -f elf32 "${SRC_DIR}/isr.asm" -o "${BUILD_DIR}/isr.o"

# 3. Compile 16550 UART Serial Console Driver
echo "[ASTERIX KERNEL] Compiling serial driver: ${SRC_DIR}/serial.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/serial.c" -I"${INC_DIR}" -o "${BUILD_DIR}/serial.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/serial.c" -I"${INC_DIR}" -o "${BUILD_DIR}/serial.o"
fi

# 4. Compile Hardware MMU Paging Driver
echo "[ASTERIX KERNEL] Compiling paging driver: ${SRC_DIR}/paging.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/paging.c" -I"${INC_DIR}" -o "${BUILD_DIR}/paging.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/paging.c" -I"${INC_DIR}" -o "${BUILD_DIR}/paging.o"
fi

# 5. Compile Dynamic Heap Allocator
echo "[ASTERIX KERNEL] Compiling heap allocator: ${SRC_DIR}/heap.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/heap.c" -I"${INC_DIR}" -o "${BUILD_DIR}/heap.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/heap.c" -I"${INC_DIR}" -o "${BUILD_DIR}/heap.o"
fi

# 6. Compile 8254 PIT Timer Driver
echo "[ASTERIX KERNEL] Compiling timer driver: ${SRC_DIR}/timer.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/timer.c" -I"${INC_DIR}" -o "${BUILD_DIR}/timer.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/timer.c" -I"${INC_DIR}" -o "${BUILD_DIR}/timer.o"
fi

# 7. Compile PS/2 Keyboard Driver
echo "[ASTERIX KERNEL] Compiling keyboard driver: ${SRC_DIR}/keyboard.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/keyboard.c" -I"${INC_DIR}" -o "${BUILD_DIR}/keyboard.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/keyboard.c" -I"${INC_DIR}" -o "${BUILD_DIR}/keyboard.o"
fi

# 8. Compile Virtual File System (VFS)
echo "[ASTERIX KERNEL] Compiling VFS ramdisk: ${SRC_DIR}/vfs.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/vfs.c" -I"${INC_DIR}" -o "${BUILD_DIR}/vfs.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/vfs.c" -I"${INC_DIR}" -o "${BUILD_DIR}/vfs.o"
fi

# 9. Compile Interactive Shell
echo "[ASTERIX KERNEL] Compiling interactive shell: ${SRC_DIR}/shell.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/shell.c" -I"${INC_DIR}" -o "${BUILD_DIR}/shell.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/shell.c" -I"${INC_DIR}" -o "${BUILD_DIR}/shell.o"
fi

# 10. Compile C Microkernel Core
echo "[ASTERIX KERNEL] Compiling C core: ${SRC_DIR}/kernel.c"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/kernel.c" -I"${INC_DIR}" -o "${BUILD_DIR}/kernel.o"
else
    "$CC" -m32 -ffreestanding -fno-stack-protector -fno-pie -fno-builtin \
        -O2 -Wall -Wextra -c "${SRC_DIR}/kernel.c" -I"${INC_DIR}" -o "${BUILD_DIR}/kernel.o"
fi

# 11. Link Microkernel ELF Binary
echo "[ASTERIX KERNEL] Linking kernel image via ${SCRIPT_DIR}/linker.ld"
if [ "$CC" = "clang" ]; then
    "$CC" -target i386-unknown-none-elf -nostdlib -Wl,-T,"${SCRIPT_DIR}/linker.ld" \
        -o "${BIN_DIR}/asterix-microkernel.elf" \
        "${BUILD_DIR}/boot.o" "${BUILD_DIR}/isr.o" "${BUILD_DIR}/serial.o" "${BUILD_DIR}/paging.o" \
        "${BUILD_DIR}/heap.o" "${BUILD_DIR}/timer.o" "${BUILD_DIR}/keyboard.o" "${BUILD_DIR}/vfs.o" \
        "${BUILD_DIR}/shell.o" "${BUILD_DIR}/kernel.o"
else
    "$CC" -m32 -nostdlib -Wl,-T,"${SCRIPT_DIR}/linker.ld" \
        -o "${BIN_DIR}/asterix-microkernel.elf" \
        "${BUILD_DIR}/boot.o" "${BUILD_DIR}/isr.o" "${BUILD_DIR}/serial.o" "${BUILD_DIR}/paging.o" \
        "${BUILD_DIR}/heap.o" "${BUILD_DIR}/timer.o" "${BUILD_DIR}/keyboard.o" "${BUILD_DIR}/vfs.o" \
        "${BUILD_DIR}/shell.o" "${BUILD_DIR}/kernel.o"
fi

cp -f "${BIN_DIR}/asterix-microkernel.elf" "${BIN_DIR}/asterix-microkernel.bin"

echo ""
echo "[+] Custom ASTERIX microkernel build complete."
echo "    ELF Image: ${BIN_DIR}/asterix-microkernel.elf"
echo "    Raw Binary: ${BIN_DIR}/asterix-microkernel.bin"
echo ""
