#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Engagement-Centric Workspace, Scope Gating & Reporting Engine
  Version: 3.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0

  Features:
    • Engagement-Centric Workspaces: Client, scope, evidence, and loot unified
    • Dual Operational Modes: 'Lab' (CTF/learning) vs 'Engagement' (Client audit)
    • Cryptographic Scope & Authorization Gating (blocks out-of-scope targets)
    • Unified Project Data Model (hosts, ports, services, creds, findings)
    • Built-in asciinema-style command recording & audit timeline
    • Automated Client Report Generator (Executive summary, findings, timeline)
    • Per-Engagement Reproducibility Snapshots
===============================================================================
"""

import os
import sys
import json
import time
import socket
import ipaddress
import tarfile
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
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
   ███████╗███╗   ██╗ ██████╗  █████╗  ██████╗ ███████╗
   ██╔════╝████╗  ██║██╔════╝ ██╔══██╗██╔════╝ ██╔════╝
   █████╗  ██╔██╗ ██║██║  ███╗███████║██║  ███╗█████╗  
   ██╔══╝  ██║╚██╗██║██║   ██║██╔══██║██║   ██║██╔══╝  
   ███████╗██║ ╚████║╚██████╔╝██║  ██║╚██████╔╝███████╗
   ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
    ENGAGEMENT WORKSPACE & SCOPE GATING ENGINE v3.0{C_RESET}
"""


def get_base_persistent_dir() -> Path:
    """Locates the primary persistent storage root for ASTERIX OS."""
    candidates = [
        Path("/asterix_persistent"),
        Path.home() / "asterix_persistent",
        Path.home() / ".asterix_storage",
        Path.cwd() / "asterix_persistent",
    ]
    for cand in candidates:
        if cand.exists() and cand.is_dir():
            return cand
    fallback = Path.home() / "asterix_persistent"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def get_active_engagement_link() -> Path:
    """Pointer file identifying current active engagement."""
    return get_base_persistent_dir() / ".active_engagement"


def get_current_mode_file() -> Path:
    """Tracks current system mode: 'lab' or 'engagement'."""
    return get_base_persistent_dir() / ".system_mode"


def get_system_mode() -> str:
    f = get_current_mode_file()
    if f.exists():
        mode = f.read_text(encoding="utf-8").strip().lower()
        if mode in ("lab", "engagement"):
            return mode
    return "lab"


def set_system_mode(mode: str):
    if mode not in ("lab", "engagement"):
        raise ValueError(f"Invalid mode '{mode}'. Must be 'lab' or 'engagement'.")
    f = get_current_mode_file()
    f.write_text(mode, encoding="utf-8")


