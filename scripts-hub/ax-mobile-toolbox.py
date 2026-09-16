#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Mobile & Embedded System Toolbox (ax mobile-sys)
  Cross-Platform Telemetry, Hardware Monitor & Network Benchmark Suite
  Zero External Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import time
import socket
import shutil
import argparse
import subprocess
from pathlib import Path

# Ensure UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_GRAY    = "\033[38;5;244m"
C_WHITE   = "\033[38;5;231m"

def get_battery_info():
    """Extracts battery capacity and status across Android, Linux, and Windows."""
    info = {"percentage": "N/A", "status": "N/A", "temperature": "N/A"}

    # 1. Android Termux API
    if shutil.which("termux-battery-status"):
        try:
            out = subprocess.check_output(["termux-battery-status"], timeout=3).decode("utf-8")
            import json
            data = json.loads(out)
            info["percentage"] = f"{data.get('percentage', 'N/A')}%"
            info["status"] = data.get("status", "N/A")
            info["temperature"] = f"{data.get('temperature', 'N/A')} °C"
            return info
        except Exception:
            pass

    # 2. Linux sysfs
    bat_path = Path("/sys/class/power_supply/battery")
    if not bat_path.exists():
        bats = list(Path("/sys/class/power_supply").glob("BAT*"))
        if bats:
            bat_path = bats[0]
    if bat_path.exists():
        try:
            cap = (bat_path / "capacity").read_text().strip()
            stat = (bat_path / "status").read_text().strip()
            info["percentage"] = f"{cap}%"
            info["status"] = stat
            if (bat_path / "temp").exists():
                temp_raw = float((bat_path / "temp").read_text().strip())
                info["temperature"] = f"{temp_raw / 10.0} °C"
            return info
        except Exception:
            pass

    # 3. Windows PowerShell CIM fallback
    if sys.platform == "win32":
        try:
            cmd = "Get-CimInstance Win32_Battery | Select-Object -Property EstimatedChargeRemaining, BatteryStatus | Format-List"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], timeout=4).decode("utf-8")
            for line in out.splitlines():
                if "EstimatedChargeRemaining" in line and ":" in line:
                    val = line.split(":")[-1].strip()
                    if val and val.isdigit():
                        info["percentage"] = f"{val}%"
                if "BatteryStatus" in line and ":" in line:
                    info["status"] = "Active"
            return info
        except Exception:
            pass

    return info

def benchmark_dns():
    """Benchmarks DNS socket connect latency against major public resolvers."""
    resolvers = [
        ("Cloudflare", "1.1.1.1", 53),
        ("Google", "8.8.8.8", 53),
        ("Quad9", "9.9.9.9", 53),
        ("OpenDNS", "208.67.222.222", 53),
    ]
    results = []
    for name, host, port in resolvers:
        latencies = []
        for _ in range(2):
            t0 = time.perf_counter()
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2.0)
            try:
                s.connect((host, port))
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000)
            except Exception:
                pass
            finally:
                s.close()
        if latencies:
            avg_ms = sum(latencies) / len(latencies)
            results.append((name, host, f"{avg_ms:.1f} ms"))
        else:
            results.append((name, host, "Timeout/Blocked"))
    return results

def main():
    parser = argparse.ArgumentParser(description="ASTERIX OS Mobile & Hardware System Center")
    parser.add_argument("action", nargs="?", default="all", choices=["all", "battery", "dns", "clean", "doctor"], help="Action to perform")
    args = parser.parse_args()

    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}║   📱 ASTERIX MOBILE SYSTEM CENTER & HARDWARE TELEMETRY               ║{C_RESET}")
    print(f"{C_CYAN}{C_BOLD}╚══════════════════════════════════════════════════════════════════════╝{C_RESET}\n")

    if args.action in ["all", "battery"]:
        bat = get_battery_info()
        print(f"  {C_YELLOW}{C_BOLD}[ HARDWARE & POWER TELEMETRY ]{C_RESET}")
        print(f"    {C_WHITE}Charge Level:{C_RESET}    {C_GREEN}{bat['percentage']}{C_RESET}")
        print(f"    {C_WHITE}Power Status:{C_RESET}    {C_CYAN}{bat['status']}{C_RESET}")
        print(f"    {C_WHITE}Temperature:{C_RESET}     {C_YELLOW}{bat['temperature']}{C_RESET}")
        print(f"    {C_WHITE}CPU Cores:{C_RESET}       {C_WHITE}{os.cpu_count() or 'N/A'}{C_RESET}\n")

    if args.action in ["all", "dns"]:
        print(f"  {C_YELLOW}{C_BOLD}[ MOBILE NETWORK & RESOLVER BENCHMARK ]{C_RESET}")
        dns_res = benchmark_dns()
        for name, host, lat in dns_res:
            col = C_GREEN if "ms" in lat else C_RED
            print(f"    {C_WHITE}{name:14s}{C_RESET} ({host:15s})  ──>  {col}{lat}{C_RESET}")
        print("")

    if args.action in ["clean"]:
        print(f"  {C_YELLOW}[*] Purging Temporary Files & Caches...{C_RESET}")
        tmp_dir = Path(os.environ.get("TMPDIR", "/tmp"))
        cleaned = 0
        if tmp_dir.exists():
            for f in tmp_dir.glob("asterix_*"):
                try:
                    if f.is_file():
                        f.unlink()
                        cleaned += 1
                except Exception:
                    pass
        print(f"  {C_GREEN}[✔] Optimization complete. Purged {cleaned} temporary files.{C_RESET}\n")

if __name__ == "__main__":
    main()
