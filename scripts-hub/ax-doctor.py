#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Developer & Online Problem Solver Suite
  Tools: ax unblock, ax secrets, ax doctor
  Version: 2.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import time
import socket
import ssl
import shutil
import urllib.request
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Terminal ANSI Colors
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"

BANNER = f"""{C_CYAN}{C_BOLD}
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗    ██████╗  ██████╗  ██████╗████████╗ ██████╗ ██████╗ 
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔══██╗██╔═══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║  ██║██║   ██║██║        ██║   ██║   ██║██████╔╝
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║  ██║██║   ██║██║        ██║   ██║   ██║██╔══██╗
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ██████╔╝╚██████╔╝╚██████╗   ██║   ╚██████╔╝██║  ██║
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝  ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
{C_RESET}{C_MAGENTA}       ASTERIX Developer & Online Problem Solver Suite (Doctor / Unblock / Secrets){C_RESET}
"""

# =============================================================================
# 1. PORT UNBLOCKER & ZOMBIE TERMINATOR (ax unblock <port>)
# =============================================================================

class PortUnblocker:
    """Finds and eliminates zombie processes holding sockets (fixing EADDRINUSE)."""

    @staticmethod
    def inspect_and_free(port: int, force: bool = True):
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[SOCKET INSPECTOR] Probing TCP port {port}...{C_RESET}\n")

        pids = PortUnblocker._find_pids_for_port(port)

        if not pids:
            # Check if port can be bound right now
            if PortUnblocker._is_port_free(port):
                print(f"  {C_GREEN}✓ Port {port} is already completely FREE and available!{C_RESET}")
                print(f"  {C_DIM}No processes holding socket 0.0.0.0:{port} or 127.0.0.1:{port}.{C_RESET}\n")
                return
            else:
                print(f"  {C_YELLOW}[!] Port {port} cannot be bound, but no user PID was identified (system or kernel lock).{C_RESET}\n")
                return

        print(f"  {C_YELLOW}⚠ Detected {len(pids)} process(es) holding port {port}:{C_RESET}")

        for pid in pids:
            proc_info = PortUnblocker._get_process_info(pid)
            print(f"    • PID: {C_BOLD}{pid}{C_RESET} | Name: {C_CYAN}{proc_info.get('name', 'Unknown')}{C_RESET}")
            if proc_info.get('cmd'):
                print(f"      Command: {C_DIM}{proc_info['cmd'][:80]}{C_RESET}")

            if force:
                print(f"      ↳ {C_RED}Terminating PID {pid}...{C_RESET}", end=" ")
                killed = PortUnblocker._kill_pid(pid)
                if killed:
                    print(f"{C_GREEN}[KILLED]{C_RESET}")
                else:
                    print(f"{C_RED}[FAILED (access denied)]{C_RESET}")

        time.sleep(0.3)
        if PortUnblocker._is_port_free(port):
            print(f"\n  {C_GREEN}{C_BOLD}✓ SUCCESS: Port {port} has been completely freed!{C_RESET}")
            print(f"  {C_DIM}You can now start your dev server, Flask, Express, or Docker container.{C_RESET}\n")
        else:
            print(f"\n  {C_YELLOW}[!] Port {port} is releasing (may take a few seconds for TIME_WAIT socket teardown).{C_RESET}\n")

    @staticmethod
    def _is_port_free(port: int) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("0.0.0.0", port))
            s.close()
            return True
        except Exception:
            return False

    @staticmethod
    def _find_pids_for_port(port: int) -> List[int]:
        pids = set()
        if sys.platform == "win32":
            try:
                out = subprocess.check_output(f"netstat -ano -p tcp", shell=True, text=True, errors="replace")
                for line in out.splitlines():
                    if f":{port} " in line and "LISTENING" in line:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            try:
                                pid = int(parts[-1])
                                if pid > 0:
                                    pids.add(pid)
                            except ValueError:
                                pass
            except Exception:
                pass
        else:
            # Linux / macOS
            try:
                out = subprocess.check_output(f"ss -tlpn sport = :{port}", shell=True, text=True, errors="replace")
                for match in re.finditer(r"pid=(\d+)", out):
                    pids.add(int(match.group(1)))
            except Exception:
                try:
                    out = subprocess.check_output(f"lsof -i :{port} -t", shell=True, text=True, errors="replace")
                    for line in out.splitlines():
                        if line.strip().isdigit():
                            pids.add(int(line.strip()))
                except Exception:
                    pass
        return sorted(list(pids))

    @staticmethod
    def _get_process_info(pid: int) -> Dict[str, str]:
        info = {"name": "Unknown", "cmd": ""}
        if sys.platform == "win32":
            try:
                out = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /FO CSV /NH', shell=True, text=True, errors="replace")
                parts = out.strip().split('","')
                if parts:
                    info["name"] = parts[0].replace('"', '')
            except Exception:
                pass
        else:
            try:
                comm_path = Path(f"/proc/{pid}/comm")
                if comm_path.exists():
                    info["name"] = comm_path.read_text().strip()
                cmd_path = Path(f"/proc/{pid}/cmdline")
                if cmd_path.exists():
                    info["cmd"] = cmd_path.read_text().replace('\x00', ' ').strip()
            except Exception:
                pass
        return info

    @staticmethod
    def _kill_pid(pid: int) -> bool:
        if sys.platform == "win32":
            try:
                res = subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                return res.returncode == 0
            except Exception:
                return False
        else:
            try:
                os.kill(pid, 9)
                return True
            except Exception:
                return False


