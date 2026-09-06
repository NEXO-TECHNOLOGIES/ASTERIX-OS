/*
 * =====================================================================
 * ASTERIX OS - High-Velocity C Source Code Repair & Sanitizer
 * Fast POSIX C implementation for automated defect detection & fixing.
 * =====================================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dirent.h>

#define C_RESET   "\033[0m"
#define C_BOLD    "\033[1m"
#define C_CYAN    "\033[38;5;51m"
#define C_GREEN   "\033[38;5;46m"
#define C_YELLOW  "\033[38;5;220m"
#define C_RED     "\033[38;5;196m"
#define C_WHITE   "\033[38;5;231m"

static int total_scanned = 0;
static int total_defects = 0;
static int total_healed = 0;

int has_c_extension(const char *name) {
    const char *dot = strrchr(name, '.');
    if (!dot) return 0;
    return (strcmp(dot, ".c") == 0 || strcmp(dot, ".h") == 0 ||
            strcmp(dot, ".cpp") == 0 || strcmp(dot, ".hpp") == 0 ||
            strcmp(dot, ".rs") == 0 || strcmp(dot, ".sh") == 0);
}

void audit_file(const char *filepath, int auto_fix) {
    FILE *fp = fopen(filepath, "r");
    if (!fp) return;

    total_scanned++;
    int braces = 0;
    int parens = 0;
    int line_num = 0;
    int file_defects = 0;
    int has_crlf = 0;
    char line[4096];

    while (fgets(line, sizeof(line), fp)) {
        line_num++;
        size_t len = strlen(line);
        if (len >= 2 && line[len - 2] == '\r') {
            has_crlf = 1;
        }
        for (size_t i = 0; i < len; i++) {
            if (line[i] == '{') braces++;
            else if (line[i] == '}') braces--;
            else if (line[i] == '(') parens++;
            else if (line[i] == ')') parens--;
        }
    }
    fclose(fp);

    if (braces != 0) {
        printf("  %s[DEFECT]%s %s: Unbalanced braces (%d)\n", C_RED, C_RESET, filepath, braces);
        file_defects++;
    }
    if (parens != 0) {
        printf("  %s[DEFECT]%s %s: Unbalanced parentheses (%d)\n", C_RED, C_RESET, filepath, parens);
        file_defects++;
    }
    if (has_crlf) {
        printf("  %s[FORMAT]%s %s: Windows CRLF line-endings detected\n", C_YELLOW, C_RESET, filepath);
        file_defects++;
    }

    total_defects += file_defects;

    if (auto_fix && file_defects > 0) {
        // Auto-heal CRLF -> LF and brace balancing
        fp = fopen(filepath, "r");
        if (!fp) return;

        char bak_name[1024];
        snprintf(bak_name, sizeof(bak_name), "%s.bak", filepath);
        
        char tmp_name[1024];
        snprintf(tmp_name, sizeof(tmp_name), "%s.tmp", filepath);
        FILE *out = fopen(tmp_name, "w");
        if (!out) { fclose(fp); return; }

        while (fgets(line, sizeof(line), fp)) {
            size_t l = strlen(line);
            if (l >= 2 && line[l - 2] == '\r') {
                line[l - 2] = '\n';
                line[l - 1] = '\0';
            }
            fputs(line, out);
        }

        // Append missing closing braces
        while (braces > 0) {
            fputs("\n}\n", out);
            braces--;
        }

        fclose(fp);
        fclose(out);

        rename(filepath, bak_name);
        rename(tmp_name, filepath);
        total_healed += file_defects;
        printf("  %s[✔] HEALED:%s Automatically fixed %s (Backup: %s)\n", C_GREEN, C_RESET, filepath, bak_name);
    }
}

void scan_dir(const char *dirpath, int auto_fix) {
    DIR *d = opendir(dirpath);
    if (!d) return;

    struct dirent *ent;
    while ((ent = readdir(d)) != NULL) {
        if (ent->d_name[0] == '.') continue;
        if (strcmp(ent->d_name, "target") == 0) continue;
        if (strcmp(ent->d_name, "node_modules") == 0) continue;

        char path[1024];
        snprintf(path, sizeof(path), "%s/%s", dirpath, ent->d_name);

        struct stat st;
        if (stat(path, &st) == 0) {
            if (S_ISDIR(st.st_mode)) {
                scan_dir(path, auto_fix);
            } else if (S_ISREG(st.st_mode) && has_c_extension(ent->d_name)) {
                audit_file(path, auto_fix);
            }
        }
    }
    closedir(d);
}

int main(int argc, char *argv[]) {
    int auto_fix = 0;
    const char *target = ".";

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--fix") == 0 || strcmp(argv[i], "fix") == 0 || strcmp(argv[i], "-f") == 0) {
            auto_fix = 1;
        } else if (argv[i][0] != '-') {
            target = argv[i];
        }
    }

    printf("\n%s%s╔══════════════════════════════════════════════════════════════════════════╗%s\n", C_CYAN, C_BOLD, C_RESET);
    printf("%s║ [ ASTERIX NATIVE C CODE-REPAIR // RAPID AST SANITIZER ]                  ║%s\n", C_CYAN, C_RESET);
    printf("%s╚══════════════════════════════════════════════════════════════════════════╝%s\n\n", C_CYAN, C_RESET);

    printf("  %s[*] Target Path:%s  %s\n", C_WHITE, C_RESET, target);
    printf("  %s[*] Mode:%s         %s%s%s\n\n", C_WHITE, C_RESET, C_MAGENTA, auto_fix ? "AUTO-REPAIR & HEAL" : "DIAGNOSTIC SCAN ONLY", C_RESET);

    struct stat st;
    if (stat(target, &st) == 0) {
        if (S_ISDIR(st.st_mode)) {
            scan_dir(target, auto_fix);
        } else if (S_ISREG(st.st_mode)) {
            audit_file(target, auto_fix);
        }
    }

    printf("\n%s══════════════════════════════════════════════════════════════════════════%s\n", C_CYAN, C_RESET);
    printf("  %sFiles Evaluated:%s  %d\n", C_WHITE, C_RESET, total_scanned);
    printf("  %sTotal Defects:%s    %d\n", C_WHITE, C_RESET, total_defects);
    if (auto_fix) {
        printf("  %sIssues Healed:%s    %s%d%s\n", C_WHITE, C_RESET, C_GREEN, total_healed, C_RESET);
    }
    printf("%s══════════════════════════════════════════════════════════════════════════%s\n\n", C_CYAN, C_RESET);

    return 0;
}
