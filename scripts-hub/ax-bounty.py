#!/usr/bin/env python3
"""
ASTERIX OS — Automated Bug Bounty Recon & Attack Surface Pipeline (ax bounty)
Features:
  - Phase 1: DNS & OSINT Subdomain Enumeration via Certificate Transparency (crt.sh)
  - Phase 2: High-Speed Multithreaded Port Surface Sweep
  - Phase 3: HTTP/HTTPS Probing, Service Fingerprinting & Title Extraction
  - Phase 4: Web Application Firewall (WAF) Fingerprinting
  - Phase 5: Exposed Secrets & Dangerous Sensitive Endpoint Discovery
  - Phase 6: Executive Vulnerability Markdown & JSON Dossier Generation
Zero external dependencies — 100% Python standard library.
"""

import sys
import os
import re
import socket
import ssl
import json
import time
import urllib.request
import urllib.error
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from datetime import datetime

# UTF-8 safety on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Colors ────────────────────────────────────────────────────────────────────
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
║{C_WHITE}{C_BOLD}     [ ASTERIX AUTONOMOUS BUG BOUNTY RECON & ATTACK SURFACE v2.0 ]      {C_RESET}{C_CYAN}║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

SEP = f"{C_BLUE}{'─'*74}{C_RESET}"

TOP_PORTS = [
    (21, "FTP"),
    (22, "SSH"),
    (25, "SMTP"),
    (53, "DNS"),
    (80, "HTTP"),
    (110, "POP3"),
    (143, "IMAP"),
    (443, "HTTPS"),
    (465, "SMTPS"),
    (587, "Submission"),
    (993, "IMAPS"),
    (995, "POP3S"),
    (1433, "MSSQL"),
    (3000, "Node/React/Dev"),
    (3306, "MySQL"),
    (3389, "RDP"),
    (5000, "Flask/Dev"),
    (5432, "PostgreSQL"),
    (6379, "Redis"),
    (8000, "HTTP-Alt"),
    (8080, "HTTP-Proxy/Tomcat"),
    (8443, "HTTPS-Alt"),
    (8888, "Jupyter/HTTP"),
    (9000, "SonarQube/PHP-FPM"),
    (9200, "Elasticsearch"),
    (27017, "MongoDB"),
]

SENSITIVE_PATHS = [
    ("/.git/HEAD", "Exposed Git Repository (Critical Source Leak)", "HIGH"),
    ("/.env", "Exposed Environment File / Credentials Leak", "CRITICAL"),
    ("/robots.txt", "Search Engine Exclusion List (Target Map)", "LOW"),
    ("/sitemap.xml", "Application Site Map", "LOW"),
    ("/.well-known/security.txt", "Security Contact & Vulnerability Disclosure Policy", "INFO"),
    ("/api/", "REST API Root Endpoint", "LOW"),
    ("/swagger.json", "Exposed OpenAPI / Swagger Documentation", "MEDIUM"),
    ("/api-docs", "Exposed API Documentation", "MEDIUM"),
    ("/metrics", "Exposed Prometheus Metrics / Telemetry", "MEDIUM"),
    ("/actuator/health", "Spring Boot Actuator Health", "MEDIUM"),
    ("/actuator/env", "Spring Boot Actuator Env (Credential Leak)", "CRITICAL"),
    ("/server-status", "Apache Server Status Leak", "MEDIUM"),
    ("/phpinfo.php", "PHP Configuration Disclosure", "HIGH"),
    ("/config.json", "Client/Server Configuration JSON", "HIGH"),
    ("/backup.sql", "Exposed Database Dump Backup", "CRITICAL"),
    ("/wp-config.php.bak", "Exposed WordPress Config Backup", "CRITICAL"),
]

WAF_SIGNATURES = {
    "Cloudflare": [("server", "cloudflare"), ("cf-ray", "")],
    "AWS CloudFront": [("via", "cloudfront"), ("x-amz-cf-id", "")],
    "Akamai": [("server", "akamai"), ("x-akamai-transformed", "")],
    "Imperva / Incapsula": [("x-iinfo", ""), ("x-cdn", "incapsula")],
    "Fastly": [("via", "varnish"), ("x-fastly-request-id", "")],
    "Sucuri": [("x-sucuri-id", ""), ("server", "sucuri")],
    "ModSecurity": [("server", "mod_security"), ("server", "modsecurity")],
}

