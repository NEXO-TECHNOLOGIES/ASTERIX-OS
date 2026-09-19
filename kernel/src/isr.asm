; =====================================================================
; ASTERIX OS - CPU Exception & Hardware IRQ Assembly Stubs
; Architecture: 32-bit Protected Mode (i386)
; Defines entry points for CPU exceptions 0-31, PIC IRQs 0-15, and int 0x80
; Assembler: NASM (nasm -f elf32 isr.asm -o isr.o)
; =====================================================================

BITS 32

extern isr_handler
extern irq_handler

; Macro for exceptions that DO NOT push an error code (dummy 0 pushed)
%macro ISR_NOERRCODE 1
global isr%1
isr%1:
    push dword 0        ; Dummy error code
    push dword %1       ; Interrupt number
    jmp isr_common_stub
%endmacro

; Macro for exceptions that DO push an error code
%macro ISR_ERRCODE 1
global isr%1
isr%1:
    push dword %1       ; Interrupt number
    jmp isr_common_stub
%endmacro

; Macro for IRQs (Hardware interrupts 32-47)
%macro IRQ 2
global irq%1
irq%1:
    push dword 0        ; Dummy error code
    push dword %2       ; IRQ mapped interrupt number
    jmp irq_common_stub
%endmacro

; CPU Exceptions 0-31
ISR_NOERRCODE 0     ; 0: Divide By Zero
ISR_NOERRCODE 1     ; 1: Debug Exception
ISR_NOERRCODE 2     ; 2: Non-Maskable Interrupt (NMI)
ISR_NOERRCODE 3     ; 3: Breakpoint (INT 3)
ISR_NOERRCODE 4     ; 4: Overflow (INTO)
ISR_NOERRCODE 5     ; 5: Bound Range Exceeded
ISR_NOERRCODE 6     ; 6: Invalid Opcode
ISR_NOERRCODE 7     ; 7: Device Not Available (No Math Coprocessor)
ISR_ERRCODE   8     ; 8: Double Fault
ISR_NOERRCODE 9     ; 9: Coprocessor Segment Overrun
ISR_ERRCODE   10    ; 10: Invalid TSS
ISR_ERRCODE   11    ; 11: Segment Not Present
ISR_ERRCODE   12    ; 12: Stack-Segment Fault
ISR_ERRCODE   13    ; 13: General Protection Fault (GPF)
ISR_ERRCODE   14    ; 14: Page Fault
ISR_NOERRCODE 15    ; 15: Reserved
ISR_NOERRCODE 16    ; 16: x87 FPU Floating-Point Error
ISR_ERRCODE   17    ; 17: Alignment Check
ISR_NOERRCODE 18    ; 18: Machine Check
ISR_NOERRCODE 19    ; 19: SIMD Floating-Point Exception
ISR_NOERRCODE 20    ; 20: Virtualization Exception
ISR_NOERRCODE 21    ; 21: Control Protection Exception
ISR_NOERRCODE 22    ; 22: Reserved
ISR_NOERRCODE 23    ; 23: Reserved
ISR_NOERRCODE 24    ; 24: Reserved
ISR_NOERRCODE 25    ; 25: Reserved
ISR_NOERRCODE 26    ; 26: Reserved
ISR_NOERRCODE 27    ; 27: Reserved
ISR_NOERRCODE 28    ; 28: Hypervisor Injection Exception
ISR_NOERRCODE 29    ; 29: VMM Communication Exception
ISR_ERRCODE   30    ; 30: Security Exception
ISR_NOERRCODE 31    ; 31: Reserved

; Hardware IRQs 0-15 remapped to 32-47
IRQ 0,  32          ; IRQ0: Programmable Interval Timer (PIT)
IRQ 1,  33          ; IRQ1: PS/2 Keyboard
IRQ 2,  34          ; IRQ2: Cascade for 8259A Slave
IRQ 3,  35          ; IRQ3: COM2 / COM4 Serial
IRQ 4,  36          ; IRQ4: COM1 / COM3 Serial
IRQ 5,  37          ; IRQ5: LPT2 / Audio
IRQ 6,  38          ; IRQ6: Floppy Disk
IRQ 7,  39          ; IRQ7: LPT1 / Spurious
IRQ 8,  40          ; IRQ8: Real Time Clock (RTC)
IRQ 9,  41          ; IRQ9: ACPI / Open
IRQ 10, 42          ; IRQ10: Open / PCI NIC
IRQ 11, 43          ; IRQ11: Open / PCI Storage
IRQ 12, 44          ; IRQ12: PS/2 Mouse
IRQ 13, 45          ; IRQ13: FPU / Math Coprocessor
IRQ 14, 46          ; IRQ14: Primary ATA Hard Disk
IRQ 15, 47          ; IRQ15: Secondary ATA Hard Disk

; Software Interrupt 0x80 (Syscall)
ISR_NOERRCODE 128   ; 128 = 0x80: Syscall Gate

; Common Exception Handler Stub
isr_common_stub:
    pusha               ; Pushes edi, esi, ebp, esp, ebx, edx, ecx, eax
    push ds
    push es
    push fs
    push gs

    mov ax, 0x10        ; Load Kernel Data Segment descriptor
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    push esp            ; Pass pointer to stack frame (registers_t*)
    call isr_handler
    add esp, 4          ; Clean up argument

    pop gs
    pop fs
    pop es
    pop ds
    popa                ; Restore registers
    add esp, 8          ; Clean up interrupt number and error code
    iret                ; Return from interrupt

; Common Hardware IRQ Handler Stub
irq_common_stub:
    pusha
    push ds
    push es
    push fs
    push gs

    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax

    push esp
    call irq_handler
    add esp, 4

    pop gs
    pop fs
    pop es
    pop ds
    popa
    add esp, 8
    iret
