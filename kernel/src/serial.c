/*
 * ==============================================================================
 * ASTERIX OS - 16550 UART Serial Console Driver Implementation
 * Architecture: x86 Bare-Metal I/O (Port 0x3F8)
 * Standard Output for Kernel CI/CD, QEMU Headless, and Hardware Telemetry
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/serial.h"
#include "../include/kernel.h"

static int serial_is_transmit_empty(void) {
    return inb(COM1_PORT + 5) & 0x20;
}

int serial_init(void) {
    outb(COM1_PORT + 1, 0x00);    /* Disable all interrupts */
    outb(COM1_PORT + 3, 0x80);    /* Enable DLAB (set baud rate divisor) */
    outb(COM1_PORT + 0, 0x03);    /* Set divisor to 3 (lo byte) 38400 baud */
    outb(COM1_PORT + 1, 0x00);    /*                  (hi byte) */
    outb(COM1_PORT + 3, 0x03);    /* 8 bits, no parity, one stop bit */
    outb(COM1_PORT + 2, 0xC7);    /* Enable FIFO, clear TX/RX, 14-byte threshold */
    outb(COM1_PORT + 4, 0x0B);    /* IRQs enabled, RTS/DSR set */

    /* Self-test loopback */
    outb(COM1_PORT + 4, 0x1E);    /* Set in loopback mode */
    outb(COM1_PORT + 0, 0xAE);    /* Send test byte */

    if (inb(COM1_PORT + 0) != 0xAE) {
        return -1;                /* Hardware fault / port absent */
    }

    /* Set normal operation mode (not loopback, with OUT2, DTR, RTS) */
    outb(COM1_PORT + 4, 0x0F);
    return 0;
}

void serial_putc(char c) {
    if (c == '\n') {
        while (!serial_is_transmit_empty()) {
            io_wait();
        }
        outb(COM1_PORT, '\r');
    }
    while (!serial_is_transmit_empty()) {
        io_wait();
    }
    outb(COM1_PORT, (uint8_t)c);
}

void serial_puts(const char *str) {
    if (!str) return;
    for (size_t i = 0; str[i] != '\0'; i++) {
        serial_putc(str[i]);
    }
}

void serial_puthex(uint32_t val) {
    const char hex_chars[] = "0123456789ABCDEF";
    serial_puts("0x");
    for (int i = 28; i >= 0; i -= 4) {
        serial_putc(hex_chars[(val >> i) & 0x0F]);
    }
}

void serial_putdec(uint32_t val) {
    if (val == 0) {
        serial_putc('0');
        return;
    }
    char buf[12];
    int i = 0;
    while (val > 0) {
        buf[i++] = (char)('0' + (val % 10));
        val /= 10;
    }
    while (i > 0) {
        serial_putc(buf[--i]);
    }
}

int serial_has_char(void) {
    return inb(COM1_PORT + 5) & 0x01;
}

char serial_getchar(void) {
    while (!serial_has_char()) {
        io_wait();
    }
    return (char)inb(COM1_PORT);
}