def clean_target(target: str) -> str:
    t = target.strip()
    if t.startswith(("http://", "https://")):
        parsed = urlparse(t)
        return parsed.hostname or t
    return t.split("/")[0].split(":")[0]

def resolve_target(domain: str):
    """Resolve domain to IPv4 and IPv6 addresses."""
    ips = []
    try:
        results = socket.getaddrinfo(domain, None)
        for r in results:
            ip = r[4][0]
            if ip not in ips:
                ips.append(ip)
    except socket.gaierror:
        pass
    return ips

def fetch_crt_sh(domain: str):
    """Query Certificate Transparency logs via crt.sh."""
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    req = urllib.request.Request(url, headers={"User-Agent": "ASTERIX-Bounty/2.0"})
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                for entry in data[:100]:
                    name = entry.get("name_value", "")
                    for sub in name.splitlines():
                        sub = sub.strip().lower()
                        if sub.endswith(domain) and "*" not in sub:
                            subdomains.add(sub)
    except Exception:
        pass
    return sorted(list(subdomains))

def probe_port(ip: str, port: int, service: str, timeout: float = 1.0):
    """Probe single TCP port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((ip, port))
        if res == 0:
            return {"port": port, "service": service, "state": "open"}
    except Exception:
        pass
    finally:
        s.close()
    return None

def scan_ports(ip: str, max_threads: int = 30):
    """Multithreaded port scanner."""
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(probe_port, ip, p, s): (p, s) for p, s in TOP_PORTS}
        for future in as_completed(futures):
            res = future.result()
            if res:
                open_ports.append(res)
    open_ports.sort(key=lambda x: x["port"])
    return open_ports

def probe_http(domain: str, port: int = 80, use_ssl: bool = False):
    """Send HTTP request, extract headers, title, server banner."""
    scheme = "https" if use_ssl else "http"
    url = f"{scheme}://{domain}:{port}/" if (port not in (80, 443)) else f"{scheme}://{domain}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ASTERIX-OS/2.0 Penetration-Tester"
    }
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
            status = resp.status
            resp_headers = dict(resp.headers)
            body = resp.read(8192).decode("utf-8", errors="replace")
            title_m = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
            title = title_m.group(1).strip() if title_m else "N/A"
            return {
                "url": url,
                "status": status,
                "server": resp_headers.get("server", resp_headers.get("Server", "Unknown")),
                "title": title,
                "headers": resp_headers,
            }
    except urllib.error.HTTPError as e:
        resp_headers = dict(e.headers)
        return {
            "url": url,
            "status": e.code,
            "server": resp_headers.get("server", resp_headers.get("Server", "Unknown")),
            "title": f"HTTP {e.code}",
            "headers": resp_headers,
        }
    except Exception as e:
        return None

def detect_waf(headers: dict):
    """Detect WAF signatures in response headers."""
    detected = []
    headers_lower = {k.lower(): str(v).lower() for k, v in headers.items()}
    for waf_name, sigs in WAF_SIGNATURES.items():
        match_count = 0
        for hdr, val in sigs:
            if hdr in headers_lower:
                if not val or val in headers_lower[hdr]:
                    match_count += 1
        if match_count == len(sigs):
            detected.append(waf_name)
    return detected

def probe_sensitive_path(base_url: str, path: str, desc: str, severity: str):
    """Probe for exposed sensitive path."""
    url = base_url.rstrip("/") + path
    headers = {"User-Agent": "ASTERIX-Bounty/2.0"}
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, timeout=4, context=ctx) as resp:
            if resp.status == 200:
                body_sample = resp.read(256).decode("utf-8", errors="replace")
                # False positive check for custom 404s
                if path == "/.git/HEAD" and "ref:" not in body_sample:
                    return None
                if path == "/.env" and ("=" not in body_sample or "<html" in body_sample.lower()):
                    return None
                return {
                    "path": path,
                    "url": url,
                    "status": resp.status,
                    "desc": desc,
                    "severity": severity,
                }
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return {
                "path": path,
                "url": url,
                "status": e.code,
                "desc": f"{desc} (Access Forbidden - Endpoint Exists)",
                "severity": "LOW",
            }
    except Exception:
        pass
    return None

def run_bounty(target_raw: str):
    domain = clean_target(target_raw)
    print(BANNER)
    print(f"\n  {C_CYAN}[*] Target Domain:{C_RESET} {C_WHITE}{domain}{C_RESET}")
    print(f"  {C_CYAN}[*] Recon Mode:   {C_RESET} Full Autonomous Attack Surface Discovery")
    print(f"  {C_CYAN}[*] Started:      {C_RESET} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEP)

    # ── Phase 1: DNS & IPs ────────────────────────────────────────────────────
    print(f"\n{C_MAGENTA}{C_BOLD}[PHASE 1] DNS Resolution & Target Fingerprinting{C_RESET}")
    ips = resolve_target(domain)
    if not ips:
        print(f"  {C_RED}[!] Failed to resolve {domain}. Hostname may be unreachable.{C_RESET}")
        return
    for ip in ips:
        print(f"  {C_GREEN}[+] Resolved IP:{C_RESET} {C_WHITE}{ip}{C_RESET}")

    # Subdomains
    print(f"\n  {C_CYAN}[*] Querying Certificate Transparency Logs for Subdomains...{C_RESET}")
    subdomains = fetch_crt_sh(domain)
    if subdomains:
        print(f"  {C_GREEN}[+] Discovered {len(subdomains)} Subdomain(s) via CT logs:{C_RESET}")
        for sub in subdomains[:12]:
            print(f"    • {C_WHITE}{sub}{C_RESET}")
        if len(subdomains) > 12:
            print(f"    {C_GRAY}... and {len(subdomains)-12} more (recorded in report){C_RESET}")
    else:
        print(f"  {C_GRAY}[-] No external CT subdomains found or CT log timed out.{C_RESET}")

    # ── Phase 2: Port Surface ─────────────────────────────────────────────────
    primary_ip = ips[0]
    print(f"\n{C_MAGENTA}{C_BOLD}[PHASE 2] Port Surface Sweep (Top 26 Attack Vectors) on {primary_ip}{C_RESET}")
    open_ports = scan_ports(primary_ip)
    if open_ports:
        for p in open_ports:
            print(f"  {C_GREEN}[+] OPEN PORT:{C_RESET} {C_YELLOW}{p['port']}/TCP{C_RESET} \t({C_WHITE}{p['service']}{C_RESET})")
    else:
        print(f"  {C_YELLOW}[!] No common ports open to direct connect (Host may be behind full firewall).{C_RESET}")

    # ── Phase 3: HTTP & Service Fingerprint ───────────────────────────────────
    print(f"\n{C_MAGENTA}{C_BOLD}[PHASE 3] HTTP/HTTPS Service Fingerprinting & Title Discovery{C_RESET}")
    http_services = []
    for port, is_ssl in [(443, True), (80, False), (8443, True), (8080, False), (3000, False), (8000, False)]:
        # Check if port was found open or default web ports
        if any(op["port"] == port for op in open_ports) or port in (80, 443):
            svc = probe_http(domain, port=port, use_ssl=is_ssl)
            if svc:
                http_services.append(svc)
                print(f"  {C_GREEN}[+] Web Service:{C_RESET} {C_CYAN}{svc['url']}{C_RESET} [{C_YELLOW}{svc['status']}{C_RESET}]")
                print(f"      Server: {C_WHITE}{svc['server']}{C_RESET} | Title: {C_WHITE}{svc['title']}{C_RESET}")

    # ── Phase 4: WAF Detection ────────────────────────────────────────────────
    print(f"\n{C_MAGENTA}{C_BOLD}[PHASE 4] Web Application Firewall (WAF) Fingerprinting{C_RESET}")
    all_wafs = set()
    for svc in http_services:
        detected = detect_waf(svc.get("headers", {}))
        for w in detected:
            all_wafs.add(w)
    if all_wafs:
        for w in all_wafs:
            print(f"  {C_YELLOW}[!] DETECTED ACTIVE WAF / CDN PROTECTION:{C_RESET} {C_RED}{C_BOLD}{w}{C_RESET}")
    else:
        print(f"  {C_GREEN}[+] No standard Commercial WAF signatures detected (Direct Origin Surface Exposed){C_RESET}")

    # ── Phase 5: Exposed Sensitive Files ──────────────────────────────────────
    print(f"\n{C_MAGENTA}{C_BOLD}[PHASE 5] High-Risk Sensitive Endpoint & Secret Leak Probing{C_RESET}")
    base_url = None
    if http_services:
        # Prefer HTTPS
        https_candidates = [s["url"] for s in http_services if s["url"].startswith("https://")]
        base_url = https_candidates[0] if https_candidates else http_services[0]["url"]
    else:
        base_url = f"https://{domain}"

    print(f"  {C_CYAN}[*] Probing against base:{C_RESET} {C_WHITE}{base_url}{C_RESET}")
    leaks = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(probe_sensitive_path, base_url, path, desc, sev)
            for path, desc, sev in SENSITIVE_PATHS
        ]
        for f in as_completed(futures):
            res = f.result()
            if res:
                leaks.append(res)
                sev_color = C_RED if res["severity"] in ("CRITICAL", "HIGH") else C_YELLOW
                print(f"  {sev_color}[!] FOUND {res['severity']} EXPOSURE:{C_RESET} {C_WHITE}{res['path']}{C_RESET} ({res['desc']}) [{res['status']}]")

    if not leaks:
        print(f"  {C_GREEN}[✓] No baseline secrets or misconfigured repository paths exposed.{C_RESET}")

    # ── Phase 6: Save Dossier ─────────────────────────────────────────────────
    vault = Path.home() / ".asterix_vault" / "bounty" / domain
    vault.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save JSON
    json_path = vault / f"bounty_dossier_{ts}.json"
    dossier = {
        "timestamp": datetime.now().isoformat(),
        "target": domain,
        "ips": ips,
        "subdomains_count": len(subdomains),
        "subdomains": subdomains,
        "open_ports": open_ports,
        "web_services": [{k: v for k, v in s.items() if k != "headers"} for s in http_services],
        "waf_detected": list(all_wafs),
        "exposed_endpoints": leaks,
    }
    json_path.write_text(json.dumps(dossier, indent=2), encoding="utf-8")

    # Save Markdown Report
    md_path = vault / f"bounty_report_{ts}.md"
    md_lines = [
        f"# ASTERIX OS Bug Bounty Reconnaissance Report",
        f"**Target:** `{domain}`  ",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Discovered IPs:** {', '.join(ips)}  ",
        f"**WAF Protection:** {', '.join(all_wafs) if all_wafs else 'None detected'}  ",
        f"\n## 1. Open Port Attack Surface",
    ]
    if open_ports:
        md_lines.append("| Port | Service | Status |")
        md_lines.append("|---|---|---|")
        for p in open_ports:
            md_lines.append(f"| {p['port']}/TCP | {p['service']} | Open |")
    else:
        md_lines.append("No open ports found on primary IP.")

    md_lines.append(f"\n## 2. Web Services Discovered")
    for s in http_services:
        md_lines.append(f"- **URL:** `{s['url']}` (HTTP {s['status']})")
        md_lines.append(f"  - Server: `{s['server']}`")
        md_lines.append(f"  - Title: `{s['title']}`")

    md_lines.append(f"\n## 3. Exposed Sensitive Endpoints ({len(leaks)})")
    if leaks:
        md_lines.append("| Path | Severity | Status | Description |")
        md_lines.append("|---|---|---|---|")
        for l in leaks:
            md_lines.append(f"| `{l['path']}` | **{l['severity']}** | {l['status']} | {l['desc']} |")
    else:
        md_lines.append("No common repository or credential leaks detected.")

    md_lines.append(f"\n## 4. Subdomains ({len(subdomains)})")
    for sub in subdomains:
        md_lines.append(f"- `{sub}`")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\n{SEP}")
    print(f"  {C_GREEN}{C_BOLD}[✓] RECON DOSSIER READY:{C_RESET}")
    print(f"    • Markdown Report: {C_WHITE}{md_path}{C_RESET}")
    print(f"    • JSON Data:       {C_WHITE}{json_path}{C_RESET}")
    print(f"{SEP}\n")

def main():
    if len(sys.argv) < 2:
        print(BANNER)
        print(f"\n  {C_YELLOW}Usage:{C_RESET}  ax bounty <domain_or_url>")
        print(f"  Example: ax bounty example.com")
        print(f"  Example: ax bounty https://target.corp\n")
        sys.exit(1)

    run_bounty(sys.argv[1])

if __name__ == "__main__":
    main()
