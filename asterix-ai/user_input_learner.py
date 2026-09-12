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
PROFILE_STATUS_FILE = os.path.join(MEMORY_DIR, "profile_status.json")
WORKSPACE_PROFILE_STATUS_FILE = os.path.join(os.path.dirname(__file__), "profile_status.json")

DEFAULT_PROFILE = {
    "assistant_name": "ASTERIX AI",
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
    "self_evolution_log": [],
    "recent_queries": [],
    "mood_profile": [],
    "theme_preferences": {
        "current_theme": "matrix",
        "auto_theme_enabled": True,
        "recent_themes": ["matrix"],
        "preferred_moods": {
            "frustrated": "pulse",
            "stressed": "pulse",
            "urgent": "scan",
            "curious": "neon",
            "excited": "glitch",
            "confident": "matrix",
            "calm": "matrix"
        }
    },
    "learning_quota": 100,
    "training_completed": 0,
    "mood_quota": 50,
    "mood_training_completed": 0,
    "training_mode": "continuous",
    "response_style": "balanced"
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

def write_profile_status(profile=None):
    """Write a compact snapshot that the dashboard can poll without reading the full memory profile."""
    current = profile if isinstance(profile, dict) else load_profile()
    snapshot = {
        "assistant_name": current.get("assistant_name", "ASTERIX AI"),
        "mood": current.get("mood_profile", [])[-1].get("primary_mood", "balanced") if current.get("mood_profile") else "balanced",
        "response_style": current.get("response_style", "balanced"),
        "training_completed": current.get("training_completed", 0),
        "learning_quota": current.get("learning_quota", 100),
        "training_mode": current.get("training_mode", "continuous"),
        "confidence": round(0.75 + (current.get("mood_profile", [])[-1].get("summary", {}).get("urgency", 0) * 0.04) + (current.get("mood_profile", [])[-1].get("summary", {}).get("confidence", 0) * 0.02), 2) if current.get("mood_profile") else 0.75,
        "mood_summary": current.get("mood_profile", [])[-1].get("summary", {}) if current.get("mood_profile") else {
            "frustration": 0,
            "stress": 0,
            "urgency": 0,
            "curiosity": 0,
            "excitement": 0,
            "calm": 1,
        },
    }
    for status_path in (PROFILE_STATUS_FILE, WORKSPACE_PROFILE_STATUS_FILE):
        try:
            with open(status_path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2)
        except Exception:
            pass
    return snapshot


def save_profile(profile):
    ensure_memory_dir()
    profile["last_interaction"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    with open(PROFILE_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)
    write_profile_status(profile)

def analyze_emotional_state(query):
    """Return a compact emotional summary for the user: mood, stress, urgency, frustration, confidence."""
    text = str(query or "").lower()
    score = {
        "frustration": 0,
        "stress": 0,
        "urgency": 0,
        "confidence": 0,
        "curiosity": 0,
        "excitement": 0,
        "calm": 0,
    }

    mood_markers = {
        "frustration": ["frustrated", "annoyed", "angry", "driving me crazy", "ugh", "hate", "terrible", "bad", "broken", "awful"],
        "stress": ["stress", "stressed", "overwhelmed", "panic", "urgent", "hurry", "pressure", "crazy", "difficult", "not working"],
        "urgency": ["fast", "quick", "hurry", "immediately", "now", "urgent", "asap", "right now", "please hurry"],
        "confidence": ["sure", "confident", "clear", "yes", "definitely", "good", "works", "done", "perfect"],
        "curiosity": ["why", "how", "what", "teach me", "explain", "learn", "show me", "curious"],
        "excitement": ["love", "awesome", "great", "amazing", "cool", "excited", "nice", "super"],
        "calm": ["calm", "okay", "fine", "steady", "chill", "relaxed", "easy"],
    }

    for mood, markers in mood_markers.items():
        for marker in markers:
            if marker in text:
                score[mood] += 1

    if score["frustration"] or score["stress"]:
        primary = "frustrated" if score["frustration"] >= score["stress"] else "stressed"
    elif score["urgency"]:
        primary = "urgent"
    elif score["excitement"]:
        primary = "excited"
    elif score["curiosity"]:
        primary = "curious"
    elif score["confidence"]:
        primary = "confident"
    else:
        primary = "calm"

    # normalize strong emotional states
    summary = {
        "primary_mood": primary,
        "frustration": max(0, min(5, score["frustration"])),
        "stress": max(0, min(5, score["stress"])),
        "urgency": max(0, min(5, score["urgency"])),
        "confidence": max(0, min(5, score["confidence"])),
        "curiosity": max(0, min(5, score["curiosity"])),
        "excitement": max(0, min(5, score["excitement"])),
        "calm": max(0, min(5, score["calm"])),
    }
    return summary


def response_style_for_mood(query):
    """Return an adaptive response mode based on the current emotional context."""
    mood = analyze_emotional_state(query)
    primary = mood["primary_mood"]
    if primary in {"frustrated", "stressed"}:
        return {
            "style": "empathetic-direct",
            "tone": "short, reassuring, and action-focused",
            "empathy_level": "high",
            "escalation": "fast",
        }
    if primary == "urgent":
        return {
            "style": "urgent-priority",
            "tone": "decisive and fast",
            "empathy_level": "medium",
            "escalation": "immediate",
        }
    if primary == "curious":
        return {
            "style": "teach-and-explain",
            "tone": "educational and patient",
            "empathy_level": "medium",
            "escalation": "guided",
        }
    if primary == "excited":
        return {
            "style": "motivating",
            "tone": "positive and energized",
            "empathy_level": "medium",
            "escalation": "enthusiastic",
        }
    return {
        "style": "balanced",
        "tone": "calm and adaptive",
        "empathy_level": "low",
        "escalation": "normal",
    }


def build_adaptive_response(query):
    """Construct an emotionally-aware assistant reply and tune confidence based on user mood."""
    mood = analyze_emotional_state(query)
    style = response_style_for_mood(query)
    primary = mood["primary_mood"]

    if primary in {"frustrated", "stressed"}:
        msg = "I hear the pressure. I will fix this fast and keep the steps simple."
        confidence = 0.9
        style_name = "empathetic-direct"
    elif primary == "urgent":
        msg = "I will prioritize this now and keep the fix focused on the fastest path."
        confidence = 0.88
        style_name = "urgent-priority"
    elif primary == "curious":
        msg = "Let me explain what is happening and show the exact next step in plain language."
        confidence = 0.82
        style_name = "teach-and-explain"
    elif primary == "excited":
        msg = "Awesome. Let’s move fast and keep this momentum high."
        confidence = 0.8
        style_name = "motivating"
    else:
        msg = "I will keep this steady and efficient while we work through it."
        confidence = 0.75
        style_name = "balanced"

    return {
        "style": style_name,
        "message": msg,
        "confidence": confidence,
        "mood": primary,
        "response_tone": style["tone"],
    }


def theme_preferences_from_mood(mood_summary=None):
    """Map emotional state to a boot theme family."""
    mood = mood_summary or {"primary_mood": "calm"}
    primary = str(mood.get("primary_mood", "calm")).lower()
    mapping = {
        "frustrated": "pulse",
        "stressed": "pulse",
        "urgent": "scan",
        "curious": "neon",
        "excited": "glitch",
        "confident": "matrix",
        "calm": "matrix",
        "balanced": "matrix",
    }
    return mapping.get(primary, "matrix")


def save_theme_preference(profile, theme, reason="auto", confidence=0.8):
    """Persist the user’s current preferred visual theme in the AI profile."""
    theme_name = str(theme).strip().lower()
    if not theme_name:
        return profile

    if "theme_preferences" not in profile:
        profile["theme_preferences"] = {
            "current_theme": theme_name,
            "auto_theme_enabled": True,
            "recent_themes": [],
            "preferred_moods": {}
        }

    prefs = profile["theme_preferences"]
    prefs["current_theme"] = theme_name
    prefs["last_reason"] = reason
    prefs["last_confidence"] = float(confidence)
    prefs.setdefault("recent_themes", [])
    if theme_name not in prefs["recent_themes"]:
        prefs["recent_themes"].append(theme_name)
    if len(prefs["recent_themes"]) > 8:
        prefs["recent_themes"] = prefs["recent_themes"][-8:]
    return profile


def recommend_theme_for_user(query=None, profile=None):
    """Suggest the best boot theme based on mood, learning history, and user preferences."""
    active_profile = profile if isinstance(profile, dict) else load_profile()
    latest_mood = None
    mood_entries = active_profile.get("mood_profile", [])
    if mood_entries:
        latest_mood = mood_entries[-1].get("summary", {})
        latest_mood["primary_mood"] = mood_entries[-1].get("primary_mood", "calm")
    if query:
        parsed = analyze_emotional_state(query)
        latest_mood = parsed
        latest_mood["primary_mood"] = parsed.get("primary_mood", "calm")

    preferred_theme = theme_preferences_from_mood(latest_mood)
    prefs = active_profile.get("theme_preferences", {})
    preferred_theme = prefs.get("preferred_moods", {}).get(latest_mood.get("primary_mood", "calm"), preferred_theme)

    result = {
        "theme": preferred_theme,
        "reason": "inferred from current mood and previous theme preference history",
        "confidence": 0.82,
        "auto": True,
    }
    save_theme_preference(active_profile, preferred_theme, reason=result["reason"], confidence=result["confidence"])
    save_profile(active_profile)
    return result


def run_continuous_training_loop(events, max_cycles=3, user_active=True):
    """Keep the AI learning loop active while the user remains engaged."""
    if not user_active:
        return {"active": False, "cycles_completed": 0, "last_status": "idle"}

    if not isinstance(events, list) or not events:
        return {"active": False, "cycles_completed": 0, "last_status": "idle"}

    cycle_count = 0
    result = {"active": True, "cycles_completed": 0, "last_status": "learning"}
    for _ in range(max_cycles):
        cycle_count += 1
        current_profile = continue_training_until_quota(events, quota=max(1, cycle_count + 1))
        if current_profile.get("training_mode") == "quota_reached" and cycle_count >= max_cycles:
            result["last_status"] = "quota_reached"
            break
        result["last_status"] = "watching"

    result["cycles_completed"] = cycle_count
    result["active"] = user_active and cycle_count > 0
    return result


def ingest_query(query):
    """Analyzes user input, updates interest weights, technical depth, and history."""
    profile = load_profile()
    profile["interaction_count"] += 1
    profile["training_completed"] = profile.get("training_completed", 0) + 1
    if profile["training_completed"] >= profile.get("learning_quota", 100):
        profile["training_mode"] = "quota_reached"

    # Keep rolling window of last 20 queries
    profile["recent_queries"].append({
        "query": query,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    })
    if len(profile["recent_queries"]) > 20:
        profile["recent_queries"] = profile["recent_queries"][-20:]

    q_lower = query.lower()
    mood = analyze_emotional_state(query)
    profile["response_style"] = response_style_for_mood(query)["style"]
    profile["mood_profile"] = profile.get("mood_profile", [])
    profile["mood_profile"].append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "primary_mood": mood["primary_mood"],
        "summary": mood,
    })

    theme_suggestion = recommend_theme_for_user(query, profile)
    profile["theme_preferences"] = profile.get("theme_preferences", {})
    profile["theme_preferences"]["current_theme"] = theme_suggestion["theme"]
    profile["theme_preferences"]["auto_theme_enabled"] = True
    profile["theme_preferences"].setdefault("recent_themes", [])
    if theme_suggestion["theme"] not in profile["theme_preferences"]["recent_themes"]:
        profile["theme_preferences"]["recent_themes"].append(theme_suggestion["theme"])
    if len(profile["theme_preferences"]["recent_themes"]) > 8:
        profile["theme_preferences"]["recent_themes"] = profile["theme_preferences"]["recent_themes"][-8:]
    if len(profile["mood_profile"]) > 25:
        profile["mood_profile"] = profile["mood_profile"][-25:]
    profile["mood_training_completed"] = profile.get("mood_training_completed", 0) + 1
    if profile["mood_training_completed"] >= profile.get("mood_quota", 50):
        profile["training_mode"] = "mood_quota_reached"

    if mood["frustration"] >= 2:
        profile["interest_weights"]["autonomous_healing"] = profile["interest_weights"].get("autonomous_healing", 0) + 1
    if mood["urgency"] >= 2:
        profile["interest_weights"]["kernel_hardening"] = profile["interest_weights"].get("kernel_hardening", 0) + 1
    if mood["confidence"] >= 2:
        profile["interest_weights"]["web_security"] = profile["interest_weights"].get("web_security", 0) + 1
    if mood["curiosity"] >= 2:
        profile["interest_weights"]["reverse_engineering"] = profile["interest_weights"].get("reverse_engineering", 0) + 1

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

    advanced_terms = ["rop", "gadget", "ebpf", "vdso", "aslr", "heap", "relro", "canary", "nasm", "syscall"]
    intermediate_terms = ["sql", "xss", "suid", "proxychains", "compile", "sysctl", "nmap", "wireshark"]

    adv_hits = sum(1 for t in advanced_terms if t in q_lower)
    int_hits = sum(1 for t in intermediate_terms if t in q_lower)

    if adv_hits >= 2 or profile["interaction_count"] > 25:
        profile["technical_level"] = "elite"
    elif int_hits >= 1 or profile["interaction_count"] > 10:
        profile["technical_level"] = "advanced"

    if "rust" in q_lower and "Rust" not in profile["preferred_languages"]:
        profile["preferred_languages"].insert(0, "Rust")
    if ("assembly" in q_lower or "nasm" in q_lower) and "Assembly" not in profile["preferred_languages"]:
        profile["preferred_languages"].insert(0, "Assembly")

    save_profile(profile)
    return profile


