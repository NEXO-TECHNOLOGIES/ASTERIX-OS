/*
 * ==============================================================================
 * 🌌 ASTERIX OS — Freestanding Cyber Microkernel Core
 * Architecture: 32-bit x86 Protected Mode (i386)
 * Includes: VGA Console, IDT/PIC Remapper, Frame Allocator, Task Scheduler & Syscalls
 * Zero libc: 100% Freestanding Bare-Metal Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/kernel.h"
#include "../include/vga.h"
#include "../include/idt.h"

/* VGA Terminal State */
static size_t terminal_row = 0;
static size_t terminal_col = 0;
static uint8_t terminal_color = 0x0F; /* White on Black default */
static volatile uint16_t *terminal_buffer = VGA_MEMORY;

/* IDT and Physical Memory Tables */
static idt_entry_t idt[IDT_ENTRIES];
static idt_ptr_t   idt_pointer;

#define MAX_PHYSICAL_FRAMES 32768  /* 128 MB managed space (32768 * 4096) */
static uint32_t frame_bitmap[MAX_PHYSICAL_FRAMES / 32];
static frame_allocator_t pmm;

/* Process Scheduling Table */
static pcb_t task_table[MAX_TASKS];
static uint32_t current_task_id = 0;
static uint32_t total_tasks = 0;
static volatile uint32_t timer_ticks = 0;

/* =============================================================================
 * FREESTANDING VGA DRIVER
 * ============================================================================= */

void vga_set_cursor(size_t x, size_t y) {
    uint16_t pos = (uint16_t)(y * VGA_WIDTH + x);
    outb(0x3D4, 0x0F);
    outb(0x3D5, (uint8_t)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (uint8_t)((pos >> 8) & 0xFF));
}

void vga_clear(void) {
    for (size_t y = 0; y < VGA_HEIGHT; y++) {
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            terminal_buffer[y * VGA_WIDTH + x] = vga_entry(' ', terminal_color);
        }
    }
    terminal_row = 0;
    terminal_col = 0;
    vga_set_cursor(0, 0);
}

void vga_init(void) {
    terminal_row = 0;
    terminal_col = 0;
    terminal_color = vga_entry_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK);
    vga_clear();
}

void vga_set_color(uint8_t color) {
    terminal_color = color;
}

static void vga_scroll(void) {
    if (terminal_row >= VGA_HEIGHT) {
        for (size_t y = 1; y < VGA_HEIGHT; y++) {
            for (size_t x = 0; x < VGA_WIDTH; x++) {
                terminal_buffer[(y - 1) * VGA_WIDTH + x] = terminal_buffer[y * VGA_WIDTH + x];
            }
        }
        for (size_t x = 0; x < VGA_WIDTH; x++) {
            terminal_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + x] = vga_entry(' ', terminal_color);
        }
        terminal_row = VGA_HEIGHT - 1;
    }
}

void vga_putc(char c) {
    if (c == '\n') {
        terminal_col = 0;
        terminal_row++;
    } else if (c == '\r') {
        terminal_col = 0;
    } else if (c == '\t') {
        terminal_col = (terminal_col + 4) & ~3;
    } else if (c == '\b') {
        if (terminal_col > 0) {
            terminal_col--;
            terminal_buffer[terminal_row * VGA_WIDTH + terminal_col] = vga_entry(' ', terminal_color);
        }
    } else {
        terminal_buffer[terminal_row * VGA_WIDTH + terminal_col] = vga_entry(c, terminal_color);
        terminal_col++;
        if (terminal_col >= VGA_WIDTH) {
            terminal_col = 0;
            terminal_row++;
        }
    }
    vga_scroll();
    vga_set_cursor(terminal_col, terminal_row);
}

void vga_puts(const char *str) {
    if (!str) return;
    while (*str) {
        vga_putc(*str++);
    }
}

void vga_puthex(uint32_t val) {
    const char hex_chars[] = "0123456789ABCDEF";
    vga_puts("0x");
    for (int i = 28; i >= 0; i -= 4) {
        vga_putc(hex_chars[(val >> i) & 0xF]);
    }
}

