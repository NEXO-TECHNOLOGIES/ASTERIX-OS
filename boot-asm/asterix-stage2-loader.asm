; ==============================================================================
; 🌌 ASTERIX OS — Stage 2 Bare-Metal Bootloader & Long Mode Bootstrap
; Transition Architecture: 16-bit Real Mode -> 32-bit Protected -> 64-bit Long Mode
; Features:
;   - INT 0x15 E820 Memory Map Query & Parsing
;   - Dual A20 Line Gate Enabler (8042 Keyboard Controller + Fast A20 Port 0x92)
;   - CPUID Feature Detection (Checks for 64-bit Long Mode LM support)
;   - 4-Level Paging Initialization (PML4 at 0x1000, PDPT at 0x2000, PD at 0x3000)
;   - MSR EFER.LME Enable (0xC0000080) & Far Jump to 64-bit Subsystem
; Assembler: NASM (nasm -f bin asterix-stage2-loader.asm -o asterix-stage2-loader.bin)
; SPDX-License-Identifier: MIT OR Apache-2.0
; ==============================================================================

BITS 16
ORG 0x8000                  ; Stage 2 loaded by Stage 1 at physical address 0x8000

stage2_entry:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov sp, 0x8000          ; Temporary real-mode stack
    sti

    ; Print Stage 2 Initialization Banner
    mov si, msg_stage2_banner
    call print_str_rm

    ; Step 1: Query System Memory via INT 0x15 E820
    mov si, msg_e820_query
    call print_str_rm
    call query_e820_memory
    jnc .e820_ok
    mov si, msg_e820_fail
    call print_str_rm
    jmp halt_rm

.e820_ok:
    mov si, msg_e820_success
    call print_str_rm

    ; Step 2: Enable A20 Line Gate
    mov si, msg_a20_enabling
    call print_str_rm
    call enable_a20
    jnc .a20_ok
    mov si, msg_a20_fail
    call print_str_rm
    jmp halt_rm

.a20_ok:
    mov si, msg_a20_success
    call print_str_rm

    ; Step 3: Check CPUID & 64-bit Long Mode Support
    call check_cpuid_and_long_mode
    jnc .long_mode_supported
    mov si, msg_no_long_mode
    call print_str_rm
    jmp halt_rm

.long_mode_supported:
    mov si, msg_long_mode_ok
    call print_str_rm

    ; Step 4: Setup 4-Level Paging (Identity Map first 2MB)
    call setup_identity_paging

    ; Step 5: Transition to 32-bit Protected Mode
    cli
    lgdt [gdt64_descriptor]     ; Load 64-bit capable GDT

    mov eax, cr0
    or eax, 1                   ; Set Protected Mode bit (PE)
    mov cr0, eax

    ; Far jump to flush instruction pipeline and enter 32-bit protected mode
    jmp 0x08:protected_mode_entry

halt_rm:
    cli
    hlt
    jmp halt_rm

; ─────────────────────────────────────────────────────────────────────────────
; Real Mode Helper Routines (16-bit)
; ─────────────────────────────────────────────────────────────────────────────

print_str_rm:
    push ax
    push bx
    push si
    mov ah, 0x0E
.loop:
    lodsb
    test al, al
    jz .done
    int 0x10
    jmp .loop
.done:
    pop si
    pop bx
    pop ax
    ret

; INT 0x15 AX=0xE820 Memory Map Reader
query_e820_memory:
    mov di, 0x9000          ; Store memory map at 0x9000
    xor ebx, ebx            ; EBX = 0 to start
    mov edx, 0x534D4150     ; 'SMAP' signature
    xor bp, bp              ; BP = counter of entries

.e820_loop:
    mov eax, 0xE820
    mov ecx, 24             ; 24-byte ACPI 3.0 descriptor
    int 0x15
    jc .e820_finish
    cmp eax, 0x534D4150     ; Verify SMAP returned in EAX
    jne .e820_error
    inc bp
    add di, 24
    test ebx, ebx           ; If EBX is 0, list is complete
    jnz .e820_loop

