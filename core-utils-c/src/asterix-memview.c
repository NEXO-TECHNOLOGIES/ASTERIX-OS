/*
 * =====================================================================
 * ASTERIX OS - Native C Memory & Binary Hex Visualizer (memview)
 * Inspects process memory maps, binary buffers, and hex dumps
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_MAGENTA "\033[38;5;201m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_GRAY    "\033[38;5;240m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

#define BYTES_PER_LINE 16

void hex_dump(const unsigned char *buffer, size_t size, unsigned long base_offset) {
    printf("%s%sOFFSET     00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  | ASCII MATRIX    |%s\n", 
           C_CYAN, C_BOLD, C_RESET);
    printf("%s--------------------------------------------------------------------------------%s\n", 
           C_GRAY, C_RESET);

    for (size_t i = 0; i < size; i += BYTES_PER_LINE) {
        printf("%s%08lX%s  ", C_YELLOW, base_offset + i, C_RESET);

        for (size_t j = 0; j < BYTES_PER_LINE; j++) {
            if (i + j < size) {
                unsigned char byte = buffer[i + j];
                if (byte == 0x00) {
                    printf("%s00%s ", C_GRAY, C_RESET);
                } else if (isprint(byte)) {
                    printf("%s%02X%s ", C_GREEN, byte, C_RESET);
                } else {
                    printf("%s%02X%s ", C_MAGENTA, byte, C_RESET);
                }
            } else {
                printf("   ");
            }
            if (j == 7) printf(" ");
        }

        printf(" |%s", C_WHITE);
        for (size_t j = 0; j < BYTES_PER_LINE; j++) {
            if (i + j < size) {
                unsigned char byte = buffer[i + j];
                printf("%c", isprint(byte) ? byte : '.');
            } else {
                printf(" ");
            }
        }
        printf("%s|\n", C_RESET);
    }
}

int inspect_file(const char *path, size_t max_bytes) {
    FILE *fp = fopen(path, "rb");
    if (!fp) {
        perror("[!] Error opening target file");
        return 1;
    }

    unsigned char *buffer = (unsigned char *)malloc(max_bytes);
    if (!buffer) {
        fclose(fp);
        fprintf(stderr, "[!] Memory allocation failure.\n");
        return 1;
    }

    size_t read_bytes = fread(buffer, 1, max_bytes, fp);
    fclose(fp);

    printf("\n%s[*] Inspecting:%s %s (%zu bytes)%s\n\n", C_CYAN, C_WHITE, path, read_bytes, C_RESET);
    hex_dump(buffer, read_bytes, 0);
    free(buffer);
    return 0;
}

int inspect_process_maps(pid_t pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/maps", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) {
        fprintf(stderr, "%s[!] Unable to access memory map for PID %d%s\n", C_RED, pid, C_RESET);
        return 1;
    }

    printf("\n%s[*] Process Memory Mapping for PID %d:%s\n\n", C_CYAN, pid, C_RESET);
    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        printf("%s%s%s", C_WHITE, line, C_RESET);
    }
    fclose(fp);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("%sASTERIX OS - Native Memory & Binary Hex Inspector%s\n", C_CYAN, C_RESET);
        printf("Usage:\n");
        printf("  %s <file_path> [max_bytes]    » Hex dump binary/memory file (default: 512 bytes)\n", argv[0]);
        printf("  %s -p <pid>                   » Inspect process virtual memory layout\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "-p") == 0 && argc >= 3) {
        pid_t pid = atoi(argv[2]);
        return inspect_process_maps(pid);
    }

    size_t max_bytes = 512;
    if (argc >= 3) {
        max_bytes = (size_t)atoi(argv[2]);
        if (max_bytes == 0 || max_bytes > 65536) max_bytes = 512;
    }

    return inspect_file(argv[1], max_bytes);
}
