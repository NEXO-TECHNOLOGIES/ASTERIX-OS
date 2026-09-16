#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Zero-Dependency APT Repository Generator
  Version: 2.1.0
  Zero Dependencies: 100% Python Standard Library
  
  Capabilities:
    • Transforms any collection of .deb packages into a fully compliant APT repository
    • Parses Debian .deb archives (ar + tar.gz) and extracts control fields
    • Computes MD5, SHA-1, and SHA-256 digests for binary pools
    • Generates 'Packages', 'Packages.gz', and 'Release' indexes
    • Built-in local HTTP server for testing or LAN package distribution
    • Generates automated /etc/apt/sources.list.d/asterix.list configuration
===============================================================================
"""

import os
import sys
import io
import gzip
import tarfile
import hashlib
import shutil
import http.server
import socketserver
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 output on Windows consoles
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
C_MAGENTA = "\033[95m"
C_WHITE   = "\033[97m"

BANNER = f"""{C_CYAN}{C_BOLD}
    ___     ____  ______   ____  ______ ____     ____  __  __
   /   |   / __ \\/_  __/  / __ \\/ ____// __ \\   / __ \\/ / / /
  / /| |  / /_/ / / /    / /_/ / __/  / /_/ /  / / / / / / / 
 / ___ | / ____/ / /    / _, _/ /___ / ____/  / /_/ / /_/ /  
/_/  |_|/_/     /_/    /_/ |_/_____//_/       \\____/\\____/   
  APT REPOSITORY ENGINE & METADATA INDEXER v2.1{C_RESET}
