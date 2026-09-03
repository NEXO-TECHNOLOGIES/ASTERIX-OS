/*
 * =====================================================================
 * ASTERIX OS :: DEEP KERNEL :: Rootkit & Stealth Process Detector
 * Cross-references /proc/PID vs kernel task list via /proc/sched_debug
 * Language: C (GNU C11)
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <ctype.h>
#include <unistd.h>
#include <sys/stat.h>

#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"
#define C_GRAY    "\033[38;5;240m"
#define C_BOLD    "\033[1m"
#define C_RESET   "\033[0m"

#define MAX_PIDS 8192

typedef struct {
    int  pid;
    char name[64];
    char state;
    int  visible_proc;
    int  visible_sched;
    int  hidden;
} ProcessEntry;

/* Collect all PIDs from /proc filesystem */
int collect_proc_pids(int *pids, int max) {
    DIR *dir = opendir("/proc");
    if (!dir) return 0;

    struct dirent *e;
    int count = 0;
    while ((e = readdir(dir)) != NULL && count < max) {
        int is_pid = 1;
        for (int i = 0; e->d_name[i]; i++) {
            if (!isdigit((unsigned char)e->d_name[i])) { is_pid = 0; break; }
        }
        if (is_pid) pids[count++] = atoi(e->d_name);
    }
    closedir(dir);
    return count;
}

/* Collect PIDs visible in /proc/sched_debug (kernel task list) */
int collect_sched_pids(int *pids, int max) {
    FILE *fp = fopen("/proc/sched_debug", "r");
    if (!fp) return 0;

    int count = 0;
    char line[512];
    while (fgets(line, sizeof(line), fp) && count < max) {
        /* Lines containing task entries look like: "task_name  pid  ..." */
        char name[64];
        int pid;
        if (sscanf(line, " %63s %d", name, &pid) == 2 && pid > 0) {
            /* Validate pid looks reasonable (skip header numbers) */
            if (pid < 1000000) {
                pids[count++] = pid;
            }
        }
    }
    fclose(fp);
    return count;
}

int pid_in_list(int pid, int *list, int count) {
    for (int i = 0; i < count; i++)
        if (list[i] == pid) return 1;
    return 0;
}

void get_proc_name(int pid, char *name, size_t len) {
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/comm", pid);
    FILE *fp = fopen(path, "r");
    if (fp) {
        if (fgets(name, (int)len, fp)) {
            name[strcspn(name, "\n")] = 0;
        }
        fclose(fp);
    } else {
        snprintf(name, len, "<unknown>");
    }
}

void check_hidden_modules() {
    printf("\n%s[ MODULE INTEGRITY CHECK ]%s\n", C_YELLOW, C_RESET);

    FILE *fp = fopen("/proc/modules", "r");
    if (!fp) {
        printf("  %s[!] Cannot read /proc/modules%s\n", C_RED, C_RESET);
        return;
    }

    char line[256];
    int count = 0;
    while (fgets(line, sizeof(line), fp)) {
        char mod_name[64];
        if (sscanf(line, "%63s", mod_name) == 1) {
            printf("  • %s%-30s%s", C_WHITE, mod_name, C_RESET);
            /* Flag suspicious module names */
            if (strstr(mod_name, "hide") || strstr(mod_name, "root") ||
                strstr(mod_name, "ghost") || strstr(mod_name, "invis")) {
                printf("  %s⚠ SUSPICIOUS NAME%s", C_RED, C_RESET);
            }
            printf("\n");
            count++;
        }
    }
    fclose(fp);
    printf("  %s[*] Total loaded kernel modules: %d%s\n", C_CYAN, count, C_RESET);
}

void check_etc_passwd_integrity() {
    printf("\n%s[ /etc/passwd INTEGRITY CHECK ]%s\n", C_YELLOW, C_RESET);

    FILE *fp = fopen("/etc/passwd", "r");
    if (!fp) { printf("  [!] Cannot read /etc/passwd\n"); return; }

    char line[256];
    while (fgets(line, sizeof(line), fp)) {
        char user[64];
        int uid;
        if (sscanf(line, "%63[^:]:%*[^:]:%d", user, &uid) == 2) {
            if (uid == 0 && strcmp(user, "root") != 0) {
                printf("  %s⚠ UID-0 BACKDOOR ACCOUNT: %s%s\n", C_RED, user, C_RESET);
            }
        }
    }
    fclose(fp);
    printf("  %s[✔] /etc/passwd scan complete%s\n", C_GREEN, C_RESET);
}

int main() {
    printf("%s%s\n", C_BOLD, C_CYAN);
    printf("  ██████╗  ██████╗  ██████╗ ████████╗██╗  ██╗██╗████████╗\n");
    printf("  ██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝██║ ██╔╝██║╚══██╔══╝\n");
    printf("  ██████╔╝██║   ██║██║   ██║   ██║   █████╔╝ ██║   ██║   \n");
    printf("  ██╔══██╗██║   ██║██║   ██║   ██║   ██╔═██╗ ██║   ██║   \n");
    printf("  ██║  ██║╚██████╔╝╚██████╔╝   ██║   ██║  ██╗██║   ██║   \n");
    printf("  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═╝╚═╝   ╚═╝   \n");
    printf("  DEEP KERNEL ROOTKIT & HIDDEN PROCESS DETECTOR\n%s\n", C_RESET);

    int proc_pids[MAX_PIDS];
    int sched_pids[MAX_PIDS];

    int proc_count  = collect_proc_pids(proc_pids, MAX_PIDS);
    int sched_count = collect_sched_pids(sched_pids, MAX_PIDS);

    printf("%s[ /proc VISIBILITY vs KERNEL TASK LIST ]%s\n", C_CYAN, C_RESET);
    printf("  • /proc PIDs found:  %s%d%s\n", C_GREEN, proc_count, C_RESET);
    printf("  • Scheduler PIDs found: %s%d%s\n\n", C_YELLOW, sched_count, C_RESET);

    int hidden_count = 0;
    if (sched_count > 0) {
        printf("%s[ HIDDEN PROCESS ANALYSIS ]%s\n", C_RED, C_RESET);
        for (int i = 0; i < sched_count; i++) {
            if (!pid_in_list(sched_pids[i], proc_pids, proc_count)) {
                char name[64] = "<kernel-hidden>";
                printf("  %s⚠ HIDDEN PID: %-7d  NAME: %s%s\n",
                       C_RED, sched_pids[i], name, C_RESET);
                hidden_count++;
            }
        }
        if (hidden_count == 0)
            printf("  %s[✔] No hidden processes detected via scheduler comparison%s\n",
                   C_GREEN, C_RESET);
    } else {
        printf("  %s[!] /proc/sched_debug unavailable — kernel comparison skipped%s\n",
               C_YELLOW, C_RESET);
    }

    check_hidden_modules();
    check_etc_passwd_integrity();

    printf("\n%s[✔] Rootkit detection scan complete.%s\n\n", C_GREEN, C_RESET);
    return 0;
}
