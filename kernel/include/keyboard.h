/*
 * ==============================================================================
 * ASTERIX OS - PS/2 Keyboard Driver Header
 * Scancode Set 1 decoding, Shift/Caps state tracking, and input buffering
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_KEYBOARD_H
#define ASTERIX_KEYBOARD_H

#include <stdint.h>
#include <stddef.h>

#define KEYBOARD_DATA_PORT   0x60
#define KEYBOARD_STATUS_PORT 0x64
#define KEYBOARD_BUFFER_SIZE 256

void keyboard_init(void);
void keyboard_on_irq(void);
int  keyboard_has_key(void);
char keyboard_getchar(void);
void keyboard_getline(char *buffer, size_t max_len);

#endif /* ASTERIX_KEYBOARD_H */
