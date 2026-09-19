/*
 * ==============================================================================
 * ASTERIX OS - Hardware MMU Virtual Memory Paging Header
 * Architecture: 32-bit x86 Two-Tier Paging (Directory + Tables)
 * Zero libc: 100% Freestanding Bare-Metal Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_PAGING_H
#define ASTERIX_PAGING_H

#include <stdint.h>
#include <stddef.h>
#include "idt.h"

#define PAGE_PRESENT  0x001
#define PAGE_WRITE    0x002
#define PAGE_USER     0x004
#define PAGE_SIZE     4096
#define PAGES_PER_TBL 1024
#define TABLES_PER_DIR 1024

void paging_init(void);
void page_fault_handler(registers_t *regs);
int  paging_map_page(uint32_t virt_addr, uint32_t phys_addr, uint32_t flags);

#endif /* ASTERIX_PAGING_H */
