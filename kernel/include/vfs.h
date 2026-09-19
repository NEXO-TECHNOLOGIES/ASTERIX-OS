/*
 * ==============================================================================
 * ASTERIX OS - Virtual File System (VFS) & Embedded Ramdisk Header
 * In-memory POSIX-compatible filesystem tree (/etc, /proc, /dev, /bin)
 * Zero libc: 100% Freestanding Implementation
 * SPDX-License-Identifier: MIT OR Apache-2.0
 * ==============================================================================
 */

#ifndef ASTERIX_VFS_H
#define ASTERIX_VFS_H

#include <stdint.h>
#include <stddef.h>

#define FS_FILE        0x01
#define FS_DIRECTORY   0x02
#define FS_CHARDEVICE  0x03

#define VFS_MAX_NODES  32
#define VFS_NAME_MAX   32

typedef struct vfs_node {
    char     name[VFS_NAME_MAX];
    uint32_t flags;
    size_t   size;
    const char *content;
    struct vfs_node *next;
} vfs_node_t;

void        vfs_init(void);
vfs_node_t *vfs_find(const char *path);
int         vfs_read(vfs_node_t *node, char *out_buf, size_t max_len);
vfs_node_t *vfs_get_root_files(void);

#endif /* ASTERIX_VFS_H */