.e820_finish:
    mov [0x8FF0], bp        ; Save total entries count at 0x8FF0
    clc
    ret
.e820_error:
    stc
    ret

; A20 Line Gate Enabler (Fast A20 & Keyboard Controller)
enable_a20:
    ; Try Fast A20 Gate (Port 0x92)
    in al, 0x92
    or al, 2
    out 0x92, al
    call test_a20
    jnc .done_a20

    ; Fallback to 8042 Keyboard Controller
    call a20_wait_input
    mov al, 0xAD            ; Disable keyboard
    out 0x64, al
    call a20_wait_input

    mov al, 0xD0            ; Read output port
    out 0x64, al
    call a20_wait_output
    in al, 0x60
    push ax

    call a20_wait_input
    mov al, 0xD1            ; Write output port
    out 0x64, al
    call a20_wait_input
    pop ax
    or al, 2                ; Enable A20 bit
    out 0x60, al

    call a20_wait_input
    mov al, 0xAE            ; Enable keyboard
    out 0x64, al
    call a20_wait_input

    call test_a20
.done_a20:
    ret

a20_wait_input:
    in al, 0x64
    test al, 2
    jnz a20_wait_input
    ret

a20_wait_output:
    in al, 0x64
    test al, 1
    jz a20_wait_output
    ret

test_a20:
    push ds
    push es
    xor ax, ax
    mov ds, ax              ; DS = 0x0000
    not ax
    mov es, ax              ; ES = 0xFFFF
    mov di, 0x7DFE
    mov si, 0x7E0E
    mov al, [ds:di]
    push ax
    mov al, [es:si]
    push ax
    mov byte [ds:di], 0x00
    mov byte [es:si], 0xFF
    cmp byte [ds:di], 0xFF
    pop ax
    mov [es:si], al
    pop ax
    mov [ds:di], al
    pop es
    pop ds
    je .disabled
    clc
    ret
.disabled:
    stc
    ret

; CPUID Verification & Long Mode Bit Check
check_cpuid_and_long_mode:
    ; Test if CPUID is supported by toggling EFLAGS ID bit (bit 21)
    pushfd
    pop eax
    mov ecx, eax
    xor eax, 1 << 21
    push eax
    popfd
    pushfd
    pop eax
    push ecx
    popfd
    cmp eax, ecx
    je .no_cpuid

    ; Check extended function support (0x80000000)
    mov eax, 0x80000000
    cpuid
    cmp eax, 0x80000001
    jb .no_cpuid

    ; Check Long Mode availability (0x80000001, EDX bit 29)
    mov eax, 0x80000001
    cpuid
    test edx, 1 << 29
    jz .no_cpuid
    clc
    ret

.no_cpuid:
    stc
    ret

; Setup 4-Level Paging Tables at 0x1000 - 0x4000
setup_identity_paging:
    ; Zero out 16KB for PML4, PDPT, PD, PT
    mov edi, 0x1000
    mov cr3, edi            ; Point CR3 to PML4 table base
    xor eax, eax
    mov ecx, 4096
    rep stosd
    mov edi, cr3

    ; PML4[0] -> PDPT at 0x2000 (Present | Read/Write)
    mov dword [edi], 0x2003
    add edi, 0x1000

    ; PDPT[0] -> PD at 0x3000 (Present | Read/Write)
    mov dword [edi], 0x3003
    add edi, 0x1000

    ; PD[0] -> 2MB Huge Page (Present | Read/Write | PageSize bit 7 = 2MB page)
    mov dword [edi], 0x000083
    ret

; ─────────────────────────────────────────────────────────────────────────────
; 32-bit Protected Mode Segment
; ─────────────────────────────────────────────────────────────────────────────

