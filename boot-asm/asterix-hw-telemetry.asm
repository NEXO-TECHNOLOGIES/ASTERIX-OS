; =====================================================================
; ASTERIX OS :: x86-64 Low-Level Assembly Hardware Telemetry Probe
; Direct register access: CPUID vendor/brand, TSC cycle counter & features
; Assembler: NASM (nasm -f elf64 / win64 asterix-hw-telemetry.asm)
; =====================================================================

BITS 64
SECTION .text

global asterix_get_cpu_vendor
global asterix_get_cpu_brand
global asterix_read_tsc
global asterix_get_features

; ---------------------------------------------------------------------
; void asterix_get_cpu_vendor(char *out_13bytes)
; Writes 12-byte vendor string (e.g. "GenuineIntel", "AuthenticAMD") + null
; Windows x64: RCX = buffer | System V AMD64: RDI = buffer
; ---------------------------------------------------------------------
asterix_get_cpu_vendor:
    push rbx
    push rdi
    push rsi

    ; Standardize pointer across Windows (RCX) and Linux (RDI)
    mov r8, rcx
    test rdi, rdi
    cmovnz r8, rdi

    mov eax, 0
    cpuid

    ; Vendor string is in EBX, EDX, ECX
    mov [r8], ebx
    mov [r8 + 4], edx
    mov [r8 + 8], ecx
    mov byte [r8 + 12], 0

    pop rsi
    pop rdi
    pop rbx
    ret

; ---------------------------------------------------------------------
; void asterix_get_cpu_brand(char *out_49bytes)
; Writes 48-byte ASCII CPU brand string + null terminator
; ---------------------------------------------------------------------
asterix_get_cpu_brand:
    push rbx
    push rdi
    push rsi

    mov r8, rcx
    test rdi, rdi
    cmovnz r8, rdi

    ; Query 0x80000002
    mov eax, 0x80000002
    cpuid
    mov [r8], eax
    mov [r8 + 4], ebx
    mov [r8 + 8], ecx
    mov [r8 + 12], edx

    ; Query 0x80000003
    mov eax, 0x80000003
    cpuid
    mov [r8 + 16], eax
    mov [r8 + 20], ebx
    mov [r8 + 24], ecx
    mov [r8 + 28], edx

    ; Query 0x80000004
    mov eax, 0x80000004
    cpuid
    mov [r8 + 32], eax
    mov [r8 + 36], ebx
    mov [r8 + 40], ecx
    mov [r8 + 44], edx

    mov byte [r8 + 48], 0

    pop rsi
    pop rdi
    pop rbx
    ret

; ---------------------------------------------------------------------
; uint64_t asterix_read_tsc(void)
; Returns 64-bit time-stamp counter in RAX
; ---------------------------------------------------------------------
asterix_read_tsc:
    rdtsc
    shl rdx, 32
    or rax, rdx
    ret

; ---------------------------------------------------------------------
; uint32_t asterix_get_features(void)
; Returns feature flags from CPUID function 1 (EDX)
; ---------------------------------------------------------------------
asterix_get_features:
    push rbx
    mov eax, 1
    cpuid
    mov eax, edx
    pop rbx
    ret
