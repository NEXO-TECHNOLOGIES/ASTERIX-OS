#!/usr/bin/env python3
"""
ASTERIX OS — User Input Learner & Cognitive Adaptation Engine v1.0
Continuously learns from user prompts, syntax habits, preferred toolchains,
and explicitly taught rules/facts to tailor ASTERIX AI responses to the user's thinking.
Zero external dependencies (pure Python 3 standard library).
"""

import sys
import os
import json
import time
import re

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[38;5;51m"
C_GREEN = "\033[38;5;46m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE = "\033[38;5;231m"
C_BLUE = "\033[38;5;45m"
C_GRAY = "\033[38;5;244m"

MEMORY_DIR = os.path.expanduser("~/.asterix_vault/ai_memory")
PROFILE_FILE = os.path.join(MEMORY_DIR, "user_profile.json")

DEFAULT_PROFILE = {
    "version": "1.0",
    "created_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    "last_interaction": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
    "interaction_count": 0,
    "technical_level": "intermediate",
    "inferred_role": "Security Researcher & Systems Engineer",
    "preferred_languages": ["Rust", "C", "Bash", "Python"],
    "favorite_tools": ["ax", "nmap", "proxychains4", "cargo"],
    "interest_weights": {
        "kernel_hardening": 5,
        "exploit_mitigation": 5,
        "autonomous_healing": 5,
        "network_warfare": 5,
        "web_security": 5,
        "reverse_engineering": 5
    },
    "learned_facts": [],
    "recent_queries": []
}

def ensure_memory_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)
    if not os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PROFILE, f, indent=2)

def load_profile():
    ensure_memory_dir()
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with default in case new keys were added
            for k, v in DEFAULT_PROFILE.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return DEFAULT_PROFILE.copy()

def save_profile(profile):
    ensure_memory_dir()
    profile["last_interaction"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def ingest_query(query):
    """Analyzes user input, updates interest weights, technical depth, and history."""
    profile = load_profile()
    profile["interaction_count"] += 1

    # Keep rolling window of last 20 queries
    profile["recent_queries"].append({
        "query": query,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    })
    if len(profile["recent_queries"]) > 20:
        profile["recent_queries"] = profile["recent_queries"][-20:]

    q_lower = query.lower()

    # Topic interest mining
    topic_keywords = {
        "kernel_hardening": ["aslr", "kptr", "sysctl", "hardening", "kernel", "yama", "ptrace", "swappiness"],
        "exploit_mitigation": ["buffer", "overflow", "rop", "canary", "payload", "shellcode", "heap"],
        "autonomous_healing": ["repair", "fix", "compiler", "build", "broken", "syntax", "heal"],
        "network_warfare": ["proxy", "socks", "proxychains", "syn", "dos", "arp", "packet", "sniff"],
        "web_security": ["sql", "injection", "xss", "csrf", "ssrf", "web", "waf", "portswigger"],
        "reverse_engineering": ["disassembly", "radare", "gdb", "ida", "ghidra", "elf", "binary"]
    }

    for topic, kws in topic_keywords.items():
        for kw in kws:
            if kw in q_lower:
                profile["interest_weights"][topic] = profile["interest_weights"].get(topic, 0) + 1

    # Inferred technical level
    advanced_terms = ["rop", "gadget", "ebpf", "vdso", "aslr", "heap", "relro", "canary", "nasm", "syscall"]
    intermediate_terms = ["sql", "xss", "suid", "proxychains", "compile", "sysctl", "nmap", "wireshark"]

    adv_hits = sum(1 for t in advanced_terms if t in q_lower)
    int_hits = sum(1 for t in intermediate_terms if t in q_lower)

    if adv_hits >= 2 or profile["interaction_count"] > 25:
        profile["technical_level"] = "elite"
    elif int_hits >= 1 or profile["interaction_count"] > 10:
        profile["technical_level"] = "advanced"

    # Detect user language preference in query
    if "rust" in q_lower:
        if "Rust" not in profile["preferred_languages"]:
            profile["preferred_languages"].insert(0, "Rust")
    if "assembly" in q_lower or "nasm" in q_lower:
        if "Assembly" not in profile["preferred_languages"]:
            profile["preferred_languages"].insert(0, "Assembly")

    save_profile(profile)
    return profile

def teach_fact(fact):
    """Explicitly stores a user rule or fact into AI memory."""
    profile = load_profile()
    fact_entry = {
        "fact": fact,
        "keywords": list(set(re.findall(r"\w+", fact.lower()))),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }
    profile["learned_facts"].append(fact_entry)
    save_profile(profile)
    return len(profile["learned_facts"])

def recall_relevant_facts(query):
    """Retrieves learned facts that match query tokens."""
    profile = load_profile()
    tokens = set(re.findall(r"\w+", query.lower()))
    matches = []
    for item in profile.get("learned_facts", []):
        kws = set(item.get("keywords", []))
        overlap = len(tokens.intersection(kws))
        if overlap > 0:
            matches.append((overlap, item["fact"]))
    matches.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matches[:3]]

