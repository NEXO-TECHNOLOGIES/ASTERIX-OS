#!/usr/bin/env python3
"""
ASTERIX AI brain.

This module connects to a local Ollama server and asks the model for the
best next bash command. It deliberately avoids cloud APIs and keeps the
logic minimal enough to run on a low-memory phone.
"""

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

OLLAMA_URL = os.getenv("ASTERIX_OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("ASTERIX_OLLAMA_MODEL", "qwen2.5:3b-instruct")
AI_NAME = os.getenv("ASTERIX_AI_NAME", "ASTERIX AI")
SAFE_DEFAULT = f"echo '{AI_NAME} offline; no action taken'"
DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -r /",
    "dd if=",
    "mkfs",
    "fdisk",
    "parted",
    "shutdown",
    "reboot",
    "poweroff",
    "> /dev/",
    "/dev/sda",
    "chmod 777 /",
    "chown root",
    "sudo rm",
    "curl .*| bash",
    "wget .*| bash",
    "bash -c \"curl",
    "pkill -9",
    "kill -9 -1",
]


def _post_json(url: str, payload: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    """Send JSON to Ollama and read the raw response."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _strip_command(raw: str) -> str:
    """Normalize a command string returned by the model."""
    if not raw:
        return SAFE_DEFAULT

    cleaned = raw.strip()
    cleaned = cleaned.replace("```bash", "").replace("```", "")
    cleaned = cleaned.replace("```", "")
    cleaned = cleaned.strip()

    # Remove common assistant wrappers like "Command: ..."
    cleaned = re.sub(r"^(command|Command)\s*:\s*", "", cleaned, count=1)

    # Keep only the first logical line so we don't return extra explanatory text.
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if not lines:
        return SAFE_DEFAULT

    candidate = lines[0]
    candidate = candidate.strip("'\"")
    return candidate or SAFE_DEFAULT


def _is_dangerous(command: str) -> bool:
    """Block destructive or security-risky commands from being executed."""
    lower = command.lower()
    return any(pattern in lower for pattern in DANGEROUS_PATTERNS) or any(
        token in lower for token in [
            "rm -rf",
            "rm -r /",
            "dd if=",
            "mkfs",
            "fdisk",
            "parted",
            "shutdown",
            "reboot",
            "poweroff",
            "> /dev/",
            "/dev/sda",
            "chmod 777 /",
            "passwd",
            "chattr +i",
            "iptables -f",
            "ufw disable",
        ]
    )


def _fallback_command() -> str:
    """Safe, minimal fallback if the model or server is unavailable."""
    return f"echo '{AI_NAME} offline; no action taken'"


def build_security_summary(system_state: Dict[str, Any], memory_log: str) -> Dict[str, Any]:
    """Convert the system snapshot into a lightweight security posture summary."""
    issues = []
    cpu_value = system_state.get("cpu", "unknown")
    ram_value = system_state.get("ram", "unknown")
    battery_value = system_state.get("battery", "unknown")
    network_value = system_state.get("network", "unknown")

    try:
        cpu_num = float(str(cpu_value).replace("%", ""))
        if cpu_num > 85:
            issues.append("CPU saturation")
    except Exception:
        pass

    try:
        ram_num = float(str(ram_value).replace("%", ""))
        if ram_num > 85:
            issues.append("memory pressure")
    except Exception:
        pass

    try:
        battery_num = float(str(battery_value).replace("%", ""))
        if battery_num < 25:
            issues.append("battery critical")
    except Exception:
        pass

    if str(network_value).lower() == "offline":
        issues.append("network unavailable")

    if memory_log:
        lower_log = memory_log.lower()
        if any(token in lower_log for token in ["fail", "error", "attack", "suspicious", "unauthorized"]):
            issues.append("recent anomalies in memory")

    risk = "LOW"
    if len(issues) >= 3:
        risk = "HIGH"
    elif len(issues) == 2:
        risk = "MEDIUM"

    return {
        "risk_level": risk,
        "issues": issues,
        "cpu": cpu_value,
        "ram": ram_value,
        "battery": battery_value,
        "network": network_value,
    }


def _build_prompt(system_state: Dict[str, Any], memory_log: str) -> str:
    """Build the exact prompt that tells Ollama what decision is needed."""
    state_text = json.dumps(system_state, sort_keys=True, ensure_ascii=False)
    memory_text = memory_log.strip()[-2000:] if memory_log else "No memory yet."
    security = build_security_summary(system_state, memory_log)
    issues_text = ", ".join(security["issues"]) if security["issues"] else "no major issues"
    return (
        "You are ASTERIX OS security AI. Based on the system state, security posture, and memory, "
        "what 1 bash command should I run to protect or stabilize the machine? Only return the command.\n"
        f"risk_level: {security['risk_level']}\n"
        f"security_issues: {issues_text}\n"
        f"System state: {state_text}\n"
        f"Memory: {memory_text}"
    )


def suggest_action(system_state: Dict[str, Any], memory_log: str) -> str:
    """Ask Ollama for the single best bash command and sanitize the reply."""
    prompt = _build_prompt(system_state, memory_log)

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 64,
            },
        }

        result = _post_json(f"{OLLAMA_URL}/api/generate", payload, timeout=20)
        raw_text = result.get("response", "")
        command = _strip_command(raw_text)

        if not command or _is_dangerous(command):
            return _fallback_command()

        return command

    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return _fallback_command()


def security_scan(system_state: Dict[str, Any], memory_log: str) -> Dict[str, Any]:
    """Return a security posture summary for ASTERIX dashboards and audits."""
    summary = build_security_summary(system_state, memory_log)
    summary["safe_default"] = SAFE_DEFAULT
    return summary


def suggest_fix(code: str, error_message: str = "", language: str = "python") -> str:
    """Ask Ollama for a code fix, or fall back to the local ASTERIX code healer."""
    prompt = (
        "You are ASTERIX OS AI. Fix this code with the smallest possible safe change. "
        "Return only the corrected code. Do not explain.\n"
        f"Language: {language}\n"
        f"Error: {error_message or 'No explicit error given'}\n\n"
        f"Code:\n{code[:8000]}"
    )

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 512,
            },
        }
        result = _post_json(f"{OLLAMA_URL}/api/generate", payload, timeout=25)
        candidate = result.get("response", "").strip()
        if not candidate:
            raise ValueError("empty repair response")

        cleaned = candidate.replace("```python", "").replace("```", "").strip()
        if cleaned:
            return cleaned
        raise ValueError("repair response missing code")
    except Exception:
        try:
            from code_healer import heal_code
            healed, _, _ = heal_code(code, forced_lang=language)
            return healed
        except Exception:
            return code


def learning_mode(memory_log_path: str = "memory.log", output_path: str = "suggested_rules.txt") -> str:
    """Read memory.log and ask Ollama to produce 3 simple IF/THEN rules."""
    try:
        with open(memory_log_path, "r", encoding="utf-8", errors="ignore") as handle:
            memory_lines = handle.read().strip()
    except FileNotFoundError:
        memory_lines = "No memory log found yet."

    prompt = (
        "You are ASTERIX OS AI. Review this memory log and find the 3 strongest patterns. "
        "Output exactly 3 lines in this format: IF [condition] THEN [action]. "
        "Do not add any explanation.\n"
        f"Memory log:\n{memory_lines[-4000:]}"
    )

    try:
        result = _post_json(
            f"{OLLAMA_URL}/api/generate",
            {"model": MODEL_NAME, "prompt": prompt, "stream": False},
            timeout=25,
        )
        output = result.get("response", "")
        rules = []
        for line in output.splitlines():
            cleaned = line.strip()
            if cleaned.lower().startswith("if ") and " then " in cleaned.lower():
                rules.append(cleaned)
        if len(rules) >= 3:
            final_rules = "\n".join(rules[:3]) + "\n"
        else:
            final_rules = (
                "IF CPU usage is high THEN inspect processes and throttle workloads\n"
                "IF battery is low THEN enable power-saving mode\n"
                "IF network is offline OR memory shows anomalies THEN isolate and audit connectivity\n"
            )
    except Exception:
        final_rules = (
            "IF CPU usage is high THEN inspect processes and throttle workloads\n"
            "IF battery is low THEN enable power-saving mode\n"
            "IF network is offline OR memory shows anomalies THEN isolate and audit connectivity\n"
        )

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write(final_rules)

    return output_path


if __name__ == "__main__":
    sample_state = {
        "cpu": "20%",
        "ram": "30%",
        "battery": "80%",
        "network": "online",
    }
    sample_history = '{"problem": "cpu spike"}'
    print(suggest_action(sample_state, sample_history))
