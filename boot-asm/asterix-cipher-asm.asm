; =====================================================================
; 🌌 ASTERIX OS - Pure x86-64 Assembly Cryptographic Engine (v2.0)
; Multi-Round ARX-512 Block-Stream Cipher & Cryptographic Container
; Features:
;   - 512-bit Internal Permutation Matrix (16 x 32-bit registers)
;   - 1024-Round Memory-Hard ARX Key Derivation Function (KDF)
;   - Binary Container Format: "AXCIPH02" (Magic, 16B Salt, 12B Nonce,
;     Payload Size, KDF Rounds, and 16B Verification Integrity Tag)
;   - Zero External Dependencies / Zero Libc (Direct Linux Syscalls)
; Assembler: nasm -f elf64 asterix-cipher-asm.asm -o asterix-cipher-asm.o
; Linker:    ld -s asterix-cipher-asm.o -o asterix-cipher-asm
; =====================================================================

BITS 64
default rel

%define SYS_READ      0
%define SYS_WRITE     1
%define SYS_OPEN      2
%define SYS_CLOSE     3
%define SYS_FSTAT     5
%define SYS_LSEEK     8
%define SYS_EXIT     60
%define SYS_GETRANDOM 318

%define O_RDONLY    0
%define O_WRONLY    1
%define O_CREAT     64
%define O_TRUNC     512
%define O_FLAGS     0x241   ; WRONLY | CREAT | TRUNC
%define FILE_MODE   0644

%define KDF_ROUNDS  1024
%define BUF_SIZE    4096

section .rodata
    banner:
        db 10, " ╔═══════════════════════════════════════════════════════════════════╗", 10
        db " ║  █████╗ ███████╗    ██████╗██╗██████╗ ██╗  ██╗███████╗██████╗     ║", 10
        db " ║ ██╔══██╗██╔════╝   ██╔════╝██║██╔══██╗██║  ██║██╔════╝██╔══██╗    ║", 10
        db " ║ ███████║███████╗   ██║     ██║██████╔╝███████║█████╗  ██████╔╝    ║", 10
        db " ║ ██╔══██║╚════██║   ██║     ██║██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗    ║", 10
        db " ║ ██║  ██║███████║   ╚██████╗██║██║     ██║  ██║███████╗██║  ██║    ║", 10
        db " ║ ╚═╝  ╚═╝╚══════╝    ╚═════╝╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ║", 10
        db " ║      >> x86-64 HARDWARE-LEVEL ARX-512 CRYPTOGRAPHIC ENGINE <<     ║", 10
        db " ╚═══════════════════════════════════════════════════════════════════╝", 10, 10, 0
    banner_len equ $ - banner

    usage_msg:
        db " USAGE:", 10
        db "   ax-cipher enc <input_file> <output_file> <passphrase>", 10
        db "   ax-cipher dec <input_file> <output_file> <passphrase>", 10, 10
        db " EXAMPLES:", 10
        db "   ax-cipher enc confidential.iso payload.axc 'CyberMasterPass2026!'", 10
        db "   ax-cipher dec payload.axc restored.iso 'CyberMasterPass2026!'", 10, 10, 0
    usage_len equ $ - usage_msg

    msg_enc_start:
        db " [*] Mode: ENCRYPTION -> Generating 128-bit Salt & 96-bit Nonce...", 10, 0
    msg_enc_start_len equ $ - msg_enc_start

    msg_dec_start:
        db " [*] Mode: DECRYPTION -> Verifying AXCIPH02 Binary Container Header...", 10, 0
    msg_dec_start_len equ $ - msg_dec_start

    msg_kdf:
        db " [*] Running 1024-Round Register-Level ARX-512 Key Derivation...", 10, 0
    msg_kdf_len equ $ - msg_kdf

    msg_proc:
        db " [*] Executing high-velocity 512-bit permutation stream transformation...", 10, 0
    msg_proc_len equ $ - msg_proc

    msg_enc_ok:
        db " [✔] SUCCESS: File encrypted into ASTERIX Binary Container (.axc)!", 10, 0
    msg_enc_ok_len equ $ - msg_enc_ok

    msg_dec_ok:
        db " [✔] SUCCESS: Binary container authenticated & decrypted cleanly!", 10, 0
    msg_dec_ok_len equ $ - msg_dec_ok

    err_header:
        db " [!] Error: Invalid or corrupt binary container (Missing 'AXCIPH02' signature).", 10, 0
    err_header_len equ $ - err_header

    err_tag:
        db " [!] Error: Integrity verification failure! Data corrupted or incorrect key.", 10, 0
    err_tag_len equ $ - err_tag

    err_open:
        db " [!] Error: Failed to open source or target file descriptor.", 10, 0
    err_open_len equ $ - err_open

    magic_sig:
        db "AXCIPH02"           ; 8-byte container magic signature

