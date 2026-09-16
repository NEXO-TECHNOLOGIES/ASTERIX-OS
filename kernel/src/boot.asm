; =====================================================================
; 🌌 ASTERIX OS — Freestanding Multiboot Kernel Bootstrap Stub (x86)
; Architecture: 32-bit Protected Mode (i386 / x86_32)
; Conforms to Multiboot v1 Specification (GNU GRUB & QEMU direct boot)
; Assembler: NASM (nasm -f elf32 boot.asm -o boot.o)
; =====================================================================

BITS 32

; Multiboot header constants
MB_MAGIC    equ 0x1BADB002
MB_ALIGNED  equ 1 << 0
MB_MEMINFO  equ 1 << 1
MB_FLAGS    equ MB_ALIGNED | MB_MEMINFO
MB_CHECKSUM equ -(MB_MAGIC + MB_FLAGS)

section .multiboot
align 4
    dd MB_MAGIC
    dd MB_FLAGS
    dd MB_CHECKSUM

section .bss
align 16
stack_bottom:
    resb 32768      ; 32 KB Initial Kernel Stack
stack_top:

section .data
align 8
; Global Descriptor Table (GDT)
gdt_start:
    ; Null Descriptor (0x00)
    dd 0x00000000
    dd 0x00000000

    ; Kernel Code Segment (0x08): Base 0, Limit 4GB, Ring 0, Read/Execute
    dw 0xFFFF       ; Limit 0:15
    dw 0x0000       ; Base 0:15
    db 0x00         ; Base 16:23
    db 10011010b    ; Access: Present, Ring 0, Exec/Read
    db 11001111b    ; Flags: 4KB Granularity, 32-bit protected
    db 0x00         ; Base 24:31

    ; Kernel Data Segment (0x10): Base 0, Limit 4GB, Ring 0, Read/Write
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 10010010b    ; Access: Present, Ring 0, Read/Write
    db 11001111b
    db 0x00

    ; User Code Segment (0x18): Base 0, Limit 4GB, Ring 3, Read/Execute
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 11111010b    ; Access: Present, Ring 3, Exec/Read
    db 11001111b
    db 0x00

    ; User Data Segment (0x20): Base 0, Limit 4GB, Ring 3, Read/Write
    dw 0xFFFF
    dw 0x0000
    db 0x00
    db 11110010b    ; Access: Present, Ring 3, Read/Write
    db 11001111b
    db 0x00
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

section .text
global _start
extern kmain

_start:
    ; Disable hardware interrupts during bootstrap
    cli

    ; Load Kernel Global Descriptor Table
    lgdt [gdt_descriptor]

    ; Far jump to flush CPU pipeline and reload CS with kernel code selector (0x08)
    jmp 0x08:.reload_segments

.reload_segments:
    ; Reload data segment registers with kernel data selector (0x10)
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Initialize kernel stack pointer
    mov esp, stack_top
    mov ebp, esp

    ; Push Multiboot structure pointer (EBX) and magic number (EAX)
    push ebx
    push eax

    ; Call the C Microkernel Entry Point
    call kmain

    ; If kmain returns, enter infinite halt loop
.halt_loop:
    cli
    hlt
    jmp .halt_loop
