; =====================================================================
; ASTERIX OS :: x86-64 ASSEMBLY :: Custom Bootloader MBR Sector
; Prints ASTERIX boot banner and chainloads second stage
; Assembler: NASM (nasm -f bin asterix-mbr.asm -o asterix-mbr.bin)
; =====================================================================

BITS 16
ORG 0x7C00

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    ; Set video mode 80x25 text
    mov ax, 0x0003
    int 0x10

    ; Set foreground color to cyan on black
    mov ax, 0x0600
    mov bh, 0x0B          ; Attribute: bright cyan on black
    xor cx, cx
    mov dx, 0x184F
    int 0x10

    ; Print ASTERIX banner line by line
    mov si, msg_banner
    call print_string

    mov si, msg_line1
    call print_string

    mov si, msg_line2
    call print_string

    mov si, msg_line3
    call print_string

    mov si, msg_line4
    call print_string

    mov si, msg_line5
    call print_string

    mov si, msg_line6
    call print_string

    mov si, msg_loading
    call print_string

    ; Simple spinner loop to simulate loading
    mov cx, 0x0FFF
.spin_loop:
    call delay
    loop .spin_loop

    mov si, msg_done
    call print_string

    ; Halt
.halt:
    cli
    hlt
    jmp .halt

; ──────────────────────────────────────────────────────────────────
; Subroutine: print_string
; SI = pointer to null-terminated string
; ──────────────────────────────────────────────────────────────────
print_string:
    push ax
    push bx
.loop:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    mov bx, 0x000B        ; Page 0, bright cyan
    int 0x10
    jmp .loop
.done:
    pop bx
    pop ax
    ret

; ──────────────────────────────────────────────────────────────────
; Subroutine: delay (simple busy-wait)
; ──────────────────────────────────────────────────────────────────
delay:
    push cx
    mov cx, 0xFFFF
.d_loop:
    nop
    loop .d_loop
    pop cx
    ret

; ──────────────────────────────────────────────────────────────────
; String Data
; ──────────────────────────────────────────────────────────────────
msg_banner  db 13, 10
            db '    ___   _____ ______ ______ ____     ____  _____', 13, 10, 0
msg_line1   db '   /   | / ___//_  __// ____// __ \   / __ \/ ___/', 13, 10, 0
msg_line2   db '  / /| | \__ \  / /  / __/  / /_/ /  / / / /\__ \ ', 13, 10, 0
msg_line3   db ' / ___ |___/ / / /  / /___ / _, _/  / /_/ /___/ / ', 13, 10, 0
msg_line4   db '/_/  |_/____/ /_/  /_____//_/ |_|   \____//____/  ', 13, 10, 0
msg_line5   db '', 13, 10, 0
msg_line6   db '       CYBERNETIC SECURITY PLATFORM v4.9.0-SEC', 13, 10, 0
msg_loading db 13, 10, '  [*] Initializing ASTERIX boot sequence...', 13, 10, 0
msg_done    db '  [OK] Boot stage 1 complete.', 13, 10, 0

; ──────────────────────────────────────────────────────────────────
; Boot Signature: Pad to 510 bytes and add 0xAA55 signature
; ──────────────────────────────────────────────────────────────────
TIMES 510 - ($ - $$) db 0
DW 0xAA55
