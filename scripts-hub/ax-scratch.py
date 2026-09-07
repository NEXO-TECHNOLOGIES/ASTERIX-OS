#!/usr/bin/env python3
"""
ASTERIX OS — Developer Scratchpad Studio & Live Hot-Reload Playground (ax scratch)
Features:
  - Instant zero-friction scratchpad creation for Rust, Python, C, Go, Bash, Node.js
  - Automatic template generation with benchmarks & idiomatic scaffolding
  - Live File-Watcher loop (--watch) for automatic compile & hot-reload execution
  - Benchmark performance timer on every execution
  - Multi-language toolchain auto-discovery (rustc, gcc/clang, go, node, python, bash)
Zero external dependencies — 100% Python standard library.
"""

import sys
import os
import time
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# UTF-8 safety on Windows consoles
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

BANNER = f"""{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║{C_WHITE}{C_BOLD}    [ ASTERIX DEVELOPER SCRATCHPAD STUDIO // HOT-RELOAD PLAYGROUND ]     {C_RESET}{C_CYAN}║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

SEP = f"{C_BLUE}{'─'*74}{C_RESET}"

TEMPLATES = {
    "python": {
        "ext": ".py",
        "name": "Python 3",
        "file": "scratch.py",
        "code": """#!/usr/bin/env python3
# ASTERIX OS — Python Rapid Scratchpad
import sys
import time

def main():
    t0 = time.perf_counter()
    print("[*] ASTERIX Scratchpad Running (Python)")
    
    # ── Write rapid prototype code here ──
    data = [x**2 for x in range(1000)]
    print(f"[+] Processed {len(data)} elements. Max = {max(data)}")

    elapsed = (time.perf_counter() - t0) * 1000
    print(f"[*] Execution time: {elapsed:.3f} ms")

if __name__ == "__main__":
    main()
""",
    },
    "rust": {
        "ext": ".rs",
        "name": "Rust",
        "file": "scratch.rs",
        "code": """// ASTERIX OS — Rust Rapid Scratchpad
use std::time::Instant;

fn main() {
    let t0 = Instant::now();
    println!("[*] ASTERIX Scratchpad Running (Rust)");

    // ── Write rapid prototype code here ──
    let numbers: Vec<u64> = (1..=10_000).collect();
    let sum: u64 = numbers.iter().sum();
    println!("[+] Computed sum of 10,000 numbers: {}", sum);

    let elapsed = t0.elapsed();
    println!("[*] Execution time: {:?}", elapsed);
}
""",
    },
    "c": {
        "ext": ".c",
        "name": "C99/C11",
        "file": "scratch.c",
        "code": """// ASTERIX OS — C Rapid Scratchpad
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main(void) {
    clock_t start = clock();
    printf("[*] ASTERIX Scratchpad Running (C)\\n");

    // ── Write rapid prototype code here ──
    long long total = 0;
    for (long long i = 1; i <= 100000; i++) {
        total += i;
    }
    printf("[+] Sum 1..100000 = %lld\\n", total);

    double elapsed_ms = (double)(clock() - start) * 1000.0 / CLOCKS_PER_SEC;
    printf("[*] Execution time: %.3f ms\\n", elapsed_ms);
    return 0;
}
""",
    },
    "go": {
        "ext": ".go",
        "name": "Go",
        "file": "scratch.go",
        "code": """// ASTERIX OS — Go Rapid Scratchpad
package main

import (
	"fmt"
	"time"
)

func main() {
	start := time.Now()
	fmt.Println("[*] ASTERIX Scratchpad Running (Go)")

	// ── Write rapid prototype code here ──
	sum := 0
	for i := 1; i <= 10000; i++ {
		sum += i
	}
	fmt.Printf("[+] Computed sum: %d\\n", sum)

	fmt.Printf("[*] Execution time: %v\\n", time.Since(start))
}
""",
    },
    "bash": {
        "ext": ".sh",
        "name": "Bash Shell",
        "file": "scratch.sh",
        "code": """#!/usr/bin/env bash
# ASTERIX OS — Bash Rapid Scratchpad
set -euo pipefail

start_ns=$(date +%s%N 2>/dev/null || echo 0)
echo "[*] ASTERIX Scratchpad Running (Bash)"

# ── Write rapid prototype script here ──
echo "[+] Kernel: $(uname -srm 2>/dev/null || echo 'Unknown')"
echo "[+] User:   $USER"
echo "[+] Host:   $HOSTNAME"

if [ "$start_ns" -ne 0 ]; then
    end_ns=$(date +%s%N 2>/dev/null || echo 0)
    ms=$(( (end_ns - start_ns) / 1000000 ))
    echo "[*] Execution time: ~${ms} ms"
