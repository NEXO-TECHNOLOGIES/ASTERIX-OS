/*
 * ==============================================================================
 * ASTERIX OS - Programmable Interval Timer (PIT 8254) Implementation
 * Programs hardware oscillator frequency on I/O ports 0x40/0x43
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/timer.h"
#include "../include/kernel.h"
#include "../include/serial.h"

static volatile uint32_t system_ticks = 0;
static uint32_t timer_hz = 100;

void timer_init(uint32_t frequency_hz) {
    timer_hz = frequency_hz;
    uint32_t divisor = PIT_BASE_HZ / frequency_hz;

    /* Command byte 0x36: Channel 0, lobyte/hibyte, Mode 3 square-wave */
    outb(PIT_COMMAND_REG, 0x36);
    outb(PIT_CHANNEL0_DATA, (uint8_t)(divisor & 0xFF));
    outb(PIT_CHANNEL0_DATA, (uint8_t)((divisor >> 8) & 0xFF));

    serial_puts("[+] 8254 PIT Initialized at ");
    serial_putdec(frequency_hz);
    serial_puts(" Hz.\n");
}

void timer_on_tick(void) {
    system_ticks++;
}

uint32_t timer_get_ticks(void) {
    return system_ticks;
}

uint32_t timer_uptime_seconds(void) {
    return system_ticks / timer_hz;
}

void sleep_ms(uint32_t ms) {
    uint32_t target_ticks = system_ticks + ((ms * timer_hz) / 1000);
    while (system_ticks < target_ticks) {
        __asm__ volatile("hlt");
    }
}
