/*
 * ==============================================================================
 * ASTERIX OS - Interactive Microkernel Shell Implementation
 * Dual-console interactive CLI running simultaneously over VGA (0xB8000)
 * and 16550 UART Serial COM1 (0x3F8) for Headless and Mobile OTG terminals.
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/shell.h"
#include "../include/vga.h"
#include "../include/serial.h"
#include "../include/keyboard.h"
#include "../include/timer.h"
#include "../include/heap.h"
#include "../include/vfs.h"
#include "../include/kernel.h"

static void shell_puts(const char *s) {
    vga_puts(s);
    serial_puts(s);
}

__attribute__((unused)) static void shell_putc(char c) {
    vga_putc(c);
    serial_putc(c);
}

static void shell_putdec(uint32_t val) {
    vga_putdec(val);
    serial_putdec(val);
}

static void shell_puthex(uint32_t val) {
    vga_puthex(val);
    serial_puthex(val);
}

static int str_starts_with(const char *str, const char *prefix) {
    size_t i = 0;
    while (prefix[i] != '\0') {
        if (str[i] != prefix[i]) return 0;
        i++;
    }
    return 1;
}

static int str_equal(const char *s1, const char *s2) {
    size_t i = 0;
    while (s1[i] != '\0' && s2[i] != '\0') {
        if (s1[i] != s2[i]) return 0;
        i++;
    }
    return s1[i] == s2[i];
}

void shell_init(void) {
    vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK));
    shell_puts("\n===============================================================================\n");
    shell_puts("  ASTERIX OS Interactive Shell v1.0 (Dual-Console: VGA + COM1 Serial)\n");
    shell_puts("  Type 'help' to list commands. Real-time MMU and VFS operational.\n");
    shell_puts("===============================================================================\n\n");
    vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
}

void shell_execute_command(const char *cmd) {
    /* Skip leading whitespace */
    while (*cmd == ' ' || *cmd == '\t') cmd++;
    if (*cmd == '\0') return;

    if (str_equal(cmd, "help")) {
        vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK));
        shell_puts("ASTERIX OS Built-in Shell Commands:\n");
        vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
        shell_puts("  help             Display this help menu\n");
        shell_puts("  version / uname  Display OS and microkernel architecture\n");
        shell_puts("  meminfo          Display physical RAM, PMM frames & dynamic heap stats\n");
        shell_puts("  uptime           Display system running time and PIT clock ticks\n");
        shell_puts("  mmu              Display CPU hardware MMU Paging telemetry\n");
        shell_puts("  offload [type]   Offload compute (physics/ai/decompress) via int 0x80 to cluster\n");
        shell_puts("  ls               List files and pseudo-devices in VFS ramdisk\n");
        shell_puts("  cat <path>       Display contents of a file from VFS\n");
        shell_puts("  echo <message>   Print a message to the active consoles\n");
        shell_puts("  tasks            Display running tasks and PCBs\n");
        shell_puts("  clear            Clear the VGA terminal screen\n");
        shell_puts("  reboot           Halt and reset system\n");
    }
    else if (str_starts_with(cmd, "offload")) {
        uint32_t type = 1; /* Default: Physics Simulation */
        if (str_starts_with(cmd, "offload ai")) {
            type = 2; /* AI Tensor Sharding */
        } else if (str_starts_with(cmd, "offload decompress")) {
            type = 3; /* Asset Decompression */
        }
        uint32_t units = 1000;
        uint32_t target_node = 0; /* Auto-distribute across cluster */

        /* Trigger Kernel Syscall SYS_CLUSTER_OFFLOAD (int 0x80, EAX=7) */
        int result_node;
        __asm__ volatile (
            "pushl %%ebx\n"
            "movl %2, %%ebx\n"
            "int $0x80\n"
            "popl %%ebx\n"
            : "=a"(result_node)
            : "a"(7), "r"(type), "c"(units), "d"(target_node)
            : "memory"
        );

        shell_puts("[OK] Syscall SYS_CLUSTER_OFFLOAD executed. Task assigned to Cluster Node ");
        shell_putdec((uint32_t)result_node);
        shell_puts(".\n");
    }
    else if (str_equal(cmd, "version") || str_equal(cmd, "uname")) {
        shell_puts("ASTERIX OS 3.5.0-CYBER (i386 Protected Mode, Multiboot v1, Ring-0 MMU)\n");
        shell_puts("Built with Clang 23.1.1 + NASM 3.02 (Freestanding, Zero-libc)\n");
    }
    else if (str_equal(cmd, "meminfo")) {
        shell_puts("Memory Architecture Subsystem:\n");
        shell_puts("  - PMM Frame Size:   4096 bytes\n");
        shell_puts("  - Dynamic Heap:     2048 KB (Arena: 0x00500000 - 0x00700000)\n");
        shell_puts("  - Heap Bytes Used:  ");
        shell_putdec((uint32_t)heap_get_used_bytes());
        shell_puts(" bytes\n");
        shell_puts("  - Heap Bytes Free:  ");
        shell_putdec((uint32_t)heap_get_free_bytes());
        shell_puts(" bytes\n");
    }
    else if (str_equal(cmd, "uptime")) {
        uint32_t sec = timer_uptime_seconds();
        uint32_t ticks = timer_get_ticks();
        shell_puts("System Uptime: ");
        shell_putdec(sec);
        shell_puts(" seconds (");
        shell_putdec(ticks);
        shell_puts(" PIT clock ticks @ 100 Hz)\n");
    }
    else if (str_equal(cmd, "mmu")) {
        uint32_t cr0, cr2, cr3;
        __asm__ volatile("mov %%cr0, %0" : "=r"(cr0));
        __asm__ volatile("mov %%cr2, %0" : "=r"(cr2));
        __asm__ volatile("mov %%cr3, %0" : "=r"(cr3));

        shell_puts("Hardware MMU Paging Status:\n");
        shell_puts("  - CR0: ");
        shell_puthex(cr0);
        shell_puts(cr0 & 0x80000000 ? " [PAGING ENABLED (Bit 31)]\n" : " [PAGING DISABLED]\n");
        shell_puts("  - CR3 (Page Directory Base): ");
        shell_puthex(cr3);
        shell_puts("\n  - CR2 (Last Page Fault Addr): ");
        shell_puthex(cr2);
        shell_puts("\n  - Virtual Memory Mapping: 8 MB Identity Map Active\n");
    }
    else if (str_equal(cmd, "ls")) {
        vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_CYAN, VGA_COLOR_BLACK));
        shell_puts("VFS Ramdisk Contents:\n");
        vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
        vfs_node_t *curr = vfs_get_root_files();
        while (curr) {
            if (curr->flags == FS_DIRECTORY) {
                shell_puts("  [DIR]  ");
            } else if (curr->flags == FS_CHARDEVICE) {
                shell_puts("  [DEV]  ");
            } else {
                shell_puts("  [FILE] ");
            }
            shell_puts(curr->name);
            shell_puts(" (");
            shell_putdec((uint32_t)curr->size);
            shell_puts(" bytes)\n");
            curr = curr->next;
        }
    }
    else if (str_starts_with(cmd, "cat ")) {
        const char *path = cmd + 4;
        while (*path == ' ') path++;
        vfs_node_t *node = vfs_find(path);
        if (node) {
            char buf[512];
            vfs_read(node, buf, sizeof(buf));
            shell_puts(buf);
        } else {
            vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK));
            shell_puts("cat: file not found: ");
            shell_puts(path);
            shell_puts("\n");
            vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
        }
    }
    else if (str_starts_with(cmd, "echo ")) {
        shell_puts(cmd + 5);
        shell_puts("\n");
    }
    else if (str_equal(cmd, "clear")) {
        vga_clear();
    }
    else if (str_equal(cmd, "tasks")) {
        shell_puts("Active Process Control Blocks (PCBs):\n");
        shell_puts("  PID 0: kernel_init (RUNNING, Ring-0 Supervisor)\n");
        shell_puts("  PID 1: shell_daemon (READY, Interactive Dual-Console)\n");
    }
    else if (str_equal(cmd, "reboot")) {
        shell_puts("Restarting ASTERIX OS...\n");
        outb(0x64, 0xFE); /* Pulse CPU reset line via keyboard controller */
        __asm__ volatile("cli; hlt");
    }
    else {
        vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_RED, VGA_COLOR_BLACK));
        shell_puts("Unknown command: '");
        shell_puts(cmd);
        shell_puts("'. Type 'help' for available commands.\n");
        vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));
    }
}

void shell_run_interactive(void) {
    char input_buf[128];
    shell_init();

    for (;;) {
        vga_set_color(vga_entry_color(VGA_COLOR_LIGHT_GREEN, VGA_COLOR_BLACK));
        shell_puts("asterix> ");
        vga_set_color(vga_entry_color(VGA_COLOR_WHITE, VGA_COLOR_BLACK));

        keyboard_getline(input_buf, sizeof(input_buf));
        shell_execute_command(input_buf);
    }
}
