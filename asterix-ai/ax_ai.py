#!/usr/bin/env python3
"""
ASTERIX OS AI CLI.

This script collects system state, queries the local Ollama model for a command,
prints the command, and asks for confirmation before running anything.
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ai_brain import suggest_action, suggest_fix, security_scan


def get_cpu_usage() -> str:
    """Return a simple CPU status string."""
    try:
        with open("/proc/loadavg", "r", encoding="utf-8") as handle:
            load = handle.read().strip().split()[0]
        return load
    except Exception:
        return "unknown"


def get_ram_usage() -> str:
    """Read RAM usage from /proc/meminfo if available."""
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as handle:
            lines = handle.read().splitlines()
        total = 0
        available = 0
        for line in lines:
            if line.startswith("MemTotal:"):
                total = int(line.split()[1])
            if line.startswith("MemAvailable:"):
                available = int(line.split()[1])
        if total:
            used = (total - available) / total * 100.0
            return f"{used:.1f}%"
    except Exception:
        pass
    return "unknown"


def get_battery_level() -> str:
    """Try to read battery percentage from Android/Linux sysfs."""
    for candidate in [
        "/sys/class/power_supply/*/capacity",
        "/sys/class/power_supply/*/energy_now",
    ]:
        matches = sorted(Path("/sys/class/power_supply").glob("*")) if "/sys/class/power_supply" in candidate else []
        for folder in matches:
            cap_file = folder / "capacity"
            if cap_file.exists():
                try:
                    return (cap_file.read_text(encoding="utf-8", errors="ignore")).strip() + "%"
                except Exception:
                    pass
    return "unknown"


def get_network_status() -> str:
    """Check if the device can reach a known public IP. Lightweight and offline-safe."""
    try:
        socket.setdefaulttimeout(1)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return "online"
    except Exception:
        return "offline"


def load_system_state() -> dict:
    """Collect the data the model uses to decide on the best command."""
    return {
        "cpu": get_cpu_usage(),
        "ram": get_ram_usage(),
        "battery": get_battery_level(),
        "network": get_network_status(),
    }


def load_recent_memory(path: str = "memory.log", lines: int = 50) -> str:
    """Read the last N lines of the memory log."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            log_data = handle.read().splitlines()
        return "\n".join(log_data[-lines:])
    except FileNotFoundError:
        return "No memory log yet."


def is_safe_command(command: str) -> bool:
    """Reject commands that would be destructive or dangerous."""
    if not command:
        return False

    lower = command.lower()
    blocked = [
        "rm -rf",
        "rm -r /",
        "dd if=",
        "mkfs",
        "fdisk",
        "parted",
        "shutdown",
        "reboot",
        "poweroff",
        ":(){ :|:& };:",
        "chmod 777 /",
        "> /dev/",
        "sudo rm",
        "curl .*| bash",
        "wget .*| bash",
        "kill -9 -1",
        "chown root",
        "iptables -f",
    ]
    return not any(token in lower for token in blocked)


def run_command(command: str) -> int:
    """Run a safe command via bash."""
    if not is_safe_command(command):
        print("[!] Refusing to run a dangerous command.")
        return 1

    try:
        completed = subprocess.run(["bash", "-lc", command], capture_output=False, text=True)
        return completed.returncode
    except FileNotFoundError:
        print("[!] bash not found. Please run this on a Unix-like system or Termux.")
        return 1


def fix_code_file(file_path: str) -> int:
    """Use the local AI to repair a code file and optionally apply the patch."""
    path = Path(file_path)
    if not path.exists():
        print(f"[!] File not found: {file_path}")
        return 1

    try:
        original = path.read_text(encoding="utf-8")
    except Exception:
        try:
            original = path.read_text(encoding="latin-1")
        except Exception:
            print("[!] Could not read file for repair.")
            return 1

    language = "python" if path.suffix.lower() == ".py" else "c"

    # Try a quick syntax sanity check first for Python files.
    error_message = ""
    if path.suffix.lower() == ".py":
        try:
            compile(original, str(path), "exec")
            print("[i] Python syntax looks valid; AI will still check for a safer fix if needed.")
        except SyntaxError as exc:
            error_message = f"SyntaxError: {exc.msg} at line {exc.lineno}"

    fixed = suggest_fix(original, error_message, language)
    print("\nASTERIX AI code repair preview:")
    print(fixed)

    answer = input("Apply this fix? [y/N]: ").strip().lower()
    if answer in {"y", "yes"}:
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            backup.write_text(original, encoding="utf-8")
        path.write_text(fixed, encoding="utf-8")
        print(f"[+] Applied fix and backed up original to {backup}")
        return 0

    print("[!] Fix not applied.")
    return 0


