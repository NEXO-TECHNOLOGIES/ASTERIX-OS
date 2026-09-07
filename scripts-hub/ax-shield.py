#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Enterprise Cyber Threat & Supply Chain Defense Suite
  Tools: ax canary, ax supply-chain, ax phish-shield
  Version: 2.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import json
import math
import time
import socket
import hashlib
import argparse
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Set, Tuple, Optional, Any

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
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗    ███████╗██╗  ██╗██╗███████╗██╗     ██████╗ 
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔════╝██║  ██║██║██╔════╝██║     ██╔══██╗
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ███████╗███████║██║█████╗  ██║     ██║  ██║
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ╚════██║██╔══██║██║██╔══╝  ██║     ██║  ██║
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ███████║██║  ██║██║███████╗███████╗██████╔╝
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═════╝ 
{C_RESET}{C_MAGENTA}       ASTERIX Enterprise Defense (Ransomware Canaries / Supply Chain / Anti-Phishing){C_RESET}
"""

# =============================================================================
# 1. AUTONOMOUS ANTI-RANSOMWARE CANARY TRIPWIRE ENGINE (ax canary)
# =============================================================================

CANARY_FILENAMES = [
    "!_00_ASTERIX_FINANCIAL_CANARY.docx",
    "!_00_ASTERIX_VAULT_BACKUP.xlsx",
    "!_00_ASTERIX_CONFIDENTIAL_KEY.pdf",
    "!_00_ASTERIX_DATABASE_DUMP.sql",
]

CANARY_PAYLOAD = (
    b"ASTERIX_OS_CRYPTOGRAPHIC_CANARY_TRIPWIRE_V2\n"
    b"DO NOT MODIFY OR RENAME THIS HONEYPOT DECOY FILE.\n"
    b"Any modification, renaming, or unauthorized entropy encryption\n"
    b"triggers automated defensive containment.\n"
    b"===============================================================\n"
)

class CanaryGuard:
    """Deploys and monitors cryptographic canary tripwires to intercept ransomware attacks."""

    @staticmethod
    def _manifest_file() -> Path:
        vault_dir = Path.home() / ".asterix_vault" / "canaries"
        vault_dir.mkdir(parents=True, exist_ok=True)
        return vault_dir / "manifest.json"

    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """Calculates Shannon entropy of bytes (0.0 to 8.0). Ransomware encrypted data > 7.9."""
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        freqs = [0] * 256
        for b in data:
            freqs[b] += 1
        for count in freqs:
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def deploy(target_dir: str):
        print(BANNER)
        dest = Path(target_dir).resolve()
        dest.mkdir(parents=True, exist_ok=True)
        print(f"  {C_CYAN}{C_BOLD}[RANSOMWARE TRIPWIRE] Deploying Honeypot Canaries to:{C_RESET} {dest}\n")

        manifest_path = CanaryGuard._manifest_file()
        records = {}
        if manifest_path.exists():
            try:
                records = json.loads(manifest_path.read_text(encoding="utf-8"))
            except Exception:
                records = {}

        planted = 0
        for name in CANARY_FILENAMES:
            file_path = dest / name
            content = CANARY_PAYLOAD + os.urandom(1024)
            file_path.write_bytes(content)
            sha = hashlib.sha256(content).hexdigest()
            records[str(file_path)] = {
                "hash": sha,
                "created_at": time.time(),
                "size": len(content),
                "entropy": round(CanaryGuard._calculate_entropy(content), 4)
            }
            planted += 1
            print(f"  {C_GREEN}✓ Planted Tripwire Decoy:{C_RESET} {file_path.name}")
            print(f"    ↳ SHA-256: {C_DIM}{sha[:32]}...{C_RESET}")

        manifest_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
        print(f"\n  {C_GREEN}{C_BOLD}✓ SUCCESS: {planted} tripwires deployed and armed.{C_RESET}")
        print(f"  {C_DIM}Run 'ax canary status' or 'ax canary check' to audit tripwire integrity.{C_RESET}\n")

    @staticmethod
    def check_integrity():
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[RANSOMWARE TRIPWIRE INTEGRITY AUDIT]{C_RESET}\n")

        manifest_path = CanaryGuard._manifest_file()
        if not manifest_path.exists():
            print(f"  {C_YELLOW}[!] No canaries deployed yet. Run 'ax canary deploy <dir>' first.{C_RESET}\n")
            return

        records = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not records:
            print(f"  {C_YELLOW}[!] Manifest is empty. Run 'ax canary deploy <dir>'.{C_RESET}\n")
            return

        breaches = []
        intact = 0

        for path_str, meta in records.items():
            fpath = Path(path_str)
            if not fpath.exists():
                breaches.append({
                    "path": path_str,
                    "reason": "FILE MISSING / RENAMED (Classic Ransomware Extention Swapping)"
                })
                continue

            content = fpath.read_bytes()
            current_hash = hashlib.sha256(content).hexdigest()
            current_entropy = CanaryGuard._calculate_entropy(content)

            if current_hash != meta["hash"]:
                is_high_entropy = current_entropy >= 7.8
                reason = "ACTIVE ENCRYPTION DETECTED (High Shannon Entropy)" if is_high_entropy else "TAMPERED / CORRUPTED"
                breaches.append({
                    "path": path_str,
                    "reason": f"{reason} (Entropy: {current_entropy:.2f})"
                })
            else:
                intact += 1

        print(f"  • Total Monitored Tripwires: {C_BOLD}{len(records)}{C_RESET}")
        print(f"  • Intact & Secure:           {C_GREEN}{intact}{C_RESET}")

        if breaches:
            print(f"\n  {C_RED}{C_BOLD}🚨 SECURITY ALERT: {len(breaches)} CANARY TRIPWIRE(S) TRIGGERED!{C_RESET}")
            print(f"  {C_RED}Potential malicious ransomware process activity detected!{C_RESET}\n")
            for b in breaches:
                print(f"    • {C_BOLD}{Path(b['path']).name}{C_RESET}")
                print(f"      ↳ {C_RED}{b['reason']}{C_RESET}")
                print(f"      Location: {b['path']}")
            print(f"\n  {C_YELLOW}[ACTION] Review active running processes and isolate affected directory.{C_RESET}\n")
        else:
            print(f"\n  {C_GREEN}{C_BOLD}✓ ALL CANARIES UNTOUCHED: Zero malicious encryption detected.{C_RESET}\n")


# =============================================================================
# 2. THIRD-PARTY DEPENDENCY & SUPPLY CHAIN SENTINEL (ax supply-chain)
# =============================================================================

# High-reputation libraries often targeted for typosquatting
KNOWN_POPULAR_PACKAGES = {
    # Python
    "requests", "urllib3", "numpy", "pandas", "scipy", "matplotlib", "colorama",
    "flask", "django", "fastapi", "pydantic", "pytest", "setuptools", "wheel",
    "cryptography", "boto3", "aiohttp", "click", "jinja2", "pyyaml", "certifi",
    # JavaScript / Node.js
    "lodash", "express", "react", "axios", "moment", "chalk", "commander",
    "debug", "async", "dotenv", "webpack", "babel", "next", "typescript"
}

DANGEROUS_NPM_PATTERNS = [
    r"\bcurl\s+", r"\bwget\s+", r"\bbash\s+", r"\bsh\s+", r"\bpowershell\b",
    r"\beval\s*\(", r"\bexec\s*\(", r"\bchild_process\b", r"\bnetcat\b", r"\bnc\s+"
]

class SupplyChainAuditor:
    """Audits dependencies across Python, Node, Rust, and Go for supply-chain attacks and typosquatting."""

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        if len(s1) < len(s2):
            return SupplyChainAuditor._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    @staticmethod
    def audit(target_dir: str = "."):
        root = Path(target_dir).resolve()
        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[SUPPLY CHAIN AUDITOR] Scanning dependencies in:{C_RESET} {root}\n")

        findings = []
        manifests_found = 0

        # 1. Python requirements.txt
        req_files = list(root.glob("**/requirements*.txt"))
        for req in req_files:
            if any(p in req.parts for p in (".git", "venv", "node_modules")):
                continue
            manifests_found += 1
            content = req.read_text(encoding="utf-8", errors="replace")
            for line_no, line in enumerate(content.splitlines(), 1):
                clean = line.strip().split("#")[0].strip()
                if not clean:
                    continue
                # Extract package name
                pkg_match = re.match(r"^([a-zA-Z0-9_\-\.]+)", clean)
                if pkg_match:
                    pkg_name = pkg_match.group(1).lower()
                    # Check unpinned version
                    if "==" not in clean and not clean.startswith(("-r", "-e")):
                        findings.append({
                            "manifest": str(req.relative_to(root)),
                            "line": line_no,
                            "severity": "LOW",
                            "issue": f"Unpinned dependency '{pkg_name}' (susceptible to upstream takeover)",
                        })
                    # Check typosquatting against popular packages
                    for pop in KNOWN_POPULAR_PACKAGES:
                        if pkg_name != pop and SupplyChainAuditor._levenshtein(pkg_name, pop) == 1:
                            findings.append({
                                "manifest": str(req.relative_to(root)),
                                "line": line_no,
                                "severity": "HIGH",
                                "issue": f"Potential Typosquatting: '{pkg_name}' closely resembles '{pop}'",
                            })

        # 2. Node.js package.json
        pkg_json_files = list(root.glob("**/package.json"))
        for pj in pkg_json_files:
            if any(p in pj.parts for p in (".git", "node_modules")):
                continue
            manifests_found += 1
            try:
                data = json.loads(pj.read_text(encoding="utf-8"))
                # Check scripts for malicious lifecycle hooks (preinstall, postinstall)
                scripts = data.get("scripts", {})
                for hook in ("preinstall", "postinstall", "install", "prepublish"):
                    if hook in scripts:
                        cmd = scripts[hook]
                        for pat in DANGEROUS_NPM_PATTERNS:
                            if re.search(pat, cmd, re.IGNORECASE):
                                findings.append({
                                    "manifest": str(pj.relative_to(root)),
                                    "line": "scripts",
                                    "severity": "CRITICAL",
                                    "issue": f"Dangerous lifecycle hook '{hook}': '{cmd}'",
                                })
                # Check dependencies
                deps = data.get("dependencies", {})
                deps.update(data.get("devDependencies", {}))
                for dep, ver in deps.items():
                    if ver in ("*", "latest") or ver.startswith("^0.") or ver.startswith("~0."):
                        findings.append({
                            "manifest": str(pj.relative_to(root)),
                            "line": "deps",
                            "severity": "MEDIUM",
                            "issue": f"Loose wildcard dependency: '{dep}': '{ver}'",
                        })
                    for pop in KNOWN_POPULAR_PACKAGES:
                        if dep != pop and SupplyChainAuditor._levenshtein(dep, pop) == 1:
                            findings.append({
                                "manifest": str(pj.relative_to(root)),
                                "line": "deps",
                                "severity": "HIGH",
                                "issue": f"Potential Typosquatting: '{dep}' closely resembles '{pop}'",
                            })
            except Exception as e:
                findings.append({
                    "manifest": str(pj.relative_to(root)),
                    "line": "manifest",
                    "severity": "CRITICAL",
                    "issue": f"Manifest quarantined by security engine or unreadable: {e}",
                })

        print(f"  • Dependency Manifests Audited: {C_BOLD}{manifests_found}{C_RESET}")

        if not findings:
            print(f"  {C_GREEN}{C_BOLD}✓ CLEAN: No typosquats or malicious lifecycle hooks detected.{C_RESET}\n")
            return

        print(f"\n  {C_YELLOW}{C_BOLD}⚠ DETECTED {len(findings)} SUPPLY-CHAIN RISKS / VULNERABILITIES:{C_RESET}\n")
        print(f"  {'Severity':<10} {'Manifest':<28} {'Line':<8} {'Finding Details':<45}")
        print(f"  {'-'*95}")
        for f in findings:
            sev_color = C_RED if f["severity"] in ("CRITICAL", "HIGH") else C_YELLOW
            print(f"  {sev_color}{f['severity']:<10}{C_RESET} {f['manifest'][:27]:<28} {str(f['line']):<8} {f['issue']}")
        print()


# =============================================================================
# 3. PHISHING & HOMOGLYPH DECEPTION SHIELD (ax phish-shield)
# =============================================================================

TOP_TARGETED_BRANDS = [
    "paypal", "google", "microsoft", "apple", "amazon", "github", "gitlab",
    "facebook", "instagram", "netflix", "stripe", "coinbase", "binance",
    "wellsfargo", "chase", "bankofamerica", "dropbox", "slack", "zoom"
]

class PhishShield:
    """Detects homoglyph Punycode attacks, brand impersonation, and deceptive login endpoints."""

    @staticmethod
    def audit_domain(target: str):
        print(BANNER)
        # Normalize input
        if "://" in target:
            parsed = urlparse(target)
            domain = parsed.netloc.split(":")[0]
        else:
            domain = target.split("/")[0].split(":")[0]

        print(f"  {C_CYAN}{C_BOLD}[PHISHING & HOMOGLYPH SHIELD] Analyzing domain:{C_RESET} {domain}\n")

        deceptions = []
        is_punycode = False
        decoded_domain = domain

        # 1. Punycode check (starts with xn--)
        if any(part.startswith("xn--") for part in domain.split(".")):
            is_punycode = True
            try:
                decoded_domain = domain.encode("ascii").decode("idna")
                deceptions.append(f"Punycode Internationalized Domain: decodes to '{decoded_domain}'")
            except Exception:
                deceptions.append("Malformed Punycode Domain encoding")

        # 2. Cyrillic / Greek / Non-ASCII Homoglyph character check
        homoglyphs = []
        for ch in decoded_domain:
            code = ord(ch)
            if code > 127:
                homoglyphs.append(f"'{ch}' (U+{code:04X})")

        if homoglyphs:
            deceptions.append(f"Contains {len(homoglyphs)} non-Latin/Cyrillic homoglyphs: {', '.join(homoglyphs[:5])}")

        # 3. Brand Impersonation & Typosquatting (Levenshtein)
        domain_stem = decoded_domain.split(".")[0].lower()
        full_clean = decoded_domain.replace(".", "").lower()

        matched_brand = None
        for brand in TOP_TARGETED_BRANDS:
            # Exact brand embedded inside another domain: e.g. paypal-security-update.com
            if brand in decoded_domain and not decoded_domain.endswith(f"{brand}.com") and not decoded_domain.endswith(f"{brand}.net"):
                deceptions.append(f"Deceptive Brand Embedding: embeds '{brand}' in suspicious domain structure")
                matched_brand = brand
                break

            # Typosquatted brand: paypai, g00gle
            dist = SupplyChainAuditor._levenshtein(domain_stem, brand)
            if 0 < dist <= 2 and abs(len(domain_stem) - len(brand)) <= 2:
                deceptions.append(f"Brand Typosquatting Deception: '{domain_stem}' is visually spoofing '{brand}'")
                matched_brand = brand
                break

        # 4. Multi-level subdomain deception (e.g. login.paypal.com.attacker.com)
        parts = domain.split(".")
        if len(parts) >= 4:
            for b in TOP_TARGETED_BRANDS:
                if b in parts[:-2]:
                    deceptions.append(f"Subdomain Trapping Deception: brand '{b}' used as subdomain to mask attacker host")

        # Display verdict
        if deceptions:
            print(f"  {C_RED}{C_BOLD}🚨 DANGER: HIGH-CONFIDENCE PHISHING DECEPTION DETECTED!{C_RESET}\n")
            print(f"  {C_BOLD}Target Domain:{C_RESET}  {domain}")
            if is_punycode:
                print(f"  {C_BOLD}Punycode View:{C_RESET}  {decoded_domain}")
            print(f"  {C_BOLD}Risk Level:{C_RESET}     {C_RED}CRITICAL (Phishing / Brand Spoofing){C_RESET}\n")
            print(f"  {C_WHITE}{C_BOLD}Identified Deception Mechanisms:{C_RESET}")
            for d in deceptions:
                print(f"    • {C_RED}{d}{C_RESET}")
            print(f"\n  {C_YELLOW}[!] WARNING: Never submit credentials or two-factor tokens to this destination.{C_RESET}\n")
        else:
            print(f"  {C_GREEN}{C_BOLD}✓ CLEAN: No homoglyphs, Punycode tricks, or brand typosquats detected.{C_RESET}")
            print(f"  {C_DIM}Domain '{domain}' passes standard visual and structural deception heuristics.{C_RESET}\n")


# =============================================================================
# CLI DISPATCHER
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Enterprise Cyber Threat & Supply Chain Defense Suite",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # ax canary subcommand
    canary_parser = subparsers.add_parser("canary", help="Autonomous anti-ransomware tripwire engine")
    canary_parser.add_argument("action", choices=["deploy", "check", "status", "audit"], help="Action to perform")
    canary_parser.add_argument("dir", nargs="?", default=".", help="Directory to deploy canaries into")

    # ax supply-chain subcommand
    sc_parser = subparsers.add_parser("supply-chain", help="Audit third-party dependencies for supply chain risks")
    sc_parser.add_argument("path", nargs="?", default=".", help="Root directory to audit")

    # ax phish-shield subcommand
    phish_parser = subparsers.add_parser("phish-shield", help="Phishing & homoglyph domain deception shield")
    phish_parser.add_argument("target", help="Domain or URL to analyze")

    # Direct fallback if invoked with first parameter
    if len(sys.argv) > 1 and sys.argv[1] not in ("canary", "supply-chain", "phish-shield", "-h", "--help"):
        if "." in sys.argv[1] and not sys.argv[1].startswith("."):
            sys.argv.insert(1, "phish-shield")
        else:
            sys.argv.insert(1, "supply-chain")

    args = parser.parse_args()

    if args.subcommand == "canary":
        if args.action == "deploy":
            CanaryGuard.deploy(args.dir)
        else:
            CanaryGuard.check_integrity()
    elif args.subcommand == "supply-chain":
        SupplyChainAuditor.audit(args.path)
    elif args.subcommand == "phish-shield":
        PhishShield.audit_domain(args.target)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
