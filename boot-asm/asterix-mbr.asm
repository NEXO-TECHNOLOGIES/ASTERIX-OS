; =====================================================================
; 🌌 ASTERIX OS - Next-Generation Master MBR Bootloader (x86 Assembly)
; Dual Operation: Autonomous VBR Chainloader & Cyber Diagnostic Console
; Conforms to Standard PC MBR: Relocates to 0x0600, Parses Partition Table (0x01BE),
; Chains to Active Partition VBR at 0x7C00, and verifies 0xAA55 signature.
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

    ; Save BIOS boot drive passed in DL
    mov [boot_drive], dl

    ; Relocate self from 0x7C00 to 0x0600 (Free up 0x7C00 for VBR chainloading)
    mov cx, 256             ; 256 words = 512 bytes
    mov si, 0x7C00
    mov di, 0x0600
    rep movsw

    ; Jump to relocated code at 0x0600
    jmp 0x0000:relocated_entry

relocated_entry:
    ; Set video mode 80x25 16-color text
    mov ax, 0x0003
    int 0x10

    ; Print ASTERIX Cyber Banner
    mov si, msg_banner
    call print_str

    ; Check if user presses a key within timeout for diagnostic menu
    mov cx, 0x0020
.timeout_poll:
    mov ah, 0x01            ; Check keystroke buffer
    int 0x16
    jnz .interactive_mode
    call delay_tick
    loop .timeout_poll

    ; Auto-chainload mode: Search for active bootable partition (flag 0x80)
    mov si, 0x0600 + 0x01BE ; Start of MBR Partition Table in relocated memory
    mov cx, 4               ; 4 Primary MBR partitions

.check_partition:
    cmp byte [si], 0x80     ; 0x80 = Active / Bootable partition
    je .found_active_partition
    add si, 16              ; Move to next 16-byte partition entry
    loop .check_partition

    ; If no active partition found, fall back to interactive console
    mov si, msg_no_active
    call print_str
    jmp .interactive_mode

.found_active_partition:
    mov [active_part_ptr], si
    mov si, msg_chainload
    call print_str

    ; Extract LBA Start Sector from partition entry (offset 8 in entry)
    mov si, [active_part_ptr]
    mov eax, [si + 8]       ; Starting LBA sector
    mov [dap_lba_low], eax

    ; Use BIOS INT 0x13 Extended Read (LBA Packet)
    mov si, disk_address_packet
    mov dl, [boot_drive]
    mov ah, 0x42
    int 0x13
    jc .read_error

    ; Verify boot signature 0xAA55 on loaded VBR at 0x7C00
    cmp word [0x7DFE], 0xAA55
    jne .invalid_vbr

    mov si, msg_vbr_ok
    call print_str

    ; Prepare registers for stage 2 / VBR:
    ; DL = Boot drive number
    ; DS:SI = Pointer to active partition table entry
    mov dl, [boot_drive]
    mov si, [active_part_ptr]

    ; Jump to loaded VBR at 0x0000:0x7C00
    jmp 0x0000:0x7C00

.read_error:
    mov si, msg_read_err
    call print_str
    jmp .interactive_mode

.invalid_vbr:
    mov si, msg_bad_vbr
    call print_str

.interactive_mode:
    ; Flush keybuffer
    mov ah, 0x00
    int 0x16

    mov si, msg_menu
    call print_str

.menu_loop:
    mov ah, 0x00
    int 0x16

    cmp al, '1'
    je .retry_boot
    cmp al, '2'
    je .hardware_telemetry
    cmp al, '3'
    je .reboot_pc
    jmp .menu_loop

.retry_boot:
    jmp relocated_entry

.hardware_telemetry:
    mov si, msg_hw_info
    call print_str

    ; Query Base Memory via BIOS INT 0x12
    clc
    int 0x12
    mov si, msg_mem_base
    call print_str
    call print_hex16
    mov si, msg_kb
    call print_str

    ; Query Boot Drive Parameters via INT 0x13 AH=0x08
    mov ah, 0x08
    mov dl, [boot_drive]
    xor di, di
    int 0x13
    jc .telemetry_done

    mov si, msg_drive_ok
    call print_str

