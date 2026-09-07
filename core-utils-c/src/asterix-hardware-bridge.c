/*
 * =====================================================================
 * ASTERIX OS - Hardware Telemetry C Bridge (Tier 2 Converter)
 * Interfaces with x86-64 assembly / CPUID registers and system kernel,
 * converting raw hardware data into structured C structs for Python FFI.
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#ifdef _WIN32
#include <windows.h>
#include <intrin.h>
#define EXPORT_API __declspec(dllexport)
#else
#include <unistd.h>
#include <cpuid.h>
#include <sys/sysinfo.h>
#define EXPORT_API __attribute__((visibility("default")))
#endif

#pragma pack(push, 8)
typedef struct {
    char cpu_vendor[16];
    char cpu_brand[64];
    uint64_t tsc_cycles;
    uint32_t cpu_cores;
    uint32_t cpu_logical;
    uint64_t ram_total_mb;
    uint64_t ram_free_mb;
    uint32_t ram_load_pct;
    uint32_t status_code;
} HardwareTelemetry;
#pragma pack(pop)

static inline uint64_t native_rdtsc(void) {
#ifdef _WIN32
    return __rdtsc();
#else
    uint32_t lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
#endif
}

static void query_cpu_details(char *vendor, char *brand) {
    int cpu_info[4] = {0};

    // 1. Query CPU Vendor String
#ifdef _WIN32
    __cpuid(cpu_info, 0);
    memcpy(vendor, &cpu_info[1], 4);       // EBX
    memcpy(vendor + 4, &cpu_info[3], 4);   // EDX
    memcpy(vendor + 8, &cpu_info[2], 4);   // ECX
    vendor[12] = '\0';
#else
    __cpuid(0, cpu_info[0], cpu_info[1], cpu_info[2], cpu_info[3]);
    memcpy(vendor, &cpu_info[1], 4);
    memcpy(vendor + 4, &cpu_info[3], 4);
    memcpy(vendor + 8, &cpu_info[2], 4);
    vendor[12] = '\0';
#endif

    // 2. Query Extended CPU Brand String
#ifdef _WIN32
    __cpuid(cpu_info, 0x80000000);
    unsigned int max_ext = (unsigned int)cpu_info[0];
    if (max_ext >= 0x80000004) {
        __cpuid((int*)(brand), 0x80000002);
        __cpuid((int*)(brand + 16), 0x80000003);
        __cpuid((int*)(brand + 32), 0x80000004);
        brand[48] = '\0';
    } else {
        strncpy(brand, vendor, 48);
    }
#else
    unsigned int max_ext = 0;
    __cpuid(0x80000000, max_ext, cpu_info[1], cpu_info[2], cpu_info[3]);
    if (max_ext >= 0x80000004) {
        __cpuid(0x80000002, *(int*)(brand), *(int*)(brand+4), *(int*)(brand+8), *(int*)(brand+12));
        __cpuid(0x80000003, *(int*)(brand+16), *(int*)(brand+20), *(int*)(brand+24), *(int*)(brand+28));
        __cpuid(0x80000004, *(int*)(brand+32), *(int*)(brand+36), *(int*)(brand+40), *(int*)(brand+44));
        brand[48] = '\0';
    } else {
        strncpy(brand, vendor, 48);
    }
#endif

    // Clean leading whitespace from brand if any
    char *p = brand;
    while (*p == ' ') p++;
    if (p != brand) {
        memmove(brand, p, strlen(p) + 1);
    }
}

EXPORT_API int get_hardware_telemetry(HardwareTelemetry *out) {
    if (!out) return -1;
    memset(out, 0, sizeof(HardwareTelemetry));

    query_cpu_details(out->cpu_vendor, out->cpu_brand);
    out->tsc_cycles = native_rdtsc();

#ifdef _WIN32
    SYSTEM_INFO sys_info;
    GetSystemInfo(&sys_info);
    out->cpu_logical = sys_info.dwNumberOfProcessors;
    out->cpu_cores = sys_info.dwNumberOfProcessors / 2;
    if (out->cpu_cores == 0) out->cpu_cores = 1;

    MEMORYSTATUSEX mem_stat;
    mem_stat.dwLength = sizeof(MEMORYSTATUSEX);
    if (GlobalMemoryStatusEx(&mem_stat)) {
        out->ram_total_mb = (uint64_t)(mem_stat.ullTotalPhys / (1024 * 1024));
        out->ram_free_mb = (uint64_t)(mem_stat.ullAvailPhys / (1024 * 1024));
        out->ram_load_pct = (uint32_t)mem_stat.dwMemoryLoad;
    }
#else
    out->cpu_logical = sysconf(_SC_NPROCESSORS_ONLN);
    out->cpu_cores = out->cpu_logical;

    struct sysinfo si;
    if (sysinfo(&si) == 0) {
        out->ram_total_mb = (uint64_t)((si.totalram * si.mem_unit) / (1024 * 1024));
        out->ram_free_mb = (uint64_t)((si.freeram * si.mem_unit) / (1024 * 1024));
        if (out->ram_total_mb > 0) {
            out->ram_load_pct = (uint32_t)(((out->ram_total_mb - out->ram_free_mb) * 100) / out->ram_total_mb);
        }
    }
#endif

    out->status_code = 200;
    return 0;
}
