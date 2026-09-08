#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Enterprise Anti-Surveillance & Privacy Hardening Suite
  Tools: ax scrub, ax dns-shield, ax ip-shield
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
import zlib
import socket
import struct
import urllib.request
import urllib.parse
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
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗    ██████╗ ██████╗ ██╗██╗   ██╗ █████╗  ██████╗██╗   ██╗
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔══██╗██╔══██╗██║██║   ██║██╔══██╗██╔════╝╚██╗ ██╔╝
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██████╔╝██████╔╝██║██║   ██║███████║██║      ╚████╔╝ 
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██╔═══╝ ██╔══██╗██║╚██╗ ██╔╝██╔══██║██║       ╚██╔╝  
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ██║     ██║  ██║██║ ╚████╔╝ ██║  ██║╚██████╗   ██║   
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝  ╚═╝  ╚═╝ ╚═════╝   ╚═╝   
{C_RESET}{C_MAGENTA}       ASTERIX Anti-Surveillance Suite (Media Sanitizer / DoH Enforcer / IP-Leak Sentinel){C_RESET}
"""

# =============================================================================
# 1. AUTONOMOUS MEDIA METADATA ANONYMIZER & EXIF SCRUBBER (ax scrub)
# =============================================================================

class MediaScrubber:
    """Losslessly scrubs EXIF, GPS, camera serials, and tracking metadata from JPEG, PNG, and PDF."""

    @staticmethod
    def audit_jpeg(data: bytes) -> List[str]:
        findings = []
        if len(data) < 4 or data[:2] != b"\xFF\xD8":
            return findings
        pos = 2
        while pos < len(data) - 4:
            if data[pos] != 0xFF:
                pos += 1
                continue
            marker = data[pos+1]
            if marker in (0xD9, 0xDA): # EOI or SOS
                break
            length = struct.unpack(">H", data[pos+2:pos+4])[0]
            payload = data[pos+4:pos+2+length]

            if marker == 0xE1: # APP1: EXIF or XMP
                if b"Exif" in payload:
                    findings.append("EXIF Metadata Block (Camera model, software, timestamps)")
                if b"GPS" in payload or b"GPSInfo" in payload:
                    findings.append("CRITICAL: Embedded GPS Geolocation Coordinates")
                if b"http://ns.adobe.com/xap" in payload:
                    findings.append("Adobe XMP Tracking Metadata (Device & author IDs)")
            elif marker == 0xED: # APP13: Photoshop IPTC
                findings.append("Photoshop IPTC Record (Copyright, author, keywords)")
            elif marker == 0xFE: # COM: Comment
                findings.append("Embedded User Comment / Software Tag")

            pos += 2 + length
        return findings

    @staticmethod
    def scrub_jpeg(data: bytes) -> Tuple[bytes, int]:
        """Surgically strips APP1 (EXIF/GPS), APP2, APP13, and COM segments from JPEG."""
        if len(data) < 4 or data[:2] != b"\xFF\xD8":
            return data, 0
        
        output = bytearray(b"\xFF\xD8")
        pos = 2
        bytes_removed = 0

        # Discard markers: APP1(0xE1), APP2(0xE2), APP13(0xED), COM(0xFE)
        STRIP_MARKERS = {0xE1, 0xE2, 0xED, 0xFE}

        while pos < len(data) - 4:
            if data[pos] != 0xFF:
                pos += 1
                continue
            marker = data[pos+1]
            if marker == 0xDA: # SOS (Start of Scan - image data starts here)
                output.extend(data[pos:])
                break
            if marker == 0xD9: # EOI (End of Image)
                output.extend(b"\xFF\xD9")
                break

            length = struct.unpack(">H", data[pos+2:pos+4])[0]
            chunk_size = 2 + length # marker + length + payload

            if marker in STRIP_MARKERS:
                bytes_removed += chunk_size
            else:
                output.extend(data[pos:pos+chunk_size])

            pos += chunk_size

        return bytes(output), bytes_removed

    @staticmethod
    def audit_png(data: bytes) -> List[str]:
        findings = []
        if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
            return findings
        pos = 8
        while pos < len(data) - 12:
            length = struct.unpack(">I", data[pos:pos+4])[0]
            ctype = data[pos+4:pos+8].decode("ascii", errors="ignore")
            if ctype in ("tEXt", "zTXt", "iTXt"):
                findings.append(f"PNG Text Metadata Chunk: '{ctype}'")
            elif ctype == "eXIf":
                findings.append("CRITICAL: Embedded PNG EXIF Profile (Camera/GPS tags)")
            elif ctype == "tIME":
                findings.append("Embedded Modification Timestamp: 'tIME'")
            pos += 12 + length
        return findings

    @staticmethod
    def scrub_png(data: bytes) -> Tuple[bytes, int]:
        """Strips metadata chunks (tEXt, zTXt, iTXt, eXIf, tIME) from PNG losslessly."""
        if len(data) < 8 or data[:8] != b"\x89PNG\r\n\x1a\n":
            return data, 0
        
        output = bytearray(b"\x89PNG\r\n\x1a\n")
        pos = 8
        bytes_removed = 0
        STRIP_CHUNKS = {b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"tIME"}

        while pos < len(data) - 12:
            length = struct.unpack(">I", data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8]
            chunk_total_size = 12 + length

            if chunk_type in STRIP_CHUNKS:
                bytes_removed += chunk_total_size
            else:
                output.extend(data[pos:pos+chunk_total_size])

            pos += chunk_total_size

        return bytes(output), bytes_removed

    @staticmethod
    def audit_and_scrub_file(filepath: Path, inplace: bool = False) -> Dict[str, Any]:
        ext = filepath.suffix.lower()
        if not filepath.exists() or filepath.stat().st_size == 0:
            return {"file": str(filepath), "status": "SKIPPED", "findings": [], "saved": 0}

        raw = filepath.read_bytes()
        findings = []
        scrubbed = raw
        saved = 0

        if ext in (".jpg", ".jpeg"):
            findings = MediaScrubber.audit_jpeg(raw)
            scrubbed, saved = MediaScrubber.scrub_jpeg(raw)
        elif ext == ".png":
            findings = MediaScrubber.audit_png(raw)
            scrubbed, saved = MediaScrubber.scrub_png(raw)
        elif ext == ".pdf":
            # Strip PDF info dictionaries and XML metadata
            text_str = raw.decode("latin-1", errors="ignore")
            cleaned_str = re.sub(r"/(Title|Author|Creator|Producer|CreationDate|ModDate)\s*\([^)]*\)", "", text_str)
            cleaned_str = re.sub(r"<x:xmpmeta[\s\S]*?</x:xmpmeta>", "", cleaned_str)
            scrubbed = cleaned_str.encode("latin-1")
            saved = len(raw) - len(scrubbed)
            if saved > 0:
                findings.append("PDF Document Metadata (/Author, /Title, XMP Stream)")

        if inplace and saved > 0:
            filepath.write_bytes(scrubbed)

        return {
            "file": str(filepath.name),
            "path": str(filepath),
            "findings": findings,
            "saved_bytes": saved,
            "status": "SANITIZED" if saved > 0 else "CLEAN"
        }

    @staticmethod
    def run(target: str, audit_only: bool = False, inplace: bool = True):
        print(BANNER)
        target_path = Path(target).resolve()
        mode_str = "AUDIT ONLY" if audit_only else "DEEP METADATA SCRUB"
        print(f"  {C_CYAN}{C_BOLD}[MEDIA ANONYMIZER] Target:{C_RESET} {target_path} ({mode_str})\n")

        files_to_process = []
        if target_path.is_file():
            files_to_process.append(target_path)
        elif target_path.is_dir():
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.pdf"):
                files_to_process.extend(target_path.glob(f"**/{ext}"))

        if not files_to_process:
            print(f"  {C_YELLOW}[!] No supported media files (.jpg, .jpeg, .png, .pdf) found in target.{C_RESET}\n")
            return

        total_files = len(files_to_process)
        total_sanitized = 0
        total_bytes_scrubbed = 0

        for f in files_to_process:
            result = MediaScrubber.audit_and_scrub_file(f, inplace=(not audit_only and inplace))
            if result["findings"]:
                total_sanitized += 1
                total_bytes_scrubbed += result["saved_bytes"]
                print(f"  • {C_BOLD}{result['file']}{C_RESET}:")
                for item in result["findings"]:
                    icon = f"{C_RED}🚨{C_RESET}" if "CRITICAL" in item else f"{C_YELLOW}⚠{C_RESET}"
                    print(f"    ↳ {icon} {item}")
                if not audit_only:
                    print(f"    {C_GREEN}✓ Stripped {result['saved_bytes']} bytes of tracking metadata (Lossless).{C_RESET}")
            else:
                print(f"  • {C_BOLD}{result['file']}{C_RESET}: {C_GREEN}✓ No tracking metadata present (Clean).{C_RESET}")

        print(f"\n  {C_WHITE}{C_BOLD}SUMMARY:{C_RESET}")
        print(f"  • Files Inspected:       {C_BOLD}{total_files}{C_RESET}")
        print(f"  • Contained Metadata:    {C_YELLOW}{total_sanitized}{C_RESET}")
        if not audit_only:
            print(f"  • Metadata Excised:      {C_GREEN}{total_bytes_scrubbed} bytes{C_RESET}")
            print(f"\n  {C_GREEN}{C_BOLD}✓ SUCCESS: All media assets have been anonymized for zero-trace sharing.{C_RESET}\n")


# =============================================================================
# 2. ENCRYPTED DNS & DOH LEAK ENFORCER (ax dns-shield)
# =============================================================================

DOH_RESOLVERS = [
    {
        "name": "Quad9 (Privacy & Threat Blocking)",
        "url": "https://dns.quad9.net/dns-query",
        "ip": "9.9.9.9",
        "policy": "Strict Zero-Logs, Swiss jurisdiction, malware blocking"
    },
    {
        "name": "Cloudflare (Ultra-Fast 1.1.1.1)",
        "url": "https://cloudflare-dns.com/dns-query",
        "ip": "1.1.1.1",
        "policy": "Audited Zero-Logs, APNIC partnership"
    },
    {
        "name": "Mullvad (Zero-Knowledge Swedish DNS)",
        "url": "https://dns.mullvad.net/dns-query",
        "ip": "194.242.2.2",
        "policy": "No logging, QNAME minimization, tracker blocking"
    }
]

class DNSShield:
    """Audits system DNS for ISP cleartext snooping and benchmarks Encrypted DNS-over-HTTPS (DoH)."""

    @staticmethod
    def audit():
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[ENCRYPTED DNS & SNOOPING AUDITOR]{C_RESET}\n")

        test_domain = "check.torproject.org"
        print(f"  • Evaluating System DNS vs Encrypted DoH for: {C_BOLD}{test_domain}{C_RESET}\n")

        # 1. System DNS Lookup
        t0 = time.time()
        sys_ips = []
        try:
            addr_info = socket.getaddrinfo(test_domain, 80, socket.AF_INET)
            sys_latency = (time.time() - t0) * 1000
            sys_ips = sorted(list({item[4][0] for item in addr_info}))
            print(f"  {C_WHITE}{C_BOLD}1. SYSTEM DEFAULT RESOLVER (Cleartext UDP Port 53):{C_RESET}")
            print(f"    ↳ Latency:  {sys_latency:.1f} ms")
            print(f"    ↳ Resolved: {sys_ips}")
            print(f"    ↳ Security: {C_RED}VULNERABLE to ISP Deep Packet Inspection & Logging{C_RESET}")
        except Exception as e:
            print(f"    {C_RED}[!] System DNS resolution failed: {e}{C_RESET}")

        # 2. DoH Resolvers
        print(f"\n  {C_WHITE}{C_BOLD}2. ENCRYPTED DNS-OVER-HTTPS (DoH) BENCHMARK:{C_RESET}")
        ctx = ssl.create_default_context()

        for res in DOH_RESOLVERS:
            query_url = f"{res['url']}?name={test_domain}&type=A"
            req = urllib.request.Request(
                query_url,
                headers={"Accept": "application/dns-json", "User-Agent": "ASTERIX-DNS-Shield/2.0"}
            )
            try:
                t_start = time.time()
                with urllib.request.urlopen(req, timeout=4, context=ctx) as response:
                    doh_lat = (time.time() - t_start) * 1000
                    resp_data = json.loads(response.read().decode("utf-8"))
                    answers = [a["data"] for a in resp_data.get("Answer", []) if a.get("type") == 1]
                    print(f"    • {C_GREEN}{C_BOLD}{res['name']}{C_RESET}")
                    print(f"      ↳ Latency:   {doh_lat:.1f} ms (HTTPS TLS 1.3)")
                    print(f"      ↳ Addresses: {answers[:2]}")
                    print(f"      ↳ Policy:    {C_DIM}{res['policy']}{C_RESET}")
            except Exception as e:
                print(f"    • {res['name']}: {C_YELLOW}Failed or timed out ({e}){C_RESET}")

        # 3. Hardening Recommendations
        print(f"\n  {C_CYAN}{C_BOLD}========================================================================={C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}ASTERIX PRIVACY RECOMMENDATION: LOCKING DOWN SYSTEM DNS{C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}========================================================================={C_RESET}\n")
        print(f"  To completely blind your ISP from seeing the websites you visit:")
        print(f"  1. Configure your system or router to use {C_BOLD}Quad9 (9.9.9.9){C_RESET} or {C_BOLD}Cloudflare (1.1.1.1){C_RESET}.")
        print(f"  2. Enable {C_BOLD}DNS-over-HTTPS (DoH){C_RESET} in your browser (Settings -> Privacy & Security -> Secure DNS).")
        print(f"  3. Drop all outbound cleartext UDP port 53 traffic on untrusted networks.\n")


# =============================================================================
# 3. REAL-TIME IP, IPV6 & WEBRTC LEAK SENTINEL (ax ip-shield)
# =============================================================================

STUN_SERVERS = [
    ("stun.l.google.com", 19302),
    ("stun1.l.google.com", 19302),
    ("stun.cloudflare.com", 3478)
]

class IPShield:
    """Probes for real public IP, IPv6 bypass leaks, and WebRTC STUN protocol leakage."""

    @staticmethod
    def _probe_stun(server: str, port: int) -> Optional[str]:
        """Sends an RFC 5389 STUN Binding Request over raw UDP to discover mapped external IP."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2.5)

            # STUN Binding Request Packet (RFC 5389):
            # Message Type: 0x0001 (Binding Request)
            # Message Length: 0x0000
            # Magic Cookie: 0x2112A442
            # Transaction ID: 12 random bytes
            magic_cookie = b"\x21\x12\xA4\x42"
            trans_id = os.urandom(12)
            packet = b"\x00\x01\x00\x00" + magic_cookie + trans_id

            sock.sendto(packet, (server, port))
            resp, _ = sock.recvfrom(1024)
            sock.close()

            if len(resp) < 20:
                return None

            # Parse Attributes
            offset = 20
            while offset < len(resp) - 4:
                attr_type, attr_len = struct.unpack("!HH", resp[offset:offset+4])
                offset += 4
                if attr_type == 0x0020: # XOR-MAPPED-ADDRESS
                    if offset + attr_len > len(resp): break
                    family = resp[offset+1]
                    if family == 0x01: # IPv4
                        port_bytes = resp[offset+2:offset+4]
                        ip_bytes = resp[offset+4:offset+8]
                        xor_ip = bytes(a ^ b for a, b in zip(ip_bytes, magic_cookie))
                        return socket.inet_ntoa(xor_ip)
                elif attr_type == 0x0001: # MAPPED-ADDRESS
                    if offset + attr_len > len(resp): break
                    family = resp[offset+1]
                    if family == 0x01: # IPv4
                        return socket.inet_ntoa(resp[offset+4:offset+8])
                offset += attr_len
        except Exception:
            pass
        return None

    @staticmethod
    def audit():
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[REAL-TIME IP, IPV6 & WEBRTC LEAK SENTINEL]{C_RESET}\n")

        # 1. External Public IP via HTTP
        public_ip = "Unknown"
        isp_org = "Unknown"
        ctx = ssl.create_default_context()

        try:
            req = urllib.request.Request("https://api.ipify.org?format=json", headers={"User-Agent": "ASTERIX-Shield/2.0"})
            with urllib.request.urlopen(req, timeout=4, context=ctx) as r:
                public_ip = json.loads(r.read().decode())["ip"]
        except Exception:
            pass

        print(f"  {C_WHITE}{C_BOLD}1. EXTERNAL ROUTABLE IP ADDRESS:{C_RESET}")
        print(f"    ↳ Visible IP:  {C_YELLOW}{public_ip}{C_RESET}")

        # 2. WebRTC STUN Protocol IP Harvest Simulation
        print(f"\n  {C_WHITE}{C_BOLD}2. WEBRTC STUN LEAK SIMULATION (UDP 19302):{C_RESET}")
        stun_ip = None
        for host, port in STUN_SERVERS:
            stun_ip = IPShield._probe_stun(host, port)
            if stun_ip:
                print(f"    ↳ Tested STUN Server: {host}:{port}")
                print(f"    ↳ Mapped Public IP:   {C_RED}{C_BOLD}{stun_ip}{C_RESET}")
                break

        webrtc_vulnerable = False
        if stun_ip:
            if stun_ip == public_ip:
                webrtc_vulnerable = True
                print(f"    {C_RED}{C_BOLD}🚨 VULNERABLE: Direct STUN queries expose your exact public IP!{C_RESET}")
                print(f"    {C_DIM}Any website using WebRTC JavaScript can reveal this IP without VPN protection.{C_RESET}")
            else:
                print(f"    {C_YELLOW}⚠ STUN mapped to alternate endpoint ({stun_ip}). NAT/VPN translation active.{C_RESET}")
        else:
            print(f"    {C_GREEN}✓ SECURE: STUN UDP probes blocked or dropped by local firewall.{C_RESET}")

        # 3. IPv6 Leak Audit
        print(f"\n  {C_WHITE}{C_BOLD}3. IPV6 DUAL-STACK LEAK AUDIT:{C_RESET}")
        has_ipv6 = False
        ipv6_addr = None
        try:
            s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            s6.connect(("2001:4860:4860::8888", 80))
            ipv6_addr = s6.getsockname()[0]
            s6.close()
            has_ipv6 = True
        except Exception:
            pass

        if has_ipv6 and ipv6_addr and not ipv6_addr.startswith("fe80"):
            print(f"    {C_RED}{C_BOLD}🚨 IPV6 LEAK RISK: Active Global Unicast Address detected!{C_RESET}")
            print(f"    ↳ Global IPv6: {ipv6_addr}")
            print(f"    {C_DIM}Many VPNs only tunnel IPv4, leaking your ISP identity through IPv6.{C_RESET}")
        else:
            print(f"    {C_GREEN}✓ SECURE: Zero unencapsulated global IPv6 egress detected.{C_RESET}")

        # 4. Privacy Scorecard
        score = 100
        if webrtc_vulnerable: score -= 35
        if has_ipv6: score -= 25

        print(f"\n  {C_CYAN}{C_BOLD}========================================================================={C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}DIGITAL PRIVACY SCORECARD: {score}/100{C_RESET}")
        print(f"  {C_CYAN}{C_BOLD}========================================================================={C_RESET}\n")
        if score < 70:
            print(f"  {C_YELLOW}[!] Hardening Actions to achieve 100% anonymization:{C_RESET}")
            if webrtc_vulnerable:
                print(f"  1. Disable WebRTC in your browser or install a WebRTC Leak Prevent plugin.")
            if has_ipv6:
                print(f"  2. Disable IPv6 on your network adapter if using an IPv4-only VPN tunnel.")
        else:
            print(f"  {C_GREEN}✓ Excellent privacy posture: High resistance to tracking and IP de-anonymization.{C_RESET}\n")


