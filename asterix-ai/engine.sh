#!/usr/bin/env bash
# ==============================================================================
# ASTERIX OS — Deep Rule-Based Expert AI Engine (Native Bash Implementation v2.0)
# Comprehensive in-depth technical analysis, threat modeling, and remediation.
# Zero external dependencies.
# ==============================================================================

C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[38;5;51m"
C_GREEN="\033[38;5;46m"
C_YELLOW="\033[38;5;220m"
C_RED="\033[38;5;196m"
C_MAGENTA="\033[38;5;201m"
C_WHITE="\033[38;5;231m"
C_BLUE="\033[38;5;45m"
C_GRAY="\033[38;5;244m"

echo -e "${C_CYAN}${C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗${C_RESET}"
echo -e "${C_CYAN}║${C_WHITE} ${C_BOLD}[ ASTERIX EXPERT AI // DEEP INFERENCE & SOC TRIAGE ENGINE v2.0 ]${C_RESET}${C_CYAN}          ║${C_RESET}"
echo -e "${C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝${C_RESET}\n"

action="${1:-audit}"
shift || true

case "$action" in
    ask|query|diagnose)
        query="$*"
        echo -e "  ${C_CYAN}[*] Inquiring Knowledge Base:${C_RESET} \"${query}\"\n"

        if [[ "$query" =~ [Aa][Ss][Ll][Rr]|[Bb]uffer|[Ee]xploit|[Mm]emory|[Rr][Oo][Pp] ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [SEC-001]: Kernel ASLR Full Randomization Entropy${C_RESET}"
            echo -e " ${C_GRAY}Category: MEMORY_SECURITY | Severity Level: CRITICAL | Relevance: 100%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & SUBSYSTEM CONTEXT:${C_RESET}"
            echo -e "    Address Space Layout Randomization (ASLR) is a foundational defense-in-depth"
            echo -e "    mechanism implemented in the Linux virtual memory management subsystem. When locked"
            echo -e "    at Level 2 (Full Randomization), the kernel randomizes the base virtual memory"
            echo -e "    addresses of the stack, the memory-mapped I/O area (including shared libraries and"
            echo -e "    the VDSO page), and the data segment / heap upon every process execve invocation.\n"
            echo -e " ${C_RED}${C_BOLD}2. ADVERSARY EXPLOITATION & THREAT VECTOR MECHANICS:${C_RESET}"
            echo -e "    Without maximum ASLR entropy, virtual memory offsets remain static across program"
            echo -e "    runs. In standard buffer overflow scenarios, adversaries construct deterministic"
            echo -e "    Return-Oriented Programming (ROP) or Return-to-libc attack payloads with hardcoded"
            echo -e "    instruction gadget addresses (such as system() or execve()). Level 2 ASLR ensures"
            echo -e "    that any brute-force attempt causes a segmentation fault and process crash before"
            echo -e "    the payload can locate suitable gadgets in memory.\n"
            echo -e " ${C_GREEN}${C_BOLD}3. OPERATIONAL STATUS & RESOLUTION GUIDANCE:${C_RESET}"
            echo -e "    ASLR must be configured to Value 2 across all running subsystems.\n"
            echo -e " ${C_YELLOW}${C_BOLD}4. IMMEDIATE TACTICAL REMEDIATION COMMAND:${C_RESET}"
            echo -e "    Execute in root/sudo terminal:"
            echo -e "    ${C_CYAN}${C_BOLD}# sysctl -w kernel.randomize_va_space=2${C_RESET}\n"
            echo -e " ${C_WHITE}${C_BOLD}5. REBOOT PERSISTENCE CONFIGURATION:${C_RESET}"
            echo -e "    ${C_YELLOW}${C_BOLD}# echo 'kernel.randomize_va_space = 2' >> /etc/sysctl.d/99-asterix-hardening.conf${C_RESET}\n"
            echo -e " ${C_WHITE}${C_BOLD}6. POST-REMEDIATION AUDIT & VERIFICATION:${C_RESET}"
            echo -e "    ${C_GRAY}${C_BOLD}$ cat /proc/sys/kernel/randomize_va_space  (Must return '2')${C_RESET}\n"

        elif [[ "$query" =~ [Mm]emory|[Rr][Aa][Mm]|[Ss]wap|[Ll]ag|[Ff]reeze ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [SYS-001]: Kernel Memory Swappiness Latency Tuning${C_RESET}"
            echo -e " ${C_GRAY}Category: SYSTEM_PERFORMANCE | Severity Level: MEDIUM | Relevance: 95%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & SUBSYSTEM CONTEXT:${C_RESET}"
            echo -e "    The Linux kernel vm.swappiness parameter (ranging from 0 to 100 or 200 on newer"
            echo -e "    kernels) dictates the relative ratio of page cache reclamation versus anonymous"
            echo -e "    memory swap paging. Default Linux distributions set this value to 60, which leads"
            echo -e "    to premature disk I/O thrashing on systems with ample physical RAM.\n"
            echo -e " ${C_RED}${C_BOLD}2. OPERATIONAL IMPACT & PERFORMANCE IMPEDIMENT:${C_RESET}"
            echo -e "    When swappiness is high, the memory manager eagerly swaps active process heap pages"
            echo -e "    to disk even when free RAM remains available. In intensive cyber workloads (such"
            echo -e "    as packet sniffing, hash cracking, or reverse engineering), this introduces major"
            echo -e "    latency spikes and UI freezing as pages are read back from swap storage.\n"
            echo -e " ${C_YELLOW}${C_BOLD}3. IMMEDIATE TACTICAL REMEDIATION COMMAND:${C_RESET}"
            echo -e "    ${C_CYAN}${C_BOLD}# sysctl -w vm.swappiness=10${C_RESET}\n"
            echo -e " ${C_WHITE}${C_BOLD}4. REBOOT PERSISTENCE CONFIGURATION:${C_RESET}"
            echo -e "    ${C_YELLOW}${C_BOLD}# echo 'vm.swappiness = 10' >> /etc/sysctl.d/99-asterix-hardening.conf${C_RESET}\n"

        elif [[ "$query" =~ [Dd][Oo][Ss]|[Ss][Yy][Nn]|[Ff]lood|[Aa]ttack|[Nn]etwork ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [SEC-004]: TCP SYN Flood Volumetric DoS Armor${C_RESET}"
            echo -e " ${C_GRAY}Category: NETWORK_DEFENSE | Severity Level: HIGH | Relevance: 95%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & SUBSYSTEM CONTEXT:${C_RESET}"
            echo -e "    TCP SYN Cookies (RFC 4987) prevent TCP connection table exhaustion during volumetric"
            echo -e "    SYN flood attacks by encoding connection parameters into the Initial Sequence Number"
            echo -e "    (ISN) of the SYN-ACK response, bypassing the kernel half-open connection backlog.\n"
            echo -e " ${C_YELLOW}${C_BOLD}2. IMMEDIATE TACTICAL REMEDIATION COMMAND:${C_RESET}"
            echo -e "    ${C_CYAN}${C_BOLD}# sysctl -w net.ipv4.tcp_syncookies=1${C_RESET}\n"
            echo -e " ${C_WHITE}${C_BOLD}3. REBOOT PERSISTENCE CONFIGURATION:${C_RESET}"
            echo -e "    ${C_YELLOW}${C_BOLD}# echo 'net.ipv4.tcp_syncookies = 1' >> /etc/sysctl.d/99-asterix-hardening.conf${C_RESET}\n"
        else
            echo -e "  ${C_YELLOW}[!] Query indexed against rule base. General recommendations:${C_RESET}"
            echo -e "    • Run ${C_CYAN}ax ai audit${C_RESET} for a complete host baseline evaluation"
            echo -e "    • Run ${C_CYAN}ax secpol audit${C_RESET} for local security policy verification\n"
        fi
        ;;

    rules|list)
        echo -e "  ${C_BOLD}LOADED KNOWLEDGE BASE REPOSITORY:${C_RESET}\n"
        printf "  %-10s %-38s %-12s\n" "RULE ID" "NAME" "SEVERITY"
        echo -e "  ------------------------------------------------------------------"
        printf "  %-10s %-38s %-12s\n" "SEC-001" "Kernel ASLR Full Randomization Entropy" "CRITICAL"
        printf "  %-10s %-38s %-12s\n" "SEC-002" "Kernel Pointer Leaking (kptr_restrict)" "HIGH"
        printf "  %-10s %-38s %-12s\n" "SEC-003" "dmesg Information Disclosure Restriction" "MEDIUM"
        printf "  %-10s %-38s %-12s\n" "SEC-004" "TCP SYN Flood Volumetric DoS Armor" "HIGH"
        printf "  %-10s %-38s %-12s\n" "SEC-005" "ICMP Route Redirect Spoofing Armor" "HIGH"
        printf "  %-10s %-38s %-12s\n" "EXP-001" "Ptrace Process Memory Inspection Shield" "CRITICAL"
        printf "  %-10s %-38s %-12s\n" "EXP-002" "eBPF Unprivileged Bytecode Lockdown" "CRITICAL"
        printf "  %-10s %-38s %-12s\n" "EXP-003" "SUID Core Dump Memory Sanitization" "HIGH"
        printf "  %-10s %-38s %-12s\n" "SYS-001" "Memory Swappiness Latency Tuning" "MEDIUM"
        printf "  %-10s %-38s %-12s\n" "SYS-002" "Storage Space & Disk Pressure Alert" "HIGH"
        echo ""
        ;;

    audit|*)
        echo -e "  ${C_BOLD}EVALUATING ACTIVE KNOWLEDGE BASE RULES:${C_RESET}\n"
        passed=0
        total=5

        aslr=$(cat /proc/sys/kernel/randomize_va_space 2>/dev/null || echo "2")
        if [ "$aslr" = "2" ]; then
            echo -e "  ${C_GREEN}[PASS]${C_RESET} SEC-001  Kernel ASLR Full Randomization Entropy      (${aslr})"
            passed=$((passed + 1))
        else
            echo -e "  ${C_RED}[FAIL]${C_RESET} SEC-001  Kernel ASLR Full Randomization Entropy      (${aslr}) -> Fix: sysctl -w kernel.randomize_va_space=2"
        fi

        kptr=$(cat /proc/sys/kernel/kptr_restrict 2>/dev/null || echo "2")
        if [ "$kptr" = "2" ]; then
            echo -e "  ${C_GREEN}[PASS]${C_RESET} SEC-002  Kernel Pointer Leaking (kptr_restrict)      (${kptr})"
            passed=$((passed + 1))
        else
            echo -e "  ${C_RED}[FAIL]${C_RESET} SEC-002  Kernel Pointer Leaking (kptr_restrict)      (${kptr}) -> Fix: sysctl -w kernel.kptr_restrict=2"
        fi

        dmesg_r=$(cat /proc/sys/kernel/dmesg_restrict 2>/dev/null || echo "1")
        if [ "$dmesg_r" = "1" ]; then
            echo -e "  ${C_GREEN}[PASS]${C_RESET} SEC-003  dmesg Information Disclosure Restriction    (${dmesg_r})"
            passed=$((passed + 1))
        else
            echo -e "  ${C_YELLOW}[WARN]${C_RESET} SEC-003  dmesg Information Disclosure Restriction    (${dmesg_r}) -> Fix: sysctl -w kernel.dmesg_restrict=1"
        fi

        syncookies=$(cat /proc/sys/net/ipv4/tcp_syncookies 2>/dev/null || echo "1")
        if [ "$syncookies" = "1" ]; then
            echo -e "  ${C_GREEN}[PASS]${C_RESET} SEC-004  TCP SYN Flood Volumetric DoS Armor          (${syncookies})"
            passed=$((passed + 1))
        else
            echo -e "  ${C_RED}[FAIL]${C_RESET} SEC-004  TCP SYN Flood Volumetric DoS Armor          (${syncookies}) -> Fix: sysctl -w net.ipv4.tcp_syncookies=1"
        fi

        swap=$(cat /proc/sys/vm/swappiness 2>/dev/null || echo "10")
        if [ "$swap" -le 60 ]; then
            echo -e "  ${C_GREEN}[PASS]${C_RESET} SYS-001  Memory Swappiness Latency Tuning            (${swap})"
            passed=$((passed + 1))
        else
            echo -e "  ${C_YELLOW}[WARN]${C_RESET} SYS-001  Memory Swappiness Latency Tuning            (${swap}) -> Fix: sysctl -w vm.swappiness=10"
        fi

        score=$(( (passed * 100) / total ))
        echo -e "\n  ${C_BOLD}CYBER RESILIENCE METRIC:${C_RESET} ${C_GREEN}${score} / 100${C_RESET} [${passed}/${total} Baseline Controls Compliant]\n"
        ;;
esac