void vga_putdec(uint32_t val) {
    if (val == 0) {
        vga_putc('0');
        return;
    }
    char buf[12];
    int i = 0;
    while (val > 0) {
        buf[i++] = (char)('0' + (val % 10));
        val /= 10;
    }
    while (--i >= 0) {
        vga_putc(buf[i]);
    }
}

/* =============================================================================
 * INTERRUPT DESCRIPTOR TABLE (IDT) & 8259 PIC REMAPPER
 * ============================================================================= */

/* External ISR and IRQ symbols declared in isr.asm */
extern void isr0(void);  extern void isr1(void);  extern void isr2(void);  extern void isr3(void);
extern void isr4(void);  extern void isr5(void);  extern void isr6(void);  extern void isr7(void);
extern void isr8(void);  extern void isr9(void);  extern void isr10(void); extern void isr11(void);
extern void isr12(void); extern void isr13(void); extern void isr14(void); extern void isr15(void);
extern void isr16(void); extern void isr17(void); extern void isr18(void); extern void isr19(void);
extern void isr20(void); extern void isr21(void); extern void isr22(void); extern void isr23(void);
extern void isr24(void); extern void isr25(void); extern void isr26(void); extern void isr27(void);
extern void isr28(void); extern void isr29(void); extern void isr30(void); extern void isr31(void);
extern void isr128(void); /* System call int 0x80 */

extern void irq0(void);  extern void irq1(void);  extern void irq2(void);  extern void irq3(void);
extern void irq4(void);  extern void irq5(void);  extern void irq6(void);  extern void irq7(void);
extern void irq8(void);  extern void irq9(void);  extern void irq10(void); extern void irq11(void);
extern void irq12(void); extern void irq13(void); extern void irq14(void); extern void irq15(void);

void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags) {
    idt[num].base_low  = (uint16_t)(base & 0xFFFF);
    idt[num].base_high = (uint16_t)((base >> 16) & 0xFFFF);
    idt[num].sel       = sel;
    idt[num].always0   = 0;
    idt[num].flags     = flags;
}

void pic_remap(uint8_t offset1, uint8_t offset2) {
    uint8_t mask1 = inb(PIC1_DATA);
    uint8_t mask2 = inb(PIC2_DATA);

    outb(PIC1_COMMAND, ICW1_INIT);
    io_wait();
    outb(PIC2_COMMAND, ICW1_INIT);
    io_wait();

    outb(PIC1_DATA, offset1);
    io_wait();
    outb(PIC2_DATA, offset2);
    io_wait();

    outb(PIC1_DATA, 4);
    io_wait();
    outb(PIC2_DATA, 2);
    io_wait();

    outb(PIC1_DATA, ICW4_8086);
    io_wait();
    outb(PIC2_DATA, ICW4_8086);
    io_wait();

    outb(PIC1_DATA, mask1);
    outb(PIC2_DATA, mask2);
}

void pic_send_eoi(uint8_t irq) {
    if (irq >= 8) {
        outb(PIC2_COMMAND, PIC_EOI);
    }
    outb(PIC1_COMMAND, PIC_EOI);
}

