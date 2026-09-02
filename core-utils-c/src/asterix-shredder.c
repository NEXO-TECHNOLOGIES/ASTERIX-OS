/*
 * =====================================================================
 * ASTERIX OS - Native C Secure Storage Shredder (asterix-shredder)
 * Multi-pass secure file wiper (DoD 5220.22-M / Zero-Fill)
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <time.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

#define CHUNK_SIZE 65536

void fill_random(unsigned char *buf, size_t size) {
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd >= 0) {
        read(fd, buf, size);
        close(fd);
    } else {
        for (size_t i = 0; i < size; i++) buf[i] = rand() % 256;
    }
}

int shred_file(const char *path, int passes) {
    struct stat st;
    if (stat(path, &st) != 0) {
        perror("[!] Target file does not exist");
        return 1;
    }

    if (!S_ISREG(st.st_mode)) {
        fprintf(stderr, "%s[!] Target is not a regular file.%s\n", C_RED, C_RESET);
        return 1;
    }

    off_t file_size = st.st_size;
    FILE *fp = fopen(path, "r+b");
    if (!fp) {
        perror("[!] Unable to open file with write permissions");
        return 1;
    }

    unsigned char *chunk = (unsigned char *)malloc(CHUNK_SIZE);
    if (!chunk) {
        fclose(fp);
        return 1;
    }

    printf("\n%s[*] Securely Sanitizing:%s %s (%ld bytes, %d passes)%s\n", 
           C_CYAN, C_WHITE, path, file_size, passes, C_RESET);

    for (int p = 1; p <= passes; p++) {
        fseek(fp, 0, SEEK_SET);
        off_t written = 0;

        if (p == passes) {
            memset(chunk, 0x00, CHUNK_SIZE);
            printf("  • Pass %d/%d: %s[ Zero-Fill Sanitization ]%s\n", p, passes, C_GREEN, C_RESET);
        } else if (p % 2 == 1) {
            fill_random(chunk, CHUNK_SIZE);
            printf("  • Pass %d/%d: %s[ Cryptographic Random Noise ]%s\n", p, passes, C_YELLOW, C_RESET);
        } else {
            memset(chunk, 0xFF, CHUNK_SIZE);
            printf("  • Pass %d/%d: %s[ One-Fill Inversion ]%s\n", p, passes, C_MAGENTA, C_RESET);
        }

        while (written < file_size) {
            size_t to_write = (file_size - written > CHUNK_SIZE) ? CHUNK_SIZE : (size_t)(file_size - written);
            fwrite(chunk, 1, to_write, fp);
            written += to_write;
        }
        fflush(fp);
        fsync(fileno(fp));
    }

    free(chunk);
    fclose(fp);

    // Truncate and unlink file
    truncate(path, 0);
    unlink(path);

    printf("%s[✔] File successfully shredded and unlinked from filesystem.%s\n\n", C_GREEN, C_RESET);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("%sASTERIX OS - Secure Storage & File Shredder%s\n", C_CYAN, C_RESET);
        printf("Usage: %s <file_path> [passes (default: 3)]\n", argv[0]);
        return 1;
    }

    int passes = 3;
    if (argc >= 3) {
        passes = atoi(argv[2]);
        if (passes < 1 || passes > 35) passes = 3;
    }

    srand(time(NULL));
    return shred_file(argv[1], passes);
}
