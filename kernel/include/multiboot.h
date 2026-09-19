/*
 * ==============================================================================
 * ASTERIX OS - Multiboot Specification v1 Header
 * Standard x86 Multiboot Information Structure & Memory Map
 * Zero libc: 100% Freestanding Bare-Metal Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_MULTIBOOT_H
#define ASTERIX_MULTIBOOT_H

#include <stdint.h>

#define MULTIBOOT_BOOTLOADER_MAGIC    0x2BADB002
#define MULTIBOOT_INFO_MEMORY         0x00000001
#define MULTIBOOT_INFO_BOOTDEV        0x00000002
#define MULTIBOOT_INFO_CMDLINE        0x00000004
#define MULTIBOOT_INFO_MODS           0x00000008
#define MULTIBOOT_INFO_AOUT_SYMS      0x00000010
#define MULTIBOOT_INFO_ELF_SHDR       0x00000020
#define MULTIBOOT_INFO_MEM_MAP        0x00000040

#define MULTIBOOT_MEMORY_AVAILABLE        1
#define MULTIBOOT_MEMORY_RESERVED         2
#define MULTIBOOT_MEMORY_ACPI_RECLAIMABLE 3
#define MULTIBOOT_MEMORY_NVS              4
#define MULTIBOOT_MEMORY_BADRAM           5

typedef struct multiboot_mmap_entry {
    uint32_t size;
    uint32_t addr_low;
    uint32_t addr_high;
    uint32_t len_low;
    uint32_t len_high;
    uint32_t type;
} __attribute__((packed)) multiboot_memory_map_t;

typedef struct multiboot_info {
    uint32_t flags;
    uint32_t mem_lower;
    uint32_t mem_upper;
    uint32_t boot_device;
    uint32_t cmdline;
    uint32_t mods_count;
    uint32_t mods_addr;
    uint32_t num;
    uint32_t size;
    uint32_t addr;
    uint32_t shndx;
    uint32_t mmap_length;
    uint32_t mmap_addr;
    uint32_t drives_length;
    uint32_t drives_addr;
    uint32_t config_table;
    uint32_t boot_loader_name;
    uint32_t apm_table;
    uint32_t vbe_control_info;
    uint32_t vbe_mode_info;
    uint16_t vbe_mode;
    uint16_t vbe_interface_seg;
    uint16_t vbe_interface_off;
    uint16_t vbe_interface_len;
} __attribute__((packed)) multiboot_info_t;

#endif /* ASTERIX_MULTIBOOT_H */
