/*
 * ==============================================================================
 * ASTERIX OS - Interactive Microkernel Shell Header
 * Dual-console interactive CLI running over VGA (0xB8000) and COM1 (0x3F8)
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_SHELL_H
#define ASTERIX_SHELL_H

void shell_init(void);
void shell_execute_command(const char *cmd_line);
void shell_run_interactive(void);

#endif /* ASTERIX_SHELL_H */
