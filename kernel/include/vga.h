/*
 * ==============================================================================
 * 🌌 ASTERIX OS — Freestanding Video Graphics Array (VGA) Terminal Driver
 * Physical Buffer: 0x000B8000 | Text Mode 80x25 | 16 Hardware Colors
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_VGA_H
#define ASTERIX_VGA_H

#include <stdint.h>
#include <stddef.h>

#define VGA_WIDTH  80
#define VGA_HEIGHT 25
#define VGA_MEMORY ((volatile uint16_t*)0xB8000)

/* VGA 16-Color Palette */
typedef enum {
    VGA_COLOR_BLACK         = 0,
    VGA_COLOR_BLUE          = 1,
    VGA_COLOR_GREEN         = 2,
    VGA_COLOR_CYAN          = 3,
    VGA_COLOR_RED           = 4,
    VGA_COLOR_MAGENTA       = 5,
    VGA_COLOR_BROWN         = 6,
    VGA_COLOR_LIGHT_GREY    = 7,
    VGA_COLOR_DARK_GREY     = 8,
    VGA_COLOR_LIGHT_BLUE    = 9,
    VGA_COLOR_LIGHT_GREEN   = 10,
    VGA_COLOR_LIGHT_CYAN    = 11,
    VGA_COLOR_LIGHT_RED     = 12,
    VGA_COLOR_LIGHT_MAGENTA = 13,
    VGA_COLOR_LIGHT_BROWN   = 14,
    VGA_COLOR_WHITE         = 15,
} vga_color_t;

static inline uint8_t vga_entry_color(vga_color_t fg, vga_color_t bg) {
    return (uint8_t)(fg | (bg << 4));
}

static inline uint16_t vga_entry(unsigned char uc, uint8_t color) {
    return (uint16_t)(uc | ((uint16_t)color << 8));
}

void vga_init(void);
void vga_set_color(uint8_t color);
void vga_putc(char c);
void vga_puts(const char *str);
void vga_puthex(uint32_t val);
void vga_putdec(uint32_t val);
void vga_clear(void);
void vga_set_cursor(size_t x, size_t y);

#endif /* ASTERIX_VGA_H */