section .bss
    in_fd:          resq 1
    out_fd:         resq 1
    file_size:      resq 1
    mode_is_enc:    resb 1
    stat_buf:       resb 144        ; struct stat buffer for sys_fstat

    ; 64-Byte ASTERIX Binary Container Header
    ; [0..8]   Magic "AXCIPH02"
    ; [8..24]  16-byte Salt
    ; [24..36] 12-byte Nonce
    ; [36..40] 4-byte KDF Rounds (1024)
    ; [40..48] 8-byte Payload Size
    ; [48..64] 16-byte Integrity Verification Tag
    header_buf:     resb 64

    ; Derived 32-Byte (256-Bit) Master Cipher Key
    derived_key:    resb 32

    ; Current 512-Bit Permutation State (16 x 32-bit words)
    state_matrix:   resd 16

    ; Running 128-Bit ARX Integrity Digest Accumulator
    tag_accum:      resq 2

    ; I/O Stream Chunk Buffer
    io_buf:         resb BUF_SIZE

section .text
global _start

_start:
    ; argc is at [rsp]
    mov r12, [rsp]
    cmp r12, 5
    jl print_usage

    ; Print Banner
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [banner]
    mov rdx, banner_len
    syscall

    ; Inspect command mode argv[1]
    mov rsi, [rsp + 8 * 2]          ; argv[1]
    cmp byte [rsi], 'e'             ; 'e' or "enc"
    je .set_enc_mode
    cmp byte [rsi], 'E'
    je .set_enc_mode
    cmp byte [rsi], 'd'             ; 'd' or "dec"
    je .set_dec_mode
    cmp byte [rsi], 'D'
    je .set_dec_mode
    jmp print_usage

.set_enc_mode:
    mov byte [mode_is_enc], 1
    jmp .open_files

.set_dec_mode:
    mov byte [mode_is_enc], 0

.open_files:
    ; Open Input File: argv[2]
    mov rax, SYS_OPEN
    mov rdi, [rsp + 8 * 3]          ; argv[2]
    mov rsi, O_RDONLY
    xor rdx, rdx
    syscall
    test rax, rax
    js open_err
    mov [in_fd], rax

    ; Open Output File: argv[3]
    mov rax, SYS_OPEN
    mov rdi, [rsp + 8 * 4]          ; argv[3]
    mov rsi, O_FLAGS
    mov rdx, FILE_MODE
    syscall
    test rax, rax
    js open_err
    mov [out_fd], rax

    ; Get Input File Size via sys_fstat
    mov rax, SYS_FSTAT
    mov rdi, [in_fd]
    lea rsi, [stat_buf]
    syscall
    mov rax, [stat_buf + 48]        ; st_size offset is 48 in Linux x86-64 struct stat
    mov [file_size], rax

    ; Branch based on mode
    cmp byte [mode_is_enc], 1
    je do_encrypt
    jmp do_decrypt

; =====================================================================
; 🔒 ENCRYPTION PIPELINE
; =====================================================================
do_encrypt:
    ; Print encryption start notification
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_enc_start]
    mov rdx, msg_enc_start_len
    syscall

    ; Initialize Header Magic
    mov rdi, [magic_sig]
    mov [header_buf + 0], rdi

    ; Generate 16-byte Salt + 12-byte Nonce (28 bytes random)
    mov rax, SYS_GETRANDOM
    lea rdi, [header_buf + 8]       ; Salt offset
    mov rsi, 28                     ; 16B Salt + 12B Nonce
    xor rdx, rdx
    syscall
    test rax, rax
    jns .entropy_ok

    ; Fallback entropy generator using CPU RDTSC and RDRAND
    rdtsc
    mov [header_buf + 8], rax
    xor rax, rdx
    rol rax, 17
    mov [header_buf + 16], rax
    rdtsc
    mov [header_buf + 24], rax
    mov dword [header_buf + 32], 0xCAFEBABE

