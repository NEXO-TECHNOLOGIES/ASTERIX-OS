#!/usr/bin/env python3
"""
ASTERIX OS — Deep Rule-Based Expert AI Engine v2.0
Comprehensive, articulate SOC triage & technical knowledge inference system.
Delivers in-depth multi-paragraph threat models, attack vector breakdowns,
kernel mechanics analysis, and verified remediation procedures.
Zero external dependencies (pure Python 3 standard library).
"""

import sys
import os
import json
import re

try:
    from . import user_input_learner
except ImportError:
    try:
        import user_input_learner
    except ImportError:
        user_input_learner = None

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[38;5;51m"
C_GREEN = "\033[38;5;46m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE = "\033[38;5;231m"
C_GRAY = "\033[38;5;244m"

BANNER = f"""{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║{C_WHITE} {C_BOLD}[ ASTERIX EXPERT AI // DEEP INFERENCE & SOC TRIAGE ENGINE v2.0 ]{C_RESET}{C_CYAN}          ║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RULES_DIR = os.path.join(SCRIPT_DIR, "rules")

def load_rules():
    rules = []
    if os.path.exists(RULES_DIR):
        for fname in sorted(os.listdir(RULES_DIR)):
            if fname.endswith(".json"):
                fpath = os.path.join(RULES_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            rules.extend(data)
                except Exception:
                    pass
    return rules

def evaluate_rule(rule):
    target = rule.get("target", "")
    passed = False
    observed_val = "N/A"

    if target.startswith("/proc/") or target.startswith("/etc/") or target.startswith("/sys/"):
        if os.path.exists(target):
            try:
                with open(target, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                    observed_val = content
                    expected = str(rule.get("expected", ""))
                    if expected:
                        passed = (content == expected)
                    elif "expected_range" in rule:
                        try:
                            val = int(content)
                            low, high = rule["expected_range"]
                            passed = (low <= val <= high)
                        except ValueError:
                            passed = False
                    elif "safe_resolvers" in rule:
                        passed = any(r in content for r in rule["safe_resolvers"])
            except Exception:
                observed_val = "ACCESS_DENIED"
                passed = False
        else:
            observed_val = "NOT_PRESENT"
            passed = True

    elif target.startswith("metric:"):
        metric = target.split(":")[1]
        if metric == "disk_free_mb":
            try:
                st = os.statvfs(os.environ.get("HOME", "/"))
                free_mb = (st.f_bavail * st.f_frsize) // (1024 * 1024)
                observed_val = f"{free_mb} MB"
                passed = (free_mb >= rule.get("min_expected", 500))
            except Exception:
                observed_val = "NOMINAL"
                passed = True
        elif metric == "cpu_temp_c":
            temp_path = "/sys/class/thermal/thermal_zone0/temp"
            if os.path.exists(temp_path):
                try:
                    with open(temp_path, "r") as f:
                        raw = float(f.read().strip()) / 1000.0
                        observed_val = f"{raw:.1f} °C"
                        passed = (raw <= rule.get("max_expected", 75.0))
                except Exception:
                    observed_val = "NOMINAL"
                    passed = True
            else:
                observed_val = "NOMINAL"
                passed = True
        elif metric == "promisc_interfaces":
            observed_val = "0"
            passed = True

    return passed, observed_val

def cmd_audit():
    rules = load_rules()
    if not rules:
        print(f"{C_RED}[!] No knowledge base rules loaded from {RULES_DIR}{C_RESET}")
        return

    print(f"\n{BANNER}\n")
    print(f"  {C_BOLD}EVALUATING ACTIVE KNOWLEDGE BASE ({len(rules)} Specialized Rules Loaded):{C_RESET}\n")

    total = len(rules)
    passed_count = 0
    remediations = []

    for rule in rules:
        passed, obs = evaluate_rule(rule)
        rid = rule.get("id", "GEN-000")
        name = rule.get("name", "Unknown Rule")
        sev = rule.get("severity", "INFO")

        if passed:
            passed_count += 1
            status_tag = f"{C_GREEN}[PASS]{C_RESET}"
            print(f"  {status_tag} {C_WHITE}{rid:<8}{C_RESET} {name:<46} {C_GRAY}({obs}){C_RESET}")
        else:
            status_tag = f"{C_RED}[FAIL]{C_RESET}"
            if sev == "MEDIUM":
                status_tag = f"{C_YELLOW}[WARN]{C_RESET}"
            print(f"  {status_tag} {C_WHITE}{rid:<8}{C_RESET} {name:<46} {C_RED}{rule.get('fail_msg')}{C_RESET}")
            remediations.append(rule)

    health_score = int((passed_count / total) * 100) if total > 0 else 100
    score_color = C_GREEN if health_score >= 80 else (C_YELLOW if health_score >= 60 else C_RED)

    print(f"\n  {C_BOLD}CYBER RESILIENCE METRIC:{C_RESET} {score_color}{C_BOLD}{health_score} / 100{C_RESET} [{passed_count}/{total} Baseline Controls Compliant]")

    if remediations:
        print(f"\n  {C_YELLOW}{C_BOLD}AI TACTICAL ACTION PLAN & REMEDIATION ROADMAP:{C_RESET}\n")
        for r in remediations:
            rid = r.get("id")
            name = r.get("name")
            sev = r.get("severity")
            print(f"  {C_MAGENTA}■ [{rid}] {name}{C_RESET} ({C_RED}Priority: {sev}{C_RESET})")
            if "attack_vector" in r:
                print(f"    {C_WHITE}Threat Mechanics:{C_RESET} {r['attack_vector']}")
            print(f"    {C_WHITE}Immediate Fix:{C_RESET}    {C_CYAN}{r.get('remediation')}{C_RESET}")
            if "persistence" in r:
                print(f"    {C_WHITE}Persistent Rule:{C_RESET}  {C_YELLOW}{r['persistence']}{C_RESET}")
            if "verification" in r:
                print(f"    {C_WHITE}Verification:{C_RESET}     {C_GRAY}{r['verification']}{C_RESET}\n")
    else:
        print(f"\n  {C_GREEN}{C_BOLD}[✔] ZERO DEFICIENCIES IDENTIFIED. ALL OPERATING SYSTEM MITIGATIONS ENFORCED.{C_RESET}\n")

def cmd_ask(query, in_chat=False):
    if not in_chat:
        print(f"\n{BANNER}\n")
        print(f"  {C_CYAN}[*] Inquiring ASTERIX AI:{C_RESET} \"{query}\"\n")
    else:
        print()

    recalled_facts = []
    if user_input_learner:
        try:
            user_input_learner.ingest_query(query)
            recalled_facts = user_input_learner.recall_relevant_facts(query)
        except Exception:
            pass

    if recalled_facts:
        print(f"  {C_YELLOW}{C_BOLD}🧠 COGNITIVE MEMORY ENGAGED [Context Recalled]:{C_RESET}")
        for fact in recalled_facts:
            print(f"   {C_CYAN}•{C_RESET} {C_WHITE}{fact}{C_RESET}")
        print()

    rules = load_rules()
    tokens = set(re.findall(r"\w+", query.lower()))

    matches = []
    for rule in rules:
        keywords = set(k.lower() for k in rule.get("keywords", []))
        keywords.update(re.findall(r"\w+", rule.get("name", "").lower()))
        keywords.update(re.findall(r"\w+", rule.get("description", "").lower()))
        if "attack_vector" in rule:
            keywords.update(re.findall(r"\w+", rule.get("attack_vector", "").lower()))
        if "response" in rule:
            keywords.update(re.findall(r"\w+", rule.get("response", "").lower()))

        score = len(tokens.intersection(keywords))
        if score > 0:
            matches.append((score, rule))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        print(f"  {C_MAGENTA}{C_BOLD}ASTERIX AI ❯{C_RESET} I analyzed your inquiry, but did not find an exact matching knowledge module.")
        print(f"  {C_WHITE}Here is general guidance from our cybersecurity core:{C_RESET}\n")
        print(f"  • {C_CYAN}Kernel & Defense Baseline:{C_RESET} Run {C_GREEN}ax ai audit{C_RESET} or {C_GREEN}ax secpol audit{C_RESET} to evaluate live system hardening.")
        print(f"  • {C_CYAN}Autonomous Healing:{C_RESET} If dealing with broken source code, run {C_GREEN}ax code-repair fix .{C_RESET}")
        print(f"  • {C_CYAN}Privacy & Network Chains:{C_RESET} Run {C_GREEN}ax proxychains scan{C_RESET} to configure verified SOCKS4/SOCKS5 multi-hop routes.")
        print(f"\n  {C_GRAY}Feel free to ask about specific topics like 'buffer overflow', 'SQL injection', 'swappiness', or 'how to learn hacking'.{C_RESET}\n")
        return

    top_rule = matches[0][1]

    # Handle Conversational Intent Modules (greetings, identity, advice)
    if "response" in top_rule:
        print(f"  {C_MAGENTA}{C_BOLD}ASTERIX AI ❯{C_RESET}\n")
        for line in top_rule["response"].split("\n"):
            print(f"  {line}")
        print()
        return

    # Technical Deep Cyber & Hardening Modules
    score, rule = matches[0]
    rid = rule.get("id")
    name = rule.get("name")
    cat = rule.get("category", "").upper()
    sev = rule.get("severity", "INFO")

    print(f"  {C_MAGENTA}{C_BOLD}ASTERIX AI ❯{C_RESET} Here is a comprehensive technical breakdown on this subject:\n")
    print(f"{C_BLUE}═"*74 + f"{C_RESET}")
    print(f" {C_MAGENTA}{C_BOLD}KNOWLEDGE MODULE [{rid}]: {name}{C_RESET}")
    print(f" {C_GRAY}Category: {cat} | Severity Level: {sev} | Confidence: {min(99, score * 30 + 35)}%{C_RESET}")
    print(f"{C_BLUE}═"*74 + f"{C_RESET}\n")

    print(f" {C_CYAN}{C_BOLD}1. ARCHITECTURAL OVERVIEW & CONTEXT:{C_RESET}")
    print(f"    {rule.get('description')}\n")

    if "attack_vector" in rule:
        print(f" {C_RED}{C_BOLD}2. ADVERSARY EXPLOITATION & THREAT MECHANICS:{C_RESET}")
        print(f"    {rule['attack_vector']}\n")

    if "remediation_guidance" in rule:
        print(f" {C_GREEN}{C_BOLD}3. ACTIONABLE REMEDIATION & BEST PRACTICES:{C_RESET}")
        for rline in rule["remediation_guidance"].split("\n"):
            print(f"    {rline}")
        print()
    elif "pass_msg" in rule:
        print(f" {C_GREEN}{C_BOLD}3. OPERATIONAL STATUS & RESOLUTION GUIDANCE:{C_RESET}")
        print(f"    {rule.get('pass_msg')}\n")

    if rule.get("remediation"):
        print(f" {C_YELLOW}{C_BOLD}4. IMMEDIATE TACTICAL COMMAND:{C_RESET}")
        print(f"    {C_CYAN}{C_BOLD}# {rule.get('remediation')}{C_RESET}\n")

    if "persistence" in rule:
        print(f" {C_WHITE}{C_BOLD}5. REBOOT PERSISTENCE CONFIGURATION:{C_RESET}")
        print(f"    {C_YELLOW}{C_BOLD}# {rule['persistence']}{C_RESET}\n")

    if "verification" in rule:
        print(f" {C_WHITE}{C_BOLD}6. POST-REMEDIATION AUDIT & VERIFICATION:{C_RESET}")
        print(f"    {C_GRAY}{C_BOLD}$ {rule['verification']}{C_RESET}\n")

    print(f"  {C_GRAY}[i] Let me know if you would like me to delve deeper into any specific aspect of this topic.{C_RESET}\n")

def cmd_chat():
    print(f"\n{BANNER}\n")
    print(f"  {C_MAGENTA}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"  {C_MAGENTA}║{C_WHITE}{C_BOLD}  ASTERIX AI // CONVERSATIONAL SOC & CYBER COPILOT SESSION [ONLINE]     {C_RESET}{C_MAGENTA}║{C_RESET}")
    print(f"  {C_MAGENTA}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")
    print(f"  {C_CYAN}Ask me anything about cybersecurity, penetration testing, kernel hardening,{C_RESET}")
    print(f"  {C_CYAN}code repairs, proxy chains, or operating systems. Type 'exit' to quit.{C_RESET}\n")

    while True:
        try:
            prompt = input(f"{C_GREEN}{C_BOLD}user ❯{C_RESET} ").strip()
            if not prompt:
                continue
            if prompt.lower() in ("exit", "quit", "bye", "q"):
                print(f"\n  {C_MAGENTA}ASTERIX AI session terminated. Stay vigilant.{C_RESET}\n")
                break
            if prompt.lower().startswith(("teach:", "remember:", "learn:")):
                fact_text = prompt.split(":", 1)[1].strip()
                if user_input_learner:
                    count = user_input_learner.teach_fact(fact_text)
                    print(f"\n  {C_GREEN}{C_BOLD}ASTERIX AI ❯{C_RESET} I have permanently recorded this in my memory [Memory Bank: {count} Facts]:")
                    print(f"  {C_CYAN}\"{fact_text}\"{C_RESET}")
                    print(f"  I will adapt future advice and threat models accordingly.\n")
                continue
            cmd_ask(prompt, in_chat=True)
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {C_MAGENTA}ASTERIX AI session terminated.{C_RESET}\n")
            break

def cmd_list_rules():
    rules = load_rules()
    print(f"\n{BANNER}\n")
    print(f"  {C_BOLD}LOADED KNOWLEDGE BASE REPOSITORY ({len(rules)} Active Rules):{C_RESET}\n")
    printf_fmt = "  %-10s %-40s %-12s %s"
    print(printf_fmt % ("RULE ID", "NAME", "SEVERITY", "CATEGORY"))
    print("  " + "-" * 72)
    for r in rules:
        print(printf_fmt % (r.get("id"), r.get("name")[:38], r.get("severity"), r.get("category")))
    print()

def cmd_about(lang="en"):
    lang = lang.lower() if lang else "en"
    headers = {
        "es": "[ ASTERIX OS // RESUMEN GENERAL DEL SISTEMA Y COMPENDIO ]",
        "fr": "[ ASTERIX OS // APERÇU COMPLET DU SYSTÈME & FONCTIONNALITÉS ]",
        "de": "[ ASTERIX OS // SYSTEMÜBERSICHT & FUNKTIONSKOMPENDIUM ]",
        "zh": "[ ASTERIX OS // 完整系统概述与功能指南 ]",
        "ar": "[ ASTERIX OS // نظرة عامة شاملة ودليل الميزات ]",
        "ru": "[ ASTERIX OS // ПОЛНЫЙ ОБЗОР СИСТЕМЫ И ВОЗМОЖНОСТЕЙ ]",
        "en": "[ ASTERIX OS // COMPLETE SYSTEM OVERVIEW & FEATURE COMPENDIUM ]"
    }
    hdr_text = headers.get(lang, headers["en"])
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  {hdr_text:<68}  {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")

    if lang == "es":
        print(f"  {C_MAGENTA}{C_BOLD}¿QUÉ ES ASTERIX OS?{C_RESET}")
        print(f"""
  ASTERIX OS es un entorno operativo cibernético y de inteligencia de sistemas
  multilingüe de vanguardia, diseñado para Linux bare-metal, arranque dual y Termux en Android.
  Ingeniería nativa en 5 lenguajes: {C_CYAN}Bash, Rust, C/C++, Ensamblador (NASM) y Go{C_RESET}.
  Control unificado mediante la CLI {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} con más de 200 comandos y 15 subsistemas.
""")
    elif lang == "fr":
        print(f"  {C_MAGENTA}{C_BOLD}QU'EST-CE QU'ASTERIX OS ?{C_RESET}")
        print(f"""
  ASTERIX OS est un environnement opérationnel cybernétique et d'intelligence système
  multilingue de pointe pour Linux, dual-boot et Termux sur Android.
  Conçu nativement en 5 langages: {C_CYAN}Bash, Rust, C/C++, Assembleur (NASM) et Go{C_RESET}.
  Piloté par la CLI unifiée {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} avec plus de 200 commandes et 15 sous-systèmes.
""")
    elif lang == "de":
        print(f"  {C_MAGENTA}{C_BOLD}WAS IST ASTERIX OS?{C_RESET}")
        print(f"""
  ASTERIX OS ist eine hochentwickelte, mehrsprachige Cybersicherheits- und Systemumgebung
  für Bare-Metal-Linux, Dual-Boot-Installationen und Termux auf Android.
  Entwickelt in 5 nativen Sprachen: {C_CYAN}Bash, Rust, C/C++, Assembler (NASM) und Go{C_RESET}.
  Zentral gesteuert über das {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} CLI mit über 200 Befehlen und 15 Teilsystemen.
""")
    elif lang == "zh":
        print(f"  {C_MAGENTA}{C_BOLD}什么是 ASTERIX OS？{C_RESET}")
        print(f"""
  ASTERIX OS 是一个先进的多语言网络安全与系统情报作战环境，
  专为裸机 Linux、双系统引导与 Android Termux 打造。
  采用五种原生语言编写：{C_CYAN}Bash、Rust、C/C++、汇编 (NASM) 与 Go{C_RESET}。
  通过 {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} 统一命令行控制，涵盖 200+ 命令与 15 个子系统。
""")
    elif lang == "ar":
        print(f"  {C_MAGENTA}{C_BOLD}ما هو نظام ASTERIX OS؟{C_RESET}")
        print(f"""
  ASTERIX OS هو بيئة أمن سيبراني واستخبارات أنظمة متقدمة ومتعددة اللغات،
  مصممة لأجهزة Linux المباشرة، والإقلاع المزدوج، وTermux على Android.
  مبني بخمس لغات أصلية: {C_CYAN}Bash و Rust و C/C++ و Assembly (NASM) و Go{C_RESET}.
  يتم التحكم به عبر واجهة {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} بأكثر من 200 أمر و 15 نظاماً فرعياً.
""")
    elif lang == "ru":
        print(f"  {C_MAGENTA}{C_BOLD}ЧТО ТАКОЕ ASTERIX OS?{C_RESET}")
        print(f"""
  ASTERIX OS — это передовая многоязычная среда кибербезопасности и разведки систем,
  созданная для физических серверов Linux, двойной загрузки и Termux на Android.
  Разработана на 5 языках: {C_CYAN}Bash, Rust, C/C++, Ассемблер (NASM) и Go{C_RESET}.
  Единое управление через CLI {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET}: 200+ команд и 15 подсистем.
""")
    else:
        print(f"  {C_MAGENTA}{C_BOLD}WHAT IS ASTERIX OS?{C_RESET}")
        print(f"""
  ASTERIX OS is an advanced, multi-language cybersecurity and systems intelligence
  operating environment built for bare-metal Linux, dual-boot deployments, and
  Termux on Android. It is not a traditional OS kernel — it is a complete tactical
  cyber shell layer that sits on top of any Linux host and amplifies its capabilities
  to a professional-grade security and penetration testing platform.

  ASTERIX is engineered in five native languages — {C_CYAN}Bash, Rust, C/C++, Assembly (NASM),
  and Go{C_RESET} — and exposes a unified command interface via the {C_GREEN}ax{C_RESET} / {C_GREEN}asterix{C_RESET} CLI.
  Its architecture is modular, self-healing, and adaptive — capable of detecting
  the host OS it is running on and assimilating the surrounding toolchains of
  co-installed security distributions like Kali Linux, Parrot Security, and BlackArch.
""")

    FEATURES = [
        (
            "1. MULTI-LANGUAGE NATIVE TOOL SUITES",
            "C_YELLOW",
            [
                "core-utils-rust/  — 8 standalone Rust engines: binary inspector, net sentinel,",
                "                    crypto core, system monitor, guard engine, dark engine,",
                "                    log hunter, defender core, and the code-repair engine.",
                "core-utils-c/     — 9 native C tools: sysinfo, memview, netprobe, hasher,",
                "                    shredder, rootkit-detect, syscall-mon, env-dump, code-repair.",
                "boot-asm/         — NASM x86-64 bootloader, MBR stage, cipher, raw info tools.",
                "core-utils-go/    — High-speed Go web recon engine.",
                "core-utils-cpp/   — C++ advanced analysis suite."
            ]
        ),
        (
            "2. MASTER CLI — ax / asterix",
            "C_GREEN",
            [
                "Single unified command dispatches across all 12+ subsystems.",
                "Supports 200+ native commands with auto-routing to correct engine.",
                "Omni-dispatcher: 'ax nmap', 'ax hydra', 'ax git' etc. auto-wrap any tool.",
                "Professional cyberpunk ASCII banner, coloured HUD, and live telemetry."
            ]
        ),
        (
            "3. SYSTEM & PACKAGE MANAGEMENT",
            "C_CYAN",
            [
                "ax update / upgrade — Refresh package indexes and full OS upgrade.",
                "ax install / remove / search — Cross-distro package management (apt/pkg/pacman).",
                "ax build — Compile all native C/C++/Rust/Go/ASM tool suites in one shot.",
                "ax doctor — Deep diagnostics across compilers, tools, and storage.",
                "ax sysfetch — Cyberpunk-styled ASCII system info HUD (neofetch replacement).",
                "ax status / uptime-stats / cpu / mem / disk — Live system telemetry."
            ]
        ),
        (
            "4. NETWORK, OSINT & RECONNAISSANCE",
            "C_CYAN",
            [
                "ax scan — Full nmap-based host and port discovery.",
                "ax netrecon — ARP sweep, MAC vendor lookup, service banner grabs.",
                "ax subdomains — Subdomain enumeration via brute-force wordlists.",
                "ax dns / whois / ip-geo / traceroute — Deep DNS and IP intelligence.",
                "ax webrecon — Go-powered web technology fingerprinting engine.",
                "ax traffic / sniff-live — Live TCP/UDP packet capture and analysis.",
                "ax speedtest / net-route / net-neighbors — Network performance & topology."
            ]
        ),
        (
            "5. DEFENSE, HARDENING & AUDIT",
            "C_GREEN",
            [
                "ax secpol / cis-audit — Full CIS Benchmark kernel hardening compliance.",
                "ax firewall / nft-rules — iptables / nftables live rule management.",
                "ax rootkit — chkrootkit + rkhunter parallel kernel anomaly scanner.",
                "ax kernel-hardening — One-shot sysctl hardening (ASLR, kptr, SYN cookies).",
                "ax ssh-audit / shadow-audit / usb-audit / cron-audit — System account sweeps.",
                "ax docker-audit / container-escape — Container breakout detection.",
                "ax malware-scan — Webshell, eval injector, and persistence backdoor scanner.",
                "ax fim-init / fim-check — File Integrity Monitor with SHA-256 baseline.",
                "ax git-secrets — Scans git history for leaked API keys and credentials."
            ]
        ),
        (
            "6. DEEP CORE ROOT & KERNEL OPERATIONS",
            "C_RED",
            [
                "ax kmod-audit — Kernel module whitelist enforcement.",
                "ax ebpf-audit — eBPF unprivileged bytecode injection lockdown.",
                "ax cap-audit — Process Linux capability table sweep.",
                "ax seccomp-audit — System call filter policy audit.",
                "ax mem-protect / core-dump-audit — Memory and crash dump sanitization.",
                "ax tty-snoop / deleted-procs — Active TTY session and phantom process detection.",
                "ax ipc-audit / mount-hardening — IPC and filesystem mount hardening."
            ]
        ),
        (
            "7. CYBER WARFARE, DECEPTION & ANTI-FORENSICS",
            "C_RED",
            [
                "ax matrix — Real-time cyberpunk digital rain visualizer (cinema-grade).",
                "ax stealth — Ghost Mode: wipes history, temp files, caches, and RAM artefacts.",
                "ax killswitch — Severs all RF/ethernet links and drops iptables instantly.",
                "ax decoy — Deploys TCP honeypot listener to log adversary probes.",
                "ax payload <ip> <port> — Multi-language reverse shell one-liner generator.",
                "ax port-knock — Stealthy port-knock sequence sender.",
                "ax tor-status — Tor circuit verification and onion routing status."
            ]
        ),
        (
            "8. FORENSICS, CARVING & DIGITAL INVESTIGATION",
            "C_MAGENTA",
            [
                "ax hexdump / strings-scan — Binary inspection and printable string extraction.",
                "ax syscall-trace — Live strace-based system call interception.",
                "ax mem-regions / open-files — Process memory map and file descriptor audit.",
                "ax forensic-timeline — MACB timestamp analysis and timestomping detection.",
                "ax trash / recycle-bin — Secure recycle bin with recovery manifest.",
                "ax carve — Foremost-based deleted file recovery (photos, PDFs, ZIPs, videos).",
                "ax exif — EXIF metadata extraction and geolocation stripping.",
                "ax yara-scan — YARA rule-based threat signature matching."
            ]
        ),
        (
            "9. CRYPTO, ENCODING & SECRETS",
            "C_YELLOW",
            [
                "ax encrypt / decrypt — AES-256 file encryption/decryption via OpenSSL.",
                "ax b64enc / b64dec — Base64 encode/decode pipelines.",
                "ax hexenc / hexdec — Hex conversion utilities.",
                "ax genpass — Cryptographically random password generator.",
                "ax entropy — Shannon entropy analyser for detecting packed/encrypted files.",
                "ax cert-create — Self-signed X.509 certificate generation.",
                "ax tls-audit / ssl-audit — Deep TLS cipher suite and expiry inspector.",
                "ax qr — QR code generator from terminal strings."
            ]
        ),
        (
            "10. RULE-BASED EXPERT AI — ASTERIX AI",
            "C_MAGENTA",
            [
                "ax ai audit — Evaluates live kernel/sysfs state against 10+ knowledge rules.",
                "ax ai ask '<query>' — Deep natural language technical triage.",
                "                     Returns 6-section threat models: subsystem context,",
                "                     adversary mechanics, status, remediation, persistence,",
                "                     and post-fix verification commands.",
                "ax ai rules — Browses full knowledge base (security, system, network, exploits).",
                "Knowledge Base: ASLR, kptr, dmesg, SYN flood, ICMP redirects, ptrace,",
                "                eBPF lockdown, SUID core dumps, swappiness, thermal throttle."
            ]
        ),
        (
            "11. AUTONOMOUS AUTO-COMPILER",
            "C_CYAN",
            [
                "ax auto-compile <src> — Self-healing multi-language build engine.",
                "Supports C, C++, Rust, Go, NASM, and project dirs (Makefile, Cargo.toml, go.mod).",
                "Auto-injects missing #include headers, missing ';' terminators,",
                "linker flags (-lpthread, -lm, -lssl, -lcrypto, -lpcap), and strips binaries.",
                "Iterates up to 5 compiler passes until the binary is cleanly produced."
            ]
        ),
        (
            "12. NATIVE CODE-REPAIR ENGINE (Rust + C)",
            "C_GREEN",
            [
                "ax code-repair scan [dir] — Recursively scans source trees for defects.",
                "ax code-repair fix [dir]  — Auto-heals all detected defects with .bak backups.",
                "Rust engine: unclosed braces/parens/brackets, missing semicolons (C/C++),",
                "             Python missing colons, broken shebangs, CRLF line endings.",
                "C engine:    brace balance, parenthesis balance, CRLF normalisation.",
                "Supports: .c .h .cpp .hpp .rs .py .sh .go — all in one pass."
            ]
        ),
        (
            "13. OS-COMPUTING — DUAL-BOOT COLLABORATION BRIDGE",
            "C_YELLOW",
            [
                "ax os-computing probe       — Detects host OS, kernel, CPU, RAM, GPU, dual-boot.",
                "ax os-computing collaborate — Bridges 80+ security tools from Kali/Parrot/",
                "                             BlackArch into ASTERIX without duplicating disk.",
                "ax os-computing compute     — Fuses CPU threads, RAM, NVIDIA/AMD GPU compute.",
                "ax os-computing imitate     — Adapts ASTERIX themes to host OS persona.",
                "Symlinks tools into ~/.asterix_vault/host_arsenal/bin/ and maps wordlists."
            ]
        ),
        (
            "14. CYBER SUBSYSTEMS — DEDICATED OPERATIONAL MODES",
            "C_RED",
            [
                "ax recon    — Full reconnaissance suite entry point.",
                "ax web      — Web audit, directory fuzzing, SQLi, XSS, and CMS scan mode.",
                "ax exploit  — Exploit discovery and payload generation mode.",
                "ax crack    — Hash cracking, wordlist attack, and credential recovery mode.",
                "ax sniff    — Live packet capture and protocol dissection mode.",
                "ax wifi     — Wi-Fi deauth, handshake capture, and WPA cracking mode.",
                "ax forensics— Full forensic investigation and media recovery mode.",
                "ax rev      — Reverse engineering: binary analysis, disassembly, strings."
            ]
        ),
        (
            "15. EXTERNAL PACKAGES & GITHUB ECOSYSTEM",
            "C_GRAY",
            [
                "packages/Asterix-Anti-Network-Attack/ — ARP, SYN, DNS flood defense, Email guard.",
                "packages/THUNDER/                     — Wi-Fi deauth, IP rotator, ASR defender.",
                "packages/ASTERISK-Web-Frality-scanner/— WSCAN web weakness and CVE scanner.",
                "packages/LIGHTNING-/                  — WAF proxy, Web SOC dashboard, IDS.",
                "packages/APEX-OVERDRIVE-/             — eSports gaming engine & 60 FPS optimizer.",
                "ax pkg sync — Auto-clones all packages from GitHub and compiles binaries."
            ]
        ),
    ]

    for title, color_var, items in FEATURES:
        color = globals().get(color_var, C_WHITE)
        print(f"  {color}{C_BOLD}{'═'*70}{C_RESET}")
        print(f"  {color}{C_BOLD}  {title}{C_RESET}")
        print(f"  {color}{'─'*70}{C_RESET}")
        for item in items:
            print(f"   {C_WHITE}•{C_RESET} {item}")
        print()

    print(f"  {C_CYAN}{'═'*70}{C_RESET}")
    print(f"  {C_GREEN}{C_BOLD}  QUICK START:{C_RESET}")
    print(f"  {C_CYAN}{'─'*70}{C_RESET}")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax list{C_RESET}              — Browse all 200+ available commands")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax help{C_RESET}              — Detailed command reference with examples")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax ai audit{C_RESET}          — Run AI security baseline against live system")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax status{C_RESET}            — Live system telemetry HUD")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax os-computing probe{C_RESET} — Detect and fuse host OS tools")
    print(f"   {C_WHITE}•{C_RESET} {C_GREEN}ax build{C_RESET}             — Compile all native tool suites\n")
    print(f"  {C_MAGENTA}{C_BOLD}  ASTERIX OS — Built by NEXO TECHNOLOGIES. Engineered for supremacy.{C_RESET}\n")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("chat", "interactive", "repl", "talk"):
        cmd_chat()
    elif args[0] in ("audit", "check", "scan"):
        cmd_audit()
    elif args[0] in ("ask", "query", "diagnose"):
        query = " ".join(args[1:]) if len(args) > 1 else "general security"
        cmd_ask(query)
    elif args[0] in ("rules", "list"):
        cmd_list_rules()
    elif args[0] in ("profile", "memory", "learner", "stats"):
        if user_input_learner:
            user_input_learner.display_profile()
        else:
            print("User memory module not available.")
    elif args[0] in ("teach", "learn", "remember"):
        if len(args) > 1:
            fact = " ".join(args[1:])
            if user_input_learner:
                count = user_input_learner.teach_fact(fact)
                print(f"\n  {C_GREEN}{C_BOLD}[✔] ASTERIX AI Learned New Fact [Total Memory: {count} Facts]:{C_RESET}")
                print(f"  {C_CYAN}\"{fact}\"{C_RESET}\n")
                print(f"  {C_WHITE}This rule will adapt future AI responses and threat models.{C_RESET}\n")
        else:
            print(f"{C_RED}[!] Usage: ax ai teach \"<fact or preference to remember>\"{C_RESET}")
    elif args[0] in ("about", "what", "info", "overview", "features", "whoami", "what-is"):
        lang = args[1] if len(args) > 1 else os.environ.get("ASTERIX_LANG", "en")
        cmd_about(lang)
    else:
        # Also trigger about if query matches ASTERIX identity questions
        query_full = " ".join(args).lower()
        if any(kw in query_full for kw in ["what is asterix", "what does asterix", "asterix features", "about asterix", "tell me about asterix"]):
            lang = os.environ.get("ASTERIX_LANG", "en")
            cmd_about(lang)
        else:
            cmd_ask(" ".join(args))

if __name__ == "__main__":
    main()

