# ASTERIX OS - Freestanding Cyber Microkernel Core

Technical specification and architectural manual for the ASTERIX OS custom microkernel.

## Architectural Overview

ASTERIX Microkernel is a freestanding, zero-libc, 32-bit x86 protected mode microkernel engineered from source. It contains no external runtime dependencies, no copied Linux environments, and no host installer baggage.

```
+-------------------------------------------------------------------------+
|                        ASTERIX OS Microkernel Core                      |
+-------------------------------------------------------------------------+
|  VGA Console (0xB8000)  |  16550 UART (COM1 0x3F8)  | Syscall (int 0x80)|
+-------------------------+---------------------------+-------------------+
|               Round-Robin Process Scheduler (PCBs)                      |
+-------------------------------------------------------------------------+
| Hardware MMU Paging (CR0.PG, CR3, Page Directory/Tables, CR2 Handler)   |
+-------------------------------------------------------------------------+
| Physical Memory Manager (PMM: Bitmap Frame Allocator across RAM)        |
+-------------------------------------------------------------------------+
| Interrupt Descriptor Table (IDT: 256 Gates) | 8259 PIC Remapper (32-47) |
+-------------------------------------------------------------------------+
| Global Descriptor Table (GDT) | Multiboot v1 Header | Protected Mode    |
+-------------------------------------------------------------------------+
|                            x86 Hardware / QEMU                          |
+-------------------------------------------------------------------------+
```

---

## Subsystem Specifications

### 1. Bootstrap & CPU Context (`src/boot.asm`)
* **Specification**: Conforms strictly to the GNU Multiboot v1 standard (`0x1BADB002`).
* **GDT Configuration**:
  - `0x00`: Null Descriptor
  - `0x08`: Kernel Code Segment (Base 0, Limit 4GB, Ring 0, Exec/Read)
  - `0x10`: Kernel Data Segment (Base 0, Limit 4GB, Ring 0, Read/Write)
  - `0x18`: User Code Segment (Base 0, Limit 4GB, Ring 3, Exec/Read)
  - `0x20`: User Data Segment (Base 0, Limit 4GB, Ring 3, Read/Write)
* **Stack**: 32 KB initial kernel stack allocated in `.bss`.

### 2. Interrupts & Exceptions (`src/isr.asm`, `include/idt.h`)
* **IDT**: 256 gates with complete CPU state preservation macros.
* **Exceptions (0-31)**: Dedicated entry stubs for all x86 exceptions (Divide Error, Double Fault, GP Fault, etc.).
* **Hardware IRQs (32-47)**: Master and Slave 8259 PICs remapped from default BIOS interrupts to avoid CPU exception collisions.
* **Syscall Gateway**: Software interrupt `int 0x80` (ISR 128) routed to `syscall_dispatch()`.

### 3. Hardware MMU Two-Tier Virtual Memory (`src/paging.c`, `include/paging.h`)
* **Hardware Enforcement**: Page Directory and Page Tables are 4096-byte aligned. Paging is actively enabled by loading `CR3` and setting bit 31 (`CR0.PG`).
* **Memory Map**: 8 MB identity mapping covering real-mode IVT, BIOS, VGA buffer (`0x000B8000`), 1 MB kernel load space, stack, and frame management tables.
* **Page Fault Handler**: Interrogates Control Register 2 (`CR2`) upon Exception 14, extracting the faulting linear address, faulting `EIP`, and decoding violation flags (`NOT_PRESENT`, `WRITE`, `USER_MODE`, `RESERVED`, `INSTRUCTION_FETCH`).

### 4. Physical Memory Manager (`src/kernel.c`, `include/kernel.h`)
* **Bitmask Allocator**: Dynamically sizes physical memory management frames based on Multiboot memory detection.
* **Operations**: Fast `pmm_alloc_frame()` and `pmm_free_frame()` with page-aligned tracking.

### 5. Dual-Channel Output Drivers
* **16550 UART Serial (`src/serial.c`, `include/serial.h`)**: Base port `0x03F8` (COM1), 38,400 baud, 8N1, 14-byte FIFO buffer, hardware loopback self-test.
* **VGA Text Console (`include/vga.h`)**: Direct video buffer operations at `0x000B8000`, 80x25 text mode, color attribute formatting.

---

## Build System & Verification

### Prerequisites
* `clang` (LLVM 18+ or 23+)
* `nasm` (v2.16+ or 3.02+)
* `lld` (LLVM Linker)

### Building the Kernel

From the repository root:
```powershell
# PowerShell
.\bin\ax.ps1 kernel

# Bash / Git Bash
./bin/ax kernel
```

Direct script execution:
```powershell
cd kernel
powershell.exe -ExecutionPolicy Bypass -File .\build-kernel.ps1
```

### Build Artifacts
Outputs are placed under `kernel/bin/`:
* `asterix-microkernel.elf` - 32-bit ELF executable (`EM_386`), entry at `0x100010`.
* `asterix-microkernel.bin` - Raw binary image for direct bootloaders.

### Running in QEMU
```powershell
.\kernel\build-kernel.ps1 --run
# Or directly:
qemu-system-i386 -kernel kernel/bin/asterix-microkernel.elf -serial stdio
```

---

## Strict RECHANGE Discipline
* Zero emojis, zero unicode artifacts in kernel buffers.
* 100% pure 7-bit ASCII throughout all sources.
* No Ubuntu, WSL, or host-cloned environments required.
