#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Pure-Python Debian Package Builder (.deb)
  Version: 2.1.0
  Zero Dependencies: 100% Python Standard Library
  
  Capabilities:
    • Assembles valid Debian binary packages (.deb) on any OS (Windows, Linux, Termux)
    • Constructs standard 'ar' archive containing:
        1. debian-binary (2.0)
        2. control.tar.gz (control metadata, md5sums, postinst)
        3. data.tar.gz (filesystem tree / docs / binaries)
    • Generates Kali-style cybersecurity metapackages (network, web, wireless, etc.)
    • Requires zero third-party dependencies (no dpkg-deb or external ar needed)
===============================================================================
"""

import os
import sys
import io
import time
import gzip
import tarfile
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Union

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
    _   ____  ______   ____  ______ ____     ____  __  __
   / | / / / / / __ \\ / __ \\/ ____// __ )   / __ \\/ / / /
  /  |/ / / / / / / // / / / __/  / __  |  / / / / / / / 
 / /|  / /_/ / /_/ // /_/ / /___ / /_/ /  / /_/ / /_/ /  
/_/ |_/\\____/\\____//_____/_____//_____/   \\____/\\____/   
  DEBIAN METAPACKAGE & BINARY BUILDER v2.1{C_RESET}
"""

# Standard ASTERIX OS Metapackage Definitions (Kali-Style Architecture)
STANDARD_METAPACKAGES = {
    "asterix-core": {
        "section": "admin",
        "priority": "standard",
        "architecture": "all",
        "description": "ASTERIX OS Core Subsystem\n Master CLI dispatcher, Debian PRoot manager, and persistent store engine.",
        "depends": "python3, bash, coreutils, tar, gzip, curl, procps, ca-certificates",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-tools-network": {
        "section": "net",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Network Security & Reconnaissance Metapackage\n High-performance network scanning, packet analysis, port probes, and discovery tools.",
        "depends": "nmap, masscan, tcpdump, tshark, socat, netcat-openbsd, dnsutils, iproute2, ethtool, iputils-ping, traceroute",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-tools-web": {
        "section": "net",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Web Application Security & Auditing Metapackage\n Web vulnerability assessment, HTTP fuzzing, API audit, and DOM analysis tools.",
        "depends": "sqlmap, nikto, dirb, curl, wget, python3, ca-certificates, jq, openssl",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-tools-wireless": {
        "section": "net",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Wireless Security & Signal Auditing Metapackage\n 802.11 Wi-Fi monitoring, spectrum analysis, and rogue AP detection tools.",
        "depends": "aircrack-ng, wireless-tools, iw, rfkill",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-tools-re": {
        "section": "devel",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Reverse Engineering & Binary Inspection Metapackage\n Disassemblers, binary analysis tools, debuggers, and ELF inspectors.",
        "depends": "radare2, gdb, binutils, file, strace, ltrace, hexedit",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-tools-crypto": {
        "section": "utils",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Cryptographic & Forensic Tools Metapackage\n Password auditing, cryptographic digest utilities, and volume encryption tools.",
        "depends": "hashcat, john, cryptsetup, bzip2, xz-utils, gnupg",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    },
    "asterix-default": {
        "section": "metapackages",
        "priority": "optional",
        "architecture": "all",
        "description": "ASTERIX OS Default Mobile Security Suite\n Top-level metapackage bundling core, network, web, and reverse engineering toolsets.",
        "depends": "asterix-core, asterix-tools-network, asterix-tools-web, asterix-tools-re, asterix-tools-crypto",
        "homepage": "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"
    }
}


class ArArchiveWriter:
    r"""
    Constructs a standard POSIX Common 'ar' archive format file.
    The Debian .deb container format requires this specific structure:
      - 8-byte magic: '!<arch>\n'
      - 60-byte headers for each member
      - 2-byte trailer: '`\n'
      - 2-byte alignment padding (\n) when data length is odd
    """
    MAGIC = b"!<arch>\n"

    def __init__(self, output_stream: io.BytesIO):
        self.stream = output_stream
        self.stream.write(self.MAGIC)

    def add_file(self, name: str, data: bytes, mtime: int = 0, mode: int = 0o100644, uid: int = 0, gid: int = 0):
        # Format name with trailing slash (System V / GNU ar format standard for deb)
        ar_name = name.ljust(16)[:16].encode("ascii")
        ar_mtime = str(mtime).ljust(12)[:12].encode("ascii")
        ar_uid = str(uid).ljust(6)[:6].encode("ascii")
        ar_gid = str(gid).ljust(6)[:6].encode("ascii")
        ar_mode = oct(mode)[2:].rjust(8)[:8].encode("ascii")
        ar_size = str(len(data)).ljust(10)[:10].encode("ascii")
        ar_trailer = b"`\n"

        header = ar_name + ar_mtime + ar_uid + ar_gid + ar_mode + ar_size + ar_trailer
        self.stream.write(header)
        self.stream.write(data)

        # 2-byte alignment padding if size is odd
        if len(data) % 2 != 0:
            self.stream.write(b"\n")