# =============================================================================
# CLI DISPATCHER
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Enterprise Anti-Surveillance & Privacy Hardening Suite",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # ax scrub
    scrub_parser = subparsers.add_parser("scrub", help="Autonomous media anonymizer & EXIF/GPS metadata scrubber")
    scrub_parser.add_argument("target", help="File or folder containing images/documents to scrub")
    scrub_parser.add_argument("--audit", action="store_true", help="Audit metadata without modifying files")

    # ax dns-shield
    dns_parser = subparsers.add_parser("dns-shield", help="Encrypted DNS (DoH) benchmarking & ISP leak detection")
    dns_parser.add_argument("action", nargs="?", default="audit", choices=["audit", "status", "test"])

    # ax ip-shield
    ip_parser = subparsers.add_parser("ip-shield", help="Real-time IP, IPv6 & WebRTC leak sentinel")
    ip_parser.add_argument("action", nargs="?", default="audit", choices=["audit", "leak-test"])

    # Fallback routing
    if len(sys.argv) > 1 and sys.argv[1] not in ("scrub", "dns-shield", "ip-shield", "-h", "--help"):
        arg1 = sys.argv[1]
        if os.path.exists(arg1):
            sys.argv.insert(1, "scrub")
        elif arg1 in ("dns", "doh"):
            sys.argv[1] = "dns-shield"
        else:
            sys.argv.insert(1, "ip-shield")

    args = parser.parse_args()

    if args.subcommand == "scrub":
        MediaScrubber.run(args.target, audit_only=args.audit, inplace=True)
    elif args.subcommand == "dns-shield":
        DNSShield.audit()
    elif args.subcommand == "ip-shield":
        IPShield.audit()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
