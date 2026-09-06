#!/usr/bin/env python3
"""
ASTERIX OS - Live Auto-Update Daemon v1.0 (F-Droid Style)
Continuously monitors the remote GitHub repository for new commits.
When a new commit is detected, it automatically pulls the latest changes
and applies them to the local installation - exactly like F-Droid.

Zero external dependencies (pure Python 3 standard library).
Runs as a background daemon or one-shot check.
"""

import sys
import os
import json
import time
import subprocess
import urllib.request
import urllib.error
import datetime
import signal

# Color palette
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE   = "\033[38;5;231m"
C_GRAY    = "\033[38;5;244m"

# Config
GITHUB_OWNER  = "NEXO-TECHNOLOGIES"
GITHUB_REPO   = "ASTERIX-OS"
BRANCH        = "main"
POLL_INTERVAL = 60
MAX_RETRIES   = 3
API_TIMEOUT   = 15

STATE_DIR  = os.path.expanduser("~/.asterix_vault/auto-updater")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
LOG_FILE   = os.path.join(STATE_DIR, "update.log")
PID_FILE   = os.path.join(STATE_DIR, "daemon.pid")

GITHUB_COMMITS_URL = (
    f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/commits/{BRANCH}"
)

def banner():
    print(f"\n{C_CYAN}{C_BOLD}" + "=" * 74 + C_RESET)
    print(f"{C_CYAN}{C_BOLD}  [ ASTERIX OS // LIVE AUTO-UPDATER DAEMON v1.0 - F-Droid Style ]{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}" + "=" * 74 + C_RESET + "\n")

def timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def log(msg, level="INFO"):
    entry = f"[{timestamp()}] [{level}] {msg}"
    print(f"  {C_GRAY}{entry}{C_RESET}")
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass

def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"last_known_sha": None, "last_checked": None, "update_count": 0}

def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

def get_local_sha():
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception:
        return ""

def pull_latest():
    try:
        result = subprocess.run(
            ["git", "pull", "origin", BRANCH, "--rebase=false"],
            capture_output=True, text=True, timeout=120
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "git pull timed out"
    except FileNotFoundError:
        return False, "git not found"
    except Exception as e:
        return False, str(e)

def fetch_remote_sha():
    req = urllib.request.Request(
        GITHUB_COMMITS_URL,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"ASTERIX-OS-AutoUpdater/1.0"
        }
    )
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=API_TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("sha", "")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                log(f"Rate-limited (attempt {attempt}) - waiting 30s", "WARN")
                time.sleep(30)
            else:
                log(f"HTTP error {e.code} (attempt {attempt})", "WARN")
                time.sleep(5 * attempt)
        except urllib.error.URLError as e:
            log(f"Network error: {e.reason} (attempt {attempt})", "WARN")
            time.sleep(5 * attempt)
        except Exception as e:
            log(f"Error: {e}", "WARN")
            time.sleep(5 * attempt)
    return None

def check_and_update(state, verbose=True):
    if verbose:
        print(f"  {C_CYAN}[*] Checking remote repository for updates...{C_RESET}")
    remote_sha = fetch_remote_sha()
    state["last_checked"] = timestamp()
    if remote_sha is None:
        log("Could not reach GitHub API - skipping", "WARN")
        save_state(state)
        return state
    local_sha = get_local_sha()
    short_r   = remote_sha[:10] if remote_sha else "unknown"
    short_l   = local_sha[:10]  if local_sha  else "unknown"
    if remote_sha == local_sha:
        if verbose:
            print(f"  {C_GREEN}[OK] Already up-to-date{C_RESET}  {C_GRAY}(local={short_l} | remote={short_r}){C_RESET}\n")
        state["last_known_sha"] = remote_sha
        save_state(state)
        return state
    print(f"\n  {C_MAGENTA}{C_BOLD}[ NEW COMMIT DETECTED - APPLYING UPDATE ]{C_RESET}")
    print(f"  {C_GRAY}Local  SHA: {short_l}{C_RESET}")
    print(f"  {C_CYAN}Remote SHA: {short_r}{C_RESET}\n")
    log(f"New commit: {short_l} -> {short_r}", "UPDATE")
    print(f"  {C_YELLOW}[v] Pulling latest changes from origin/{BRANCH}...{C_RESET}")
    success, output = pull_latest()
    if success:
        new_local = get_local_sha()
        print(f"  {C_GREEN}{C_BOLD}[OK] UPDATE APPLIED SUCCESSFULLY{C_RESET}  {C_GRAY}(HEAD={new_local[:10]}){C_RESET}")
        log(f"Update applied: HEAD={new_local}", "UPDATE")
        state["update_count"] = state.get("update_count", 0) + 1
        state["last_known_sha"] = new_local
    else:
        print(f"  {C_RED}[X] Pull failed!{C_RESET} {C_GRAY}{output}{C_RESET}")
        log(f"Pull failed: {output}", "ERROR")
        state["last_known_sha"] = remote_sha
    print()
    save_state(state)
    return state

_running = True

def _handle_signal(sig, frame):
    global _running
    print(f"\n  {C_YELLOW}[!] Shutting down daemon...{C_RESET}\n")
    _running = False