def make_tar_gz(members: List[Dict[str, Union[str, bytes, int]]]) -> bytes:
    """Creates a deterministic gzipped tar archive from a list of member specs."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.GNU_FORMAT) as tar:
            for member in members:
                path = member["name"]
                content = member.get("content", b"")
                mode = member.get("mode", 0o644)
                mtime = member.get("mtime", 0)
                is_dir = member.get("is_dir", False)
                link_target = member.get("link_target", None)

                ti = tarfile.TarInfo(name=path)
                ti.mtime = mtime
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "root"

                if link_target is not None:
                    ti.type = tarfile.SYMTYPE
                    ti.linkname = link_target
                    tar.addfile(ti)
                elif is_dir:
                    ti.type = tarfile.DIRTYPE
                    ti.mode = mode if mode else 0o755
                    tar.addfile(ti)
                else:
                    ti.type = tarfile.REGTYPE
                    ti.mode = mode if mode else 0o644
                    ti.size = len(content)
                    tar.addfile(ti, io.BytesIO(content))

    return buf.getvalue()


def build_deb(
    package_name: str,
    version: str,
    description: str,
    maintainer: str = "NEXO TECHNOLOGIES GROUP <security@asterixos.org>",
    architecture: str = "all",
    section: str = "utils",
    priority: str = "optional",
    depends: Optional[str] = None,
    homepage: str = "https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS",
    data_members: Optional[List[Dict]] = None,
    postinst_script: Optional[str] = None,
    output_path: Optional[Path] = None
) -> Path:
    """
    Builds a compliant Debian .deb package and saves it to output_path.
    """
    if data_members is None:
        data_members = []

    # Ensure doc dir exists with copyright/README
    doc_dir = f"./usr/share/doc/{package_name}"
    has_doc_dir = any(m["name"] == doc_dir for m in data_members)
    if not has_doc_dir:
        data_members.insert(0, {"name": doc_dir, "is_dir": True, "mode": 0o755})
        data_members.append({
            "name": f"{doc_dir}/copyright",
            "content": (
                f"Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\n"
                f"Upstream-Name: {package_name}\n"
                f"Source: {homepage}\n\n"
                f"Files: *\n"
                f"Copyright: 2026 NEXO TECHNOLOGIES GROUP\n"
                f"License: MIT or Apache-2.0\n"
            ).encode("utf-8"),
            "mode": 0o644
        })

    # 1. Compute md5sums of all regular data files
    md5_lines = []
    installed_size_kb = 0
    for m in data_members:
        if not m.get("is_dir") and "content" in m:
            content = m["content"]
            installed_size_kb += (len(content) + 1023) // 1024
            # Path without leading './'
            rel_path = m["name"].lstrip("./")
            digest = hashlib.md5(content).hexdigest()
            md5_lines.append(f"{digest}  {rel_path}")

    md5sums_bytes = ("\n".join(md5_lines) + "\n").encode("utf-8") if md5_lines else b""

    # 2. Construct control file content
    control_lines = [
        f"Package: {package_name}",
        f"Version: {version}",
        f"Architecture: {architecture}",
        f"Maintainer: {maintainer}",
        f"Installed-Size: {max(installed_size_kb, 1)}",
        f"Section: {section}",
        f"Priority: {priority}",
        f"Homepage: {homepage}",
    ]
    if depends:
        control_lines.append(f"Depends: {depends}")

    # Format multi-line description properly (Debian control syntax requires leading space on subsequent lines)
    desc_parts = description.strip().split("\n")
    short_desc = desc_parts[0].strip()
    long_desc_lines = desc_parts[1:] if len(desc_parts) > 1 else []
    control_lines.append(f"Description: {short_desc}")
    for line in long_desc_lines:
        line_clean = line.strip()
        if not line_clean:
            control_lines.append(" .")
        else:
            control_lines.append(f" {line_clean}")

    control_content = ("\n".join(control_lines) + "\n").encode("utf-8")

    # 3. Create control.tar.gz
    control_members = [
        {"name": "./control", "content": control_content, "mode": 0o644},
    ]
    if md5sums_bytes:
        control_members.append({"name": "./md5sums", "content": md5sums_bytes, "mode": 0o644})
    if postinst_script:
        control_members.append({"name": "./postinst", "content": postinst_script.encode("utf-8"), "mode": 0o755})

    control_tar_gz = make_tar_gz(control_members)

    # 4. Create data.tar.gz
    data_tar_gz = make_tar_gz(data_members)

    # 5. Pack into ar archive (.deb)
    deb_buffer = io.BytesIO()
    ar = ArArchiveWriter(deb_buffer)
    ar.add_file("debian-binary", b"2.0\n", mtime=0, mode=0o100644)
    ar.add_file("control.tar.gz", control_tar_gz, mtime=0, mode=0o100644)
    ar.add_file("data.tar.gz", data_tar_gz, mtime=0, mode=0o100644)

    deb_bytes = deb_buffer.getvalue()

    if output_path is None:
        output_path = Path(f"{package_name}_{version}_{architecture}.deb")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as f:
        f.write(deb_bytes)

    return output_path


def build_all_metapackages(out_dir: Path, version: str = "2.1.0") -> List[Path]:
    """Builds all curated Kali-style metapackages for ASTERIX OS."""
    built_packages = []
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {C_CYAN}[*] Compiling {len(STANDARD_METAPACKAGES)} Kali-style metapackages (Version: {version})...{C_RESET}")
    for name, spec in STANDARD_METAPACKAGES.items():
        deb_file = out_dir / f"{name}_{version}_{spec['architecture']}.deb"
        build_deb(
            package_name=name,
            version=version,
            description=spec["description"],
            architecture=spec["architecture"],
            section=spec["section"],
            priority=spec["priority"],
            depends=spec.get("depends"),
            homepage=spec["homepage"],
            output_path=deb_file
        )
        size_kb = deb_file.stat().st_size / 1024
        print(f"    {C_GREEN}✔{C_RESET} {name:<26} -> {deb_file.name} ({size_kb:.1f} KB)")
        built_packages.append(deb_file)

    return built_packages


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Pure-Python Debian Package & Metapackage Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python ax-deb-builder.py build-all -o dist/debs
  python ax-deb-builder.py meta asterix-tools-network 2.1.0 --depends "nmap, masscan"
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand")

    # build-all command
    cmd_all = subparsers.add_parser("build-all", help="Build all standard ASTERIX OS metapackages")
    cmd_all.add_argument("-o", "--out-dir", default="packages/debs", help="Output directory for .deb files")
    cmd_all.add_argument("-v", "--version", default="2.1.0", help="Package version string (default: 2.1.0)")

    # meta command
    cmd_meta = subparsers.add_parser("meta", help="Build a single custom metapackage")
    cmd_meta.add_argument("name", help="Package name (e.g. asterix-tools-custom)")
    cmd_meta.add_argument("version", help="Version string (e.g. 1.0.0)")
    cmd_meta.add_argument("--depends", required=True, help="Comma-separated package dependencies")
    cmd_meta.add_argument("--desc", default="Custom ASTERIX security metapackage", help="Package description")
    cmd_meta.add_argument("-o", "--out", default=None, help="Output .deb path")

    args = parser.parse_args()

    print(BANNER)

    if args.command == "build-all" or not args.command:
        out_dir = Path(getattr(args, "out_dir", "packages/debs"))
        ver = getattr(args, "version", "2.1.0")
        packages = build_all_metapackages(out_dir, version=ver)
        print(f"\n  {C_BOLD}{C_GREEN}✓ Complete: Successfully generated {len(packages)} Debian metapackages in '{out_dir}'.{C_RESET}\n")

    elif args.command == "meta":
        out = Path(args.out) if args.out else Path(f"{args.name}_{args.version}_all.deb")
        deb_file = build_deb(
            package_name=args.name,
            version=args.version,
            description=args.desc,
            depends=args.depends,
            output_path=out
        )
        print(f"  {C_GREEN}✔ Metapackage created:{C_RESET} {deb_file} ({deb_file.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