try:
    from peak_brain import peak_ai
    from cloud_memory import memory_hub
except ImportError:
    try:
        from .peak_brain import peak_ai
        from .cloud_memory import memory_hub
    except ImportError:
        peak_ai = None
        memory_hub = None


def interactive_chat():
    """Starts an interactive cybernetic conversational session with Asterix Peak AI."""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║   [ASTERIX] ASTERIX AI // PEAK CONVERSATIONAL COGNITIVE CONSOLE v3.5        ║")
    print("║   [ Cloud & Vector Memory Active • Type 'exit' or 'quit' to close ]  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    if memory_hub:
        stats = memory_hub.get_stats()
        print(f"  • Cognitive Memories: {stats['total_memories']} ({stats['synced_to_cloud']} synced to Supabase/Cloud)")
        print(f"  • Cloud Connection:   {'Connected' if stats['cloud_connected'] else 'Local Offline Cache'}\n")

    while True:
        try:
            prompt = input("asterix-ai  ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

        if not prompt:
            continue
        if prompt.lower() in {"exit", "quit", "q", ":q"}:
            print("Disconnecting cognitive console.")
            break

        if peak_ai:
            reply = peak_ai.reason(prompt)
            print(f"\n{reply}\n")
        else:
            print(f"\nASTERIX AI: Ready. Query received: '{prompt}'\n")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="ASTERIX AI Command & Intelligence Hub")
    parser.add_argument("--fix", dest="fix_file", help="Repair a source file with the local AI")
    parser.add_argument("--security", action="store_true", help="Run a security posture scan before suggesting actions")
    parser.add_argument("--chat", action="store_true", help="Launch interactive conversational chat with cognitive memory")
    parser.add_argument("--ask", type=str, help="Inquire Asterix Peak AI on any cyber vector, C/Assembly code or OS topic")
    parser.add_argument("--cloud-sync", action="store_true", help="Synchronize cognitive memory with Supabase or Cloud REST API")
    parser.add_argument("--cloud-setup", nargs=2, metavar=("URL", "KEY"), help="Configure Supabase Cloud Memory (URL KEY)")
    parser.add_argument("--memory", action="store_true", help="Display cognitive memory statistics and recent items")
    args = parser.parse_args()

    if args.cloud_setup:
        url, key = args.cloud_setup
        if memory_hub:
            memory_hub.save_config(url, key)
            print(f"[[OK]] Supabase Cloud Memory configured for {url}")
            return 0

    if args.cloud_sync:
        if memory_hub:
            print("[*] Synchronizing cognitive memory with Supabase Cloud...")
            res = memory_hub.sync_cloud()
            print(f"[[OK]] Cloud Sync Result: {res}")
            return 0

    if args.memory:
        if memory_hub:
            stats = memory_hub.get_stats()
            print("\nASTERIX Cognitive Memory State:")
            for k, v in stats.items():
                print(f"  • {k}: {v}")
            return 0

    if args.chat:
        interactive_chat()
        return 0

    if args.ask:
        if peak_ai:
            ans = peak_ai.reason(args.ask)
            print(f"\n{ans}\n")
            return 0

    if args.fix_file:
        return fix_code_file(args.fix_file)

    system_state = load_system_state()
    memory_log = load_recent_memory("memory.log", 50)

    if args.security:
        scan = security_scan(system_state, memory_log)
        print("\nASTERIX security posture:")
        print(f"Risk level: {scan['risk_level']}")
        print(f"Issues: {', '.join(scan['issues']) if scan['issues'] else 'none'}")

    suggestion = suggest_action(system_state, memory_log)

    print("\nASTERIX AI suggestion:")
    print(suggestion)

    if sys.stdin.isatty():
        try:
            answer = input("Run this? [y/N]: ").strip().lower()
            if answer in {"y", "yes"}:
                print("[+] Executing safe command...")
                return run_command(suggestion)
        except (KeyboardInterrupt, EOFError):
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