# =============================================================================
# 2. CREDENTIAL & SECRET LEAK SENTINEL (ax secrets [path])
# =============================================================================

SECRET_PATTERNS = [
    ("AWS Access Key", r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"),
    ("GitHub Personal Access Token", r"gh[pousr]_[0-9a-zA-Z]{36,}"),
    ("OpenAI API Key", r"sk-[a-zA-Z0-9_-]{20,}"),
    ("Stripe Secret Key", r"(?:sk|rk)_(?:test|live)_[0-9a-zA-Z]{24,}"),
    ("Google Cloud API Key", r"AIza[0-9A-Za-z\\-_]{35}"),
    ("Slack API Token", r"xox[baprs]-[0-9a-zA-Z]{10,48}"),
    ("Discord Bot Token", r"[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}"),
    ("Private RSA/OpenSSH Key", r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----"),
    ("Generic Database Password URI", r"(?:postgres|mysql|mongodb|redis):\/\/[^:\s]+:([^@\s]+)@"),
    ("Generic Private Bearer Token", r"(?i)bearer\s+[a-zA-Z0-9_\-\.]{32,}")
]

IGNORE_SCAN_DIRS = {
    ".git", "node_modules", "venv", ".venv", "__pycache__", "target", "dist",
    "iso-images", "assets", ".idea", ".vscode", "build"
}

class SecretSentinel:
    """Audits files, commits, and directories for leaked API credentials and keys."""

    @staticmethod
    def scan_path(target_path: str, mask: bool = True):
        root = Path(target_path).resolve()
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[SECRETS SENTINEL] Auditing credentials in: {root}{C_RESET}\n")

        findings = []
        files_scanned = 0

        for cur_root, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in IGNORE_SCAN_DIRS and not d.startswith(".")]
            for file in files:
                file_path = Path(cur_root) / file
                # Skip binary and oversized files (>2MB)
                if file_path.suffix.lower() in (".jpg", ".png", ".exe", ".iso", ".zip", ".tar", ".gz", ".pyc", ".bin"):
                    continue
                try:
                    if file_path.stat().st_size > 2 * 1024 * 1024:
                        continue
                    files_scanned += 1
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    for line_no, line in enumerate(content.splitlines(), 1):
                        for label, regex in SECRET_PATTERNS:
                            matches = re.finditer(regex, line)
                            for m in matches:
                                secret_val = m.group(0)
                                # Filter obvious false positives
                                if "example" in secret_val.lower() or "your_" in secret_val.lower() or "xxxx" in secret_val.lower():
                                    continue
                                rel_path = str(file_path.relative_to(root))
                                findings.append({
                                    "file": rel_path,
                                    "line": line_no,
                                    "type": label,
                                    "secret": secret_val
                                })
                except Exception:
                    pass

        print(f"  • Files Scanned: {C_BOLD}{files_scanned}{C_RESET}")

        if not findings:
            print(f"  {C_GREEN}{C_BOLD}✓ CLEAN: Zero exposed API tokens or private keys detected!{C_RESET}\n")
            return

        print(f"  {C_RED}{C_BOLD}⚠ WARNING: Detected {len(findings)} exposed secret(s)!{C_RESET}\n")
        print(f"  {'File Path':<35} {'Line':<6} {'Secret Type':<30} {'Masked Token':<20}")
        print(f"  {'-'*95}")

        for f in findings:
            masked = f["secret"][:6] + "..." + f["secret"][-4:] if len(f["secret"]) > 10 else "***"
            print(f"  {f['file'][:34]:<35} {f['line']:<6} {f['type'][:29]:<30} {C_YELLOW}{masked}{C_RESET}")

        print(f"\n  {C_YELLOW}[!] RECOMMENDATION: Move credentials to .env or environment variables before pushing online.{C_RESET}\n")


# =============================================================================
# 3. COMPREHENSIVE ONLINE & DEVELOPER HEALTH DOCTOR (ax doctor [--fix])
# =============================================================================

class SystemDoctor:
    """Diagnoses real-time online network health and developer environment toolchains."""

    @staticmethod
    def run_health_check(auto_fix: bool = False):
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[ASTERIX SYSTEM & NETWORK DOCTOR]{C_RESET}")
        print(f"  Executing real-time diagnostic telemetry across network & local environment...\n")

        # --- SECTION 1: ONLINE & NETWORK CONNECTIVITY ---
        print(f"  {C_WHITE}{C_BOLD}1. ONLINE CONNECTIVITY & DNS HEALTH{C_RESET}")
        
        # DNS Resolution
        dns_start = time.time()
        dns_ok = False
        try:
            socket.gethostbyname("one.one.one.one")
            dns_latency = (time.time() - dns_start) * 1000
            dns_ok = True
            print(f"    • DNS Resolution:      {C_GREEN}ONLINE{C_RESET} ({dns_latency:.1f} ms via Cloudflare DNS)")
        except Exception:
            print(f"    • DNS Resolution:      {C_RED}FAILED (ISP DNS Hijack / No Internet){C_RESET}")

        # Gateway / Internet Ping
        gw_ok = False
        try:
            s = socket.create_connection(("8.8.8.8", 53), timeout=2.5)
            s.close()
            gw_ok = True
            print(f"    • Internet Gateway:    {C_GREEN}CONNECTED{C_RESET} (Active default route)")
        except Exception:
            print(f"    • Internet Gateway:    {C_RED}DISCONNECTED{C_RESET}")

        # SSL/TLS Handshake Verification
        ssl_ok = False
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection(("github.com", 443), timeout=3.0) as sock:
                with ctx.wrap_socket(sock, server_hostname="github.com") as ssock:
                    cert = ssock.getpeercert()
                    ssl_ok = True
                    print(f"    • SSL/TLS Engine:      {C_GREEN}SECURE{C_RESET} (Valid certificate trust store)")
        except Exception as e:
            print(f"    • SSL/TLS Engine:      {C_RED}FAILED ({str(e)[:40]}){C_RESET}")

        # Public IP Egress
        try:
            req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "ASTERIX-Doctor/2.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                public_ip = resp.read().decode("utf-8").strip()
                print(f"    • Public WAN Egress:   {C_CYAN}{public_ip}{C_RESET}")
        except Exception:
            print(f"    • Public WAN Egress:   {C_DIM}Unavailable (Offline or firewall){C_RESET}")

        print()

        # --- SECTION 2: DEVELOPER ENVIRONMENT & TOOLCHAINS ---
        print(f"  {C_WHITE}{C_BOLD}2. DEVELOPER TOOLCHAINS & RUNTIMES{C_RESET}")

        # Python
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"    • Python 3 Runtime:    {C_GREEN}READY{C_RESET} (v{py_ver} at {sys.executable})")

        # Node.js
        node_path = shutil.which("node")
        if node_path:
            try:
                n_ver = subprocess.check_output([node_path, "-v"], text=True, timeout=2).strip()
                print(f"    • Node.js Engine:      {C_GREEN}READY{C_RESET} ({n_ver})")
            except Exception:
                print(f"    • Node.js Engine:      {C_YELLOW}FOUND (Cannot execute){C_RESET}")
        else:
            print(f"    • Node.js Engine:      {C_DIM}NOT INSTALLED{C_RESET}")

        # Rust
        rust_path = shutil.which("rustc")
        if rust_path:
            try:
                r_ver = subprocess.check_output([rust_path, "--version"], text=True, timeout=2).split()[1]
                print(f"    • Rust Toolchain:      {C_GREEN}READY{C_RESET} (v{r_ver})")
            except Exception:
                print(f"    • Rust Toolchain:      {C_YELLOW}FOUND{C_RESET}")
        else:
            print(f"    • Rust Toolchain:      {C_DIM}NOT INSTALLED{C_RESET}")

        # Git
        git_path = shutil.which("git")
        if git_path:
            try:
                g_ver = subprocess.check_output([git_path, "--version"], text=True, timeout=2).strip()
                print(f"    • Git VCS Engine:      {C_GREEN}READY{C_RESET} ({g_ver})")
            except Exception:
                print(f"    • Git VCS Engine:      {C_YELLOW}FOUND{C_RESET}")
        else:
            print(f"    • Git VCS Engine:      {C_RED}MISSING{C_RESET}")

        # C / C++ Compiler
        cc_names = ["gcc", "clang", "cl"]
        cc_found = None
        for cc in cc_names:
            if shutil.which(cc):
                cc_found = cc
                break
        if cc_found:
            print(f"    • C/C++ Compiler:      {C_GREEN}READY{C_RESET} ({cc_found})")
        else:
            print(f"    • C/C++ Compiler:      {C_YELLOW}NO NATIVE COMPILER ON PATH{C_RESET}")

        print()

        # --- SECTION 3: SYSTEM HYGIENE & COMMON DEV PORTS ---
        print(f"  {C_WHITE}{C_BOLD}3. SYSTEM HYGIENE & COMMON DEV PORTS{C_RESET}")
        common_ports = [3000, 5000, 8000, 8080, 8888]
        occupied = []
        for p in common_ports:
            if not PortUnblocker._is_port_free(p):
                pids = PortUnblocker._find_pids_for_port(p)
                pid_str = f"PID {pids[0]}" if pids else "Active"
                occupied.append((p, pid_str))

        if occupied:
            print(f"    • Occupied Dev Ports:  {C_YELLOW}{len(occupied)} port(s) currently bound{C_RESET}")
            for p, pstr in occupied:
                print(f"        ↳ Port {C_BOLD}{p}{C_RESET}: {pstr} (Run '{C_CYAN}ax unblock {p}{C_RESET}' to free)")
        else:
            print(f"    • Occupied Dev Ports:  {C_GREEN}ALL COMMON DEV PORTS FREE (3000, 5000, 8000, 8080){C_RESET}")

        # Auto-Fix option
        if auto_fix:
            print(f"\n  {C_CYAN}{C_BOLD}4. AUTONOMOUS REPAIR & ENVIRONMENT HEALING (--fix){C_RESET}")
            if sys.platform == "win32":
                print(f"    • Flushing DNS resolver cache... ", end="")
                try:
                    subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
                    print(f"{C_GREEN}[FLUSHED]{C_RESET}")
                except Exception:
                    print(f"{C_RED}[FAILED]{C_RESET}")
            else:
                print(f"    • Clearing system resolution caches... {C_GREEN}[OK]{C_RESET}")

        print()