def continue_training_until_quota(events, quota=100):
    """Continue learning in batches until the configured learning quota is reached."""
    profile = load_profile()
    quota = max(1, int(quota))
    profile["learning_quota"] = quota
    profile["training_completed"] = profile.get("training_completed", 0)

    if isinstance(events, list) and events:
        for event in events:
            if not isinstance(event, dict):
                continue
            problem = str(event.get("problem", "")).strip()
            action = str(event.get("action", "")).strip()
            result = str(event.get("result", "")).strip()
            combined = " ".join(part for part in [problem, action, result] if part)
            if combined:
                profile = ingest_query(combined)
                if problem or action or result:
                    teach_fact(combined)
            if profile.get("training_completed", 0) >= quota:
                profile["training_mode"] = "quota_reached"
                save_profile(profile)
                return profile

    profile["training_mode"] = "quota_reached" if profile.get("training_completed", 0) >= quota else "continuous"
    save_profile(profile)
    return profile

def self_evolve_decision(change_description, domain="project", user_approved=False):
    """Allow project-level self-evolution while blocking system-critical mutation without permission."""
    description = str(change_description or "").lower()
    scope = str(domain or "project").lower()

    project_safe_domains = {
        "project", "workspace", "repo", "codebase", "learning", "memory", "ai", "repair",
        "project_files", "docs", "dashboard", "web", "code", "config", "debugger"
    }
    restricted_domains = {
        "system", "os", "kernel", "boot", "bootloader", "grub", "mbr", "firmware",
        "filesystem", "partition", "hardware", "device", "registry", "service", "sudo",
        "security_system"
    }
    dangerous_markers = [
        "bootloader", "grub", "mbr", "reboot", "poweroff", "shutdown",
        "format disk", "rm -rf /", "chmod 777", "mkfs", "dd if=",
        "partition", "registry", "systemctl", "install driver"
    ]

    if scope in project_safe_domains:
        return {
            "allowed": True,
            "requires_approval": False,
            "domain": scope,
            "reason": "project-safe self-evolution permitted for learning, docs, and code adaptation",
        }

    if scope in restricted_domains or any(marker in description for marker in dangerous_markers):
        return {
            "allowed": user_approved,
            "requires_approval": True,
            "domain": scope,
            "reason": "system-critical mutation is blocked until explicit user approval",
        }

    return {
        "allowed": user_approved or scope in project_safe_domains,
        "requires_approval": not (user_approved or scope in project_safe_domains),
        "domain": scope,
        "reason": "defaulted to safe project-only evolution policy",
    }