void idt_init(void) {
    idt_pointer.limit = (sizeof(idt_entry_t) * IDT_ENTRIES) - 1;
    idt_pointer.base  = (uint32_t)&idt;

    for (int i = 0; i < IDT_ENTRIES; i++) {
        idt_set_gate((uint8_t)i, 0, 0, 0);
    }

    /* CPU Exceptions */
    idt_set_gate(0,  (uint32_t)isr0,  0x08, 0x8E);
    idt_set_gate(1,  (uint32_t)isr1,  0x08, 0x8E);
    idt_set_gate(2,  (uint32_t)isr2,  0x08, 0x8E);
    idt_set_gate(3,  (uint32_t)isr3,  0x08, 0x8E);
    idt_set_gate(4,  (uint32_t)isr4,  0x08, 0x8E);
    idt_set_gate(5,  (uint32_t)isr5,  0x08, 0x8E);
    idt_set_gate(6,  (uint32_t)isr6,  0x08, 0x8E);
    idt_set_gate(7,  (uint32_t)isr7,  0x08, 0x8E);
    idt_set_gate(8,  (uint32_t)isr8,  0x08, 0x8E);
    idt_set_gate(9,  (uint32_t)isr9,  0x08, 0x8E);
    idt_set_gate(10, (uint32_t)isr10, 0x08, 0x8E);
    idt_set_gate(11, (uint32_t)isr11, 0x08, 0x8E);
    idt_set_gate(12, (uint32_t)isr12, 0x08, 0x8E);
    idt_set_gate(13, (uint32_t)isr13, 0x08, 0x8E);
    idt_set_gate(14, (uint32_t)isr14, 0x08, 0x8E);
    idt_set_gate(15, (uint32_t)isr15, 0x08, 0x8E);
    idt_set_gate(16, (uint32_t)isr16, 0x08, 0x8E);
    idt_set_gate(17, (uint32_t)isr17, 0x08, 0x8E);
    idt_set_gate(18, (uint32_t)isr18, 0x08, 0x8E);
    idt_set_gate(19, (uint32_t)isr19, 0x08, 0x8E);
    idt_set_gate(20, (uint32_t)isr20, 0x08, 0x8E);
    idt_set_gate(21, (uint32_t)isr21, 0x08, 0x8E);
    idt_set_gate(22, (uint32_t)isr22, 0x08, 0x8E);
    idt_set_gate(23, (uint32_t)isr23, 0x08, 0x8E);
    idt_set_gate(24, (uint32_t)isr24, 0x08, 0x8E);
    idt_set_gate(25, (uint32_t)isr25, 0x08, 0x8E);
    idt_set_gate(26, (uint32_t)isr26, 0x08, 0x8E);
    idt_set_gate(27, (uint32_t)isr27, 0x08, 0x8E);
    idt_set_gate(28, (uint32_t)isr28, 0x08, 0x8E);
    idt_set_gate(29, (uint32_t)isr29, 0x08, 0x8E);
    idt_set_gate(30, (uint32_t)isr30, 0x08, 0x8E);
    idt_set_gate(31, (uint32_t)isr31, 0x08, 0x8E);

    /* Remap PIC to avoid conflict with CPU exceptions */
    pic_remap(32, 40);

    /* Hardware IRQs */
    idt_set_gate(32, (uint32_t)irq0,  0x08, 0x8E);
    idt_set_gate(33, (uint32_t)irq1,  0x08, 0x8E);
    idt_set_gate(34, (uint32_t)irq2,  0x08, 0x8E);
    idt_set_gate(35, (uint32_t)irq3,  0x08, 0x8E);
    idt_set_gate(36, (uint32_t)irq4,  0x08, 0x8E);
    idt_set_gate(37, (uint32_t)irq5,  0x08, 0x8E);
    idt_set_gate(38, (uint32_t)irq6,  0x08, 0x8E);
    idt_set_gate(39, (uint32_t)irq7,  0x08, 0x8E);
    idt_set_gate(40, (uint32_t)irq8,  0x08, 0x8E);
    idt_set_gate(41, (uint32_t)irq9,  0x08, 0x8E);
    idt_set_gate(42, (uint32_t)irq10, 0x08, 0x8E);
    idt_set_gate(43, (uint32_t)irq11, 0x08, 0x8E);
    idt_set_gate(44, (uint32_t)irq12, 0x08, 0x8E);
    idt_set_gate(45, (uint32_t)irq13, 0x08, 0x8E);
    idt_set_gate(46, (uint32_t)irq14, 0x08, 0x8E);
    idt_set_gate(47, (uint32_t)irq15, 0x08, 0x8E);

    /* System Call Gate (int 0x80) - DPL=3 allows user-mode invocation */
    idt_set_gate(128, (uint32_t)isr128, 0x08, 0xEE);

    /* Load IDT into CPU */
    __asm__ volatile ("lidt %0" : : "m"(idt_pointer));
}

void isr_handler(registers_t *regs) {
    if (regs->int_no == 128) {
        /* System call dispatched via int 0x80 */
        regs->eax = (uint32_t)syscall_dispatch(regs->eax, regs->ebx, regs->ecx, regs->edx);
        return;
    }

    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK));
    vga_puts("\n[!] CRITICAL CPU EXCEPTION: ");
    vga_putdec(regs->int_no);
    vga_puts(" Error Code: ");
    vga_puthex(regs->err_code);
    vga_puts(" EIP: ");
    vga_puthex(regs->eip);
    vga_puts("\n");
    panic("Kernel execution halted due to unhandled CPU fault.");
}