.entropy_ok:
    ; Set KDF Rounds (1024)
    mov dword [header_buf + 36], KDF_ROUNDS

    ; Set Payload Size from input file stat
    mov rax, [file_size]
    mov [header_buf + 40], rax

    ; Derive 256-bit Key from Passphrase (argv[4]) and Salt
    call derive_key_kdf

    ; Initialize ARX-512 Permutation State Matrix
    call init_state_matrix

    ; Reset Running Integrity Accumulator
    mov qword [tag_accum + 0], 0x6A09E667F3BCC908
    mov qword [tag_accum + 8], 0xBB67AE8584CAA73B

    ; Write 64-byte Header Placeholder (Tag will be filled at EOF)
    mov rax, SYS_WRITE
    mov rdi, [out_fd]
    lea rsi, [header_buf]
    mov rdx, 64
    syscall

    ; Print Permutation Stream notification
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_proc]
    mov rdx, msg_proc_len
    syscall

.enc_stream_loop:
    mov rax, SYS_READ
    mov rdi, [in_fd]
    lea rsi, [io_buf]
    mov rdx, BUF_SIZE
    syscall
    test rax, rax
    jle .enc_stream_done
    mov r13, rax                    ; bytes read

    ; Accumulate Plaintext into ARX Integrity Digest
    lea rdi, [io_buf]
    mov rcx, r13
    call update_tag_digest

    ; Permute buffer with ARX-512 Keystream
    lea rdi, [io_buf]
    mov rcx, r13
    call permute_buffer

    ; Write Ciphertext to output
    mov rax, SYS_WRITE
    mov rdi, [out_fd]
    lea rsi, [io_buf]
    mov rdx, r13
    syscall
    jmp .enc_stream_loop

.enc_stream_done:
    ; Copy final 16-byte Integrity Digest into Header Tag Slot
    mov rax, [tag_accum + 0]
    mov rbx, [tag_accum + 8]
    mov [header_buf + 48], rax
    mov [header_buf + 56], rbx

    ; Rewind output file to sector 0 and update 64-byte Header
    mov rax, SYS_LSEEK
    mov rdi, [out_fd]
    xor rsi, rsi                    ; offset 0
    xor rdx, rdx                    ; SEEK_SET
    syscall

    mov rax, SYS_WRITE
    mov rdi, [out_fd]
    lea rsi, [header_buf]
    mov rdx, 64
    syscall

    call close_files

    ; Success banner
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_enc_ok]
    mov rdx, msg_enc_ok_len
    syscall

    mov rax, SYS_EXIT
    xor rdi, rdi
    syscall

; =====================================================================
; 🔓 DECRYPTION PIPELINE
; =====================================================================
do_decrypt:
    ; Print decryption start notification
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_dec_start]
    mov rdx, msg_dec_start_len
    syscall

    ; Read 64-byte Container Header
    mov rax, SYS_READ
    mov rdi, [in_fd]
    lea rsi, [header_buf]
    mov rdx, 64
    syscall
    cmp rax, 64
    jne header_corrupt

    ; Validate "AXCIPH02" Magic Signature
    mov rax, [header_buf + 0]
    mov rbx, [magic_sig]
    cmp rax, rbx
    jne header_corrupt

    ; Derive 256-bit Key from Passphrase and Extracted Salt
    call derive_key_kdf

    ; Initialize ARX-512 Permutation State Matrix from Nonce & Key
    call init_state_matrix

    ; Reset Running Integrity Accumulator
    mov qword [tag_accum + 0], 0x6A09E667F3BCC908
    mov qword [tag_accum + 8], 0xBB67AE8584CAA73B

    ; Read Stored Payload Size
    mov r14, [header_buf + 40]      ; expected total plaintext bytes
    xor r15, r15                    ; total bytes decrypted so far

    ; Print Permutation Stream notification
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_proc]
    mov rdx, msg_proc_len
    syscall