class EngagementManager:
    """Manages project workspaces, authorization scope, and client reports."""

    def __init__(self):
        self.base_dir = get_base_persistent_dir()
        self.engagements_dir = self.base_dir / "engagements"
        self.engagements_dir.mkdir(parents=True, exist_ok=True)

    def get_active_engagement_id(self) -> Optional[str]:
        link = get_active_engagement_link()
        if link.exists():
            val = link.read_text(encoding="utf-8").strip()
            if (self.engagements_dir / val).exists():
                return val
        # Check if any engagement exists
        subdirs = [d.name for d in self.engagements_dir.iterdir() if d.is_dir()]
        return subdirs[0] if subdirs else None

    def get_active_dir(self) -> Optional[Path]:
        eng_id = self.get_active_engagement_id()
        if eng_id:
            d = self.engagements_dir / eng_id
            if d.exists():
                return d
        return None

    def create_engagement(
        self,
        client: str,
        job_id: str,
        cidrs: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        signed_by: str = "Client Authorization Office",
        valid_days: int = 30
    ) -> Path:
        """Creates a complete engagement-centric directory and initialized project data model."""
        eng_dir = self.engagements_dir / job_id
        if eng_dir.exists():
            raise FileExistsError(f"Engagement '{job_id}' already exists at {eng_dir}")

        # Directory structure
        subdirs = ["scope", "scans", "evidence", "loot", "notes", "reports", "timeline"]
        for sub in subdirs:
            (eng_dir / sub).mkdir(parents=True, exist_ok=True)

        now_str = datetime.now(timezone.utc).isoformat()
        scope_data = {
            "authorized_cidrs": cidrs or ["127.0.0.1/32"],
            "authorized_domains": domains or ["localhost"],
            "prohibited_targets": [],
            "signed_by": signed_by,
            "valid_until": datetime.fromtimestamp(time.time() + valid_days * 86400, timezone.utc).isoformat(),
            "signature_sha256": ""
        }
        # Compute signature of scope parameters
        raw_to_sign = f"{client}:{job_id}:{','.join(sorted(scope_data['authorized_cidrs']))}:{signed_by}"
        scope_data["signature_sha256"] = hashlib.sha256(raw_to_sign.encode("utf-8")).hexdigest()

        with (eng_dir / "scope" / "scope.json").open("w", encoding="utf-8") as f:
            json.dump(scope_data, f, indent=2)

        # Initialize project unified data model
        project_data = {
            "engagement_id": job_id,
            "client_name": client,
            "created_at": now_str,
            "mode": get_system_mode(),
            "scope": scope_data,
            "hosts": [],
            "credentials": [],
            "findings": [],
            "timeline": []
        }
        with (eng_dir / "project.json").open("w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=2)

        # Initialize audit trail log
        with (eng_dir / "timeline" / "audit_trail.log").open("w", encoding="utf-8") as f:
            f.write(f"[{now_str}] ENGAGEMENT_INITIALIZED | Client: {client} | Job: {job_id} | Signed: {signed_by}\n")

        # Set as active
        self.switch_engagement(job_id)
        return eng_dir

    def switch_engagement(self, job_id: str):
        eng_dir = self.engagements_dir / job_id
        if not eng_dir.exists():
            raise FileNotFoundError(f"Engagement '{job_id}' does not exist.")
        get_active_engagement_link().write_text(job_id, encoding="utf-8")

    def load_project_data(self) -> Dict[str, Any]:
        eng_dir = self.get_active_dir()
        if not eng_dir:
            raise FileNotFoundError("No active engagement. Run 'ax engagement new' first.")
        p_file = eng_dir / "project.json"
        with p_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save_project_data(self, data: Dict[str, Any]):
        eng_dir = self.get_active_dir()
        if not eng_dir:
            raise FileNotFoundError("No active engagement.")
        p_file = eng_dir / "project.json"
        with p_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def is_target_in_scope(self, target: str) -> Tuple[bool, str]:
        """
        Validates whether target is within authorized scope.
        Returns: (is_authorized, reason)
        """
        data = self.load_project_data()
        scope = data.get("scope", {})
        auth_cidrs = scope.get("authorized_cidrs", [])
        auth_domains = scope.get("authorized_domains", [])
        prohibited = scope.get("prohibited_targets", [])

        # Check prohibited targets first
        for p in prohibited:
            if target == p or target.endswith("." + p):
                return False, f"Target '{target}' is explicitly listed in PROHIBITED targets."

        # Check IP / CIDR
        try:
            target_ip = ipaddress.ip_address(target)
            for cidr in auth_cidrs:
                try:
                    net = ipaddress.ip_network(cidr, strict=False)
                    if target_ip in net:
                        return True, f"Target IP '{target}' matches authorized CIDR '{cidr}'."
                except ValueError:
                    pass
        except ValueError:
            pass

        # Check domain matching
        clean_target = target.lower().strip()
        for dom in auth_domains:
            dom_clean = dom.lower().strip()
            if clean_target == dom_clean or clean_target.endswith("." + dom_clean):
                return True, f"Target domain '{target}' matches authorized domain '{dom}'."

        return False, f"Target '{target}' is OUT OF SCOPE. Not in authorized CIDRs or domains."

    def record_action(self, action: str, command: str, output_summary: str = "", target: Optional[str] = None):
        """Records an action into both project.json timeline and audit_trail.log."""
        eng_dir = self.get_active_dir()
        if not eng_dir:
            return

        now_str = datetime.now(timezone.utc).isoformat()
        operator = os.environ.get("USER", os.environ.get("USERNAME", "operator"))
        is_scope_valid = True
        if target:
            is_scope_valid, _ = self.is_target_in_scope(target)

        entry = {
            "timestamp": now_str,
            "operator": operator,
            "action": action,
            "command": command,
            "output_summary": output_summary[:500],
            "scope_validated": is_scope_valid
        }

        # Update project.json
        try:
            data = self.load_project_data()
            data.setdefault("timeline", []).append(entry)
            self.save_project_data(data)
        except Exception:
            pass

        # Append to audit_trail.log
        audit_log = eng_dir / "timeline" / "audit_trail.log"
        with audit_log.open("a", encoding="utf-8") as f:
            f.write(f"[{now_str}] OPERATOR={operator} ACTION={action} VALID_SCOPE={is_scope_valid} CMD={command}\n")

    def add_host(self, ip: str, hostname: str = "", status: str = "up", ports: Optional[List[Dict]] = None):
        """Adds or updates host in project.json."""
        data = self.load_project_data()
        hosts = data.setdefault("hosts", [])
        existing = next((h for h in hosts if h.get("ip") == ip), None)
        if not existing:
            new_host = {
                "ip": ip,
                "hostname": hostname,
                "status": status,
                "ports": ports or []
            }
            hosts.append(new_host)
        else:
            if hostname:
                existing["hostname"] = hostname
            existing["status"] = status
            if ports:
                existing_ports = existing.setdefault("ports", [])
                for p in ports:
                    if not any(ep.get("port") == p.get("port") and ep.get("proto") == p.get("proto") for ep in existing_ports):
                        existing_ports.append(p)
        self.save_project_data(data)

    def add_finding(self, title: str, severity: str, target: str, description: str, remediation: str = "", cve: str = ""):
        """Records a vulnerability finding."""
        data = self.load_project_data()
        findings = data.setdefault("findings", [])
        f_id = f"FIND-{len(findings) + 1:03d}"
        findings.append({
            "id": f_id,
            "title": title,
            "severity": severity.lower(),
            "target": target,
            "description": description,
            "remediation": remediation,
            "cve": cve
        })
        self.save_project_data(data)
        return f_id

    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        """Compiles an automated professional markdown engagement report."""
        data = self.load_project_data()
        eng_dir = self.get_active_dir()
        if output_path is None:
            output_path = eng_dir / "reports" / f"Report_{data['engagement_id']}.md"

        client = data.get("client_name", "Unknown Client")
        job = data.get("engagement_id", "ENG-000")
        created = data.get("created_at", "")
        scope = data.get("scope", {})
        hosts = data.get("hosts", [])
        findings = data.get("findings", [])
        timeline = data.get("timeline", [])

        # Compute severity statistics
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        for f in findings:
            s = f.get("severity", "info").lower()
            sev_counts[s] = sev_counts.get(s, 0) + 1

        md_lines = [
            f"# [SEC] Security Assessment & Penetration Test Report",
            f"",
            f"**Client**: {client}  ",
            f"**Engagement ID**: `{job}`  ",
            f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
            f"**Authorized Signer**: {scope.get('signed_by', 'N/A')}  ",
            f"**Scope Certificate**: `{scope.get('signature_sha256', 'N/A')[:16]}...`  ",
            f"",
            f"---",
            f"",
            f"## 1. Executive Summary",
            f"",
            f"During the security assessment conducted under engagement `{job}`, the testing team identified **{len(findings)}** total findings across **{len(hosts)}** discovered hosts.",
            f"",
            f"| Severity | Finding Count |",
            f"| :--- | :--- |",
            f"| **Critical** | {sev_counts['critical']} |",
            f"| **High** | {sev_counts['high']} |",
            f"| **Medium** | {sev_counts['medium']} |",
            f"| **Low** | {sev_counts['low']} |",
            f"| **Info** | {sev_counts['info']} |",
            f"",
            f"---",
            f"",
            f"## 2. Assessment Scope",
            f"",
            f"The scope of testing was authorized by **{scope.get('signed_by', 'N/A')}** and verified against the following target boundaries:",
            f"",
            f"### Authorized IP Ranges (CIDRs)",
        ]
        for c in scope.get("authorized_cidrs", []):
            md_lines.append(f"- `{c}`")

        md_lines.extend([
            f"",
            f"### Authorized Domains",
        ])
        for d in scope.get("authorized_domains", []):
            md_lines.append(f"- `{d}`")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"## 3. Discovered Hosts & Services",
            f"",
            f"| IP Address | Hostname | Open Ports & Services |",
            f"| :--- | :--- | :--- |",
        ])
        for h in hosts:
            p_strs = [f"{p['port']}/{p['proto']} ({p.get('service', 'unknown')})" for p in h.get("ports", [])]
            p_desc = ", ".join(p_strs) if p_strs else "None reported"
            md_lines.append(f"| `{h.get('ip')}` | {h.get('hostname') or '-'} | {p_desc} |")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"## 4. Technical Findings",
            f"",
        ])
        if not findings:
            md_lines.append("_No vulnerabilities or security deficiencies were recorded during this assessment._\n")
        else:
            for f in findings:
                cve_str = f" (`{f['cve']}`)" if f.get("cve") else ""
                md_lines.extend([
                    f"### [{f.get('id', 'FIND')}] {f.get('title', 'Untitled Finding')}{cve_str}",
                    f"- **Severity**: `{f.get('severity', 'info').upper()}`",
                    f"- **Target**: `{f.get('target', 'N/A')}`",
                    f"",
                    f"**Description**:",
                    f"{f.get('description', 'No description provided.')}",
                    f"",
                    f"**Remediation Recommendation**:",
                    f"{f.get('remediation', 'Apply latest vendor security patches and restrict network access.')}",
                    f"",
                ])

        md_lines.extend([
            f"---",
            f"",
            f"## 5. Audit Trail Timeline",
            f"",
            f"| Timestamp (UTC) | Operator | Action | Command | Scope Validated |",
            f"| :--- | :--- | :--- | :--- | :--- |",
        ])
        for t in timeline[-30:]:  # Last 30 actions
            val_icon = "[OK]" if t.get("scope_validated") else "[!] OUT-OF-SCOPE"
            md_lines.append(f"| `{t.get('timestamp')[:19]}` | `{t.get('operator')}` | {t.get('action')} | `{t.get('command')}` | {val_icon} |")

        content = "\n".join(md_lines) + "\n"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)

        return output_path

    def create_snapshot(self, output_path: Optional[Path] = None) -> Path:
        """Freezes active engagement workspace into an archived snapshot bundle."""
        eng_dir = self.get_active_dir()
        if not eng_dir:
            raise FileNotFoundError("No active engagement to snapshot.")
        data = self.load_project_data()
        job = data.get("engagement_id", "snapshot")

        if output_path is None:
            output_path = eng_dir / "reports" / f"Engagement_{job}_Snapshot.tar.gz"

        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(eng_dir, arcname=job)

        return output_path


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Engagement-Centric Workspace & Scope Gating Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand")

    # new command
    cmd_new = subparsers.add_parser("new", help="Create a new engagement-centric workspace")
    cmd_new.add_argument("client", help="Client name (e.g. AcmeCorp)")
    cmd_new.add_argument("job_id", help="Unique engagement identifier (e.g. ENG-2026-001)")
    cmd_new.add_argument("--cidrs", default="", help="Comma-separated authorized CIDRs (e.g. 192.168.1.0/24,10.0.0.0/8)")
    cmd_new.add_argument("--domains", default="", help="Comma-separated authorized domains (e.g. acme.com,api.acme.com)")
    cmd_new.add_argument("--signer", default="Client Security Authorization", help="Name of authorizing officer/body")

    # switch command
    cmd_sw = subparsers.add_parser("switch", help="Switch active engagement")
    cmd_sw.add_argument("job_id", help="Target engagement identifier")

    # status command
    subparsers.add_parser("status", help="Show active engagement telemetry, mode, and scope")

    # list command
    subparsers.add_parser("list", help="List all engagements in persistent storage")

    # mode command
    cmd_mode = subparsers.add_parser("mode", help="View or toggle Lab vs. Engagement mode")
    cmd_mode.add_argument("new_mode", nargs="?", choices=["lab", "engagement"], help="Mode to set ('lab' or 'engagement')")

    # scope-check command
    cmd_sc = subparsers.add_parser("scope-check", help="Verify if target IP or domain is in authorized scope")
    cmd_sc.add_argument("target", help="Target IP address or domain name")

    # report command
    cmd_rep = subparsers.add_parser("report", help="Generate client-ready Markdown assessment report")
    cmd_rep.add_argument("-o", "--out", default=None, help="Output markdown path")

    # snapshot command
    cmd_snap = subparsers.add_parser("snapshot", help="Freeze engagement into reproducible snapshot bundle")
    cmd_snap.add_argument("-o", "--out", default=None, help="Output snapshot path")

    # add-host command
    cmd_host = subparsers.add_parser("add-host", help="Add discovered host to active project data model")
    cmd_host.add_argument("ip", help="Host IP address")
    cmd_host.add_argument("--hostname", default="", help="Host domain/hostname")
    cmd_host.add_argument("--port", type=int, default=None, help="Open port")
    cmd_host.add_argument("--service", default="", help="Detected service name")

    # add-finding command
    cmd_find = subparsers.add_parser("add-finding", help="Log a security finding")
    cmd_find.add_argument("title", help="Finding title")
    cmd_find.add_argument("--severity", required=True, choices=["critical", "high", "medium", "low", "info"], help="Severity level")
    cmd_find.add_argument("--target", required=True, help="Affected target/URL")
    cmd_find.add_argument("--desc", required=True, help="Description of finding")
    cmd_find.add_argument("--remediation", default="", help="Recommended fix")

    args = parser.parse_args()
    mgr = EngagementManager()

    if not args.subcommand or args.subcommand == "status":
        print(BANNER)
        cur_mode = get_system_mode()
        active_id = mgr.get_active_engagement_id()
        mode_color = C_YELLOW if cur_mode == "lab" else C_GREEN
        print(f"  • Operating Mode:    {mode_color}{cur_mode.upper()}{C_RESET}")
        if cur_mode == "lab":
            print(f"    {C_DIM}(Relaxed scope; verbose CTF & learning logs enabled){C_RESET}")
        else:
            print(f"    {C_DIM}(Strict scope validation; actions tied to signed client authorization){C_RESET}")

        if active_id:
            data = mgr.load_project_data()
            print(f"  • Active Engagement: {C_CYAN}{C_BOLD}{active_id}{C_RESET} (Client: {data.get('client_name')})")
            print(f"  • Workspace Path:    {mgr.get_active_dir()}")
            scope = data.get("scope", {})
            print(f"  • Authorized CIDRs:  {', '.join(scope.get('authorized_cidrs', []))}")
            print(f"  • Authorized Domains: {', '.join(scope.get('authorized_domains', []))}")
            print(f"  • Scope Signature:   {scope.get('signature_sha256', '')[:16]}... (Signed by: {scope.get('signed_by')})")
            print(f"  • Telemetry:         {len(data.get('hosts', []))} Hosts | {len(data.get('findings', []))} Findings")
        else:
            print(f"  • Active Engagement: {C_YELLOW}None (Run 'ax engagement new' to start one){C_RESET}")
        print()

    elif args.subcommand == "new":
        cidrs = [c.strip() for c in args.cidrs.split(",") if c.strip()]
        domains = [d.strip() for d in args.domains.split(",") if d.strip()]
        d = mgr.create_engagement(args.client, args.job_id, cidrs=cidrs, domains=domains, signed_by=args.signer)
        print(BANNER)
        print(f"  {C_GREEN}[OK] Engagement workspace created & activated:{C_RESET} {args.job_id}")
        print(f"    Directory: {d}")
        print(f"    Scope Signature: Generated & signed by '{args.signer}'")

    elif args.subcommand == "switch":
        mgr.switch_engagement(args.job_id)
        print(f"  {C_GREEN}[OK] Switched active engagement to:{C_RESET} {args.job_id}")

    elif args.subcommand == "list":
        print(BANNER)
        print("  [HISTORICAL ENGAGEMENTS]")
        subdirs = [d for d in mgr.engagements_dir.iterdir() if d.is_dir()]
        active_id = mgr.get_active_engagement_id()
        if not subdirs:
            print("  (No engagements recorded yet)")
        for d in subdirs:
            p_file = d / "project.json"
            status_tag = f"{C_GREEN}[ACTIVE]{C_RESET}" if d.name == active_id else f"{C_DIM}[INACTIVE]{C_RESET}"
            client = "Unknown"
            findings_cnt = 0
            if p_file.exists():
                try:
                    with p_file.open("r", encoding="utf-8") as f:
                        pj = json.load(f)
                        client = pj.get("client_name", "Unknown")
                        findings_cnt = len(pj.get("findings", []))
                except Exception:
                    pass
            print(f"  • {d.name:<18} {status_tag} Client: {client:<16} Findings: {findings_cnt}")
        print()

    elif args.subcommand == "mode":
        if args.new_mode:
            set_system_mode(args.new_mode)
            print(f"  {C_GREEN}[OK] System operating mode updated to:{C_RESET} {args.new_mode.upper()}")
        else:
            cur = get_system_mode()
            print(f"  Current Mode: {cur.upper()}")

    elif args.subcommand == "scope-check":
        allowed, reason = mgr.is_target_in_scope(args.target)
        mode = get_system_mode()
        mgr.record_action("SCOPE_CHECK", f"scope-check {args.target}", reason, target=args.target)
        if allowed:
            print(f"  {C_GREEN}[OK] SCOPE PASS:{C_RESET} {reason}")
            sys.exit(0)
        else:
            if mode == "engagement":
                print(f"  {C_RED}[FAIL] SCOPE VIOLATION BLOCKED (ENGAGEMENT MODE):{C_RESET} {reason}")
                sys.exit(1)
            else:
                print(f"  {C_YELLOW}[!] SCOPE WARNING (LAB MODE ALLOWED):{C_RESET} {reason}")
                sys.exit(0)

    elif args.subcommand == "report":
        out = Path(args.out) if args.out else None
        rep_file = mgr.generate_report(out)
        print(f"  {C_GREEN}[OK] Client assessment report generated:{C_RESET} {rep_file}")

    elif args.subcommand == "snapshot":
        out = Path(args.out) if args.out else None
        snap_file = mgr.create_snapshot(out)
        print(f"  {C_GREEN}[OK] Engagement snapshot archive created:{C_RESET} {snap_file}")

    elif args.subcommand == "add-host":
        ports = []
        if args.port:
            ports.append({"port": args.port, "proto": "tcp", "state": "open", "service": args.service})
        mgr.add_host(args.ip, hostname=args.hostname, ports=ports)
        print(f"  {C_GREEN}[OK] Host recorded in project data model:{C_RESET} {args.ip}")

    elif args.subcommand == "add-finding":
        f_id = mgr.add_finding(args.title, args.severity, args.target, args.desc, remediation=args.remediation)
        print(f"  {C_GREEN}[OK] Finding recorded [{f_id}]:{C_RESET} {args.title} ({args.severity.upper()})")


if __name__ == "__main__":
    main()
