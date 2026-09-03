/*
 * =====================================================================
 * ASTERIX OS :: DEEP KERNEL :: Syscall & I/O Monitor
 * Reads /proc/PID/syscall and /proc/ioports and /proc/iomem
 * Language: C (GNU C11)
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <ctype.h>
#include <signal.h>
#include <time.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_GRAY    "\033[38;5;240m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

/* x86-64 syscall name table (first 60) */
static const char *SYSCALL_NAMES[] = {
    "read","write","open","close","stat","fstat","lstat","poll","lseek","mmap",
    "mprotect","munmap","brk","rt_sigaction","rt_sigprocmask","rt_sigreturn",
    "ioctl","pread64","pwrite64","readv","writev","access","pipe","select","sched_yield",
    "mremap","msync","mincore","madvise","shmget","shmat","shmctl","dup","dup2",
    "pause","nanosleep","getitimer","alarm","setitimer","getpid","sendfile","socket",
    "connect","accept","sendto","recvfrom","sendmsg","recvmsg","shutdown","bind",
    "listen","getsockname","getpeername","socketpair","setsockopt","getsockopt",
    "clone","fork","vfork","execve"
};
#define SYSCALL_COUNT (sizeof(SYSCALL_NAMES)/sizeof(SYSCALL_NAMES[0]))

static volatile int running = 1;
void handle_sig(int s) { (void)s; running = 0; }

void print_banner() {
    printf("%s%s", C_CYAN, C_BOLD);
    printf("╔═══════════════════════════════════════════════════════════╗\n");
    printf("║    ASTERIX OS ⚡ SYSCALL & I/O PORT MONITOR               ║\n");
    printf("╚═══════════════════════════════════════════════════════════╝\n%s\n", C_RESET);
}

void show_ioports() {
    FILE *fp = fopen("/proc/ioports", "r");
    if (!fp) {
        printf("%s[!] Cannot read /proc/ioports (requires root)%s\n", C_YELLOW, C_RESET);
        return;
    }
    printf("%s[ KERNEL I/O PORT MAP (/proc/ioports) ]%s\n", C_CYAN, C_RESET);
    char line[128];
    while (fgets(line, sizeof(line), fp)) {
        /* Highlight DMA, PCI, and legacy ISA ports */
        if (strstr(line, "PCI") || strstr(line, "dma") || strstr(line, "Serial")) {
            printf("  %s%s%s", C_YELLOW, line, C_RESET);
        } else {
            printf("  %s%s%s", C_GRAY, line, C_RESET);
        }
    }
    fclose(fp);
    printf("\n");
}

void show_iomem() {
    FILE *fp = fopen("/proc/iomem", "r");
    if (!fp) {
        printf("%s[!] Cannot read /proc/iomem%s\n", C_YELLOW, C_RESET);
        return;
    }
    printf("%s[ PHYSICAL MEMORY MAP (/proc/iomem) ]%s\n", C_CYAN, C_RESET);
    char line[128];
    int count = 0;
    while (fgets(line, sizeof(line), fp) && count < 30) {
        if (strstr(line, "RAM") || strstr(line, "Kernel") || strstr(line, "BIOS")) {
            printf("  %s%s%s", C_GREEN, line, C_RESET);
        } else if (strstr(line, "PCI") || strstr(line, "Video")) {
            printf("  %s%s%s", C_MAGENTA, line, C_RESET);
        } else {
            printf("  %s%s%s", C_GRAY, line, C_RESET);
        }
        count++;
    }
    fclose(fp);
    printf("\n");
}

void monitor_pid_syscall(int pid, int iterations) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/syscall", pid);

    printf("%s[ LIVE SYSCALL MONITOR: PID %d ]%s\n", C_CYAN, pid, C_RESET);
    printf("  Press Ctrl+C to stop...\n\n");

    long last_syscall = -999;
    for (int i = 0; i < iterations && running; i++) {
        FILE *fp = fopen(path, "r");
        if (!fp) {
            printf("%s[!] PID %d not found or no permission%s\n", C_RED, pid, C_RESET);
            break;
        }

        long syscall_nr;
        unsigned long args[6];
        unsigned long sp, pc;

        int n = fscanf(fp, "%ld %lx %lx %lx %lx %lx %lx %lx %lx",
                       &syscall_nr, &args[0], &args[1], &args[2],
                       &args[3], &args[4], &args[5], &sp, &pc);
        fclose(fp);

        if (n > 0 && syscall_nr != last_syscall && syscall_nr >= 0) {
            last_syscall = syscall_nr;
            const char *name = (syscall_nr < (long)SYSCALL_COUNT)
                               ? SYSCALL_NAMES[syscall_nr] : "unknown";

            time_t t = time(NULL);
            struct tm *tm = localtime(&t);

            printf("  %s[%02d:%02d:%02d]%s  %ssyscall#%-4ld%s  %-18s  "
                   "arg0=%s0x%lx%s  SP=%s0x%lx%s\n",
                   C_GRAY, tm->tm_hour, tm->tm_min, tm->tm_sec, C_RESET,
                   C_YELLOW, syscall_nr, C_RESET,
                   name,
                   C_GREEN, args[0], C_RESET,
                   C_CYAN, sp, C_RESET);
        }

        usleep(50000); /* 50ms poll */
    }
}

int main(int argc, char **argv) {
    print_banner();
    signal(SIGINT, handle_sig);

    if (argc >= 2 && strcmp(argv[1], "--ioports") == 0) {
        show_ioports();
        return 0;
    }
    if (argc >= 2 && strcmp(argv[1], "--iomem") == 0) {
        show_iomem();
        return 0;
    }
    if (argc >= 3 && strcmp(argv[1], "--pid") == 0) {
        int pid = atoi(argv[2]);
        int iters = (argc >= 5 && strcmp(argv[3], "--count") == 0) ? atoi(argv[4]) : 99999;
        monitor_pid_syscall(pid, iters);
        return 0;
    }

    /* Default: show everything */
    show_ioports();
    show_iomem();

    printf("%sUsage:%s\n", C_CYAN, C_RESET);
    printf("  asterix-syscall-mon --ioports          » Show I/O port map\n");
    printf("  asterix-syscall-mon --iomem            » Show physical memory map\n");
    printf("  asterix-syscall-mon --pid <PID>        » Live syscall monitor\n");
    printf("  asterix-syscall-mon --pid <PID> --count 100\n");
    return 0;
}