def apply_self_evolution_update(fact, domain="project", user_approved=False):
    """Commit a project-safe learning fact and keep a local evidence trail without mutating the OS."""
    decision = self_evolve_decision(fact, domain, user_approved=user_approved)
    if not decision["allowed"]:
        return {
            "updated": False,
            "fact": str(fact).strip(),
            "domain": domain,
            "decision": decision,
            "message": "blocked: system-critical change requires explicit user approval",
        }

    profile = load_profile()
    fact_text = str(fact).strip()
    if not fact_text:
        return {"updated": False, "fact": "", "domain": domain, "decision": decision}

    profile.setdefault("self_evolution_log", []).append({
        "fact": fact_text,
        "domain": domain,
        "approved": user_approved or decision["requires_approval"] is False,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    })
    if len(profile["self_evolution_log"]) > 100:
        profile["self_evolution_log"] = profile["self_evolution_log"][-100:]

    profile["training_mode"] = "project_self_evolving"
    teach_fact(fact_text)
    save_profile(profile)

    return {
        "updated": True,
        "fact": fact_text,
        "domain": domain,
        "decision": decision,
        "message": "project evolution accepted and stored in the local learning memory",
    }


def teach_fact(fact):
    """Explicitly stores a user rule or fact into AI memory."""
    profile = load_profile()
    fact_text = str(fact).strip()
    if not fact_text:
        return len(profile.get("learned_facts", []))

    for existing in profile.get("learned_facts", []):
        if str(existing.get("fact", "")).strip() == fact_text:
            return len(profile["learned_facts"])

    fact_entry = {
        "fact": fact_text,
        "keywords": list(set(re.findall(r"\w+", fact_text.lower()))),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }
    profile["learned_facts"].append(fact_entry)
    if len(profile["learned_facts"]) > 50:
        profile["learned_facts"] = profile["learned_facts"][-50:]
    save_profile(profile)
    return len(profile["learned_facts"])


