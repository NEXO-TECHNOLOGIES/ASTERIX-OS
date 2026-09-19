/*
 * ==============================================================================
 * ASTERIX OS - Dynamic Kernel Heap Allocator Header
 * Provides byte-level memory allocation (kmalloc, kfree, kcalloc)
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_HEAP_H
#define ASTERIX_HEAP_H

#include <stdint.h>
#include <stddef.h>

#define KERNEL_HEAP_START 0x00500000  /* 5 MB mark (within 8 MB identity map) */
#define KERNEL_HEAP_SIZE  0x00200000  /* 2 MB initial dynamic heap */

typedef struct heap_block {
    uint32_t size;
    uint32_t is_free;
    struct heap_block *next;
    struct heap_block *prev;
} heap_block_t;

void  heap_init(void);
void *kmalloc(size_t size);
void  kfree(void *ptr);
void *kcalloc(size_t num, size_t size);
size_t heap_get_used_bytes(void);
size_t heap_get_free_bytes(void);

#endif /* ASTERIX_HEAP_H */
