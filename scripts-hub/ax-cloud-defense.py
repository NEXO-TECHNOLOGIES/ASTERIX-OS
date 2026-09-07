#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Enterprise Cloud & Online Threat Defense Suite
  Tools: ax takeover, ax ssrf-guard, ax api-sentinel
  Version: 2.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import ssl
import json
import time
import socket
import struct
import urllib.request
import urllib.parse
import ipaddress
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
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗██╗      ██████╗ ██╗   ██╗██████╗ 
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║     ██║     ██║   ██║██║   ██║██║  ██║
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║     ██║     ██║   ██║██║   ██║██║  ██║
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝ 
{C_RESET}{C_MAGENTA}      ASTERIX Cloud & Online Defense (Dangling DNS / SSRF Egress / API Hardener){C_RESET}
"""

# =============================================================================
# 1. AUTONOMOUS DANGLING DNS & SUBDOMAIN TAKEOVER SENTINEL (ax takeover)
# =============================================================================

CLOUD_TAKEOVER_FINGERPRINTS = [
    {
        "provider": "GitHub Pages",
        "cname": ["github.io"],
        "fingerprint": "There isn't a GitHub Pages site here",
        "status_code": 404,
        "remediation": "Remove dangling CNAME or create repository with GitHub Pages enabled under your organization."
    },
    {
        "provider": "AWS S3 Bucket",
        "cname": ["s3.amazonaws.com", "s3-website"],
        "fingerprint": "NoSuchBucket",
        "status_code": 404,
        "remediation": "Immediately create an S3 bucket matching this domain or remove the DNS CNAME/Alias record."
    },
    {
        "provider": "AWS CloudFront",
        "cname": ["cloudfront.net"],
        "fingerprint": "Bad request.<br>The request could not be satisfied.",
        "status_code": 403,
        "remediation": "Claim domain in AWS CloudFront alternate domain names (CNAMEs) or purge the DNS record."
    },
    {
        "provider": "Heroku",
        "cname": ["herokuapp.com", "herokudns.com"],
        "fingerprint": "No such app",
        "status_code": 404,
        "remediation": "Add custom domain to active Heroku application or remove CNAME from DNS zone."
    },
    {
        "provider": "Microsoft Azure App Service",
        "cname": ["azurewebsites.net", "cloudapp.azure.com", "azureedge.net"],
        "fingerprint": "404 Web Site not found",
        "status_code": 404,
        "remediation": "Bind custom domain in Azure Portal under App Service / Custom Domains or delete CNAME."
    },
    {
        "provider": "Cloudflare",
        "cname": ["cloudflare.com"],
        "fingerprint": "Direct IP access not allowed",
        "status_code": 404,
        "remediation": "Add hostname to Cloudflare Custom Hostnames (SSL for SaaS) or delete DNS record."
    },
    {
        "provider": "Vercel",
        "cname": ["vercel.app", "cname.vercel-dns.com"],
        "fingerprint": "The deployment could not be found on Vercel",
        "status_code": 404,
        "remediation": "Link domain in Vercel project settings or delete DNS entry."
    },
    {
        "provider": "Netlify",
        "cname": ["netlify.app", "netlify.com"],
        "fingerprint": "Not Found - Request ID",
        "status_code": 404,
        "remediation": "Claim domain in Netlify site settings or remove dangling CNAME."
    },
    {
        "provider": "Fastly",
        "cname": ["fastly.net"],
        "fingerprint": "Fastly error: unknown domain",
        "status_code": 404,
        "remediation": "Add domain to Fastly service configuration or delete DNS record."
    },
    {
        "provider": "Shopify",
        "cname": ["myshopify.com"],
        "fingerprint": "Sorry, this shop is currently unavailable",
        "status_code": 404,
        "remediation": "Attach domain to active Shopify store or delete DNS record."
    },
    {
        "provider": "Zendesk",
        "cname": ["zendesk.com"],
        "fingerprint": "Help Center Closed",
        "status_code": 404,
        "remediation": "Map host in Zendesk Help Center settings or remove DNS CNAME."
    },
    {
        "provider": "WordPress.com",
        "cname": ["wordpress.com"],
        "fingerprint": "Do you want to register",
        "status_code": 404,
        "remediation": "Claim domain in WordPress.com blog settings or delete CNAME record."
    },
    {
        "provider": "Ghost",
        "cname": ["ghost.io"],
        "fingerprint": "The thing you were looking for is no longer here",
        "status_code": 404,
        "remediation": "Claim Ghost custom domain or remove DNS CNAME."
    },
    {
        "provider": "Surge.sh",
        "cname": ["surge.sh"],
        "fingerprint": "project not found",
        "status_code": 404,
        "remediation": "Run 'surge --domain <domain>' to claim or remove CNAME."
    },
    {
        "provider": "Bitbucket",
        "cname": ["bitbucket.io"],
        "fingerprint": "Repository not found",
        "status_code": 404,
        "remediation": "Create Bitbucket Pages repository or remove CNAME from DNS."
    },
    {
        "provider": "Fly.io",
        "cname": ["fly.dev", "edgeapp.net"],
        "fingerprint": "404 Not Found",
        "status_code": 404,
        "remediation": "Claim certificate via 'fly certs add' or purge CNAME record."
    }
]

class TakeoverSentinel:
    """Detects and alerts on dangling DNS CNAME pointers and unclaimed cloud assets."""

    @staticmethod
    def _query_cname_udp(domain: str, dns_server: str = "8.8.8.8", timeout: float = 2.0) -> Optional[str]:
        """Queries DNS server for CNAME record using raw UDP socket (100% standard library)."""
        try:
            tid = os.urandom(2)
            flags = b"\x01\x00"
            qdcount = b"\x00\x01"
            ancount = b"\x00\x00"
            nscount = b"\x00\x00"
            arcount = b"\x00\x00"
            header = tid + flags + qdcount + ancount + nscount + arcount

            qname = b""
            for part in domain.strip(".").split("."):
                qname += bytes([len(part)]) + part.encode("ascii")
            qname += b"\x00"
            qtype = b"\x00\x05" # Type 5: CNAME
            qclass = b"\x00\x01" # Class 1: IN
            packet = header + qname + qtype + qclass

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout)
            sock.sendto(packet, (dns_server, 53))
            resp, _ = sock.recvfrom(1024)
            sock.close()

            if len(resp) < 12:
                return None

            ans_count = struct.unpack("!H", resp[6:8])[0]
            if ans_count == 0:
                return None

            offset = 12
            while offset < len(resp) and resp[offset] != 0:
                offset += resp[offset] + 1
            offset += 5

            for _ in range(ans_count):
                if offset >= len(resp):
                    break
                if resp[offset] & 0xC0 == 0xC0:
                    offset += 2
                else:
                    while offset < len(resp) and resp[offset] != 0:
                        offset += resp[offset] + 1
                    offset += 1

                if offset + 10 > len(resp):
                    break

                rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", resp[offset:offset+10])
                offset += 10
                if rtype == 5:
                    cname_parts = []
                    c_offset = offset
                    end_offset = offset + rdlength
                    while c_offset < end_offset:
                        length = resp[c_offset]
                        if length == 0:
                            break
                        if length & 0xC0 == 0xC0:
                            ptr = struct.unpack("!H", resp[c_offset:c_offset+2])[0] & 0x3FFF
                            while ptr < len(resp) and resp[ptr] != 0:
                                l = resp[ptr]
                                cname_parts.append(resp[ptr+1:ptr+1+l].decode("ascii", errors="ignore"))
                                ptr += l + 1
                            break
                        else:
                            cname_parts.append(resp[c_offset+1:c_offset+1+length].decode("ascii", errors="ignore"))
                            c_offset += length + 1
                    return ".".join(cname_parts).lower()
                offset += rdlength
        except Exception:
            pass
        return None

    @staticmethod
    def audit_domain(target: str):
        print(BANNER)
        clean_target = target.strip()
        if clean_target.startswith("http://") or clean_target.startswith("https://"):
            clean_target = urllib.parse.urlparse(clean_target).netloc
        clean_target = clean_target.split(":")[0].strip()

        print(f"  {C_CYAN}{C_BOLD}[SUBDOMAIN TAKEOVER SENTINEL] Auditing Target:{C_RESET} {clean_target}\n")

        cname = TakeoverSentinel._query_cname_udp(clean_target)
        if not cname:
            try:
                hostname, aliases, _ = socket.gethostbyname_ex(clean_target)
                if aliases:
                    cname = aliases[0].lower()
                elif hostname.lower() != clean_target.lower():
                    cname = hostname.lower()
            except Exception:
                pass

        if cname:
            print(f"  • {C_BOLD}Discovered CNAME Pointer:{C_RESET} {C_YELLOW}{cname}{C_RESET}")
        else:
            print(f"  • {C_BOLD}Discovered CNAME Pointer:{C_RESET} {C_DIM}(Direct A/AAAA Record - No CNAME chain){C_RESET}")

        matched_provider = None
        if cname:
            for item in CLOUD_TAKEOVER_FINGERPRINTS:
                for c_pat in item["cname"]:
                    if c_pat in cname:
                        matched_provider = item
                        break
                if matched_provider:
                    break

        if not matched_provider:
            for item in CLOUD_TAKEOVER_FINGERPRINTS:
                for c_pat in item["cname"]:
                    if c_pat in clean_target:
                        matched_provider = item
                        break
                if matched_provider:
                    break

        body_text = ""
        http_code = 0
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        for proto in ("https://", "http://"):
            try:
                url = f"{proto}{clean_target}"
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ASTERIX-Security-Auditor/2.0"}
                )
                with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                    http_code = response.getcode()
                    body_text = response.read(65536).decode("utf-8", errors="ignore")
                    break
            except urllib.error.HTTPError as e:
                http_code = e.code
                try:
                    body_text = e.read(65536).decode("utf-8", errors="ignore")
                except Exception:
                    pass
                break
            except Exception:
                continue

        takeover_vulnerable = False
        active_finding = None

        if matched_provider:
            if matched_provider["fingerprint"].lower() in body_text.lower():
                takeover_vulnerable = True
                active_finding = matched_provider
        else:
            for item in CLOUD_TAKEOVER_FINGERPRINTS:
                if item["fingerprint"].lower() in body_text.lower() and http_code in (404, 403, 502):
                    takeover_vulnerable = True
                    active_finding = item
                    break

        if takeover_vulnerable and active_finding:
            print(f"\n  {C_RED}{C_BOLD}🚨 CRITICAL: HIGH-CONFIDENCE SUBDOMAIN TAKEOVER DETECTED!{C_RESET}")
            print(f"  {C_RED}Adversaries can claim this domain and seize full corporate identity!{C_RESET}\n")
            print(f"  {C_BOLD}Vulnerable Target:{C_RESET}   {clean_target}")
            print(f"  {C_BOLD}Targeted Service:{C_RESET}    {C_YELLOW}{active_finding['provider']}{C_RESET}")
            if cname:
                print(f"  {C_BOLD}Dangling CNAME:{C_RESET}      {cname}")
            print(f"  {C_BOLD}HTTP Status:{C_RESET}        {http_code}")
            print(f"  {C_BOLD}Matched Pattern:{C_RESET}    \"{active_finding['fingerprint']}\"\n")
            print(f"  {C_WHITE}{C_BOLD}IMMEDIATE REMEDIATION ACTION:{C_RESET}")
            print(f"  1. {active_finding['remediation']}")
            print(f"  2. Delete dangling DNS CNAME record from DNS registrar/Route53/Cloudflare zone immediately.\n")
        else:
            print(f"\n  {C_GREEN}{C_BOLD}✓ SECURE: No dangling cloud takeover signatures detected.{C_RESET}")
            if cname:
                print(f"  {C_DIM}CNAME points to active or secured provider endpoint (HTTP {http_code}).{C_RESET}\n")
            else:
                print(f"  {C_DIM}Domain does not expose unclaimed cloud resource fingerprints.{C_RESET}\n")


# =============================================================================
# 2. AUTONOMOUS SSRF & CLOUD METADATA SHIELD (ax ssrf-guard)
# =============================================================================

CLOUD_METADATA_HOSTS = {
    "169.254.169.254": "AWS EC2 / Azure / GCP IMDS Cloud Metadata",
    "169.254.169.253": "AWS Route53 VPC Resolver",
    "metadata.google.internal": "Google Cloud Platform (GCP) Metadata",
    "100.100.100.200": "Alibaba Cloud Metadata",
    "instance-data": "OpenStack / Eucalyptus Instance Metadata",
    "169.254.169.254:80": "AWS IMDSv1",
}

class SSRFGuard:
    """Analyzes outbound webhook and request URLs to prevent SSRF and cloud credential theft."""

    @staticmethod
    def _unmask_ip_address(raw_host: str) -> Tuple[Optional[ipaddress.IPv4Address | ipaddress.IPv6Address], str]:
        """Unmasks integer, octal, hex, and IPv6 obfuscated IP representations."""
        host = raw_host.strip("[]")
        
        # 1. Decimal Integer IP (e.g. 2130706433 -> 127.0.0.1)
        if host.isdigit():
            try:
                ip_int = int(host)
                if 0 <= ip_int <= 0xFFFFFFFF:
                    return ipaddress.IPv4Address(ip_int), f"Integer Decimal IP ({host})"
            except Exception:
                pass

        # 2. Hex IP (e.g. 0x7f000001 or 0x7f.0.0.1)
        if host.startswith("0x") and "." not in host:
            try:
                ip_int = int(host, 16)
                if 0 <= ip_int <= 0xFFFFFFFF:
                    return ipaddress.IPv4Address(ip_int), f"Hexadecimal IP ({host})"
            except Exception:
                pass

        # 3. Dotted Octal/Hex/Mixed IP (e.g. 0177.0.0.1 or 0x7f.0.0.1)
        parts = host.split(".")
        if len(parts) == 4:
            try:
                octets = []
                is_obfuscated = False
                for p in parts:
                    if p.startswith("0x") or p.startswith("0X"):
                        octets.append(int(p, 16))
                        is_obfuscated = True
                    elif p.startswith("0") and len(p) > 1:
                        octets.append(int(p, 8))
                        is_obfuscated = True
                    else:
                        octets.append(int(p, 10))
                if all(0 <= o <= 255 for o in octets):
                    ip_obj = ipaddress.IPv4Address(".".join(str(o) for o in octets))
                    msg = "Octal/Hex Dotted IP" if is_obfuscated else "Standard IPv4"
                    return ip_obj, msg
            except Exception:
                pass

        # 4. Standard IPv4 / IPv6
        try:
            ip_obj = ipaddress.ip_address(host)
            if isinstance(ip_obj, ipaddress.IPv6Address) and ip_obj.ipv4_mapped:
                return ip_obj.ipv4_mapped, "IPv4-Mapped IPv6 Tunnel"
            return ip_obj, "Direct IP Address"
        except Exception:
            pass

        return None, "Hostname"

    @staticmethod
    def audit_target(raw_input: str):
        print(BANNER)
        target = raw_input.strip()
        parsed = urllib.parse.urlparse(target)

        if not parsed.scheme:
            parsed = urllib.parse.urlparse("http://" + target)

        hostname = (parsed.hostname or target).lower().strip()
        port = parsed.port or (443 if parsed.scheme == "https" else 80)

        print(f"  {C_CYAN}{C_BOLD}[SSRF & CLOUD METADATA SHIELD] Analyzing Outbound Target:{C_RESET} {target}\n")
        print(f"  • {C_BOLD}Evaluated Host:{C_RESET} {hostname}")
        print(f"  • {C_BOLD}Target Port:{C_RESET}    {port}")
        print(f"  • {C_BOLD}Protocol:{C_RESET}       {parsed.scheme or 'http'}\n")

        risks = []

        if hostname in CLOUD_METADATA_HOSTS:
            risks.append(f"CRITICAL CLOUD METADATA ENDPOINT: '{hostname}' ({CLOUD_METADATA_HOSTS[hostname]})")

        direct_ip, ip_type = SSRFGuard._unmask_ip_address(hostname)

        resolved_ips = []
        if direct_ip:
            resolved_ips.append((direct_ip, ip_type))
        else:
            try:
                addrs1 = socket.getaddrinfo(hostname, port, socket.AF_INET)
                time.sleep(0.05)
                addrs2 = socket.getaddrinfo(hostname, port, socket.AF_INET)
                
                ips1 = {item[4][0] for item in addrs1}
                ips2 = {item[4][0] for item in addrs2}
                if ips1 != ips2:
                    risks.append(f"DNS REBINDING DETECTED: Hostname dynamically toggles IPs ({ips1} vs {ips2})")

                for ip_str in (ips1 | ips2):
                    try:
                        resolved_ips.append((ipaddress.ip_address(ip_str), "Resolved Hostname IP"))
                    except Exception:
                        pass
            except socket.gaierror as e:
                print(f"  {C_YELLOW}[!] Notice: Hostname failed DNS resolution ({e}). Evaluating structural rules.{C_RESET}\n")

        for ip_obj, origin in resolved_ips:
            ip_str = str(ip_obj)
            if ip_str == "169.254.169.254":
                risks.append(f"CLOUD METADATA THEFT (IMDSv1/v2): Targets AWS/GCP/Azure credential service via {origin} [{ip_str}]")
            elif ip_obj.is_link_local:
                risks.append(f"LINK-LOCAL ADDR (RFC 3927): Internal network reachability violation via {origin} [{ip_str}]")
            
            if ip_obj.is_loopback:
                risks.append(f"LOOPBACK / LOCALHOST FORGERY: Direct host exploitation attempt via {origin} [{ip_str}]")

            if ip_obj.is_private and not ip_obj.is_link_local and not ip_obj.is_loopback:
                risks.append(f"RFC 1918 PRIVATE NETWORK ACCESS: Egress to internal intranet via {origin} [{ip_str}]")

            if ip_obj.is_multicast:
                risks.append(f"MULTICAST EGRESS: Non-routable address targeting via {origin} [{ip_str}]")
            if ip_obj.is_reserved:
                risks.append(f"RESERVED SUBNET VIOLATION: Access to special-purpose IANA space via {origin} [{ip_str}]")

        if risks:
            print(f"  {C_RED}{C_BOLD}🚨 EGRESS BLOCKED: DANGEROUS SSRF / CLOUD THEFT THREAT DETECTED!{C_RESET}\n")
            print(f"  {C_WHITE}{C_BOLD}Identified Threat Violations:{C_RESET}")
            for r in risks:
                print(f"    • {C_RED}{C_BOLD}{r}{C_RESET}")
            print(f"\n  {C_YELLOW}{C_BOLD}[DEFENSIVE REMEDIATION CODE]{C_RESET}")
            print(f"  Paste the following drop-in validation filter in your application backend:\n")
            print(f"""{C_CYAN}# Python Safe URL Egress Validator:
