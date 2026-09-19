/*
 * ==============================================================================
 * ASTERIX OS - Cyber Microkernel Core Header
 * High-Security Microkernel: Paging, Memory Allocator, Task Scheduler & Syscalls
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_KERNEL_H
#define ASTERIX_KERNEL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "vga.h"
#include "idt.h"

#define KERNEL_NAME        "ASTERIX Microkernel"
#define KERNEL_VERSION     "3.5.0-CYBER"
#define PAGE_SIZE          4096
#define MAX_TASKS          16
#define KERNEL_STACK_SIZE  16384

/* Hardware I/O Port Routines */
static inline void outb(uint16_t port, uint8_t val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void io_wait(void) {
    outb(0x80, 0);
}

/* Microkernel System Call Identifiers */
typedef enum {
    SYS_EXIT            = 0,
    SYS_WRITE           = 1,
    SYS_READ            = 2,
    SYS_YIELD           = 3,
    SYS_GETPID          = 4,
    SYS_AUDIT           = 5,
    SYS_SECLOG          = 6,
    SYS_CLUSTER_OFFLOAD = 7,
} syscall_t;

/* Process / Task Execution State */
typedef enum {
    TASK_STATE_UNUSED   = 0,
    TASK_STATE_READY    = 1,
    TASK_STATE_RUNNING  = 2,
    TASK_STATE_SLEEPING = 3,
    TASK_STATE_ZOMBIE   = 4,
} task_state_t;

/* Process Control Block (PCB) */
typedef struct {
    uint32_t     pid;
    char         name[32];
    task_state_t state;
    uint32_t     esp;
    uint32_t     ebp;
    uint32_t     cr3;           /* Page directory base */
    uint32_t     ticks;         /* Execution runtime */
    uint32_t     priority;      /* 1 = Highest, 10 = Idle */
    uint8_t      stack[KERNEL_STACK_SIZE];
} pcb_t;

/* Physical Frame Allocator State */
typedef struct {
    uint32_t total_frames;
    uint32_t used_frames;
    uint32_t memory_limit;
    uint8_t  *bitmap;
} frame_allocator_t;

/* Global Kernel Functions */
void kmain(uint32_t magic, uint32_t mb_addr);
void panic(const char *msg);
void gdt_init(void);
void memory_init(uint32_t mem_size_kb);
void *pmm_alloc_frame(void);
void pmm_free_frame(void *frame);
void scheduler_init(void);
void scheduler_yield(void);
int  syscall_dispatch(uint32_t num, uint32_t arg1, uint32_t arg2, uint32_t arg3);

#endif /* ASTERIX_KERNEL_H */