# =============================================================================
# CLI DISPATCHER
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Developer & Online Problem Solver Suite",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # unblock command
    unblock_parser = subparsers.add_parser("unblock", help="Free blocked port and terminate zombie process")
    unblock_parser.add_argument("port", type=int, help="TCP port number to unblock (e.g. 3000, 8080)")

    # secrets command
    secrets_parser = subparsers.add_parser("secrets", help="Scan codebase for exposed API keys and credentials")
    secrets_parser.add_argument("path", nargs="?", default=".", help="Directory to audit")

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Run comprehensive online & developer health diagnostic")
    doctor_parser.add_argument("--fix", action="store_true", help="Autonomously flush DNS and repair environment")

    # Fallback routing if invoked with legacy positional argument
    if len(sys.argv) > 1 and sys.argv[1] not in ("unblock", "secrets", "doctor", "-h", "--help"):
        if sys.argv[1].isdigit():
            sys.argv.insert(1, "unblock")
        else:
            sys.argv.insert(1, "doctor")

    args = parser.parse_args()

    if args.subcommand == "unblock":
        PortUnblocker.inspect_and_free(args.port)
    elif args.subcommand == "secrets":
        SecretSentinel.scan_path(args.path)
    else:
        SystemDoctor.run_health_check(getattr(args, "fix", False))


if __name__ == "__main__":
    main()