def write_pid():
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pid():
    try:
        os.remove(PID_FILE)
    except Exception:
        pass

def read_pid():
    try:
        with open(PID_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return None

def cmd_start(interval=POLL_INTERVAL):
    banner()
    pid = read_pid()
    if pid:
        try:
            os.kill(pid, 0)
            print(f"  {C_YELLOW}[!] Daemon already running (PID {pid}).{C_RESET}")
            print(f"  {C_GRAY}Use: ax auto-update stop{C_RESET}\n")
            return
        except (ProcessLookupError, PermissionError):
            remove_pid()
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT,  _handle_signal)
    write_pid()
    state = load_state()
    print(f"  {C_GREEN}{C_BOLD}[ ASTERIX AUTO-UPDATER DAEMON STARTED ]{C_RESET}  "
          f"{C_GRAY}PID={os.getpid()} | interval={interval}s{C_RESET}\n")
    log(f"Daemon started PID={os.getpid()} interval={interval}s", "DAEMON")
    while _running:
        state = check_and_update(state, verbose=True)
        if not _running:
            break
        for _ in range(interval):
            if not _running:
                break
            time.sleep(1)
    remove_pid()
    log("Daemon stopped", "DAEMON")
    print(f"  {C_CYAN}[OK] Auto-update daemon stopped.{C_RESET}\n")

def cmd_stop():
    banner()
    pid = read_pid()
    if not pid:
        print(f"  {C_YELLOW}[!] No daemon PID file found.{C_RESET}\n")
        return
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"  {C_GREEN}[OK] Stop signal sent to daemon PID {pid}.{C_RESET}\n")
        remove_pid()
    except ProcessLookupError:
        print(f"  {C_GRAY}[i] PID {pid} not running - cleaning PID file.{C_RESET}\n")
        remove_pid()
    except PermissionError:
        print(f"  {C_RED}[X] Permission denied - cannot stop PID {pid}.{C_RESET}\n")

def cmd_status():
    banner()
    state = load_state()
    pid   = read_pid()
    print(f"  {C_CYAN}{C_BOLD}[ ASTERIX AUTO-UPDATER STATUS ]{C_RESET}\n")
    alive = False
    if pid:
        try:
            os.kill(pid, 0)
            alive = True
        except Exception:
            pass
    status_str = f"{C_GREEN}RUNNING  PID {pid}{C_RESET}" if alive else f"{C_GRAY}STOPPED{C_RESET}"
    print(f"  Daemon         : {status_str}")
    print(f"  Remote repo    : {C_CYAN}github.com/{GITHUB_OWNER}/{GITHUB_REPO}{C_RESET} ({BRANCH})")
    print(f"  Last checked   : {C_WHITE}{state.get('last_checked', 'Never')}{C_RESET}")
    print(f"  Local HEAD     : {C_WHITE}{get_local_sha()[:14] or 'unknown'}{C_RESET}")
    print(f"  Remote SHA     : {C_WHITE}{(state.get('last_known_sha') or 'unknown')[:14]}{C_RESET}")
    print(f"  Updates pulled : {C_GREEN}{state.get('update_count', 0)}{C_RESET}")
    print(f"  Log file       : {C_GRAY}{LOG_FILE}{C_RESET}\n")

def cmd_check():
    banner()
    state = load_state()
    check_and_update(state, verbose=True)

def cmd_log(lines=20):
    banner()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            entries = f.readlines()
        tail = entries[-lines:]
        print(f"  {C_CYAN}{C_BOLD}[ AUTO-UPDATER LOG - last {lines} entries ]{C_RESET}\n")
        for line in tail:
            print(f"  {C_GRAY}{line.rstrip()}{C_RESET}")
        print()
    except FileNotFoundError:
        print(f"  {C_YELLOW}[i] No log yet. Run: ax auto-update check{C_RESET}\n")

def main():
    args = sys.argv[1:]
    if not args:
        cmd_status()
        return
    cmd = args[0].lower()
    if cmd in ("start", "daemon", "run", "watch"):
        interval = int(args[1]) if len(args) > 1 and args[1].isdigit() else POLL_INTERVAL
        cmd_start(interval)
    elif cmd in ("stop", "kill", "halt"):
        cmd_stop()
    elif cmd in ("status", "info", "state"):
        cmd_status()
    elif cmd in ("check", "sync", "now", "force"):
        cmd_check()
    elif cmd in ("log", "logs", "history"):
        lines = int(args[1]) if len(args) > 1 and args[1].isdigit() else 20
        cmd_log(lines)
    else:
        banner()
        print(f"  {C_YELLOW}Usage:{C_RESET} ax auto-update <command>\n")
        print(f"  Commands:")
        print(f"    start [secs]  - Start background daemon (default: {POLL_INTERVAL}s)")
        print(f"    stop          - Stop the running daemon")
        print(f"    status        - Show daemon status and last sync info")
        print(f"    check         - One-shot check and pull if update available")
        print(f"    log [N]       - Show last N update log entries\n")

if __name__ == "__main__":
    main()