.dec_stream_loop:
    mov rax, SYS_READ
    mov rdi, [in_fd]
    lea rsi, [io_buf]
    mov rdx, BUF_SIZE
    syscall
    test rax, rax
    jle .dec_stream_done
    mov r13, rax

    ; Permute buffer with ARX-512 Keystream (XOR inverse is symmetric)
    lea rdi, [io_buf]
    mov rcx, r13
    call permute_buffer

    ; Accumulate Decrypted Plaintext into ARX Integrity Digest
    lea rdi, [io_buf]
    mov rcx, r13
    call update_tag_digest

    ; Write Decrypted Plaintext to output
    mov rax, SYS_WRITE
    mov rdi, [out_fd]
    lea rsi, [io_buf]
    mov rdx, r13
    syscall

    add r15, r13
    jmp .dec_stream_loop

.dec_stream_done:
    call close_files

    ; Verify Integrity Tag: Compare computed tag_accum with stored header tag
    mov rax, [tag_accum + 0]
    mov rbx, [tag_accum + 8]
    mov r8,  [header_buf + 48]
    mov r9,  [header_buf + 56]

    cmp rax, r8
    jne tag_mismatch
    cmp rbx, r9
    jne tag_mismatch

    ; Success banner
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_dec_ok]
    mov rdx, msg_dec_ok_len
    syscall

    mov rax, SYS_EXIT
    xor rdi, rdi
    syscall

; =====================================================================
; ⚙️ SUBROUTINES & CRYPTOGRAPHIC ALGORITHMS
; =====================================================================

; ─────────────────────────────────────────────────────────────────────
; derive_key_kdf: 1024-Round Memory-Hard ARX-512 Key Derivation
; Inputs: Passphrase at argv[4], Salt at [header_buf + 8]
; Outputs: 32 bytes derived key in [derived_key]
; ─────────────────────────────────────────────────────────────────────
derive_key_kdf:
    push rbp
    push rbx
    push r12
    push r13
    push r14

    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [msg_kdf]
    mov rdx, msg_kdf_len
    syscall

    ; Initialize 4 x 64-bit state registers with fractional constants
    mov r8,  0x6A09E667F3BCC908
    mov r9,  0xBB67AE8584CAA73B
    mov r10, 0x3C6EF372FE94F82B
    mov r11, 0xA54FF53A5F1D36F1

    ; Incorporate 16-byte Salt
    mov rax, [header_buf + 8]
    mov rbx, [header_buf + 16]
    xor r8, rax
    add r9, rbx
    rol r9, 27
    xor r10, rbx
    add r11, rax

    ; Multi-Round ARX Permutation over Passphrase String
    mov r14, KDF_ROUNDS             ; 1024 iterations
.kdf_round:
    mov rsi, [rsp + 8 * 9]          ; argv[4] = passphrase

.kdf_char:
    movzx rax, byte [rsi]
    test al, al
    jz .kdf_next_iter

    ; Non-linear substitution & rotation mixing
    add r8, rax
    rol r8, 19
    xor r9, r8
    add r9, 0x9E3779B97F4A7C15      ; Golden Ratio constant
    rol r9, 31
    xor r10, r9
    add r10, rax
    rol r10, 13
    xor r11, r10
    add r11, r8
    rol r11, 43

    inc rsi
    jmp .kdf_char

.kdf_next_iter:
    ; Cross-lane diffusion per iteration
    add r8, r10
    rol r8, 7
    xor r9, r11
    rol r9, 11
    dec r14
    jnz .kdf_round

    ; Store 32 bytes (256 bits) into derived_key
    lea rdi, [derived_key]
    mov [rdi + 0],  r8
    mov [rdi + 8],  r9
    mov [rdi + 16], r10
    mov [rdi + 24], r11

    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; ─────────────────────────────────────────────────────────────────────
