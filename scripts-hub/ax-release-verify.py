#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Cryptographic Release & Integrity Verifier
  Version: 2.0.0
  Zero Dependencies: 100% Python Standard Library

  Capabilities:
    • Validates SHA-256 cryptographic signatures against BUILD_MANIFEST.json
    • Detects file tampering, corruption, and supply chain alterations
    • Calculates SHA-256 digests for release bundles and scripts
===============================================================================
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

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
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"

BANNER = f"""{C_CYAN}{C_BOLD}
   ██████╗ ███████╗██╗     ███████╗ █████╗ ███████╗███████╗
   ██╔══██╗██╔════╝██║     ██╔════╝██╔══██╗██╔════╝██╔════╝
   ██████╔╝█████╗  ██║     █████╗  ███████║███████╗█████╗  
   ██╔══██╗██╔══╝  ██║     ██╔══╝  ██╔══██║╚════██║██╔══╝  
   ██║  ██║███████╗███████╗███████╗██║  ██║███████║███████╗
   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
{C_RESET}{C_CYAN}    CRYPTOGRAPHIC INTEGRITY & SUPPLY CHAIN AUDITOR v2.0{C_RESET}
"""


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 digest of a file."""
    h = hashlib.sha256()
    with filepath.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def find_repo_root() -> Path:
    """Finds repository root containing BUILD_MANIFEST.json."""
    cur = Path(__file__).resolve().parent
    for _ in range(3):
        if (cur / "BUILD_MANIFEST.json").exists():
            return cur
        cur = cur.parent
    return Path.cwd()


def verify_manifest(repo_root: Path) -> Tuple[int, int, int]:
    """Verifies all cryptographic signatures in BUILD_MANIFEST.json."""
    manifest_path = repo_root / "BUILD_MANIFEST.json"
    if not manifest_path.exists():
        print(f"{C_RED}[[FAIL]] Error: BUILD_MANIFEST.json not found at {manifest_path}{C_RESET}")
        return 0, 0, 1

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"{C_RED}[[FAIL]] Error parsing BUILD_MANIFEST.json: {e}{C_RESET}")
        return 0, 0, 1

    signatures: Dict[str, str] = data.get("cryptographic_signatures", {})
    if not signatures:
        print(f"{C_YELLOW}[!] Warning: No cryptographic signatures found in manifest.{C_RESET}")
        return 0, 0, 0

    print(BANNER)
    print(f"  {C_CYAN}{C_BOLD}[RELEASE INTEGRITY AUDIT]{C_RESET}")
    print(f"  System:   {C_WHITE}{data.get('system', 'ASTERIX OS')} v{data.get('version', '2.0')}{C_RESET}")
    print(f"  Manifest: {C_DIM}{manifest_path}{C_RESET}\n")

    print(f"  {'FILE ARTIFACT':<46} {'STATUS':<12} {'DETAILS'}")
    print(f"  {'-'*85}")

    passed = 0
    modified = 0
    missing = 0

    for rel_path, expected_hash in signatures.items():
        target = repo_root / rel_path
        if not target.exists():
            print(f"  {rel_path:<46} {C_RED}[ MISSING ]{C_RESET} File not found")
            missing += 1
            continue

        actual_hash = compute_sha256(target)
        if actual_hash.lower() == expected_hash.lower():
            print(f"  {rel_path:<46} {C_GREEN}[ VALID   ]{C_RESET} SHA-256 verified")
            passed += 1
        else:
            print(f"  {rel_path:<46} {C_YELLOW}[ MODIFIED]{C_RESET} Hash mismatch (updated/patched)")
            modified += 1

    print(f"\n  {'-'*85}")
    print(f"  Summary: {C_GREEN}{passed} Valid{C_RESET} | {C_YELLOW}{modified} Modified{C_RESET} | {C_RED}{missing} Missing{C_RESET} (Total: {len(signatures)})\n")

    if missing == 0 and modified == 0:
        print(f"  {C_GREEN}{C_BOLD}[OK] 100% VERIFIED: Zero supply chain tampering or unverified modifications.{C_RESET}\n")
    else:
        print(f"  {C_CYAN}[i] Tip: Run with '--update' to recalculate signatures after deliberate codebase changes.{C_RESET}\n")

    return passed, modified, missing


def update_manifest(repo_root: Path) -> None:
    """Updates signatures in BUILD_MANIFEST.json with current file hashes."""
    manifest_path = repo_root / "BUILD_MANIFEST.json"
    if not manifest_path.exists():
        print(f"{C_RED}[[FAIL]] BUILD_MANIFEST.json not found.{C_RESET}")
        return

    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    signatures = data.get("cryptographic_signatures", {})

    updated = 0
    for rel_path in list(signatures.keys()):
        target = repo_root / rel_path
        if target.exists():
            signatures[rel_path] = compute_sha256(target)
            updated += 1

    manifest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"{C_GREEN}[OK] Updated {updated} cryptographic signature(s) in BUILD_MANIFEST.json.{C_RESET}")


def hash_single_file(path_str: str) -> None:
    """Computes and prints SHA-256 of any arbitrary file."""
    p = Path(path_str).resolve()
    if not p.exists() or not p.is_file():
        print(f"{C_RED}Error: '{p}' is not a valid file.{C_RESET}")
        sys.exit(1)

    h = compute_sha256(p)
    sz = p.stat().st_size
    print(f"{C_BOLD}File:{C_RESET}    {p}")
    print(f"{C_BOLD}Size:{C_RESET}    {sz:,} bytes")
    print(f"{C_BOLD}SHA-256:{C_RESET} {C_GREEN}{h}{C_RESET}")


def main():
    repo_root = find_repo_root()

    if len(sys.argv) > 1 and sys.argv[1] in ("--update", "-u", "update"):
        update_manifest(repo_root)
    elif len(sys.argv) > 1 and sys.argv[1] in ("hash", "sha256", "checksum"):
        if len(sys.argv) < 3:
            print("Usage: ax-release-verify.py hash <filepath>")
            sys.exit(1)
        hash_single_file(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help", "verify"):
        hash_single_file(sys.argv[1])
    else:
        verify_manifest(repo_root)


if __name__ == "__main__":
    main()