def learn_from_memory_events(events):
    """Turn raw memory events into profile updates and structured facts."""
    profile = load_profile()
    if not isinstance(events, list):
        return profile

    aggregated_tokens = []
    for event in events:
        if not isinstance(event, dict):
            continue

        problem = str(event.get("problem", "")).strip()
        action = str(event.get("action", "")).strip()
        result = str(event.get("result", "")).strip()
        combined = " ".join(part for part in [problem, action, result] if part)
        aggregated_tokens.append((problem + " " + action).lower())

        if combined:
            profile["interaction_count"] += 1
            ingest_query(combined)
            if problem or action or result:
                teach_fact(combined)

    profile = load_profile()

    # strengthen user preference profile from observed repairs and dual-boot points
    combined_text = " ".join(aggregated_tokens).lower()
    for token in ["boot", "grub", "dual-boot", "kali", "repair", "fix", "compiler", "terminal", "desktop"]:
        if token in combined_text:
            profile["interest_weights"]["autonomous_healing"] = profile["interest_weights"].get("autonomous_healing", 0) + 1
            profile["interest_weights"]["kernel_hardening"] = profile["interest_weights"].get("kernel_hardening", 0) + 1

    save_profile(profile)
    return profile


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


def live_profile_snapshot():
    """Return the current mood, learning status, and response style for the dashboard."""
    profile = load_profile()
    mood_entries = profile.get("mood_profile", [])
    latest_mood = mood_entries[-1].get("primary_mood", "balanced") if mood_entries else "balanced"
    latest_summary = mood_entries[-1].get("summary", {}) if mood_entries else {}
    style = profile.get("response_style", "balanced")
    training_completed = profile.get("training_completed", 0)
    learning_quota = profile.get("learning_quota", 100)
    snapshot = {
        "mood": latest_mood,
        "mood_summary": latest_summary,
        "response_style": style,
        "training_completed": training_completed,
        "learning_quota": learning_quota,
        "training_mode": profile.get("training_mode", "continuous"),
        "confidence": round(0.75 + (latest_summary.get("urgency", 0) * 0.04) + (latest_summary.get("confidence", 0) * 0.02), 2),
    }
    write_profile_status(profile)
    return snapshot


def display_profile():
    profile = load_profile()
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════╗{C_RESET}")
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

    theme_prefs = profile.get("theme_preferences", {})
    current_theme = theme_prefs.get("current_theme", "matrix")
    print(f"  {C_WHITE}{C_BOLD}AUTOMATIC THEME PROFILE:{C_RESET}")
    print(f"   • Active Theme:      {C_GREEN}{current_theme}{C_RESET}")
    print(f"   • Auto Theme:        {C_CYAN}{theme_prefs.get('auto_theme_enabled', True)}{C_RESET}")
    print(f"   • Recent Themes:     {C_YELLOW}{', '.join(theme_prefs.get('recent_themes', ['matrix']))}{C_RESET}")
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