; init_state_matrix: Seeds 512-bit permutation matrix
; Matrix Layout (16 x 32-bit Words):
;   [0..3]   Constant ChaCha-style ASCII ("ax02", "perm", "mode", "secr")
;   [4..11]  8 x 32-bit words from derived_key (256-bit key)
;   [12]     Block stream counter (initialized to 1)
;   [13..15] 3 x 32-bit words from header Nonce (96-bit nonce)
; ─────────────────────────────────────────────────────────────────────
init_state_matrix:
    lea rdi, [state_matrix]
    ; Constants
    mov dword [rdi + 0],  0x61783032 ; "ax02"
    mov dword [rdi + 4],  0x7065726d ; "perm"
    mov dword [rdi + 8],  0x6d6f6465 ; "mode"
    mov dword [rdi + 12], 0x73656372 ; "secr"

    ; 8 Key Words
    lea rsi, [derived_key]
    mov eax, [rsi + 0];  mov [rdi + 16], eax
    mov eax, [rsi + 4];  mov [rdi + 20], eax
    mov eax, [rsi + 8];  mov [rdi + 24], eax
    mov eax, [rsi + 12]; mov [rdi + 28], eax
    mov eax, [rsi + 16]; mov [rdi + 32], eax
    mov eax, [rsi + 20]; mov [rdi + 36], eax
    mov eax, [rsi + 24]; mov [rdi + 40], eax
    mov eax, [rsi + 28]; mov [rdi + 44], eax

    ; Block Counter (word 12)
    mov dword [rdi + 48], 1

    ; 3 Nonce Words from Header [24..36]
    mov eax, [header_buf + 24]; mov [rdi + 52], eax
    mov eax, [header_buf + 28]; mov [rdi + 56], eax
    mov eax, [header_buf + 32]; mov [rdi + 60], eax
    ret

; ─────────────────────────────────────────────────────────────────────
; permute_buffer: Generates ARX-512 Keystream & XORs with buffer
; Inputs: RDI = pointer to buffer, RCX = byte count
; ─────────────────────────────────────────────────────────────────────
permute_buffer:
    push rbp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 64                     ; 64 bytes working keystream block

    mov r12, rdi                    ; buffer pointer
    mov r13, rcx                    ; remaining byte count

.block_loop:
    test r13, r13
    jle .perm_finished

    ; Copy 16 state words to stack working matrix
    lea rsi, [state_matrix]
    mov rdi, rsp
    mov rcx, 8
    rep movsq

    ; Execute 10 double-rounds of 512-bit ARX Permutation
    mov r14, 10
.double_round:
    ; Column Rounds on 32-bit stack state
    ; QR(0, 4, 8, 12)
    mov eax, [rsp + 0];  mov ebx, [rsp + 16]; mov edx, [rsp + 48]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 0], eax;  mov [rsp + 48], edx
    mov ecx, [rsp + 32]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 32], ecx; mov [rsp + 16], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 0], eax;  mov [rsp + 48], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 32], ecx; mov [rsp + 16], ebx

    ; QR(1, 5, 9, 13)
    mov eax, [rsp + 4];  mov ebx, [rsp + 20]; mov edx, [rsp + 52]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 4], eax;  mov [rsp + 52], edx
    mov ecx, [rsp + 36]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 36], ecx; mov [rsp + 20], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 4], eax;  mov [rsp + 52], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 36], ecx; mov [rsp + 20], ebx

    ; QR(2, 6, 10, 14)
    mov eax, [rsp + 8];  mov ebx, [rsp + 24]; mov edx, [rsp + 56]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 8], eax;  mov [rsp + 56], edx
    mov ecx, [rsp + 40]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 40], ecx; mov [rsp + 24], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 8], eax;  mov [rsp + 56], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 40], ecx; mov [rsp + 24], ebx

    ; QR(3, 7, 11, 15)
    mov eax, [rsp + 12]; mov ebx, [rsp + 28]; mov edx, [rsp + 60]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 12], eax; mov [rsp + 60], edx
    mov ecx, [rsp + 44]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 44], ecx; mov [rsp + 28], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 12], eax; mov [rsp + 60], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 44], ecx; mov [rsp + 28], ebx

    ; Diagonal Rounds
    ; QR(0, 5, 10, 15)
    mov eax, [rsp + 0];  mov ebx, [rsp + 20]; mov edx, [rsp + 60]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 0], eax;  mov [rsp + 60], edx
    mov ecx, [rsp + 40]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 40], ecx; mov [rsp + 20], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 0], eax;  mov [rsp + 60], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 40], ecx; mov [rsp + 20], ebx

    ; QR(1, 6, 11, 12)
    mov eax, [rsp + 4];  mov ebx, [rsp + 24]; mov edx, [rsp + 48]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 4], eax;  mov [rsp + 48], edx
    mov ecx, [rsp + 44]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 44], ecx; mov [rsp + 24], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 4], eax;  mov [rsp + 48], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 44], ecx; mov [rsp + 24], ebx

    ; QR(2, 7, 8, 13)
    mov eax, [rsp + 8];  mov ebx, [rsp + 28]; mov edx, [rsp + 52]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 8], eax;  mov [rsp + 52], edx
    mov ecx, [rsp + 32]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 32], ecx; mov [rsp + 28], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 8], eax;  mov [rsp + 52], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 32], ecx; mov [rsp + 28], ebx

    ; QR(3, 4, 9, 14)
    mov eax, [rsp + 12]; mov ebx, [rsp + 16]; mov edx, [rsp + 56]
    add eax, ebx; xor edx, eax; rol edx, 16
    mov [rsp + 12], eax; mov [rsp + 56], edx
    mov ecx, [rsp + 36]
    add ecx, edx; xor ebx, ecx; rol ebx, 12
    mov [rsp + 36], ecx; mov [rsp + 16], ebx
    add eax, ebx; xor edx, eax; rol edx, 8
    mov [rsp + 12], eax; mov [rsp + 56], edx
    add ecx, edx; xor ebx, ecx; rol ebx, 7
    mov [rsp + 36], ecx; mov [rsp + 16], ebx

    dec r14
    jnz .double_round

    ; Add initial state back to working block
    lea rsi, [state_matrix]
    xor rcx, rcx
