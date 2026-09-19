/*
 * ==============================================================================
 * ASTERIX OS - Dynamic Kernel Heap Allocator Implementation
 * Doubly-linked boundary-tag block allocator with coalescing & splitting
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/heap.h"
#include "../include/serial.h"

static heap_block_t *heap_head = NULL;
static size_t total_used = 0;

void heap_init(void) {
    heap_head = (heap_block_t *)KERNEL_HEAP_START;
    heap_head->size = KERNEL_HEAP_SIZE - sizeof(heap_block_t);
    heap_head->is_free = 1;
    heap_head->next = NULL;
    heap_head->prev = NULL;
    total_used = 0;

    serial_puts("[+] Kernel Dynamic Heap Initialized (Arena: 0x00500000 - 2 MB).\n");
}

void *kmalloc(size_t size) {
    if (size == 0) return NULL;

    /* 8-byte boundary alignment */
    size = (size + 7) & ~7;

    heap_block_t *curr = heap_head;
    while (curr) {
        if (curr->is_free && curr->size >= size) {
            /* Check if we can split the block */
            if (curr->size >= size + sizeof(heap_block_t) + 16) {
                heap_block_t *split = (heap_block_t *)((uint8_t *)curr + sizeof(heap_block_t) + size);
                split->size = curr->size - size - sizeof(heap_block_t);
                split->is_free = 1;
                split->next = curr->next;
                split->prev = curr;

                if (curr->next) {
                    curr->next->prev = split;
                }
                curr->next = split;
                curr->size = size;
            }

            curr->is_free = 0;
            total_used += curr->size;
            return (void *)((uint8_t *)curr + sizeof(heap_block_t));
        }
        curr = curr->next;
    }

    serial_puts("[!] Out of Memory: kmalloc request failed!\n");
    return NULL;
}

void kfree(void *ptr) {
    if (!ptr) return;

    heap_block_t *block = (heap_block_t *)((uint8_t *)ptr - sizeof(heap_block_t));
    block->is_free = 1;
    if (total_used >= block->size) {
        total_used -= block->size;
    }

    /* Coalesce with next block if free */
    if (block->next && block->next->is_free) {
        block->size += sizeof(heap_block_t) + block->next->size;
        block->next = block->next->next;
        if (block->next) {
            block->next->prev = block;
        }
    }

    /* Coalesce with previous block if free */
    if (block->prev && block->prev->is_free) {
        block->prev->size += sizeof(heap_block_t) + block->size;
        block->prev->next = block->next;
        if (block->next) {
            block->next->prev = block->prev;
        }
    }
}

void *kcalloc(size_t num, size_t size) {
    size_t total = num * size;
    void *ptr = kmalloc(total);
    if (!ptr) return NULL;

    uint8_t *byte_ptr = (uint8_t *)ptr;
    for (size_t i = 0; i < total; i++) {
        byte_ptr[i] = 0;
    }
    return ptr;
}

size_t heap_get_used_bytes(void) {
    return total_used;
}

size_t heap_get_free_bytes(void) {
    return (KERNEL_HEAP_SIZE - sizeof(heap_block_t)) - total_used;
}
