/*
 * ==============================================================================
 * ASTERIX OS - Hardware MMU Virtual Memory Paging Implementation
 * Architecture: x86 32-bit Two-Tier Paging (Directory + Tables)
 * Manages CPU MMU (CR0.PG bit 31, CR3, CR2 Page Fault Telemetry)
 * Zero libc: 100% Freestanding Bare-Metal Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/paging.h"
#include "../include/kernel.h"
#include "../include/vga.h"
#include "../include/serial.h"

/* 4096-byte aligned Page Directory and initial kernel Page Tables */
__attribute__((aligned(4096))) static uint32_t page_directory[TABLES_PER_DIR];
__attribute__((aligned(4096))) static uint32_t kernel_page_table_0[PAGES_PER_TBL];
__attribute__((aligned(4096))) static uint32_t kernel_page_table_1[PAGES_PER_TBL];

static inline void load_page_directory(uint32_t *dir) {
    __asm__ volatile("mov %0, %%cr3" : : "r"(dir));
}

static inline void enable_paging_mmu(void) {
    uint32_t cr0;
    __asm__ volatile("mov %%cr0, %0" : "=r"(cr0));
    cr0 |= 0x80000000; /* Set bit 31 (Paging Enable) */
    __asm__ volatile("mov %0, %%cr0" : : "r"(cr0));
}

static inline uint32_t read_cr2(void) {
    uint32_t val;
    __asm__ volatile("mov %%cr2, %0" : "=r"(val));
    return val;
}

void page_fault_handler(registers_t *regs) {
    uint32_t faulting_address = read_cr2();
    int not_present = !(regs->err_code & 0x1);
    int write_op    = regs->err_code & 0x2;
    int user_mode   = regs->err_code & 0x4;
    int reserved    = regs->err_code & 0x8;
    int insn_fetch  = regs->err_code & 0x10;

    serial_puts("\n\n[!] CRITICAL: HARDWARE PAGE FAULT (CR2: ");
    serial_puthex(faulting_address);
    serial_puts(" EIP: ");
    serial_puthex(regs->eip);
    serial_puts(" Flags: ");
    if (not_present) serial_puts("[NOT PRESENT] ");
    if (write_op)    serial_puts("[WRITE] ");
    if (user_mode)   serial_puts("[USER] ");
    if (reserved)    serial_puts("[RESERVED] ");
    if (insn_fetch)  serial_puts("[INSN FETCH] ");
    serial_puts(")\n");

    vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_RED));
    vga_puts("\n\n [!] ASTERIX KERNEL PAGE FAULT: Linear Addr ");
    vga_puthex(faulting_address);
    vga_puts(" at EIP ");
    vga_puthex(regs->eip);
    vga_puts("\n     Flags: ");
    if (not_present) vga_puts("NOT-PRESENT ");
    if (write_op)    vga_puts("WRITE ");
    if (user_mode)   vga_puts("USER ");
    if (reserved)    vga_puts("RESERVED ");
    if (insn_fetch)  vga_puts("FETCH ");
    vga_puts("\n System halted.\n");

    __asm__ volatile("cli; hlt");
    for (;;) {}
}

void paging_init(void) {
    /* 1. Blank out the Page Directory (Kernel Supervisor, RW, Not-Present) */
    for (int i = 0; i < TABLES_PER_DIR; i++) {
        page_directory[i] = 0x00000002;
    }

    /* 2. Identity-map 0x00000000 -> 0x003FFFFF (First 4 MB: Kernel, VGA, BIOS) */
    for (uint32_t i = 0; i < PAGES_PER_TBL; i++) {
        kernel_page_table_0[i] = (i * PAGE_SIZE) | PAGE_PRESENT | PAGE_WRITE;
    }

    /* 3. Identity-map 0x00400000 -> 0x007FFFFF (Second 4 MB: PMM frame allocator, stack) */
    for (uint32_t i = 0; i < PAGES_PER_TBL; i++) {
        kernel_page_table_1[i] = (0x00400000 + (i * PAGE_SIZE)) | PAGE_PRESENT | PAGE_WRITE;
    }

    /* 4. Install Page Tables into Page Directory */
    page_directory[0] = ((uint32_t)kernel_page_table_0) | PAGE_PRESENT | PAGE_WRITE;
    page_directory[1] = ((uint32_t)kernel_page_table_1) | PAGE_PRESENT | PAGE_WRITE;

    /* 5. Load CR3 with Physical Address of Page Directory */
    load_page_directory(page_directory);

    /* 6. Activate CPU Hardware Paging */
    enable_paging_mmu();

    serial_puts("[+] Hardware MMU Paging Initialized (CR0.PG Active | 8 MB Identity Map).\n");
}
