; =====================================================================
; ASTERIX OS :: x86-64 ASSEMBLY :: System Info via Linux Syscalls
; Reads hostname and prints via write syscall — zero C dependency
; Assembler: NASM (nasm -f elf64 asterix-raw-info.asm -o asterix-raw-info.o)
;            ld asterix-raw-info.o -o asterix-raw-info
; =====================================================================

BITS 64
SECTION .data

banner      db 27, '[38;5;51m', 27, '[1m'
            db '  ___   _____ ______ ______ ____   ___   ______  __', 10
            db ' /   | / ___//_  __// ____// __ \ /   | / ___/ |/ /', 10
            db '/ /| | \__ \  / /  / __/  / /_/ // /| | \__ \|   / ', 10
            db '/ ___ |___/ / / /  / /___ / _, _// ___ |___/ /   |  ', 10
            db '/_/  |_/____/ /_/  /_____//_/ |_//_/  |_/____/_/|_|  ', 10
            db '      x86-64 NATIVE ASSEMBLY SYSCALL ENGINE', 10
            db 27, '[0m', 10, 0
banner_len  equ $ - banner

lbl_host    db 27, '[38;5;46m', '  Hostname:  ', 27, '[0m'
lbl_host_len equ $ - lbl_host

lbl_uid     db 27, '[38;5;220m', '  UID/GID:   ', 27, '[0m'
lbl_uid_len equ $ - lbl_uid

lbl_ok      db 27, '[38;5;46m', 10, '  [OK] Assembly engine complete.', 10, 27, '[0m'
lbl_ok_len  equ $ - lbl_ok

newline     db 10
hostname_buf times 256 db 0
uid_buf     times 32 db 0

SECTION .text
GLOBAL _start

; ──────────────────────────────────────────────────────────────────
; Helper: itoa — convert rax to decimal string at [rdi], ret len in rcx
; ──────────────────────────────────────────────────────────────────
itoa:
    push rbx
    push rdx
    push rsi
    mov  rsi, rdi
    add  rsi, 31
    mov  byte [rsi], 10         ; newline at end
    dec  rsi
    xor  rcx, rcx
    test rax, rax
    jnz  .loop
    mov  byte [rsi], '0'
    inc  rcx
    jmp  .done
.loop:
    xor  rdx, rdx
    mov  rbx, 10
    div  rbx
    add  dl, '0'
    mov  [rsi], dl
    dec  rsi
    inc  rcx
    test rax, rax
    jnz  .loop
.done:
    inc  rsi                    ; rsi = start of number string
    pop  rdx
    pop  rbx
    ret

_start:
    ; Print banner
    mov rax, 1
    mov rdi, 1
    mov rsi, banner
    mov rdx, banner_len
    syscall

    ; Print hostname label
    mov rax, 1
    mov rdi, 1
    mov rsi, lbl_host
    mov rdx, lbl_host_len
    syscall

    ; syscall: gethostname(hostname_buf, 256)  => SYS_gethostname = 110
    mov rax, 110
    mov rdi, hostname_buf
    mov rsi, 256
    syscall

    ; Find length of hostname string
    mov rdi, hostname_buf
    xor rcx, rcx
.host_len:
    cmp byte [rdi + rcx], 0
    je  .host_done
    inc rcx
    jmp .host_len
.host_done:
    ; Append newline
    mov byte [rdi + rcx], 10
    inc rcx

    ; Write hostname
    mov rax, 1
    mov rdi, 1
    mov rsi, hostname_buf
    mov rdx, rcx
    syscall

    ; Print UID label
    mov rax, 1
    mov rdi, 1
    mov rsi, lbl_uid
    mov rdx, lbl_uid_len
    syscall

    ; syscall: getuid() = 102
    mov rax, 102
    syscall
    ; Convert uid to string
    mov rdi, uid_buf
    call itoa

    ; rsi = pointer to string, rcx = length (includes newline)
    mov rax, 1
    mov rdi, 1
    ; rsi already set by itoa
    mov rdx, rcx
    syscall

    ; Print done message
    mov rax, 1
    mov rdi, 1
    mov rsi, lbl_ok
    mov rdx, lbl_ok_len
    syscall

    ; syscall: exit(0) = 60
    mov rax, 60
    xor rdi, rdi
    syscall