import ipaddress, socket, urllib.parse

def is_safe_outbound_url(url: str) -> bool:
    try:
        host = urllib.parse.urlparse(url).hostname
        if not host: return False
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
    except Exception:
        return False
{C_RESET}""")
        else:
            print(f"  {C_GREEN}{C_BOLD}✓ SAFE EGRESS: URL resolves exclusively to public, routable IP space.{C_RESET}")
            print(f"  {C_DIM}Destination '{hostname}' passed RFC 1918, IMDS cloud metadata, and loopback checks.{C_RESET}\n")


# =============================================================================
# 3. AUTONOMOUS API HARDENER & EXPOSURE SCANNER (ax api-sentinel)
# =============================================================================

SECURITY_HEADERS = {
    "Strict-Transport-Security": "Enforces HTTPS connections, prevents SSL-stripping MITM attacks",
    "Content-Security-Policy": "Restricts script sources, prevents Cross-Site Scripting (XSS) and data exfiltration",
    "X-Content-Type-Options": "Prevents MIME-sniffing attacks (Must be 'nosniff')",
    "X-Frame-Options": "Prevents Clickjacking UI redressing (Must be 'DENY' or 'SAMEORIGIN')",
    "Referrer-Policy": "Prevents leaking sensitive paths/tokens in HTTP Referer headers",
    "Permissions-Policy": "Restricts browser camera, microphone, and geolocation APIs"
}

SHADOW_API_ROUTES = [
    "/swagger.json",
    "/openapi.json",
    "/v2/api-docs",
    "/v3/api-docs",
    "/api-docs",
    "/graphql",
    "/actuator/health",
    "/actuator/env",
    "/metrics",
    "/.well-known/security.txt"
]

class APISentinel:
    """Audits API endpoints for missing defense headers, CORS vulnerabilities, and shadow route exposure."""

    @staticmethod
    def audit(target: str):
        print(BANNER)
        raw_url = target.strip()
        if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
            raw_url = "https://" + raw_url

        parsed = urllib.parse.urlparse(raw_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        print(f"  {C_CYAN}{C_BOLD}[API DEFENSE SENTINEL] Auditing API Endpoint:{C_RESET} {raw_url}\n")

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        headers_found = {}
        server_info = {}
        cors_reflected = False
        cors_creds = False

        try:
            req = urllib.request.Request(
                raw_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ASTERIX-API-Sentinel/2.0",
                    "Origin": "https://evil-attacker.com",
                    "Accept": "application/json, text/html, */*"
                }
            )
            with urllib.request.urlopen(req, timeout=6, context=ctx) as resp:
                headers_found = {k.title(): v for k, v in resp.headers.items()}
        except urllib.error.HTTPError as e:
            headers_found = {k.title(): v for k, v in e.headers.items()}
        except Exception as e:
            print(f"  {C_RED}[!] Error reaching target endpoint: {e}{C_RESET}\n")
            return

        acao = headers_found.get("Access-Control-Allow-Origin", "")
        acac = headers_found.get("Access-Control-Allow-Credentials", "")
        if "evil-attacker.com" in acao or acao == "*":
            cors_reflected = True
            if acac.lower() == "true":
                cors_creds = True

        leaks = []
        for h in ("Server", "X-Powered-By", "X-Aspnet-Version", "X-Runtime"):
            if h in headers_found:
                leaks.append(f"{h}: {headers_found[h]}")

        missing_headers = []
        for h, desc in SECURITY_HEADERS.items():
            if h not in headers_found:
                missing_headers.append((h, desc))

        print(f"  {C_WHITE}{C_BOLD}1. SHADOW API & DOCUMENTATION PROBE:{C_RESET}")
        exposed_routes = []
        for route in SHADOW_API_ROUTES:
            probe_url = base_url + route
            try:
                p_req = urllib.request.Request(
                    probe_url,
                    headers={"User-Agent": "ASTERIX-API-Sentinel/2.0"}
                )
                with urllib.request.urlopen(p_req, timeout=3, context=ctx) as p_resp:
                    if p_resp.getcode() == 200:
                        content_type = p_resp.headers.get("Content-Type", "")
                        exposed_routes.append((route, p_resp.getcode(), content_type))
            except urllib.error.HTTPError as he:
                if he.code in (200, 401, 403):
                    exposed_routes.append((route, he.code, "Restricted/Auth Required"))
            except Exception:
                pass

        if exposed_routes:
            for route, code, ctype in exposed_routes:
                sev = f"{C_RED}[CRITICAL]{C_RESET}" if code == 200 and "security" not in route else f"{C_YELLOW}[WARNING]{C_RESET}"
                print(f"    {sev} Route {C_BOLD}{route}{C_RESET} returned HTTP {code} ({ctype})")
        else:
            print(f"    {C_GREEN}✓ No unauthenticated Swagger, OpenAPI, or actuator routes exposed.{C_RESET}")

        print(f"\n  {C_WHITE}{C_BOLD}2. CORS CROSS-ORIGIN POLICY AUDIT:{C_RESET}")
        if cors_creds:
            print(f"    {C_RED}{C_BOLD}🚨 CRITICAL VULNERABILITY: Arbitrary Origin Reflection with Credentials!{C_RESET}")
            print(f"    ↳ Access-Control-Allow-Origin: {acao}")
            print(f"    ↳ Access-Control-Allow-Credentials: true (Permits cross-site session theft!)")
        elif cors_reflected and acao == "*":
            print(f"    {C_YELLOW}⚠ Wildcard CORS: 'Access-Control-Allow-Origin: *' allows any website to read API data.{C_RESET}")
        else:
            print(f"    {C_GREEN}✓ Secure CORS: External attacker origin was not reflected.{C_RESET}")

        print(f"\n  {C_WHITE}{C_BOLD}3. DEFENSIVE SECURITY HEADERS POSTURE:{C_RESET}")
        if missing_headers:
            for h, desc in missing_headers:
                print(f"    {C_RED}✗ Missing:{C_RESET} {C_BOLD}{h}{C_RESET} — {C_DIM}{desc}{C_RESET}")
        else:
            print(f"    {C_GREEN}✓ Perfect score: All standard defensive headers configured.{C_RESET}")

        if leaks:
            print(f"\n  {C_WHITE}{C_BOLD}4. SENSITIVE INFRASTRUCTURE LEAKAGE:{C_RESET}")
            for l in leaks:
                print(f"    {C_YELLOW}⚠ Header Leak:{C_RESET} {l}")

        host_name = parsed.netloc.split(":")[0]
        print(f"\n  {C_CYAN}{C_BOLD}========================================================================={C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}AUTOMATED NGINX / CADDY HARDENING REMEDIATION CONFIGURATION{C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}========================================================================={C_RESET}\n")
        print(f"""{C_WHITE}# Copy-paste into your /etc/nginx/sites-available/{host_name} (inside server block):{C_RESET}
{C_GREEN}# ASTERIX Automated Security Hardening Policy
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'none';" always;
server_tokens off;
proxy_hide_header X-Powered-By;
{C_RESET}""")


# =============================================================================
# CLI DISPATCHER
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Enterprise Cloud & Online Threat Defense Suite",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    takeover_parser = subparsers.add_parser("takeover", help="Autonomous cloud subdomain & dangling DNS sentinel")
    takeover_parser.add_argument("domain", help="Domain or subdomain to audit")

    ssrf_parser = subparsers.add_parser("ssrf-guard", help="SSRF & cloud metadata egress defense shield")
    ssrf_parser.add_argument("target", help="URL or IP address to evaluate for SSRF and cloud metadata theft")

    api_parser = subparsers.add_parser("api-sentinel", help="Autonomous API hardener & exposure scanner")
    api_parser.add_argument("url", help="API URL or hostname to audit")

    if len(sys.argv) > 1 and sys.argv[1] not in ("takeover", "ssrf-guard", "api-sentinel", "-h", "--help"):
        arg1 = sys.argv[1]
        if arg1.startswith("http://") or arg1.startswith("https://"):
            sys.argv.insert(1, "ssrf-guard")
        else:
            sys.argv.insert(1, "takeover")

    args = parser.parse_args()

    if args.subcommand == "takeover":
        TakeoverSentinel.audit_domain(args.domain)
    elif args.subcommand == "ssrf-guard":
        SSRFGuard.audit_target(args.target)
    elif args.subcommand == "api-sentinel":
        APISentinel.audit(args.url)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