"""


def extract_deb_control(deb_path: Path) -> Dict[str, str]:
    """
    Parses an 'ar' formatted .deb package and extracts key-value fields
    from its control.tar.gz -> ./control member.
    """
    with deb_path.open("rb") as f:
        magic = f.read(8)
        if magic != b"!<arch>\n":
            raise ValueError(f"Invalid deb file (bad ar magic): {deb_path}")

        control_tar_bytes = None
        while True:
            header = f.read(60)
            if len(header) < 60:
                break
            name = header[:16].decode("ascii", errors="replace").strip()
            size = int(header[48:58].decode("ascii", errors="replace").strip())
            file_data = f.read(size)
            # Alignment padding if odd size
            if size % 2 != 0:
                f.read(1)

            if "control.tar" in name:
                control_tar_bytes = file_data
                break

    if not control_tar_bytes:
        raise ValueError(f"No control.tar found inside: {deb_path}")

    # Extract control file from control.tar.gz
    fields = {}
    with gzip.GzipFile(fileobj=io.BytesIO(control_tar_bytes)) as gz:
        with tarfile.open(fileobj=gz, mode="r:*") as tar:
            for member in tar.getmembers():
                if member.name in ("./control", "control"):
                    f_obj = tar.extractfile(member)
                    if f_obj:
                        text = f_obj.read().decode("utf-8", errors="replace")
                        current_key = None
                        for line in text.splitlines():
                            if not line.strip():
                                continue
                            if line.startswith(" ") or line.startswith("\t"):
                                if current_key:
                                    fields[current_key] += "\n" + line
                            elif ":" in line:
                                k, v = line.split(":", 1)
                                current_key = k.strip()
                                fields[current_key] = v.strip()
    return fields


def compute_hashes(filepath: Path) -> Tuple[str, str, str, int]:
    """Computes MD5, SHA-1, SHA-256 and size in bytes of a file."""
    md5_h = hashlib.md5()
    sha1_h = hashlib.sha1()
    sha256_h = hashlib.sha256()
    size = 0

    with filepath.open("rb") as f:
        while chunk := f.read(65536):
            md5_h.update(chunk)
            sha1_h.update(chunk)
            sha256_h.update(chunk)
            size += len(chunk)

    return md5_h.hexdigest(), sha1_h.hexdigest(), sha256_h.hexdigest(), size


def generate_apt_repository(
    debs_source_dir: Path,
    repo_root: Path,
    codename: str = "phantom",
    suite: str = "stable",
    component: str = "main",
    architectures: Optional[List[str]] = None
) -> Path:
    """
    Generates a full Debian APT repository structure in repo_root.
    Layout:
      repo_root/
        pool/main/
          *.deb
        dists/stable/
          Release
          main/
            binary-all/
              Packages
              Packages.gz
            binary-amd64/
            binary-arm64/
    """
    if architectures is None:
        architectures = ["all", "amd64", "arm64"]

    deb_files = list(debs_source_dir.glob("*.deb"))
    if not deb_files:
        raise FileNotFoundError(f"No .deb packages found in '{debs_source_dir}'. Run ax-deb-builder first!")

    pool_dir = repo_root / "pool" / component
    pool_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {C_CYAN}[*] Copying {len(deb_files)} package(s) into APT pool: {pool_dir}...{C_RESET}")
    staged_debs = []
    for deb in deb_files:
        dest = pool_dir / deb.name
        shutil.copy2(deb, dest)
        staged_debs.append(dest)

    # Group package metadata by architecture
    arch_packages: Dict[str, List[str]] = {arch: [] for arch in architectures}

    for deb in staged_debs:
        meta = extract_deb_control(deb)
        pkg_arch = meta.get("Architecture", "all")
        md5_val, sha1_val, sha256_val, file_size = compute_hashes(deb)
        rel_pool_path = f"pool/{component}/{deb.name}"

        entry_lines = [
            f"Package: {meta.get('Package', '')}",
            f"Version: {meta.get('Version', '1.0.0')}",
            f"Architecture: {pkg_arch}",
            f"Maintainer: {meta.get('Maintainer', 'NEXO TECHNOLOGIES GROUP')}",
            f"Installed-Size: {meta.get('Installed-Size', '0')}",
        ]
        if "Depends" in meta:
            entry_lines.append(f"Depends: {meta['Depends']}")
        if "Section" in meta:
            entry_lines.append(f"Section: {meta['Section']}")
        if "Priority" in meta:
            entry_lines.append(f"Priority: {meta['Priority']}")
        if "Homepage" in meta:
            entry_lines.append(f"Homepage: {meta['Homepage']}")

        entry_lines.extend([
            f"Filename: {rel_pool_path}",
            f"Size: {file_size}",
            f"MD5sum: {md5_val}",
            f"SHA1: {sha1_val}",
            f"SHA256: {sha256_val}",
        ])
        if "Description" in meta:
            entry_lines.append(f"Description: {meta['Description']}")

        entry_text = "\n".join(entry_lines) + "\n\n"

        # If architecture is "all", it belongs in all binary architecture trees
        if pkg_arch == "all":
            for arch in architectures:
                arch_packages[arch].append(entry_text)
        elif pkg_arch in arch_packages:
            arch_packages[pkg_arch].append(entry_text)
        else:
            arch_packages.setdefault(pkg_arch, []).append(entry_text)

    # Generate Packages and Packages.gz for each architecture
    dist_dir = repo_root / "dists" / suite
    indexed_files = []

    for arch, entries in arch_packages.items():
        binary_dir = dist_dir / component / f"binary-{arch}"
        binary_dir.mkdir(parents=True, exist_ok=True)

        packages_content = "".join(entries).encode("utf-8")
        packages_file = binary_dir / "Packages"
        with packages_file.open("wb") as f:
            f.write(packages_content)

        packages_gz_file = binary_dir / "Packages.gz"
        with packages_gz_file.open("wb") as raw_f:
            with gzip.GzipFile(fileobj=raw_f, mode="wb", mtime=0) as gz:
                gz.write(packages_content)

        # Track relative to dist_dir for Release index
        for fpath in (packages_file, packages_gz_file):
            rel_path = fpath.relative_to(dist_dir).as_posix()
            m, s1, s256, sz = compute_hashes(fpath)
            indexed_files.append({"path": rel_path, "md5": m, "sha1": s1, "sha256": s256, "size": sz})
            print(f"    {C_GREEN}✔{C_RESET} Generated {component}/binary-{arch}/{fpath.name} ({sz} bytes)")

    # Generate Release file
    release_lines = [
        "Origin: ASTERIX OS",
        "Label: ASTERIX OS APT Repository",
        f"Suite: {suite}",
        f"Codename: {codename}",
        f"Architectures: {' '.join(architectures)}",
        f"Components: {component}",
        "Description: Official ASTERIX OS Debian Rootless & Mobile Security Package Repository",
        "MD5Sum:",
    ]
    for info in indexed_files:
        release_lines.append(f" {info['md5']} {info['size']:>8} {info['path']}")

    release_lines.append("SHA1:")
    for info in indexed_files:
        release_lines.append(f" {info['sha1']} {info['size']:>8} {info['path']}")

    release_lines.append("SHA256:")
    for info in indexed_files:
        release_lines.append(f" {info['sha256']} {info['size']:>8} {info['path']}")

    release_content = "\n".join(release_lines) + "\n"
    release_file = dist_dir / "Release"
    with release_file.open("w", encoding="utf-8") as f:
        f.write(release_content)

    print(f"    {C_GREEN}✔{C_RESET} Generated dists/{suite}/Release")

    # Generate sources.list snippet
    sources_snippet = (
        f"# ASTERIX OS Local / Self-Hosted APT Repository\n"
        f"# Copy to: /etc/apt/sources.list.d/asterix.list\n"
        f"deb [trusted=yes] file:{repo_root.resolve().as_posix()} {suite} {component}\n"
    )
    sources_file = repo_root / "asterix.list"
    with sources_file.open("w", encoding="utf-8") as f:
        f.write(sources_snippet)

    return repo_root


def serve_repo(repo_root: Path, port: int = 8080):
    """Serves the APT repository over HTTP for local testing or LAN distribution."""
    os.chdir(str(repo_root))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n  {C_BOLD}{C_GREEN}⚡ ASTERIX APT Repository Serving on http://localhost:{port}/{C_RESET}")
        print(f"  {C_CYAN}Add to Debian / Termux PRoot sources:{C_RESET}")
        print(f"    echo 'deb [trusted=yes] http://<YOUR-IP>:{port} stable main' > /etc/apt/sources.list.d/asterix.list")
        print(f"    apt-get update\n")
        print(f"  Press Ctrl+C to terminate.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n  {C_YELLOW}[!] Server stopped.{C_RESET}")


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Zero-Dependency APT Repository Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # build command
    cmd_build = subparsers.add_parser("build", help="Generate APT repository from .deb packages")
    cmd_build.add_argument("-s", "--source", default="packages/debs", help="Directory containing .deb files")
    cmd_build.add_argument("-o", "--out", default="apt-repo", help="Output repository root directory")
    cmd_build.add_argument("--suite", default="stable", help="Debian suite name (default: stable)")
    cmd_build.add_argument("--codename", default="phantom", help="Repository codename (default: phantom)")

    # serve command
    cmd_serve = subparsers.add_parser("serve", help="Serve APT repository over HTTP")
    cmd_serve.add_argument("-r", "--repo", default="apt-repo", help="Repository directory to serve")
    cmd_serve.add_argument("-p", "--port", type=int, default=8080, help="Port to listen on (default: 8080)")

    args = parser.parse_args()

    print(BANNER)

    if args.command == "build" or not args.command:
        src = Path(getattr(args, "source", "packages/debs"))
        out = Path(getattr(args, "out", "apt-repo"))
        suite = getattr(args, "suite", "stable")
        codename = getattr(args, "codename", "phantom")

        repo_dir = generate_apt_repository(src, out, codename=codename, suite=suite)
        print(f"\n  {C_BOLD}{C_GREEN}✓ Complete: APT Repository successfully indexed at '{repo_dir}'.{C_RESET}")
        print(f"  {C_WHITE}To inspect sources line: cat {repo_dir / 'asterix.list'}{C_RESET}\n")

    elif args.command == "serve":
        repo_dir = Path(args.repo)
        if not repo_dir.exists():
            print(f"  {C_RED}[!] Error: Repository path '{repo_dir}' does not exist. Run 'build' first.{C_RESET}")
            sys.exit(1)
        serve_repo(repo_dir, port=args.port)


if __name__ == "__main__":
    main()
