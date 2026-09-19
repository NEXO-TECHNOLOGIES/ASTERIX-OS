/*
 * ==============================================================================
 * ASTERIX OS - Programmable Interval Timer (PIT 8254) Header
 * Phase-locked 100 Hz timer tick for preemptive scheduling and uptime tracking
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_TIMER_H
#define ASTERIX_TIMER_H

#include <stdint.h>

#define PIT_CHANNEL0_DATA 0x40
#define PIT_COMMAND_REG   0x43
#define PIT_BASE_HZ       1193182

void     timer_init(uint32_t frequency_hz);
void     timer_on_tick(void);
uint32_t timer_get_ticks(void);
uint32_t timer_uptime_seconds(void);
void     sleep_ms(uint32_t ms);

#endif /* ASTERIX_TIMER_H */
