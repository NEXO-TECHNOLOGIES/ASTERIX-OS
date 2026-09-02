/*
 * =====================================================================
 * ASTERIX OS - Native C Hardware & Kernel Telemetry Probe
 * Probes CPU registers, memory layout, thermal sensors, and system load
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/utsname.h>
#include <sys/sysinfo.h>
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

void print_banner() {
    printf("%s%s", C_CYAN, C_BOLD);
    printf("    ___   _____ ______ ______ ____     ______  _______ ____  \n");
    printf("   /   | / ___//_  __// ____// __ \\   / ___/ \\/ / ___// __ \\ \n");
    printf("  / /| | \\__ \\  / /  / __/  / /_/ /   \\__ \\ \\  /\\__ \\/ / / / \n");
    printf(" / ___ |___/ / / /  / /___ / _, _/   ___/ / / /___/ / /_/ /  \n");
    printf("/_/  |_/____/ /_/  /_____//_/ |_|   /____/ /_//____/\\____/   \n");
    printf("       LOW-LEVEL HARDWARE & KERNEL TELEMETRY PROBE\n%s\n", C_RESET);
}

void print_cpu_info() {
    FILE *fp = fopen("/proc/cpuinfo", "r");
    char line[256];
    char model[128] = "Unknown CPU";
    int cores = 0;
    float mhz = 0.0;

    if (fp) {
        while (fgets(line, sizeof(line), fp)) {
            if (strncmp(line, "model name", 10) == 0) {
                char *colon = strchr(line, ':');
                if (colon) {
                    strncpy(model, colon + 2, sizeof(model) - 1);
                    model[strcspn(model, "\n")] = 0;
                }
            } else if (strncmp(line, "cpu cores", 9) == 0) {
                sscanf(line, "cpu cores : %d", &cores);
            } else if (strncmp(line, "cpu MHz", 7) == 0) {
                sscanf(line, "cpu MHz : %f", &mhz);
            }
        }
        fclose(fp);
    }

    if (cores == 0) {
        cores = sysconf(_SC_NPROCESSORS_ONLN);
    }

    printf("%s[ CPU ARCHITECTURE ]%s\n", C_CYAN, C_RESET);
    printf("  • Model:        %s%s%s\n", C_WHITE, model, C_RESET);
    printf("  • Active Cores: %s%d Cores%s\n", C_GREEN, cores, C_RESET);
    if (mhz > 0.0) {
        printf("  • Core Clock:   %s%.2f MHz%s\n", C_YELLOW, mhz, C_RESET);
    }
    printf("\n");
}

void print_memory_info() {
    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        unsigned long long total_ram = (unsigned long long)si.totalram * si.mem_unit / (1024 * 1024);
        unsigned long long free_ram = (unsigned long long)si.freeram * si.mem_unit / (1024 * 1024);
        unsigned long long used_ram = total_ram - free_ram;
        unsigned long long total_swap = (unsigned long long)si.totalswap * si.mem_unit / (1024 * 1024);
        unsigned long long free_swap = (unsigned long long)si.freeswap * si.mem_unit / (1024 * 1024);

        printf("%s[ MEMORY & SWAP ALLOCATION ]%s\n", C_GREEN, C_RESET);
        printf("  • Physical RAM: %s%llu MB / %llu MB%s (Used: %llu MB)\n", 
               C_WHITE, used_ram, total_ram, C_RESET, used_ram);
        printf("  • Swap Space:   %s%llu MB / %llu MB%s\n", 
               C_WHITE, total_swap - free_swap, total_swap, C_RESET);
        printf("  • Process Count:%s %d Active Tasks%s\n\n", C_YELLOW, si.procs, C_RESET);
    }
}

void print_os_info() {
    struct utsname u;
    if (uname(&u) == 0) {
        printf("%s[ KERNEL & SYSTEM IDENTITY ]%s\n", C_MAGENTA, C_RESET);
        printf("  • Node Name:    %s%s%s\n", C_WHITE, u.nodename, C_RESET);
        printf("  • Kernel OS:    %s%s%s\n", C_CYAN, u.sysname, C_RESET);
        printf("  • Release:      %s%s%s\n", C_GREEN, u.release, C_RESET);
        printf("  • Architecture: %s%s%s\n\n", C_YELLOW, u.machine, C_RESET);
    }
}

void print_thermal_info() {
    FILE *fp = fopen("/sys/class/thermal/thermal_zone0/temp", "r");
    if (fp) {
        int temp_raw = 0;
        if (fscanf(fp, "%d", &temp_raw) == 1) {
            float temp_c = temp_raw / 1000.0f;
            printf("%s[ THERMAL TELEMETRY ]%s\n", C_YELLOW, C_RESET);
            printf("  • Thermal Zone 0: %s%.1f °C%s\n\n", 
                   (temp_c > 75.0 ? C_RED : C_GREEN), temp_c, C_RESET);
        }
        fclose(fp);
    }
}

int main() {
    print_banner();
    print_os_info();
    print_cpu_info();
    print_memory_info();
    print_thermal_info();
    return 0;
}