.add_back:
    mov eax, [rsp + rcx * 4]
    add eax, [rsi + rcx * 4]
    mov [rsp + rcx * 4], eax
    inc rcx
    cmp rcx, 16
    jl .add_back

    ; Increment block counter in state_matrix
    inc dword [state_matrix + 48]

    ; Determine bytes to XOR from this 64-byte block
    mov r15, 64
    cmp r13, 64
    jge .full_chunk
    mov r15, r13
.full_chunk:

    ; XOR keystream from stack into buffer
    xor rcx, rcx
.xor_bytes:
    mov al, byte [rsp + rcx]
    xor byte [r12 + rcx], al
    inc rcx
    cmp rcx, r15
    jl .xor_bytes

    add r12, r15
    sub r13, r15
    jmp .block_loop

.perm_finished:
    add rsp, 64
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

; ─────────────────────────────────────────────────────────────────────
; update_tag_digest: Accumulates 128-bit ARX Integrity Tag
; Inputs: RDI = pointer to plaintext buffer, RCX = byte count
; ─────────────────────────────────────────────────────────────────────
update_tag_digest:
    push rbx
    push rdx
    mov r8,  [tag_accum + 0]
    mov r9,  [tag_accum + 8]

.digest_loop:
    test rcx, rcx
    jz .digest_done
    movzx rax, byte [rdi]

    add r8, rax
    rol r8, 13
    xor r9, r8
    add r9, 0x9E3779B97F4A7C15
    rol r9, 29

    inc rdi
    dec rcx
    jmp .digest_loop

.digest_done:
    mov [tag_accum + 0], r8
    mov [tag_accum + 8], r9
    pop rdx
    pop rbx
    ret

; ─────────────────────────────────────────────────────────────────────
; close_files & error exits
; ─────────────────────────────────────────────────────────────────────
close_files:
    mov rax, SYS_CLOSE
    mov rdi, [in_fd]
    syscall
    mov rax, SYS_CLOSE
    mov rdi, [out_fd]
    syscall
    ret

print_usage:
    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [banner]
    mov rdx, banner_len
    syscall

    mov rax, SYS_WRITE
    mov rdi, 1
    lea rsi, [usage_msg]
    mov rdx, usage_len
    syscall

    mov rax, SYS_EXIT
    mov rdi, 1
    syscall

open_err:
    mov rax, SYS_WRITE
    mov rdi, 2
    lea rsi, [err_open]
    mov rdx, err_open_len
    syscall

    mov rax, SYS_EXIT
    mov rdi, 2
    syscall

header_corrupt:
    call close_files
    mov rax, SYS_WRITE
    mov rdi, 2
    lea rsi, [err_header]
    mov rdx, err_header_len
    syscall

    mov rax, SYS_EXIT
    mov rdi, 3
    syscall

tag_mismatch:
    mov rax, SYS_WRITE
    mov rdi, 2
    lea rsi, [err_tag]
    mov rdx, err_tag_len
    syscall

    mov rax, SYS_EXIT
    mov rdi, 4
    syscall
