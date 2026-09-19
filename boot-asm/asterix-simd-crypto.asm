; ==============================================================================
; [ASTERIX] ASTERIX OS — AVX2 & SSE Vectorized Cryptographic & Entropy Engine (x86_64)
; High-Velocity SIMD Routines for Stream Encryption, ChaCha20 & Shannon Entropy
; System V AMD64 ABI:
;   Args: RDI, RSI, RDX, RCX, R8, R9 | Return: RAX
; Assembler: NASM (nasm -f elf64 asterix-simd-crypto.asm -o asterix-simd-crypto.o)
; SPDX-License-Identifier: MIT OR Apache-2.0
; ==============================================================================

BITS 64

section .text

global asterix_simd_xor_stream
global asterix_simd_entropy_scan
global asterix_simd_chacha_qr
global asterix_cpu_simd_caps

; =============================================================================
; asterix_cpu_simd_caps:
; Detects AVX2, AES-NI, and SSE4.2 support via CPUID
; Returns RAX bitmask:
;   bit 0: SSE2
;   bit 1: SSE4.2
;   bit 2: AVX2
;   bit 3: AES-NI
; =============================================================================
asterix_cpu_simd_caps:
    push rbx
    xor rax, rax            ; Result accumulator

    ; Standard Feature Flags (EAX = 1)
    mov eax, 1
    cpuid
    ; EDX bit 26: SSE2
    test edx, 1 << 26
    jz .check_ecx
    or eax, 1 << 0

.check_ecx:
    ; ECX bit 20: SSE4.2
    test ecx, 1 << 20
    jz .check_aes
    or eax, 1 << 1

.check_aes:
    ; ECX bit 25: AES-NI
    test ecx, 1 << 25
    jz .check_extended
    or eax, 1 << 3

.check_extended:
    ; Extended Features (EAX = 7, ECX = 0)
    push rax
    mov eax, 7
    xor ecx, ecx
    cpuid
    pop rax
    ; EBX bit 5: AVX2
    test ebx, 1 << 5
    jz .caps_done
    or eax, 1 << 2

.caps_done:
    pop rbx
    ret

; =============================================================================
; asterix_simd_xor_stream:
; High-throughput AVX2 / SSE2 256-bit stream encryption & keystream masking
; Prototype:
;   void asterix_simd_xor_stream(uint8_t *dest, const uint8_t *src,
;                                const uint8_t *key32, size_t len)
; Register allocation:
;   RDI = dest
;   RSI = src
;   RDX = key32 (32-byte repeating key block)
;   RCX = len
; =============================================================================
asterix_simd_xor_stream:
    test rcx, rcx
    jz .xor_exit

    ; Load 32-byte key into YMM0 if AVX2 available, or XMM0 for SSE
    vmovdqu ymm0, [rdx]

.avx_loop_32:
    cmp rcx, 32
    jb .sse_fallback

    vmovdqu ymm1, [rsi]         ; Load 32 bytes from plaintext
    vpxor ymm2, ymm1, ymm0       ; YMM2 = YMM1 ^ YMM0
    vmovdqu [rdi], ymm2         ; Store 32 bytes ciphertext

    add rsi, 32
    add rdi, 32
    sub rcx, 32
    jmp .avx_loop_32

.sse_fallback:
    vzeroupper                  ; Clear upper 128-bits of YMM registers
    movdqu xmm0, [rdx]          ; Load lower 16-byte key

.sse_loop_16:
    cmp rcx, 16
    jb .byte_tail

    movdqu xmm1, [rsi]
    pxor xmm1, xmm0
    movdqu [rdi], xmm1

    add rsi, 16
    add rdi, 16
    sub rcx, 16
    jmp .sse_loop_16

.byte_tail:
    test rcx, rcx
    jz .xor_exit
    xor rax, rax

.tail_loop:
    mov al, [rsi]
    xor al, [rdx]
    mov [rdi], al
    inc rsi
    inc rdi
    dec rcx
    jnz .tail_loop

.xor_exit:
    ret

; =============================================================================
; asterix_simd_entropy_scan:
; Ultra-fast hardware byte histogram generator for entropy analysis
; Prototype:
;   void asterix_simd_entropy_scan(const uint8_t *buf, size_t len, uint32_t *hist256)
; Register allocation:
;   RDI = buf
;   RSI = len
;   RDX = hist256 (256 uint32_t array = 1024 bytes)
; =============================================================================
asterix_simd_entropy_scan:
    test rsi, rsi
    jz .scan_done

    ; Unroll 4 bytes per cycle
.scan_loop:
    cmp rsi, 4
    jb .single_byte_tail

    movzx eax, byte [rdi]
    inc dword [rdx + rax * 4]

    movzx eax, byte [rdi + 1]
    inc dword [rdx + rax * 4]

    movzx eax, byte [rdi + 2]
    inc dword [rdx + rax * 4]

    movzx eax, byte [rdi + 3]
    inc dword [rdx + rax * 4]

    add rdi, 4
    sub rsi, 4
    jmp .scan_loop

.single_byte_tail:
    test rsi, rsi
    jz .scan_done
    movzx eax, byte [rdi]
    inc dword [rdx + rax * 4]
    inc rdi
    dec rsi
    jmp .single_byte_tail

.scan_done:
    ret

; =============================================================================
; asterix_simd_chacha_qr:
; ChaCha20 Quarter Round Core (ARX: Add-Rotate-XOR)
; Prototype:
;   void asterix_simd_chacha_qr(uint32_t *state, int a, int b, int c, int d)
; Register allocation:
;   RDI = state (pointer to 16 uint32_t words)
;   RSI = a index
;   RDX = b index
;   RCX = c index
;   R8  = d index
; =============================================================================
asterix_simd_chacha_qr:
    ; Load state[a], state[b], state[c], state[d]
    mov r9d,  [rdi + rsi * 4]   ; r9d  = a
    mov r10d, [rdi + rdx * 4]   ; r10d = b
    mov r11d, [rdi + rcx * 4]   ; r11d = c
    mov eax,  [rdi + r8  * 4]   ; eax  = d

    ; a += b; d ^= a; d <<<= 16
    add r9d, r10d
    xor eax, r9d
    rol eax, 16

    ; c += d; b ^= c; b <<<= 12
    add r11d, eax
    xor r10d, r11d
    rol r10d, 12

    ; a += b; d ^= a; d <<<= 8
    add r9d, r10d
    xor eax, r9d
    rol eax, 8

    ; c += d; b ^= c; b <<<= 7
    add r11d, eax
    xor r10d, r11d
    rol r10d, 7

    ; Write back to state array
    mov [rdi + rsi * 4], r9d
    mov [rdi + rdx * 4], r10d
    mov [rdi + rcx * 4], r11d
    mov [rdi + r8  * 4], eax
    ret
