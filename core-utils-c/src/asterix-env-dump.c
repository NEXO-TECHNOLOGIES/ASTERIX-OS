/*
 * =====================================================================
 * ASTERIX OS :: DEEP KERNEL :: Full Process Environment & FD Dumper
 * Dumps all environment variables and open file descriptors for a PID
 * Language: C (GNU C11)
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_GRAY    "\033[38;5;240m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

void dump_env(int pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/environ", pid);
    FILE *fp = fopen(path, "rb");
    if (!fp) {
        fprintf(stderr, "%s[!] Cannot open %s (permission denied or PID invalid)%s\n",
                C_RED, path, C_RESET);
        return;
    }

    printf("\n%s[ ENVIRONMENT VARIABLES: PID %d ]%s\n", C_CYAN, pid, C_RESET);
    printf("%s─────────────────────────────────────────────────────────────%s\n",
           C_GRAY, C_RESET);

    char buf[65536];
    size_t read_bytes = fread(buf, 1, sizeof(buf) - 1, fp);
    fclose(fp);
    buf[read_bytes] = '\0';

    int count = 0;
    char *ptr = buf;
    while (ptr < buf + read_bytes) {
        size_t len = strlen(ptr);
        if (len > 0) {
            /* Split KEY=VALUE for colorized output */
            char *eq = strchr(ptr, '=');
            if (eq) {
                *eq = '\0';
                printf("  %s%-30s%s = %s%s%s\n",
                       C_YELLOW, ptr, C_RESET,
                       C_WHITE, eq + 1, C_RESET);
                *eq = '=';
            } else {
                printf("  %s%s%s\n", C_WHITE, ptr, C_RESET);
            }
            count++;
        }
        ptr += len + 1;
    }
    printf("%s  [*] Total env vars: %d%s\n", C_GREEN, count, C_RESET);
}

void dump_cmdline(int pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/cmdline", pid);
    FILE *fp = fopen(path, "rb");
    if (!fp) return;

    printf("\n%s[ COMMAND LINE: PID %d ]%s\n", C_CYAN, pid, C_RESET);
    char buf[4096];
    size_t n = fread(buf, 1, sizeof(buf) - 1, fp);
    fclose(fp);
    buf[n] = '\0';

    printf("  %s", C_WHITE);
    for (size_t i = 0; i < n; i++) {
        printf("%c", buf[i] == '\0' ? ' ' : buf[i]);
    }
    printf("%s\n", C_RESET);
}

void dump_fd(int pid) {
    char fd_path[64];
    snprintf(fd_path, sizeof(fd_path), "/proc/%d/fd", pid);

    DIR *dir = opendir(fd_path);
    if (!dir) {
        fprintf(stderr, "%s[!] Cannot open %s (no permission)%s\n",
                C_RED, fd_path, C_RESET);
        return;
    }

    printf("\n%s[ OPEN FILE DESCRIPTORS: PID %d ]%s\n", C_CYAN, pid, C_RESET);
    printf("%s─────────────────────────────────────────────────────────────%s\n",
           C_GRAY, C_RESET);

    struct dirent *e;
    int count = 0;
    while ((e = readdir(dir)) != NULL) {
        if (e->d_name[0] == '.') continue;

        char link_path[128], target[256];
        snprintf(link_path, sizeof(link_path), "%s/%s", fd_path, e->d_name);

        ssize_t len = readlink(link_path, target, sizeof(target) - 1);
        if (len > 0) {
            target[len] = '\0';
            const char *color = C_WHITE;
            if (strncmp(target, "socket:", 7) == 0)   color = C_CYAN;
            else if (strncmp(target, "pipe:", 5) == 0) color = C_YELLOW;
            else if (strncmp(target, "/dev/", 5) == 0) color = C_GREEN;

            printf("  fd%s%-4s%s → %s%s%s\n",
                   C_GRAY, e->d_name, C_RESET,
                   color, target, C_RESET);
            count++;
        }
    }
    closedir(dir);
    printf("%s  [*] Open file descriptors: %d%s\n", C_GREEN, count, C_RESET);
}

void dump_maps(int pid) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/maps", pid);
    FILE *fp = fopen(path, "r");
    if (!fp) return;

    printf("\n%s[ VIRTUAL MEMORY SEGMENTS: PID %d ]%s\n", C_CYAN, pid, C_RESET);
    printf("%s%-25s %-5s %-8s %s%s\n",
           C_YELLOW, "ADDRESS RANGE", "PERM", "OFFSET", "PATH/REGION", C_RESET);
    printf("%s─────────────────────────────────────────────────────────────%s\n",
           C_GRAY, C_RESET);

    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        char addr[32], perm[8], rest[200];
        if (sscanf(line, "%31s %7s %*s %*s %*s %199[^\n]", addr, perm, rest) >= 2) {
            const char *col = C_WHITE;
            if (strchr(perm, 'x')) col = C_RED;
            else if (strchr(perm, 'w')) col = C_YELLOW;
            printf("  %s%-25s%s %s%-5s%s %s%s%s\n",
                   C_GRAY, addr, C_RESET, col, perm, C_RESET, C_WHITE, rest, C_RESET);
        }
    }
    fclose(fp);
}

int main(int argc, char **argv) {
    printf("\n%s%s  ASTERIX OS ─── PROCESS ENVIRONMENT & DEEP FD DUMPER%s\n\n",
           C_BOLD, C_CYAN, C_RESET);

    if (argc < 2) {
        printf("%sUsage:%s\n", C_CYAN, C_RESET);
        printf("  asterix-env-dump <PID>               » Full dump (env + fd + maps)\n");
        printf("  asterix-env-dump <PID> --env-only    » Environment variables only\n");
        printf("  asterix-env-dump <PID> --fd-only     » File descriptors only\n");
        printf("  asterix-env-dump <PID> --maps        » Virtual memory map only\n");
        return 1;
    }

    int pid = atoi(argv[1]);
    if (pid <= 0) {
        fprintf(stderr, "%s[!] Invalid PID: %s%s\n", C_RED, argv[1], C_RESET);
        return 1;
    }

    const char *mode = (argc >= 3) ? argv[2] : "--all";

    dump_cmdline(pid);

    if (strcmp(mode, "--env-only") == 0) { dump_env(pid); }
    else if (strcmp(mode, "--fd-only") == 0) { dump_fd(pid); }
    else if (strcmp(mode, "--maps") == 0) { dump_maps(pid); }
    else {
        dump_env(pid);
        dump_fd(pid);
        dump_maps(pid);
    }

    printf("\n%s[✔] Dump complete.%s\n\n", C_GREEN, C_RESET);
    return 0;
}
