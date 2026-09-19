/*
 * ==============================================================================
 * ASTERIX OS - Virtual File System (VFS) & Embedded Ramdisk Implementation
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#include "../include/vfs.h"
#include "../include/serial.h"

static vfs_node_t node_pool[VFS_MAX_NODES];
static size_t node_count = 0;
static vfs_node_t *root_head = NULL;

static int str_equals(const char *s1, const char *s2) {
    size_t i = 0;
    while (s1[i] != '\0' && s2[i] != '\0') {
        if (s1[i] != s2[i]) return 0;
        i++;
    }
    return s1[i] == s2[i];
}

static size_t str_length(const char *s) {
    size_t len = 0;
    while (s[len] != '\0') len++;
    return len;
}

static void copy_string(char *dest, const char *src, size_t max) {
    size_t i = 0;
    while (src[i] != '\0' && i + 1 < max) {
        dest[i] = src[i];
        i++;
    }
    dest[i] = '\0';
}

static void vfs_register(const char *name, uint32_t flags, const char *content) {
    if (node_count >= VFS_MAX_NODES) return;

    vfs_node_t *node = &node_pool[node_count++];
    copy_string(node->name, name, VFS_NAME_MAX);
    node->flags = flags;
    node->content = content;
    node->size = content ? str_length(content) : 0;
    node->next = root_head;
    root_head = node;
}

void vfs_init(void) {
    node_count = 0;
    root_head = NULL;

    /* Populate standard pseudo-files */
    vfs_register("/etc/os-release", FS_FILE,
        "NAME=\"ASTERIX OS\"\nVERSION=\"3.5.0-CYBER\"\nID=asterix\nPRETTY_NAME=\"ASTERIX Freestanding Cyber Microkernel\"\n");

    vfs_register("/etc/hostname", FS_FILE,
        "asterix-baremetal-node1\n");

    vfs_register("/proc/version", FS_FILE,
        "ASTERIX OS Kernel 3.5.0 (x86_32 i386 Protected Mode) #1 PREEMPT Ring-0 MMU\n");

    vfs_register("/proc/cmdline", FS_FILE,
        "BOOT_IMAGE=/boot/asterix-microkernel.bin root=/dev/ram0 rw console=tty0 console=ttyS0,38400\n");

    vfs_register("/dev/tty0", FS_CHARDEVICE, "[VGA Console Character Device]\n");
    vfs_register("/dev/ttyS0", FS_CHARDEVICE, "[16550 UART COM1 Serial Device]\n");
    vfs_register("/bin/ax", FS_FILE, "[ASTERIX Master Dispatcher ELF Executable]\n");
    vfs_register("/bin/cluster", FS_FILE, "[ASTERIX Distributed Computing Engine]\n");

    serial_puts("[+] In-Memory Virtual File System (VFS) Initialized (/etc, /proc, /dev, /bin).\n");
}

vfs_node_t *vfs_find(const char *path) {
    vfs_node_t *curr = root_head;
    while (curr) {
        if (str_equals(curr->name, path)) {
            return curr;
        }
        curr = curr->next;
    }
    return NULL;
}

int vfs_read(vfs_node_t *node, char *out_buf, size_t max_len) {
    if (!node || !node->content || !out_buf || max_len == 0) return 0;
    size_t to_copy = node->size;
    if (to_copy >= max_len) to_copy = max_len - 1;

    for (size_t i = 0; i < to_copy; i++) {
        out_buf[i] = node->content[i];
    }
    out_buf[to_copy] = '\0';
    return (int)to_copy;
}

vfs_node_t *vfs_get_root_files(void) {
    return root_head;
}
