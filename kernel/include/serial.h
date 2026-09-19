/*
 * ==============================================================================
 * ASTERIX OS - 16550 UART Serial Console Driver Header
 * Base Port: 0x03F8 (COM1) | Baud: 38400 | Configuration: 8N1
 * Zero libc: 100% Freestanding Bare-Metal Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_SERIAL_H
#define ASTERIX_SERIAL_H

#include <stdint.h>
#include <stddef.h>

#define COM1_PORT 0x03F8

int  serial_init(void);
void serial_putc(char c);
void serial_puts(const char *str);
void serial_puthex(uint32_t val);
void serial_putdec(uint32_t val);
int  serial_has_char(void);
char serial_getchar(void);

#endif /* ASTERIX_SERIAL_H */