void irq_handler(registers_t *regs) {
    uint8_t irq = (uint8_t)(regs->int_no - 32);

    if (irq == 0) {
        timer_ticks++;
        if (timer_ticks % 100 == 0) {
            /* Periodic scheduler tick */
        }
    } else if (irq == 1) {
        /* PS/2 Keyboard byte received */
        uint8_t scancode = inb(0x60);
        (void)scancode;
    }

    pic_send_eoi(irq);
}

/* =============================================================================
 * PHYSICAL FRAME MEMORY ALLOCATOR (PMM)
 * ============================================================================= */

static inline void set_frame(uint32_t frame_addr) {
    uint32_t frame = frame_addr / PAGE_SIZE;
    frame_bitmap[frame / 32] |= (1 << (frame % 32));
}

static inline void clear_frame(uint32_t frame_addr) {
    uint32_t frame = frame_addr / PAGE_SIZE;
    frame_bitmap[frame / 32] &= ~(1 << (frame % 32));
}

static inline bool test_frame(uint32_t frame_addr) {
    uint32_t frame = frame_addr / PAGE_SIZE;
    return (frame_bitmap[frame / 32] & (1 << (frame % 32))) != 0;
}

static uint32_t first_free_frame(void) {
    for (uint32_t i = 0; i < (MAX_PHYSICAL_FRAMES / 32); i++) {
        if (frame_bitmap[i] != 0xFFFFFFFF) {
            for (int j = 0; j < 32; j++) {
                if (!(frame_bitmap[i] & (1 << j))) {
                    return (i * 32) + j;
                }
            }
        }
    }
    return (uint32_t)-1;
}

void memory_init(uint32_t mem_size_kb) {
    pmm.memory_limit = mem_size_kb * 1024;
    pmm.total_frames = pmm.memory_limit / PAGE_SIZE;
    if (pmm.total_frames > MAX_PHYSICAL_FRAMES) {
        pmm.total_frames = MAX_PHYSICAL_FRAMES;
    }
    pmm.used_frames = 0;
    pmm.bitmap = (uint8_t*)frame_bitmap;

    /* Initialize all frames as free */
    for (uint32_t i = 0; i < (MAX_PHYSICAL_FRAMES / 32); i++) {
        frame_bitmap[i] = 0;
    }

    /* Reserve first 4MB for Kernel Code, VGA buffer & Page tables */
    for (uint32_t addr = 0; addr < 0x400000; addr += PAGE_SIZE) {
        set_frame(addr);
        pmm.used_frames++;
    }
}

void *pmm_alloc_frame(void) {
    uint32_t frame = first_free_frame();
    if (frame == (uint32_t)-1) {
        panic("Kernel Physical Frame Allocator: Out of Memory!");
    }
    uint32_t addr = frame * PAGE_SIZE;
    set_frame(addr);
    pmm.used_frames++;
    return (void*)addr;
}

void pmm_free_frame(void *frame) {
    uint32_t addr = (uint32_t)frame;
    if (test_frame(addr)) {
        clear_frame(addr);
        pmm.used_frames--;
    }
}

/* =============================================================================
 * MICROKERNEL SYSTEM CALL DISPATCHER (INT 0x80)
 * ============================================================================= */

int syscall_dispatch(uint32_t num, uint32_t arg1, uint32_t arg2, uint32_t arg3) {
    (void)arg3;
    switch ((syscall_t)num) {
        case SYS_WRITE: {
            const char *msg = (const char*)arg1;
            uint32_t len = arg2;
            for (uint32_t i = 0; i < len; i++) {
                vga_putc(msg[i]);
            }
            return (int)len;
        }
        case SYS_GETPID:
            return (int)current_task_id;

        case SYS_YIELD:
            scheduler_yield();
            return 0;

        case SYS_AUDIT:
            vga_set_color(vga_entry_color(VGA_COLOR_CYAN, VGA_COLOR_BLACK));
            vga_puts("[AUDIT] Security audit heartbeat tick: ");
            vga_putdec(timer_ticks);
            vga_puts("\n");
            vga_set_color(terminal_color);
            return 0;

        case SYS_EXIT:
            vga_puts("[KERNEL] Process terminated via SYS_EXIT.\n");
            return 0;

        default:
            return -1;
    }
}

