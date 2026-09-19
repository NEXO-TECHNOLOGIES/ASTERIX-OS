/*
 * ==============================================================================
 * ASTERIX OS - PS/2 Keyboard Driver Implementation
 * Translates Scancode Set 1 into 7-bit ASCII characters
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/keyboard.h"
#include "../include/kernel.h"
#include "../include/vga.h"
#include "../include/serial.h"

static char key_buffer[KEYBOARD_BUFFER_SIZE];
static volatile size_t buf_read_idx = 0;
static volatile size_t buf_write_idx = 0;
static int shift_active = 0;
static int caps_active = 0;

static const char scancode_ascii_normal[128] = {
    0,   27, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0,   'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
    0,   '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,
    '*', 0,   ' ', 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0
};

static const char scancode_ascii_shift[128] = {
    0,   27, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '\b',
    '\t', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n',
    0,   'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '\"', '~',
    0,   '|', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 0,
    '*', 0,   ' ', 0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0
};

void keyboard_init(void) {
    buf_read_idx = 0;
    buf_write_idx = 0;
    shift_active = 0;
    caps_active = 0;
    serial_puts("[+] PS/2 Keyboard Driver Initialized (US-QWERTY Mapping Active).\n");
}

void keyboard_on_irq(void) {
    uint8_t scancode = inb(KEYBOARD_DATA_PORT);

    /* Key release */
    if (scancode & 0x80) {
        uint8_t released = scancode & 0x7F;
        if (released == 0x2A || released == 0x36) {
            shift_active = 0;
        }
        return;
    }

    /* Key press */
    if (scancode == 0x2A || scancode == 0x36) {
        shift_active = 1;
        return;
    }
    if (scancode == 0x3A) {
        caps_active = !caps_active;
        return;
    }

    if (scancode < 128) {
        char ch = (shift_active ^ caps_active) ? scancode_ascii_shift[scancode] : scancode_ascii_normal[scancode];
        if (ch != 0) {
            size_t next = (buf_write_idx + 1) % KEYBOARD_BUFFER_SIZE;
            if (next != buf_read_idx) {
                key_buffer[buf_write_idx] = ch;
                buf_write_idx = next;
            }
        }
    }
}

int keyboard_has_key(void) {
    return (buf_read_idx != buf_write_idx) || serial_has_char();
}

char keyboard_getchar(void) {
    while (!keyboard_has_key()) {
        __asm__ volatile("hlt");
    }
    if (buf_read_idx != buf_write_idx) {
        char c = key_buffer[buf_read_idx];
        buf_read_idx = (buf_read_idx + 1) % KEYBOARD_BUFFER_SIZE;
        return c;
    }
    if (serial_has_char()) {
        char c = serial_getchar();
        if (c == '\r') c = '\n';
        return c;
    }
    return 0;
}

void keyboard_getline(char *buffer, size_t max_len) {
    size_t idx = 0;
    while (idx + 1 < max_len) {
        char c = keyboard_getchar();
        if (c == '\n' || c == '\r') {
            vga_putc('\n');
            serial_putc('\n');
            break;
        } else if (c == '\b') {
            if (idx > 0) {
                idx--;
                /* Erase character visually on VGA */
                vga_putc('\b');
                vga_putc(' ');
                vga_putc('\b');
                /* Send backspace sequence over serial */
                serial_puts("\b \b");
            }
        } else {
            buffer[idx++] = c;
            vga_putc(c);
            serial_putc(c);
        }
    }
    buffer[idx] = '\0';
}