def display_profile():
    profile = load_profile()
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  [ ASTERIX AI // COGNITIVE USER ADAPTATION & MEMORY PROFILE ]          {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")

    print(f"  {C_WHITE}{C_BOLD}INTERACTION TELEMETRY:{C_RESET}")
    print(f"   • Total Dialogues:     {C_GREEN}{profile.get('interaction_count', 0)}{C_RESET}")
    print(f"   • Inferred Cognition:  {C_MAGENTA}{profile.get('technical_level', 'intermediate').upper()}{C_RESET}")
    print(f"   • Persona Specialty:   {C_CYAN}{profile.get('inferred_role', 'Security Engineer')}{C_RESET}")
    print(f"   • Preferred Stacks:    {C_YELLOW}{', '.join(profile.get('preferred_languages', []))}{C_RESET}")
    print(f"   • Active Tools:        {C_WHITE}{', '.join(profile.get('favorite_tools', []))}{C_RESET}\n")

    print(f"  {C_WHITE}{C_BOLD}CYBER TOPIC ENGAGEMENT HEATMAP:{C_RESET}")
    weights = profile.get("interest_weights", {})
    max_w = max(weights.values()) if weights else 1
    for topic, val in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        bars = int((val / max_w) * 20)
        bar_str = "█" * bars + "░" * (20 - bars)
        print(f"   {topic:<24} {C_CYAN}{bar_str}{C_RESET} {C_YELLOW}{val}{C_RESET}")
    print()

    facts = profile.get("learned_facts", [])
    print(f"  {C_WHITE}{C_BOLD}LEARNED USER FACTS & RULES ({len(facts)} Active):{C_RESET}")
    if facts:
        for idx, f in enumerate(facts[-5:], 1):
            print(f"   {C_GREEN}[#{idx}]{C_RESET} {f['fact']} {C_GRAY}({f['timestamp']}){C_RESET}")
    else:
        print(f"   {C_GRAY}No custom user facts recorded yet.{C_RESET}")
        print(f"   {C_WHITE}Teach the AI via: {C_GREEN}ax ai teach \"<custom fact or preference>\"{C_RESET}")
    print()

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("profile", "status", "memory", "show"):
        display_profile()
    elif args[0] in ("teach", "learn", "remember"):
        if len(args) > 1:
            fact = " ".join(args[1:])
            count = teach_fact(fact)
            print(f"\n  {C_GREEN}{C_BOLD}[✔] ASTERIX AI Learned New Fact [Total Memory: {count} Facts]:{C_RESET}")
            print(f"  {C_CYAN}\"{fact}\"{C_RESET}\n")
            print(f"  {C_WHITE}This rule will adapt future AI responses and threat models.{C_RESET}\n")
        else:
            print(f"{C_RED}[!] Usage: ax ai teach \"<fact or preference to remember>\"{C_RESET}")
    elif args[0] == "ingest":
        query = " ".join(args[1:])
        ingest_query(query)
    elif args[0] == "reset":
        if os.path.exists(PROFILE_FILE):
            os.remove(PROFILE_FILE)
        print(f"{C_GREEN}[✔] AI user memory profile reset to default.{C_RESET}")

if __name__ == "__main__":
    main()