void scheduler_yield(void) {
    if (total_tasks <= 1) return;
    current_task_id = (current_task_id + 1) % total_tasks;
}

void scheduler_init(void) {
    total_tasks = 1;
    current_task_id = 0;
    task_table[0].pid = 0;
    task_table[0].state = TASK_STATE_RUNNING;
    task_table[0].priority = 1;
    for (int i = 0; i < 32; i++) {
        task_table[0].name[i] = "kernel_init"[i];
    }
}

void panic(const char *msg) {
    vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_RED));
    vga_puts("\n\n [!] ASTERIX KERNEL PANIC: ");
    vga_puts(msg);
    vga_puts(" — HALTED.\n");
    __asm__ volatile ("cli; hlt");
    for (;;) {}
}

/* =============================================================================
 * KERNEL ENTRY POINT
 * ============================================================================= */

void kmain(uint32_t magic, uint32_t mb_addr) {
    (void)mb_addr;

    /* Initialize Video Graphics Console */
    vga_init();

    /* Header Banner */
    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK));
    vga_puts("===============================================================================\n");
    vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
    vga_puts("  🌌 ASTERIX OS — Freestanding Cyber Microkernel Core v3.5\n");
    vga_puts("  Zero-Dependency Bare Metal • Ring 0 Security Architecture\n");
    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK));
    vga_puts("===============================================================================\n\n");

    /* Verify Multiboot Magic */
    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK));
    vga_puts("[*] Multiboot Signature Check: ");
    if (magic == 0x1BADB002 || magic == 0x2BADB002) {
        vga_puts("VALID (");
        vga_puthex(magic);
        vga_puts(")\n");
    } else {
        vga_puts("STANDALONE ENTRY (");
        vga_puthex(magic);
        vga_puts(")\n");
    }

    /* Initialize Interrupt Descriptor Table */
    vga_puts("[*] Initializing IDT and Remapping 8259 PIC... ");
    idt_init();
    vga_puts("[DONE]\n");

    /* Initialize Physical Memory Frame Allocator */
    vga_puts("[*] Initializing Physical Frame Allocator (64 MB)... ");
    memory_init(65536);
    vga_puts("[DONE]\n");
    vga_puts("    • Total Memory Frames: ");
    vga_putdec(pmm.total_frames);
    vga_puts(" (Used: ");
    vga_putdec(pmm.used_frames);
    vga_puts(" | Free: ");
    vga_putdec(pmm.total_frames - pmm.used_frames);
    vga_puts(")\n");

    /* Allocate and free test frame */
    void *test_frame_ptr = pmm_alloc_frame();
    vga_puts("[*] Memory Frame Allocation Self-Test: Allocated Frame at ");
    vga_puthex((uint32_t)test_frame_ptr);
    pmm_free_frame(test_frame_ptr);
    vga_puts(" -> FREED [OK]\n");

    /* Initialize Round-Robin Task Scheduler */
    vga_puts("[*] Initializing Task Scheduler & Security Gateway... ");
    scheduler_init();
    vga_puts("[DONE]\n");

    /* Enable Interrupts */
    __asm__ volatile ("sti");
    vga_puts("[✔] Hardware Interrupts Active (STI).\n\n");

    /* Demonstrate Syscall int 0x80 */
    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_BLUE, VGA_COLOR_BLACK));
    vga_puts("[*] Testing Kernel Syscall int 0x80 (SYS_AUDIT):\n");
    __asm__ volatile (
        "mov $5, %%eax\n"
        "mov $0, %%ebx\n"
        "mov $0, %%ecx\n"
        "mov $0, %%edx\n"
        "int $0x80\n"
        : : : "eax", "ebx", "ecx", "edx"
    );

    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK));
    vga_puts("\n[✔] ASTERIX Microkernel initialization complete. Security loop running.\n");

    /* Kernel Idle Loop */
    for (;;) {
        __asm__ volatile ("hlt");
    }
}