fi
""",
    },
    "javascript": {
        "ext": ".js",
        "name": "Node.js / JavaScript",
        "file": "scratch.js",
        "code": """// ASTERIX OS — Node.js Rapid Scratchpad
const { performance } = require('perf_hooks');

async function main() {
    const t0 = performance.now();
    console.log("[*] ASTERIX Scratchpad Running (Node.js)");

    // ── Write rapid prototype code here ──
    const items = Array.from({ length: 5000 }, (_, i) => i * 2);
    console.log(`[+] Array of ${items.length} items ready.`);

    const elapsed = (performance.now() - t0).toFixed(3);
    console.log(`[*] Execution time: ${elapsed} ms`);
}

main();
""",
    },
}

ALIAS_MAP = {
    "py": "python",
    "python": "python",
    "python3": "python",
    "rs": "rust",
    "rust": "rust",
    "c": "c",
    "cpp": "c",
    "go": "go",
    "golang": "go",
    "sh": "bash",
    "bash": "bash",
    "shell": "bash",
    "js": "javascript",
    "javascript": "javascript",
    "node": "javascript",
}

def find_compiler_runner(lang: str, scratch_file: Path):
    """Determine the command line to compile and/or run the file."""
    if lang == "python":
        py_candidates = [
            r"C:\Users\Baha\.local\bin\python3.14.exe",
            shutil.which("python3"),
            shutil.which("python"),
            sys.executable,
        ]
        chosen = next((p for p in py_candidates if p and os.path.exists(p)), sys.executable)
        return [chosen, str(scratch_file)]

    elif lang == "rust":
        rustc_candidates = [
            r"C:\Users\Baha\.cargo\bin\rustc.exe",
            shutil.which("rustc"),
        ]
        rustc = next((p for p in rustc_candidates if p and os.path.exists(p)), None)
        if not rustc:
            return None
        out_bin = scratch_file.with_suffix(".exe" if sys.platform == "win32" else "")
        return {
            "compile": [rustc, "-O", str(scratch_file), "-o", str(out_bin)],
            "run": [str(out_bin)],
        }

    elif lang == "c":
        cc = shutil.which("gcc") or shutil.which("clang") or shutil.which("cl")
        if not cc:
            return None
        out_bin = scratch_file.with_suffix(".exe" if sys.platform == "win32" else "")
        return {
            "compile": [cc, "-O2", str(scratch_file), "-o", str(out_bin)],
            "run": [str(out_bin)],
        }

    elif lang == "go":
        go = shutil.which("go")
        if not go:
            return None
        return [go, "run", str(scratch_file)]

    elif lang == "javascript":
        node_candidates = [
            r"C:\Program Files\nodejs\node.exe",
            shutil.which("node"),
        ]
        node = next((p for p in node_candidates if p and os.path.exists(p)), None)
        if not node:
            return None
        return [node, str(scratch_file)]

    elif lang == "bash":
        bash_candidates = [
            r"C:\Program Files\Git\bin\bash.exe",
            shutil.which("bash"),
        ]
        bash = next((p for p in bash_candidates if p and os.path.exists(p)), None)
        if not bash:
            return None
        return [bash, str(scratch_file)]

    return None

def execute_scratchpad(lang: str, scratch_file: Path):
    """Compile (if needed) and execute scratch file, streaming output with timing."""
    runner = find_compiler_runner(lang, scratch_file)
    if not runner:
        print(f"  {C_RED}[!] No toolchain / runtime found for '{lang}'. Please install its compiler or interpreter.{C_RESET}")
        return False

    print(f"\n{SEP}")
    print(f"  {C_CYAN}[RUN]{C_RESET} {C_WHITE}{scratch_file.name}{C_RESET} ({TEMPLATES[lang]['name']})")
    print(SEP)

    t0 = time.perf_counter()

    # Two-step compile + run
    if isinstance(runner, dict):
        # Compile
        comp_res = subprocess.run(runner["compile"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if comp_res.returncode != 0:
            print(f"  {C_RED}[COMPILE ERROR]{C_RESET}")
            for ln in comp_res.stderr.splitlines():
                print(f"    {C_RED}{ln}{C_RESET}")
            return False
        run_cmd = runner["run"]
    else:
        run_cmd = runner

    # Run
    run_res = subprocess.run(run_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    elapsed = time.perf_counter() - t0

    if run_res.stdout:
        for ln in run_res.stdout.splitlines():
            print(f"  {C_WHITE}{ln}{C_RESET}")

    if run_res.stderr:
        print(f"  {C_YELLOW}── STDERR ──{C_RESET}")
        for ln in run_res.stderr.splitlines():
            print(f"  {C_YELLOW}{ln}{C_RESET}")

    col = C_GREEN if run_res.returncode == 0 else C_RED
    print(SEP)
    print(f"  {C_CYAN}[*] Status:{C_RESET} {col}Exit code {run_res.returncode}{C_RESET}  |  "
          f"{C_CYAN}Total Wall Time:{C_RESET} {elapsed*1000:.2f} ms\n")
    return run_res.returncode == 0

def watch_scratchpad(lang: str, scratch_file: Path):
    """Hot-reload watcher loop."""
    print(f"  {C_MAGENTA}{C_BOLD}[*] HOT-RELOAD ACTIVE:{C_RESET} Watching {C_WHITE}{scratch_file}{C_RESET}")
    print(f"  {C_GRAY}    Save the file in your editor to automatically re-compile and re-run.{C_RESET}")
    print(f"  {C_GRAY}    Press Ctrl+C to exit scratch studio.{C_RESET}\n")

    last_mtime = scratch_file.stat().st_mtime
    execute_scratchpad(lang, scratch_file)

    try:
        while True:
            time.sleep(0.5)
            if not scratch_file.exists():
                continue
            current_mtime = scratch_file.stat().st_mtime
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                print(f"\n  {C_YELLOW}[⚡ CHANGE DETECTED] Reloading...{C_RESET}")
                execute_scratchpad(lang, scratch_file)
    except KeyboardInterrupt:
        print(f"\n  {C_CYAN}[*] Scratchpad studio closed.{C_RESET}\n")

def list_scratchpads():
    scratch_root = Path.home() / ".asterix_vault" / "scratch"
    print(BANNER)
    print(f"\n  {C_CYAN}[*] Active Scratchpads in ~/.asterix_vault/scratch/:{C_RESET}\n")
    if not scratch_root.exists():
        print(f"  {C_GRAY}No scratchpads created yet. Run: ax scratch <lang>{C_RESET}\n")
        return
    count = 0
    for child in scratch_root.iterdir():
        if child.is_dir():
            files = list(child.iterdir())
            if files:
                count += 1
                print(f"  • {C_GREEN}{child.name.upper():<12}{C_RESET} → {C_WHITE}{child}{C_RESET}")
                for f in files:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    print(f"      └── {f.name} ({f.stat().st_size} bytes, modified {mtime})")
    if count == 0:
        print(f"  {C_GRAY}No scratchpads found.{C_RESET}")
    print()

def main():
    print(BANNER)
    args = sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(f"\n  {C_YELLOW}Usage:{C_RESET}")
        print(f"    ax scratch <lang>           Create and run scratchpad (python, rust, c, go, bash, js)")
        print(f"    ax scratch <lang> --watch   Start hot-reload watcher (re-runs on file save)")
        print(f"    ax scratch --list           List all existing scratchpads")
        print(f"\n  {C_CYAN}Supported Languages:{C_RESET} python, rust, c, go, bash, javascript\n")
        sys.exit(0)

    if args[0] in ("--list", "-l", "list"):
        list_scratchpads()
        sys.exit(0)

    lang_raw = args[0].lower().lstrip("-")
    lang = ALIAS_MAP.get(lang_raw)
    if not lang:
        print(f"\n  {C_RED}[!] Unsupported language '{args[0]}'.{C_RESET}")
        print(f"  Supported: {', '.join(TEMPLATES.keys())}\n")
        sys.exit(1)

    watch_mode = any(a in ("--watch", "-w", "watch") for a in args[1:])

    # Setup scratchpad path in ~/.asterix_vault/scratch/<lang>/
    vault = Path.home() / ".asterix_vault" / "scratch" / lang
    vault.mkdir(parents=True, exist_ok=True)
    tmpl = TEMPLATES[lang]
    scratch_file = vault / tmpl["file"]

    # Write template if doesn't exist
    if not scratch_file.exists():
        scratch_file.write_text(tmpl["code"], encoding="utf-8")
        print(f"\n  {C_GREEN}[+] Created new {tmpl['name']} scratchpad:{C_RESET} {C_WHITE}{scratch_file}{C_RESET}")
    else:
        print(f"\n  {C_CYAN}[*] Loaded existing {tmpl['name']} scratchpad:{C_RESET} {C_WHITE}{scratch_file}{C_RESET}")

    if watch_mode:
        watch_scratchpad(lang, scratch_file)
    else:
        execute_scratchpad(lang, scratch_file)
        print(f"  {C_GRAY}Tip: Run with {C_YELLOW}ax scratch {lang} --watch{C_GRAY} for live hot-reload on save!{C_RESET}\n")

if __name__ == "__main__":
    main()