.telemetry_done:
    jmp .interactive_mode

.reboot_pc:
    ; BIOS Warm Reboot via INT 0x19
    int 0x19
    ; Fallback far jump to BIOS reset vector
    jmp 0xFFFF:0x0000

; ──────────────────────────────────────────────────────────────────
; Helpers: print_str, print_hex16, delay_tick
; ──────────────────────────────────────────────────────────────────
print_str:
    push ax
    push bx
.loop:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    mov bx, 0x000B          ; Bright Cyan
    int 0x10
    jmp .loop
.done:
    pop bx
    pop ax
    ret

print_hex16:
    push ax
    push cx
    push dx
    mov dx, ax
    mov cx, 4
.hex_loop:
    rol dx, 4
    mov al, dl
    and al, 0x0F
    add al, '0'
    cmp al, '9'
    jle .out_char
    add al, 7
.out_char:
    mov ah, 0x0E
    mov bx, 0x000E          ; Bright Yellow
    int 0x10
    loop .hex_loop
    pop dx
    pop cx
    pop ax
    ret

delay_tick:
    push cx
    mov cx, 0x7FFF
.d_loop:
    nop
    loop .d_loop
    pop cx
    ret

; ──────────────────────────────────────────────────────────────────
; Data Structures & Strings
; ──────────────────────────────────────────────────────────────────
align 4
disk_address_packet:
    db 0x10                 ; Packet size (16 bytes)
    db 0x00                 ; Reserved (0)
    dw 1                    ; Number of sectors to read (1 sector = 512 bytes)
    dw 0x7C00               ; Offset of buffer
    dw 0x0000               ; Segment of buffer (0x0000:0x7C00)
dap_lba_low:
    dd 0x00000001           ; LBA start sector (Low 32 bits)
    dd 0x00000000           ; LBA start sector (High 32 bits)

boot_drive:         db 0x80
active_part_ptr:    dw 0x0000

msg_banner:
    db 13, 10, " [ ASTERIX OS :: NEXT-GEN SECURE MBR BOOTLOADER v2.0 ]", 13, 10
    db " -------------------------------------------------------------", 13, 10, 0
msg_no_active:  db " [!] Warning: No bootable partition (0x80) marked.", 13, 10, 0
msg_chainload:  db " [*] Active partition detected. Reading VBR sector...", 13, 10, 0
msg_vbr_ok:     db " [✔] VBR signature (0xAA55) verified. Chainloading OS...", 13, 10, 0
msg_read_err:   db " [!] Error: INT 13h disk read failed.", 13, 10, 0
msg_bad_vbr:    db " [!] Error: Missing 0xAA55 boot signature in VBR.", 13, 10, 0
msg_menu:
    db 13, 10, " ASTERIX BOOT COMMAND CONSOLE:", 13, 10
    db "  [1] Retry Boot Partition", 13, 10
    db "  [2] Hardware & Memory Telemetry", 13, 10
    db "  [3] Reboot System", 13, 10
    db " Select option > ", 0
msg_hw_info:    db 13, 10, " [*] Probing Hardware Status...", 13, 10, 0
msg_mem_base:   db "  ► Conventional RAM: 0x", 0
msg_kb:         db " KB", 13, 10, 0
msg_drive_ok:   db "  ► Boot Storage Controller: Online", 13, 10, 0

; ──────────────────────────────────────────────────────────────────
; MBR Partition Table & Boot Signature Padding
; ──────────────────────────────────────────────────────────────────
times 446 - ($ - $$) db 0

; 64 bytes for 4 standard 16-byte MBR partition entries
partition_table:
    db 0x80, 0x01, 0x01, 0x00, 0x83, 0xFE, 0xFF, 0xFF, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00
    times 48 db 0

; MBR Boot Signature
dw 0xAA55