BITS 32
protected_mode_entry:
    ; Reload data segment selectors with 32-bit data descriptor (0x10)
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000        ; 32-bit Protected Stack

    ; Step 6: Enable Physical Address Extension (PAE) in CR4 bit 5
    mov eax, cr4
    or eax, 1 << 5
    mov cr4, eax

    ; Step 7: Set Long Mode Enable (LME) bit in EFER MSR (0xC0000080)
    mov ecx, 0xC0000080     ; IA32_EFER MSR
    rdmsr
    or eax, 1 << 8          ; LME bit (bit 8)
    wrmsr

    ; Step 8: Enable Paging (PG bit 31) in CR0
    mov eax, cr0
    or eax, 1 << 31
    mov cr0, eax

    ; Far jump into 64-bit Long Mode Code Segment (Selector 0x18)
    jmp 0x18:long_mode_entry

; ─────────────────────────────────────────────────────────────────────────────
; 64-bit Long Mode Segment
; ─────────────────────────────────────────────────────────────────────────────

BITS 64
long_mode_entry:
    ; Reload segment registers with null/flat selectors in 64-bit mode
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov rsp, 0x200000       ; 2MB 64-bit kernel stack

    ; Write direct 64-bit status message to VGA buffer (0xB8000)
    mov rdi, 0xB8000 + (10 * 160)
    lea rsi, [rel msg_long_mode_banner]
    mov ah, 0x0B            ; Cyan text

.vga_print_loop:
    lodsb
    test al, al
    jz .vga_done
    mov [rdi], ax
    add rdi, 2
    jmp .vga_print_loop

.vga_done:
    ; Call external 64-bit kernel entry or idle safely
.idle_64:
    cli
    hlt
    jmp .idle_64

; ─────────────────────────────────────────────────────────────────────────────
; Global Descriptor Table (GDT) for 16, 32, and 64-bit transitions
; ─────────────────────────────────────────────────────────────────────────────

align 16
gdt64_start:
    ; 0x00: Null Descriptor
    dq 0x0000000000000000

    ; 0x08: 32-bit Kernel Code Segment (D/B=1, L=0)
    dw 0xFFFF, 0x0000
    db 0x00, 10011010b, 11001111b, 0x00

    ; 0x10: 32-bit / 64-bit Kernel Data Segment
    dw 0xFFFF, 0x0000
    db 0x00, 10010010b, 11001111b, 0x00

    ; 0x18: 64-bit Kernel Code Segment (L=1, D/B=0)
    dw 0x0000, 0x0000
    db 0x00, 10011010b, 00100000b, 0x00

    ; 0x20: 64-bit User Code Segment (DPL=3)
    dw 0x0000, 0x0000
    db 0x00, 11111010b, 00100000b, 0x00
gdt64_end:

gdt64_descriptor:
    dw gdt64_end - gdt64_start - 1
    dd gdt64_start

; ─────────────────────────────────────────────────────────────────────────────
; Status Strings
; ─────────────────────────────────────────────────────────────────────────────

msg_stage2_banner:      db 13, 10, "[ASTERIX] Stage 2 Loader Active (0x8000)...", 13, 10, 0
msg_e820_query:         db "[*] Probing System RAM via BIOS E820... ", 0
msg_e820_success:       db "SUCCESS [OK]", 13, 10, 0
msg_e820_fail:          db "FAILED!", 13, 10, 0
msg_a20_enabling:       db "[*] Enabling A20 Memory Line Gate... ", 0
msg_a20_success:        db "ENABLED [OK]", 13, 10, 0
msg_a20_fail:           db "A20 GATE ERROR!", 13, 10, 0
msg_long_mode_ok:       db "[*] 64-bit Long Mode CPUID Detected [OK]", 13, 10, 0
msg_no_long_mode:       db "[!] CPU does not support 64-bit Long Mode!", 13, 10, 0
msg_long_mode_banner:   db ">> ASTERIX OS: 64-BIT LONG MODE ACTIVATED (RING 0 SECURE) <<", 0
