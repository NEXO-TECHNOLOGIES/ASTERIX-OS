/*
 * ==============================================================================
 * ASTERIX OS - Multiboot Kernel Linker Script
 * Locates kernel binary at 1MB (0x00100000) conventional memory
 * ==============================================================================
 */

ENTRY(_start)

SECTIONS
{
    . = 1M;

    .text : ALIGN(4K)
    {
        *(.multiboot)
        *(.text)
    }

    .rodata : ALIGN(4K)
    {
        *(.rodata)
    }

    .data : ALIGN(4K)
    {
        *(.data)
    }

    .bss : ALIGN(4K)
    {
        *(COMMON)
        *(.bss)
    }
}
