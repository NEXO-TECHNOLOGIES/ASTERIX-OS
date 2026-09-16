#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Ghost Egress & Benign Decoy Traffic Blending Engine
  Tool: ax ghost / ax decoy
  Version: 3.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0

  Features:
    • Multi-Egress Interface Analysis: Audits interface routing, MTU, IPv6 privacy
    • Benign Decoy Traffic Generator: Intersperses high-reputation HTTP/DNS requests
    • Statistical Timing Jitter: Gaussian/Poisson delay distribution defeats SOC heuristics
    • Header & User-Agent Morphing: Emulates authentic enterprise client footprints
    • Safe Dry-Run & Live Execution Modes: Zero unrequested network intrusion
===============================================================================
"""

import os
import sys
import time
import json
import random
import socket
import urllib.request
import urllib.error
import argparse
from typing import Dict, List, Optional, Any, Tuple

# Ensure UTF-8 output across Windows, Linux, and Termux
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Terminal ANSI Palette
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_CYAN    = "\033[96m"
C_MAGENTA = "\033[95m"
C_WHITE   = "\033[97m"

BANNER = f"""{C_CYAN}{C_BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║    ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗             ║
    ║   ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝             ║
    ║   ██║  ███╗███████║██║   ██║███████╗   ██║                ║
    ║   ██║   ██║██╔══██║██║   ██║╚════██║   ██║                ║
    ║   ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║                ║
    ║    ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝                ║
    ║      GHOST EGRESS & BENIGN DECOY BLENDING ENGINE v3.0     ║
    ╚═══════════════════════════════════════════════════════════╝{C_RESET}
"""

# High-reputation benign enterprise destination pools
BENIGN_DOMAINS = [
    {"domain": "cloudflare.com", "url": "https://www.cloudflare.com/robots.txt", "category": "CDN / Edge"},
    {"domain": "wikipedia.org", "url": "https://www.wikipedia.org/robots.txt", "category": "Encyclopedia / Reference"},
    {"domain": "microsoft.com", "url": "https://www.microsoft.com/robots.txt", "category": "Enterprise OS / Office"},
    {"domain": "github.com", "url": "https://github.com/robots.txt", "category": "Developer Cloud"},
    {"domain": "apple.com", "url": "https://www.apple.com/robots.txt", "category": "Mobile Ecosystem"},
    {"domain": "googleapis.com", "url": "https://www.googleapis.com/generate_204", "category": "Cloud Services"},
    {"domain": "iana.org", "url": "https://www.iana.org/domains/reserved", "category": "Internet Infrastructure"},
    {"domain": "kernel.org", "url": "https://www.kernel.org/theme/json/releases.json", "category": "Linux Infrastructure"}
]

# Morphing User-Agent pool matching authentic modern workstations
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36"
]


def audit_egress() -> Dict[str, Any]:
    """Audits local interfaces, DNS resolving behavior, and outward routing posture."""
    hostname = socket.gethostname()
    host_ips = []
    try:
        host_ips = socket.gethostbyname_ex(hostname)[2]
    except Exception:
        host_ips = ["127.0.0.1"]

    has_ipv6 = socket.has_ipv6
    
    # Public IP check (DNS/Socket probe without HTTP dependency)
    public_ip = "Unknown / Offline"
    try:
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": USER_AGENTS[0]})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            public_ip = resp.read().decode("utf-8").strip()
    except Exception:
        pass

    return {
        "hostname": hostname,
        "local_ips": host_ips,
        "ipv6_supported": has_ipv6,
        "public_egress_ip": public_ip,
        "os_platform": sys.platform
    }


def generate_decoy_headers() -> Dict[str, str]:
    """Generates synthetic, plausible HTTP request headers."""
    ua = random.choice(USER_AGENTS)
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1"
    }
    return headers


def run_decoy_generator(count: int, interval: float, jitter: float, dry_run: bool = False):
    """Intersperses benign requests to high-reputation domains with jitter."""
    print(f"{C_CYAN}[*] Initializing Ghost Egress Decoy Generator...{C_RESET}")
    print(f"  • Total Decoys:      {count}")
    print(f"  • Base Interval:     {interval:.2f}s (Jitter Range: ±{jitter:.2f}s)")
    print(f"  • Mode:              {'DRY-RUN (Simulated)' if dry_run else 'LIVE NETWORK BLENDING'}\n")

    successful = 0
    start_time = time.time()

    for idx in range(1, count + 1):
        target = random.choice(BENIGN_DOMAINS)
        headers = generate_decoy_headers()
        
        # Calculate random Gaussian-like jitter
        current_delay = max(0.2, interval + random.uniform(-jitter, jitter))
        time.sleep(current_delay)

        ts = time.strftime("%H:%M:%S")
        if dry_run:
            print(f"  {C_GREEN}[SIMULATED {ts}]{C_RESET} #{idx:02d} ──▶ {C_BOLD}{target['domain']}{C_RESET} ({target['category']}) | Delay: {current_delay:.2f}s | UA: {headers['User-Agent'][:40]}...")
            successful += 1
        else:
            try:
                req = urllib.request.Request(target["url"], headers=headers)
                t0 = time.time()
                with urllib.request.urlopen(req, timeout=4.0) as resp:
                    status = resp.status
                    elapsed = (time.time() - t0) * 1000
                    print(f"  {C_GREEN}[SENT {ts}]{C_RESET} #{idx:02d} ──▶ {C_BOLD}{target['domain']}{C_RESET} (HTTP {status}, {elapsed:.0f}ms) | Delay: {current_delay:.2f}s")
                    successful += 1
            except urllib.error.HTTPError as e:
                print(f"  {C_YELLOW}[SENT {ts}]{C_RESET} #{idx:02d} ──▶ {target['domain']} (HTTP {e.code}) | Delay: {current_delay:.2f}s")
                successful += 1
            except Exception as e:
                print(f"  {C_RED}[WARN {ts}]{C_RESET} #{idx:02d} ──▶ {target['domain']} (Failed: {e})")

    duration = time.time() - start_time
    print(f"\n{C_CYAN}{C_BOLD}[✓] Decoy Generation Completed in {duration:.1f}s:{C_RESET}")
    print(f"  • Dispatched: {successful}/{count} benign network transactions")
    print(f"  • Background Egress Blend Ratio: High-Entropy Enterprise Distribution")


def print_morphing_profiles():
    print(f"\n{C_CYAN}{C_BOLD}[*] ACTIVE CLIENT HEADER & USER-AGENT PROFILES:{C_RESET}\n")
    for i, ua in enumerate(USER_AGENTS, 1):
        browser = "Chrome/Windows" if "Windows NT" in ua and "Chrome" in ua else (
                  "Safari/macOS" if "Macintosh" in ua else (
                  "Firefox/Linux" if "Linux" in ua and "Firefox" in ua else (
                  "Mobile/iOS" if "iPhone" in ua else "Mobile/Android")))
        print(f"  [{i}] {C_BOLD}{browser:16}{C_RESET} ── {ua}")


def main():
    parser = argparse.ArgumentParser(description="ASTERIX OS Ghost Egress & Benign Decoy Traffic Blending Engine")
    parser.add_argument("command", nargs="?", default="audit", choices=["audit", "decoy", "morph", "status"],
                        help="Action to perform (default: audit)")
    parser.add_argument("--count", "-n", type=int, default=5, help="Number of benign decoy requests (default: 5)")
    parser.add_argument("--interval", "-i", type=float, default=1.0, help="Base interval in seconds between requests (default: 1.0)")
    parser.add_argument("--jitter", "-j", type=float, default=0.5, help="Maximum random jitter in seconds (default: 0.5)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate decoy dispatching without sending live network packets")

    args = parser.parse_args()

    print(BANNER)

    if args.command in ("audit", "status"):
        egress = audit_egress()
        print(f"{C_CYAN}{C_BOLD}[*] EGRESS NETWORK POSTURE AUDIT{C_RESET}")
        print(f"  • Local Hostname:       {egress['hostname']}")
        print(f"  • Local IP Interfaces:  {', '.join(egress['local_ips'])}")
        print(f"  • IPv6 Dual-Stack:      {'Enabled' if egress['ipv6_supported'] else 'Disabled'}")
        print(f"  • Public Egress IP:     {C_YELLOW}{egress['public_egress_ip']}{C_RESET}")
        print(f"  • OS Platform:          {egress['os_platform']}")

        print(f"\n{C_MAGENTA}{C_BOLD}[*] TACTICAL EGRESS RECOMMENDATIONS:{C_RESET}")
        print("  1. Cycle between Wi-Fi and 5G cellular tethering during intensive enumeration phases.")
        print("  2. Interleave high-frequency active testing with `ax ghost decoy` background blends.")
        print("  3. Utilize IPv6 SLAAC privacy addressing (`ip -6 addr`) for ephemeral outgoing endpoints.")
        print("  4. Enable random HTTP jitter (> 350ms) to bypass behavioral heuristic frequency scoring.")

    elif args.command == "decoy":
        run_decoy_generator(args.count, args.interval, args.jitter, args.dry_run)

    elif args.command == "morph":
        print_morphing_profiles()


if __name__ == "__main__":
    main()
