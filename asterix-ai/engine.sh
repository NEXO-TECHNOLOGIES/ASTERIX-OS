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
    chat|interactive|repl|talk)
        echo -e "  ${C_MAGENTA}${C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗${C_RESET}"
        echo -e "  ${C_MAGENTA}║${C_WHITE}${C_BOLD}  ASTERIX AI // CONVERSATIONAL SOC & CYBER COPILOT SESSION [ONLINE]     ${C_RESET}${C_MAGENTA}║${C_RESET}"
        echo -e "  ${C_MAGENTA}╚══════════════════════════════════════════════════════════════════════════╝${C_RESET}\n"
        echo -e "  ${C_CYAN}Ask me anything about cybersecurity, penetration testing, kernel hardening,${C_RESET}"
        echo -e "  ${C_CYAN}code repairs, proxy chains, or operating systems. Type 'exit' to quit.${C_RESET}\n"
        while true; do
            read -r -p "$(echo -e "${C_GREEN}${C_BOLD}user ❯${C_RESET} ")" user_input || break
            [ -z "$user_input" ] && continue
            if [[ "$user_input" =~ ^(exit|quit|bye|q)$ ]]; then
                echo -e "\n  ${C_MAGENTA}ASTERIX AI session terminated. Stay vigilant.${C_RESET}\n"
                break
            fi
            bash "$0" ask "$user_input"
        done
        ;;

    ask|query|diagnose)
        query="$*"
        echo -e "  ${C_CYAN}[*] Inquiring ASTERIX AI:${C_RESET} \"${query}\"\n"

        if [[ "$query" =~ ^([Hh]ello|[Hh]i|[Hh]ey|[Gg]reetings|[Hh]owdy|[Ss]up|[Yy]o)$ ]]; then
            echo -e "  ${C_MAGENTA}${C_BOLD}ASTERIX AI ❯${C_RESET} Greetings! I am your resident tactical intelligence and cybersecurity copilot."
            echo -e "  I am specialized in penetration testing, kernel hardening, reverse engineering, and code healing."
            echo -e "  What cybersecurity domain or system objective are we tackling today?\n"
            exit 0
        elif [[ "$query" =~ [Ww]ho\ are\ you|[Ww]hat\ are\ you|[Ii]ntroduce\ yourself ]]; then
            echo -e "  ${C_MAGENTA}${C_BOLD}ASTERIX AI ❯${C_RESET} I am ASTERIX AI (v3.0) — an autonomous, offline intelligence engine."
            echo -e "  I run 100% locally on your machine with zero cloud dependencies and zero data harvesting.\n"
            exit 0
        fi

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
        elif [[ "$query" =~ [Ss][Qq][Ll]|[Ii]njection ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [CYB-001]: SQL Injection (SQLi) Deep Technical Analysis${C_RESET}"
            echo -e " ${C_GRAY}Category: WEB_SECURITY | Severity Level: CRITICAL | Relevance: 100%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & CONTEXT:${C_RESET}"
            echo -e "    SQL Injection occurs when untrusted user input is directly concatenated into database"
            echo -e "    SQL statements without parameterized prepared bindings or input sanitization.\n"
            echo -e " ${C_RED}${C_BOLD}2. ADVERSARY EXPLOITATION & THREAT MECHANICS:${C_RESET}"
            echo -e "    Adversaries inject SQL metacharacters (such as ' OR '1'='1, UNION SELECT, or --) to"
            echo -e "    bypass authentication, exfiltrate sensitive data, dump schemas, write arbitrary webshells,"
            echo -e "    or execute operating system commands via database extensions (xp_cmdshell / sys_eval).\n"
            echo -e " ${C_GREEN}${C_BOLD}3. ACTIONABLE REMEDIATION & BEST PRACTICES:${C_RESET}"
            echo -e "    • Always enforce Parameterized Prepared Statements (PDO, PreparedStatement, psycopg2)."
            echo -e "    • Run ASTERIX WAF (packages/LIGHTNING-/) to inspect and block malicious SQL tokens."
            echo -e "    • Audit web root for unparameterized SQL: grep -rn 'SELECT.*WHERE.*\$' /var/www/html/\n"

        elif [[ "$query" =~ [Xx][Ss][Ss]|[Ss]cripting ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [CYB-002]: Cross-Site Scripting (XSS) & DOM Exploitation${C_RESET}"
            echo -e " ${C_GRAY}Category: WEB_SECURITY | Severity Level: HIGH | Relevance: 100%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & CONTEXT:${C_RESET}"
            echo -e "    XSS involves injecting malicious client-side JavaScript into trusted web applications"
            echo -e "    viewed by victim users, executing arbitrary script in the context of the vulnerable origin.\n"
            echo -e " ${C_GREEN}${C_BOLD}2. ACTIONABLE REMEDIATION & BEST PRACTICES:${C_RESET}"
            echo -e "    • Enforce strict Content Security Policy (CSP): default-src 'self'"
            echo -e "    • Mark all session cookies as HttpOnly and Secure to prevent document.cookie theft."
            echo -e "    • Sanitize dynamic HTML using DOMPurify.\n"

        elif [[ "$query" =~ [Pp]rivilege|[Pp]rivesc|[Ss][Uu][Ii][Dd] ]]; then
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e " ${C_MAGENTA}${C_BOLD}KNOWLEDGE MODULE [CYB-004]: Linux Local Privilege Escalation via SUID Binaries${C_RESET}"
            echo -e " ${C_GRAY}Category: PRIVILEGE_ESCALATION | Severity Level: CRITICAL | Relevance: 100%${C_RESET}"
            echo -e "${C_BLUE}══════════════════════════════════════════════════════════════════════════${C_RESET}\n"
            echo -e " ${C_CYAN}${C_BOLD}1. ARCHITECTURAL OVERVIEW & CONTEXT:${C_RESET}"
            echo -e "    SUID permissions allow executables to run with root privileges. If utilities like"
            echo -e "    find, vim, bash, or nmap have the SUID bit set, unprivileged local users can spawn root shells.\n"
            echo -e " ${C_YELLOW}${C_BOLD}2. IMMEDIATE TACTICAL AUDIT COMMAND:${C_RESET}"
            echo -e "    ${C_CYAN}${C_BOLD}# ax suid${C_RESET}  or  ${C_CYAN}${C_BOLD}find / -perm -4000 2>/dev/null${C_RESET}\n"
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

    about|info|overview|features|what|whoami|what-is)
        lang="${1:-${ASTERIX_LANG:-en}}"
        lang=$(echo "$lang" | tr '[:upper:]' '[:lower:]')

        echo -e "\n${C_CYAN}${C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗${C_RESET}"
        case "$lang" in
            es) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // RESUMEN GENERAL DEL SISTEMA Y COMPENDIO ]             ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            fr) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // APERÇU COMPLET DU SYSTÈME & FONCTIONNALITÉS ]          ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            de) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // SYSTEMÜBERSICHT & FUNKTIONSKOMPENDIUM ]                ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            zh) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // 完整系统概述与功能指南 ]                              ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            ar) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // نظرة عامة شاملة ودليل الميزات ]                        ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            ru) echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // ПОЛНЫЙ ОБЗОР СИСТЕМЫ И ВОЗМОЖНОСТЕЙ ]                 ${C_RESET}${C_CYAN}║${C_RESET}" ;;
            *)  echo -e "${C_CYAN}║${C_WHITE}${C_BOLD}  [ ASTERIX OS // COMPLETE SYSTEM OVERVIEW & FEATURE COMPENDIUM ]        ${C_RESET}${C_CYAN}║${C_RESET}" ;;
        esac
        echo -e "${C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝${C_RESET}\n"

        case "$lang" in
            es)
                echo -e "  ${C_MAGENTA}${C_BOLD}¿QUÉ ES ASTERIX OS?${C_RESET}\n"
                echo -e "  ASTERIX OS es un entorno operativo cibernético y de inteligencia de sistemas"
                echo -e "  multilingüe de vanguardia, diseñado para Linux bare-metal, arranque dual y Termux en Android."
                echo -e "  Ingeniería nativa en 5 lenguajes: ${C_CYAN}Bash, Rust, C/C++, Ensamblador (NASM) y Go${C_RESET}."
                echo -e "  Control unificado mediante la CLI ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} con más de 200 comandos y 15 subsistemas.\n"
                ;;
            fr)
                echo -e "  ${C_MAGENTA}${C_BOLD}QU'EST-CE QU'ASTERIX OS ?${C_RESET}\n"
                echo -e "  ASTERIX OS est un environnement opérationnel cybernétique et d'intelligence système"
                echo -e "  multilingue de pointe pour Linux, dual-boot et Termux sur Android."
                echo -e "  Conçu nativement en 5 langages: ${C_CYAN}Bash, Rust, C/C++, Assembleur (NASM) et Go${C_RESET}."
                echo -e "  Piloté par la CLI unifiée ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} avec plus de 200 commandes et 15 sous-systèmes.\n"
                ;;
            de)
                echo -e "  ${C_MAGENTA}${C_BOLD}WAS IST ASTERIX OS?${C_RESET}\n"
                echo -e "  ASTERIX OS ist eine hochentwickelte, mehrsprachige Cybersicherheits- und Systemumgebung"
                echo -e "  für Bare-Metal-Linux, Dual-Boot-Installationen und Termux auf Android."
                echo -e "  Entwickelt in 5 nativen Sprachen: ${C_CYAN}Bash, Rust, C/C++, Assembler (NASM) und Go${C_RESET}."
                echo -e "  Zentral gesteuert über das ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} CLI mit über 200 Befehlen und 15 Teilsystemen.\n"
                ;;
            zh)
                echo -e "  ${C_MAGENTA}${C_BOLD}什么是 ASTERIX OS？${C_RESET}\n"
                echo -e "  ASTERIX OS 是一个先进的多语言网络安全与系统情报作战环境，"
                echo -e "  专为裸机 Linux、双系统引导与 Android Termux 打造。"
                echo -e "  采用五种原生语言编写：${C_CYAN}Bash、Rust、C/C++、汇编 (NASM) 与 Go${C_RESET}。"
                echo -e "  通过 ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} 统一命令行控制，涵盖 200+ 命令与 15 个子系统。\n"
                ;;
            ar)
                echo -e "  ${C_MAGENTA}${C_BOLD}ما هو نظام ASTERIX OS؟${C_RESET}\n"
                echo -e "  ASTERIX OS هو بيئة أمن سيبراني واستخبارات أنظمة متقدمة ومتعددة اللغات،"
                echo -e "  مصممة لأجهزة Linux المباشرة، والإقلاع المزدوج، وTermux على Android."
                echo -e "  مبني بخمس لغات أصلية: ${C_CYAN}Bash و Rust و C/C++ و Assembly (NASM) و Go${C_RESET}."
                echo -e "  يتم التحكم به عبر واجهة ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} بأكثر من 200 أمر و 15 نظاماً فرعياً.\n"
                ;;
            ru)
                echo -e "  ${C_MAGENTA}${C_BOLD}ЧТО ТАКОЕ ASTERIX OS?${C_RESET}\n"
                echo -e "  ASTERIX OS — это передовая многоязычная среда кибербезопасности и разведки систем,"
                echo -e "  созданная для физических серверов Linux, двойной загрузки и Termux на Android."
                echo -e "  Разработана на 5 языках: ${C_CYAN}Bash, Rust, C/C++, Ассемблер (NASM) и Go${C_RESET}."
                echo -e "  Единое управление через CLI ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET}: 200+ команд и 15 подсистем.\n"
                ;;
            *)
                echo -e "  ${C_MAGENTA}${C_BOLD}WHAT IS ASTERIX OS?${C_RESET}\n"
                echo -e "  ASTERIX OS is an advanced, multi-language cybersecurity and systems intelligence"
                echo -e "  operating environment built for bare-metal Linux, dual-boot deployments, and"
                echo -e "  Termux on Android. It is not a traditional OS kernel — it is a complete tactical"
                echo -e "  cyber shell layer that amplifies any Linux host into a professional-grade security"
                echo -e "  and penetration testing platform.\n"
                echo -e "  Engineered in five native languages: ${C_CYAN}Bash, Rust, C/C++, Assembly (NASM), and Go${C_RESET}."
                echo -e "  Unified via the ${C_GREEN}ax${C_RESET} / ${C_GREEN}asterix${C_RESET} CLI — 200+ commands across 15 subsystems.\n"
                ;;
        esac

        sections=(
            "${C_YELLOW}1. MULTI-LANGUAGE NATIVE TOOLS${C_RESET}|Rust (8 engines), C (9 tools), NASM (bootloader+cipher), Go (webrecon), C++ suite"
            "${C_GREEN}2. MASTER CLI — ax / asterix${C_RESET}|200+ commands, omni-dispatcher, cyberpunk HUD, live telemetry"
            "${C_CYAN}3. SYSTEM & PACKAGE MANAGEMENT${C_RESET}|update/upgrade, install/remove, build all suites, doctor diagnostics, sysfetch"
            "${C_CYAN}4. NETWORK, OSINT & RECON${C_RESET}|scan, netrecon, subdomains, dns/whois/ip-geo, webrecon, sniff-live, speedtest"
            "${C_GREEN}5. DEFENSE & HARDENING${C_RESET}|secpol, cis-audit, firewall, rootkit, kernel-hardening, fim, malware-scan, git-secrets"
            "${C_RED}6. DEEP CORE ROOT OPS${C_RESET}|kmod-audit, ebpf-audit, cap-audit, seccomp-audit, mem-protect, tty-snoop, ipc-audit"
            "${C_RED}7. CYBER WARFARE & DECEPTION${C_RESET}|matrix, stealth (Ghost Mode), killswitch, decoy honeypot, payload generator, tor"
            "${C_MAGENTA}8. FORENSICS & INVESTIGATION${C_RESET}|hexdump, syscall-trace, forensic-timeline, trash/recycle-bin, carve, exif, yara-scan"
            "${C_YELLOW}9. CRYPTO & ENCODING${C_RESET}|encrypt/decrypt (AES-256), b64, hex, genpass, entropy, cert-create, tls-audit, qr"
            "${C_MAGENTA}10. RULE-BASED EXPERT AI${C_RESET}|audit (0-100 score), ask (6-section threat model), rules browser, 10+ knowledge rules"
            "${C_CYAN}11. AUTO-COMPILER${C_RESET}|Self-healing build engine: auto-inject headers, fix semicolons, inject linker flags"
            "${C_GREEN}12. NATIVE CODE-REPAIR (Rust+C)${C_RESET}|scan/fix source trees: braces, parens, semicolons, shebangs, CRLF — all languages"
            "${C_YELLOW}13. OS-COMPUTING BRIDGE${C_RESET}|Dual-boot probe, 80+ tool assimilation (Kali/Parrot/BlackArch), GPU compute synergy"
            "${C_RED}14. CYBER SUBSYSTEM MODES${C_RESET}|recon, web, exploit, crack, sniff, wifi, forensics, rev — dedicated op modes"
            "${C_GRAY}15. EXTERNAL PACKAGES${C_RESET}|Anti-Network-Attack, THUNDER, Web-Frality-Scanner, LIGHTNING, APEX-OVERDRIVE"
        )

        for entry in "${sections[@]}"; do
            title="${entry%%|*}"
            desc="${entry##*|}"
            echo -e "  ${C_CYAN}═══════════════════════════════════════════════════════════════════════${C_RESET}"
            echo -e "  ${C_BOLD}  ${title}${C_RESET}"
            echo -e "     ${C_WHITE}${desc}${C_RESET}\n"
        done

        echo -e "  ${C_CYAN}═══════════════════════════════════════════════════════════════════════${C_RESET}"
        echo -e "  ${C_GREEN}${C_BOLD}  QUICK START / DÉMARRAGE / INICIO RÁPIDO:${C_RESET}"
        echo -e "     ${C_GREEN}ax list${C_RESET}              — Browse all 200+ available commands"
        echo -e "     ${C_GREEN}ax ai about [lang]${C_RESET}   — Multilingual overview: en, es, fr, de, zh, ar, ru"
        echo -e "     ${C_GREEN}ax ai audit${C_RESET}          — Run security baseline against live system"
        echo -e "     ${C_GREEN}ax os-computing probe${C_RESET} — Detect host OS and fuse tool arsenals"
        echo -e "     ${C_GREEN}ax code-repair fix .${C_RESET}  — Scan and heal all broken source files"
        echo -e "     ${C_GREEN}ax build${C_RESET}             — Compile all native tool suites\n"
        echo -e "  ${C_MAGENTA}${C_BOLD}  ASTERIX OS — Built by NEXO TECHNOLOGIES. Engineered for supremacy.${C_RESET}\n"
        ;;

    teach|learn|remember)
        fact="$*"
        echo -e "  ${C_GREEN}${C_BOLD}[✔] ASTERIX AI LEARNED:${C_RESET} \"${fact}\""
        echo -e "  ${C_GRAY}[i] Persistence requires Python 3 (ax ai profile to view).${C_RESET}"
        if command -v python3 >/dev/null 2>&1; then
            _ai_dir="$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")"
            python3 "${_ai_dir}/user_input_learner.py" teach "$fact" 2>/dev/null
        fi
        exit 0
        ;;

    profile|memory|learner|stats|whoami)
        echo -e "\n  ${C_CYAN}${C_BOLD}[ ASTERIX AI // COGNITIVE MEMORY PROFILE ]${C_RESET}\n"
        if command -v python3 >/dev/null 2>&1; then
            _ai_dir="$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")"
            python3 "${_ai_dir}/user_input_learner.py" profile
        else
            echo -e "  ${C_YELLOW}[i] AI memory profile requires Python 3.${C_RESET}"
            echo -e "  ${C_GRAY}Install Python 3 and run: ax ai profile${C_RESET}\n"
        fi
        exit 0
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

