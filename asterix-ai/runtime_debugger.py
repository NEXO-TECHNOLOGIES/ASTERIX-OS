#!/usr/bin/env python3
"""
ASTERIX OS — Runtime Debugger & Crash Interceptor (ax debug)
Features:
  - Runs any command under subprocess monitoring
  - Intercepts Python tracebacks, Rust panics, C segfaults, Node.js errors, Go panics, Shell errors
  - Correlates crash with source lines when available
  - AI-guided root cause analysis + patch proposal from ASTERIX rule base
  - Outputs structured crash report + actionable fix hint
Zero external dependencies — 100% Python standard library.
"""

import sys
import os
import re
import subprocess
import time
import json
import shlex
from pathlib import Path
from datetime import datetime

# UTF-8 safety on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── ANSI Colors ────────────────────────────────────────────────────────────────
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE   = "\033[38;5;231m"
C_GRAY    = "\033[38;5;244m"
C_BLUE    = "\033[38;5;45m"
C_ORANGE  = "\033[38;5;208m"

BANNER = f"""{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║{C_WHITE}{C_BOLD}        [ ASTERIX RUNTIME DEBUGGER // CRASH INTERCEPTOR v2.0 ]          {C_RESET}{C_CYAN}║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

SEP  = f"{C_BLUE}{'─'*74}{C_RESET}"
SEP2 = f"{C_CYAN}{'═'*74}{C_RESET}"

# ── Known crash signatures ─────────────────────────────────────────────────────
def _extract_python_tb(output):
    """Parse Python traceback: get error type, message, file, line."""
    lines = output.splitlines()
    result = {"type": "RuntimeError", "detail": "", "file": None, "line": None, "hint": ""}
    for i, ln in enumerate(lines):
        file_match = re.search(r'File "(.+?)", line (\d+)', ln)
        if file_match:
            result["file"] = file_match.group(1)
            result["line"] = int(file_match.group(2))
        err_match = re.match(r"^(\w+(?:Error|Exception|Warning|Fault|Interrupt)):\s*(.*)", ln)
        if err_match:
            result["type"] = err_match.group(1)
            result["detail"] = err_match.group(2)
            break
    return result

def _extract_python_syntax(output):
    result = {"type": "SyntaxError", "detail": "", "file": None, "line": None}
    m = re.search(r'File "(.+?)", line (\d+)', output)
    if m:
        result["file"] = m.group(1)
        result["line"] = int(m.group(2))
    d = re.search(r"SyntaxError: (.+)", output)
    if d:
        result["detail"] = d.group(1)
    return result

def _extract_rust_panic(output):
    result = {"type": "Rust Panic", "detail": "", "file": None, "line": None}
    m = re.search(r"panicked at '(.+?)', (.+):(\d+)", output)
    if m:
        result["detail"] = m.group(1)
        result["file"] = m.group(2)
        result["line"] = int(m.group(3))
    return result

def _extract_node_error(output):
    result = {"type": "JavaScript Error", "detail": "", "file": None, "line": None}
    m = re.match(r"(TypeError|ReferenceError|SyntaxError|RangeError): (.+)", output)
    if m:
        result["type"] = m.group(1)
        result["detail"] = m.group(2)
    at_m = re.search(r"at .+ \((.+):(\d+):\d+\)", output)
    if at_m:
        result["file"] = at_m.group(1)
        result["line"] = int(at_m.group(2))
    return result

def _extract_go_panic(output):
    result = {"type": "Go Panic", "detail": "", "file": None, "line": None}
    m = re.search(r"panic: (.+)", output)
    if m:
        result["detail"] = m.group(1)
    fm = re.search(r"\t(.+\.go):(\d+)", output)
    if fm:
        result["file"] = fm.group(1)
        result["line"] = int(fm.group(2))
    return result

CRASH_PATTERNS = [
    {
        "lang": "Python",
        "pattern": re.compile(r"Traceback \(most recent call last\):", re.M),
        "extract": _extract_python_tb,
    },
    {
        "lang": "Python/SyntaxError",
        "pattern": re.compile(r"SyntaxError:", re.M),
        "extract": _extract_python_syntax,
    },
    {
        "lang": "Rust",
        "pattern": re.compile(r"thread '.*' panicked at", re.M),
        "extract": _extract_rust_panic,
    },
    {
        "lang": "C/C++",
        "pattern": re.compile(r"Segmentation fault|signal 11|SIGSEGV|Aborted", re.M),
        "extract": lambda out: {"type": "Segmentation Fault / SIGSEGV", "detail": out[:800]},
    },
    {
        "lang": "Node.js",
        "pattern": re.compile(r"(TypeError|ReferenceError|SyntaxError|RangeError):.*\n.*at ", re.M),
        "extract": _extract_node_error,
    },
    {
        "lang": "Bash",
        "pattern": re.compile(r"command not found|No such file or directory|Permission denied|syntax error near unexpected token", re.M),
        "extract": lambda out: {"type": "Shell Error", "detail": out[:800]},
    },
    {
        "lang": "Go",
        "pattern": re.compile(r"goroutine \d+ \[running\]:", re.M),
        "extract": _extract_go_panic,
    },
]

# ── AI Fix Hints ───────────────────────────────────────────────────────────────
FIX_HINTS = {
    "NameError":           "Variable used before assignment. Check spelling and scope.",
    "TypeError":           "Wrong type passed to function. Inspect argument types with type().",
    "IndexError":          "List/array index out of range. Add bounds check before access.",
    "KeyError":            "Dict key missing. Use dict.get(key, default) or check 'key in dict'.",
    "AttributeError":      "Object doesn't have that attribute. Check object type or spelling.",
    "ImportError":         "Module not found. Run: pip install <module> or check PYTHONPATH.",
    "ModuleNotFoundError": "Module missing. Install via pip or verify virtual environment.",
    "ZeroDivisionError":   "Division by zero. Guard with 'if denominator != 0'.",
    "FileNotFoundError":   "File path does not exist. Verify the path with os.path.exists().",
    "PermissionError":     "Access denied. Run with elevated privileges or fix file permissions.",
    "RecursionError":      "Infinite recursion. Add a base case or increase sys.setrecursionlimit.",
    "MemoryError":         "Out of memory. Profile memory usage; reduce data size or use generators.",
    "SyntaxError":         "Invalid Python syntax. Use 'ax -fix <file>' to auto-repair.",
    "Rust Panic":          "Rust panic usually means unwrap() on None/Err. Use match or if let.",
    "Segmentation Fault":  "Null pointer / out-of-bounds memory access. Enable AddressSanitizer (-fsanitize=address).",
    "JavaScript Error":    "Check variable declarations and null checks. Use strict mode ('use strict').",
    "Go Panic":            "Nil pointer or slice out-of-bounds. Add nil checks and len guards.",
    "Shell Error":         "Check command path with 'which <cmd>' and verify file permissions.",
}

def get_ai_hint(crash_type, detail):
    """Try to match crash type to an actionable hint."""
    for key, hint in FIX_HINTS.items():
        if key.lower() in crash_type.lower() or key.lower() in detail.lower():
            return hint
    return "Review the stack trace above and cross-reference with ASTERIX knowledge base: ax ai ask \"how to fix " + crash_type + "\""

def get_source_context(filepath, line_no, context=3):
    """Extract source lines around the crash point."""
    try:
        path = Path(filepath)
        if not path.exists():
            return None
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        start = max(0, line_no - context - 1)
        end   = min(len(lines), line_no + context)
        snippet = []
        for idx in range(start, end):
            marker = ">>>" if idx == line_no - 1 else "   "
            snippet.append(f"  {marker} {idx+1:4d} | {lines[idx]}")
        return "\n".join(snippet)
    except Exception:
        return None

def analyze_crash(stdout_text, stderr_text, exit_code, elapsed):
    """Identify crash type and extract structured info from combined output."""
    combined = (stderr_text + "\n" + stdout_text).strip()
    for sig in CRASH_PATTERNS:
        if sig["pattern"].search(combined):
            info = sig["extract"](combined)
            info["lang"] = sig["lang"]
            return info
    # Generic non-zero exit
    if exit_code != 0:
        return {
            "lang": "Unknown",
            "type": f"Non-zero exit (code {exit_code})",
            "detail": combined[:500] if combined else "No output captured.",
            "file": None,
            "line": None,
        }
    return None

def resolve_runner(args):
    if not args:
        return args
    first = args[0]
    if os.path.exists(first) and not os.path.isdir(first):
        ext = os.path.splitext(first)[1].lower()
        if ext == ".py":
            return [sys.executable] + list(args)
        elif ext in (".js", ".mjs"):
            node_path = r"C:\Program Files\nodejs\node.exe" if sys.platform == "win32" and os.path.exists(r"C:\Program Files\nodejs\node.exe") else "node"
            return [node_path] + list(args)
        elif ext == ".sh":
            bash_path = r"C:\Program Files\Git\bin\bash.exe" if sys.platform == "win32" and os.path.exists(r"C:\Program Files\Git\bin\bash.exe") else "bash"
            return [bash_path] + list(args)
    return args

def run_and_debug(command_args):
    """Execute command, capture output, detect crashes, print structured report."""
    print(BANNER)
    resolved_args = resolve_runner(command_args)
    cmd_str = " ".join(resolved_args) if isinstance(resolved_args, list) else resolved_args
    print(f"\n  {C_CYAN}[*] Monitoring:{C_RESET} {C_WHITE}{cmd_str}{C_RESET}")
    print(f"  {C_CYAN}[*] Started:   {C_RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP)

    t_start = time.perf_counter()
    try:
        proc = subprocess.run(
            resolved_args if isinstance(resolved_args, list) else shlex.split(cmd_str),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        elapsed = time.perf_counter() - t_start
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        exit_code = proc.returncode

    except subprocess.TimeoutExpired:
        print(f"\n  {C_RED}[TIMEOUT]{C_RESET} Command exceeded 120 s limit. Killed.")
        return
    except FileNotFoundError as e:
        print(f"\n  {C_RED}[ERROR]{C_RESET} Command not found: {e}")
        return
    except Exception as e:
        print(f"\n  {C_RED}[ERROR]{C_RESET} Execution failed: {e}")
        return

    # Print live output
    if stdout.strip():
        print(f"\n  {C_GRAY}── STDOUT ──{C_RESET}")
        for ln in stdout.splitlines()[:60]:
            print(f"  {C_WHITE}{ln}{C_RESET}")
        if len(stdout.splitlines()) > 60:
            print(f"  {C_GRAY}  ... (truncated — {len(stdout.splitlines())} lines total){C_RESET}")

    if stderr.strip():
        print(f"\n  {C_YELLOW}── STDERR ──{C_RESET}")
        for ln in stderr.splitlines()[:60]:
            print(f"  {C_YELLOW}{ln}{C_RESET}")

    print(SEP)
    status_col = C_GREEN if exit_code == 0 else C_RED
    print(f"  {C_CYAN}[*] Exit Code:{C_RESET} {status_col}{exit_code}{C_RESET}  |  "
          f"{C_CYAN}Elapsed:{C_RESET} {elapsed:.3f}s")

    # ── Crash Analysis ──
    crash = analyze_crash(stdout, stderr, exit_code, elapsed)
    if crash is None:
        print(f"\n  {C_GREEN}[✓] No crash detected. Command exited cleanly.{C_RESET}\n")
        return

    print(f"\n{SEP2}")
    print(f"  {C_RED}{C_BOLD}[!] CRASH DETECTED — {crash.get('lang','?')} // {crash.get('type','?')}{C_RESET}")
    print(SEP2)

    if crash.get("detail"):
        print(f"\n  {C_MAGENTA}Error Message:{C_RESET}")
        print(f"    {C_WHITE}{crash['detail'][:300]}{C_RESET}")

    if crash.get("file") and crash.get("line"):
        print(f"\n  {C_MAGENTA}Crash Location:{C_RESET}")
        print(f"    File : {C_YELLOW}{crash['file']}{C_RESET}")
        print(f"    Line : {C_YELLOW}{crash['line']}{C_RESET}")
        ctx = get_source_context(crash["file"], crash["line"])
        if ctx:
            print(f"\n  {C_CYAN}Source Context:{C_RESET}")
            print(ctx)

    hint = get_ai_hint(crash.get("type",""), crash.get("detail",""))
    print(f"\n  {C_GREEN}[AI FIX HINT]{C_RESET}")
    print(f"    {C_WHITE}{hint}{C_RESET}")

    if str(crash.get("lang", "")).startswith("Python") and crash.get("file"):
        print(f"\n  {C_CYAN}[TIP]{C_RESET} Run auto-repair: {C_YELLOW}ax -fix {crash['file']}{C_RESET}")

    # ── Save crash report ──
    vault = Path.home() / ".asterix_vault" / "crash_reports"
    vault.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = vault / f"crash_{ts}.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "command":   cmd_str,
        "exit_code": exit_code,
        "elapsed_s": round(elapsed, 4),
        "crash":     crash,
        "hint":      hint,
        "stdout":    stdout[:2000],
        "stderr":    stderr[:2000],
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  {C_GRAY}[*] Crash report saved → {report_path}{C_RESET}")
    print()

def main():
    if len(sys.argv) < 2:
        print(BANNER)
        print(f"\n  {C_YELLOW}Usage:{C_RESET}  ax debug <command> [args...]")
        print(f"  Example: ax debug python3 myscript.py")
        print(f"  Example: ax debug ./my_binary --input data.txt\n")
        sys.exit(1)

    run_and_debug(sys.argv[1:])

if __name__ == "__main__":
    main()
