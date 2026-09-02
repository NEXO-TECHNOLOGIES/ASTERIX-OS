/*
 * =====================================================================
 * ASTERIX OS - Native C Process & Syscall Tracer (proc_tracer)
 * Real-time /proc filesystem process lifecycle monitor
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dirent.h>
#include <ctype.h>
#include <sys/stat.h>
#include <signal.h>
#include <time.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_MAGENTA "\033[38;5;201m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_GRAY    "\033[38;5;240m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

#define MAX_PROCS 1024

typedef struct {
    int pid;
    char name[64];
    char state;
    long vm_rss;
    long utime;
    long stime;
    char user[64];
} ProcessInfo;

static volatile int running = 1;

void handle_signal(int sig) {
    (void)sig;
    running = 0;
}

int read_proc_stat(int pid, ProcessInfo *info) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/stat", pid);

    FILE *fp = fopen(path, "r");
    if (!fp) return 0;

    char comm[64];
    char state;
    long utime, stime;

    fscanf(fp, "%d (%63[^)]) %c %*d %*d %*d %*d %*d %*u %*u %*u %*u %*u %ld %ld",
           &pid, comm, &state, &utime, &stime);
    fclose(fp);

    info->pid = pid;
    strncpy(info->name, comm, sizeof(info->name) - 1);
    info->state = state;
    info->utime = utime;
    info->stime = stime;

    // Read memory from /proc/pid/status
    snprintf(path, sizeof(path), "/proc/%d/status", pid);
    fp = fopen(path, "r");
    if (fp) {
        char line[256];
        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "VmRSS:", 6) == 0) {
                sscanf(line + 6, "%ld", &info->vm_rss);
                break;
            }
        }
        fclose(fp);
    }

    return 1;
}

void print_header() {
    printf("\033[H\033[J");
    printf("%s%s", C_CYAN, C_BOLD);
    printf("┌──────────────────────────────────────────────────────────────────────────┐\n");
    printf("│         ASTERIX OS ⚡ PROCESS & KERNEL TELEMETRY TRACER                 │\n");
    printf("│  Press Ctrl+C to exit   |   Refresh Rate: 1s   |   /proc Filesystem     │\n");
    printf("└──────────────────────────────────────────────────────────────────────────┘\n");
    printf("%s", C_RESET);

    time_t t = time(NULL);
    struct tm *tm_info = localtime(&t);
    char tbuf[32];
    strftime(tbuf, sizeof(tbuf), "%Y-%m-%d %H:%M:%S", tm_info);
    printf("%s  Timestamp: %s%s\n\n", C_GRAY, tbuf, C_RESET);

    printf("  %s%-8s  %-22s  %-6s  %-10s  %s%s\n",
           C_YELLOW, "PID", "PROCESS NAME", "STATE", "RAM (kB)", "CPU TIME", C_RESET);
    printf("  %s──────────────────────────────────────────────────────────────────%s\n",
           C_GRAY, C_RESET);
}

void print_process(const ProcessInfo *p) {
    const char *state_label;
    const char *state_color;

    switch (p->state) {
        case 'R': state_label = "RUNNING"; state_color = C_GREEN; break;
        case 'S': state_label = "SLEEP";   state_color = C_CYAN;  break;
        case 'D': state_label = "WAIT";    state_color = C_YELLOW; break;
        case 'Z': state_label = "ZOMBIE";  state_color = C_RED;   break;
        case 'T': state_label = "STOPPED"; state_color = C_MAGENTA; break;
        default:  state_label = "IDLE";    state_color = C_GRAY;  break;
    }

    printf("  %s%-8d%s  %-22s  %s%-6s%s  %-10ld  %ld\n",
           C_WHITE, p->pid, C_RESET,
           p->name,
           state_color, state_label, C_RESET,
           p->vm_rss,
           p->utime + p->stime);
}

int cmp_by_ram(const void *a, const void *b) {
    const ProcessInfo *pa = (const ProcessInfo *)a;
    const ProcessInfo *pb = (const ProcessInfo *)b;
    return (int)(pb->vm_rss - pa->vm_rss);
}

int main(int argc, char **argv) {
    int single_pid = 0;
    if (argc >= 2) single_pid = atoi(argv[1]);

    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    while (running) {
        if (single_pid > 0) {
            print_header();
            ProcessInfo info = {0};
            if (read_proc_stat(single_pid, &info)) {
                print_process(&info);
            } else {
                printf("%s[!] PID %d not found or exited.%s\n", C_RED, single_pid, C_RESET);
            }
        } else {
            ProcessInfo procs[MAX_PROCS];
            int count = 0;
            DIR *dir = opendir("/proc");
            if (!dir) break;

            struct dirent *entry;
            while ((entry = readdir(dir)) != NULL && count < MAX_PROCS) {
                int is_pid = 1;
                for (int i = 0; entry->d_name[i]; i++) {
                    if (!isdigit((unsigned char)entry->d_name[i])) { is_pid = 0; break; }
                }
                if (!is_pid) continue;

                int pid = atoi(entry->d_name);
                memset(&procs[count], 0, sizeof(ProcessInfo));
                if (read_proc_stat(pid, &procs[count])) count++;
            }
            closedir(dir);

            qsort(procs, count, sizeof(ProcessInfo), cmp_by_ram);
            print_header();

            int display = (count > 30) ? 30 : count;
            for (int i = 0; i < display; i++) {
                print_process(&procs[i]);
            }
            printf("\n%s  [*] Showing top %d of %d processes by RAM usage. PID-filter: %s --pid <PID>%s\n",
                   C_GRAY, display, count, argv[0], C_RESET);
        }

        sleep(1);
    }

    printf("\n%s[✔] ASTERIX Process Tracer exited.%s\n", C_GREEN, C_RESET);
    return 0;
}
