/*
 * ==============================================================================
 * 🌌 ASTERIX OS — Interrupt Descriptor Table (IDT) & CPU Interrupt Framework
 * Maps x86 Hardware Exceptions (0-31), 8259 Master/Slave PIC IRQs (32-47),
 * and Cybernetic System Call Gateway (int 0x80).
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_IDT_H
#define ASTERIX_IDT_H

#include <stdint.h>

#define IDT_ENTRIES 256

/* IDT Gate Descriptor */
struct idt_entry {
    uint16_t base_low;   /* Lower 16 bits of handler address */
    uint16_t sel;        /* Kernel segment selector (0x08) */
    uint8_t  always0;    /* Reserved, set to 0 */
    uint8_t  flags;      /* Type and attribute flags (0x8E for 32-bit interrupt gate) */
    uint16_t base_high;  /* Upper 16 bits of handler address */
} __attribute__((packed));
typedef struct idt_entry idt_entry_t;

/* IDT Pointer register structure passed to lidt */
struct idt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed));
typedef struct idt_ptr idt_ptr_t;

/* Saved CPU registers structure pushed by isr_stub */
typedef struct {
    uint32_t ds;                                     /* Data segment selector */
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax; /* Pushed by pusha */
    uint32_t int_no, err_code;                       /* Interrupt number and error code */
    uint32_t eip, cs, eflags, useresp, ss;           /* Pushed by processor automatically */
} registers_t;

/* 8259 Programmable Interrupt Controller (PIC) ports */
#define PIC1_COMMAND 0x20
#define PIC1_DATA    0x21
#define PIC2_COMMAND 0xA0
#define PIC2_DATA    0xA1

#define ICW1_INIT    0x11
#define ICW4_8086    0x01
#define PIC_EOI      0x20

void idt_init(void);
void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags);
void pic_remap(uint8_t offset1, uint8_t offset2);
void pic_send_eoi(uint8_t irq);

/* Global interrupt and exception handlers */
void isr_handler(registers_t *regs);
void irq_handler(registers_t *regs);

#endif /* ASTERIX_IDT_H */
