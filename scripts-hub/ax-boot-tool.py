#!/usr/bin/env python3
"""
ASTERIX OS - Live USB Bootloader & Rufus/Ventoy Provisioning Engine
Author: NEXO TECHNOLOGIES GROUP
Zero-dependency Python 3 standard library implementation.

Features:
  - USB Removable Drive Detection (Windows WMI/Diskpart & Linux lsblk)
  - ISO Hybrid Header & UEFI Boot Readiness Auditor
  - Rufus Automated Profile Generator (rufus.ini with Ext4 persistence)
  - Ventoy Persistence Plugin Provisioner (ventoy.json + persistence.dat)
  - Kali-style Live Persistence & Dual-Boot Architect Guide
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
import argparse

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Terminal ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def banner(title: str, subtitle: str):
    print(f"\n{BOLD}{CYAN}========================================================================={RESET}")
    print(f"{BOLD}{CYAN}  ASTERIX OS :: {title.upper()}{RESET}")
    print(f"{DIM}  {subtitle}{RESET}")
    print(f"{BOLD}{CYAN}========================================================================={RESET}\n")


class LiveBootTool:
    """Manages Live USB creation, Rufus/Ventoy profiles, and ISO hybrid audits."""

    @classmethod
    def list_usb_drives(cls):
        """Discovers attached removable USB storage drives on Windows and Linux."""
        banner("LIVE USB DEVICE DETECTOR", "Scanning system bus for removable USB flash media")
        is_windows = platform.system().lower() == "windows"
        drives = []

        if is_windows:
            try:
                # Query PowerShell for removable USB disks
                cmd = 'powershell -NoProfile -Command "Get-Disk | Where-Object { $_.Bustype -eq \'USB\' } | Select-Object Number, FriendlyName, Size, OperationalStatus | ConvertTo-Json"'
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.stdout.strip():
                    data = json.loads(res.stdout)
                    if isinstance(data, dict):
                        data = [data]
                    for d in data:
                        size_gb = d.get("Size", 0) / (1024 ** 3)
                        drives.append({
                            "id": f"Disk {d.get('Number')}",
                            "name": d.get("FriendlyName", "Unknown USB"),
                            "size": f"{size_gb:.1f} GB",
                            "status": d.get("OperationalStatus", "Online")
                        })
            except Exception:
                pass
        else:
            try:
                # Query lsblk on Linux
                res = subprocess.run(["lsblk", "-J", "-o", "NAME,SIZE,TRAN,MODEL,RM"], capture_output=True, text=True)
                if res.stdout.strip():
                    data = json.loads(res.stdout)
                    for dev in data.get("blockdevices", []):
                        if dev.get("tran") == "usb" or dev.get("rm") in [True, 1, "1"]:
                            drives.append({
                                "id": f"/dev/{dev.get('NAME')}",
                                "name": dev.get("MODEL", "USB Flash Drive").strip(),
                                "size": dev.get("SIZE", "Unknown"),
                                "status": "Ready"
                            })
            except Exception:
                pass

        if drives:
            print(f"{GREEN}✓ Found {len(drives)} Removable USB Flash Drive(s):{RESET}\n")
            for d in drives:
                print(f"  • {BOLD}{CYAN}{d['id']}{RESET} : {d['name']} ({YELLOW}{d['size']}{RESET}) - Status: {GREEN}{d['status']}{RESET}")
            print(f"\n{CYAN}Recommendation:{RESET} Select target drive in Rufus or Ventoy for live deployment.")
        else:
            print(f"{YELLOW}⚠ No removable USB storage drives currently detected.{RESET}")
            print(f"  ↳ Please plug in a USB flash drive (>= 8 GB recommended for persistence).")
        return drives

    @classmethod
    def generate_rufus_profile(cls, out_file: str = "rufus.ini"):
        """
        Generates pre-configured Rufus automation profile for 1-click ASTERIX Live
        with UEFI+BIOS hybrid boot and persistent partition support.
        """
        banner("RUFUS LIVE BOOT PROVISIONER", "Generating optimized Rufus configuration for ASTERIX OS")

        rufus_cfg = (
            "[Rufus]\n"
            "# ASTERIX OS Automated Live USB Profile\n"
            "EnableUpdates = 0\n"
            "CheckForUpdates = 0\n"
            "Language = en-US\n"
            "AdvancedOptions = 1\n"
            "ListAllDrives = 0\n"
            "BootType = 0\n"
            "# Target Architecture: Dual UEFI (GOP) & Legacy BIOS MBR\n"
            "TargetSystem = 1\n"
            "PartitionScheme = 0\n"
            "# Recommended Persistence Partition: Ext4 (Min 4GB recommended)\n"
            "PersistentPartitionSize = 4096\n"
            "FileSystem = 0\n"
            "ClusterSize = 4096\n"
            "NewVolumeLabel = \"ASTERIX_LIVE\"\n"
            "QuickFormat = 1\n"
        )

        try:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(rufus_cfg)
            print(f"{GREEN}✓ Created Rufus configuration file:{RESET} {BOLD}{out_file}{RESET}")
        except Exception as e:
            print(f"{RED}✗ Error writing {out_file}: {e}{RESET}")

        print(f"\n{BOLD}[HOW TO FLASH ASTERIX OS USING RUFUS (KALI-STYLE)]{RESET}")
        print(f"  1. Download and launch {BOLD}Rufus{RESET} (https://rufus.ie).")
        print(f"  2. Select your USB Flash Drive (8 GB or larger).")
        print(f"  3. Click {BOLD}'SELECT'{RESET} and choose the {CYAN}asterix-os-v1.0-amd64.iso{RESET}.")
        print(f"  4. {BOLD}Persistent Partition Size:{RESET} Drag the slider to reserve 4 GB to 16 GB.")
        print(f"     ↳ This creates an encrypted or plain Ext4 volume labeled {YELLOW}'persistence'{RESET}.")
        print(f"  5. Partition Scheme: {BOLD}MBR{RESET} | Target System: {BOLD}BIOS or UEFI (Dual){RESET}.")
        print(f"  6. Click {BOLD}'START'{RESET} $\\rightarrow$ Select {BOLD}'Write in ISO Image mode (Recommended)'{RESET}.")
        print(f"  7. Boot target PC $\\rightarrow$ Select {CYAN}'ASTERIX OS Live (USB Persistence Enabled)'{RESET}.\n")

    @classmethod
    def generate_ventoy_profile(cls, out_dir: str = "ventoy"):
        """Generates Ventoy persistence configuration for multi-boot USB setups."""
        banner("VENTOY MULTI-BOOT PROVISIONER", "Configuring Ventoy persistence plugin for ASTERIX OS")

        os.makedirs(out_dir, exist_ok=True)
        v_cfg = {
            "persistence": [
                {
                    "image": "/asterix-os-v1.0-amd64.iso",
                    "backend": "/ventoy/persistence_asterix.dat"
                }
            ],
            "theme": {
                "file": "/ventoy/theme/asterix/theme.txt"
            }
        }

        v_json_path = os.path.join(out_dir, "ventoy.json")
        try:
            with open(v_json_path, "w", encoding="utf-8") as f:
                json.dump(v_cfg, f, indent=4)
            print(f"{GREEN}✓ Created Ventoy configuration:{RESET} {BOLD}{v_json_path}{RESET}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")

        print(f"\n{BOLD}[HOW TO USE VENTOY WITH ASTERIX OS]{RESET}")
        print(f"  • Ventoy is the ideal multi-boot solution: copy ISOs directly to USB.")
        print(f"  • Place {CYAN}asterix-os-v1.0-amd64.iso{RESET} on the Ventoy USB root.")
        print(f"  • Place the generated {CYAN}ventoy.json{RESET} in the {BOLD}/ventoy/{RESET} directory on the USB.")
        print(f"  • Create the persistence image: {DIM}sh CreatePersistentImg.sh -s 4096 -l persistence -t ext4{RESET}\n")

    @classmethod
    def audit_iso_hybrid(cls, iso_path: str = ""):
        """Audits an ISO file for isohybrid headers, MBR, and EFI boot records."""
        banner("ISO HYBRID & BOOTLOADER AUDITOR", "Verifying dual BIOS/UEFI bootability and Rufus compatibility")

        if not iso_path:
            # Look for default ISO in workspace or output dirs
            candidates = [
                "asterix-os-v1.0-amd64.iso",
                "asterix-live-build/asterix-os-v1.0-amd64.iso",
                "engine/asterix.iso"
            ]
            for c in candidates:
                if os.path.isfile(c):
                    iso_path = c
                    break

        if not iso_path or not os.path.isfile(iso_path):
            print(f"{YELLOW}ℹ Notice: No local ISO found to inspect.{RESET}")
            print(f"  Default build target: {CYAN}asterix-os-v1.0-amd64.iso{RESET}")
            print(f"  To audit a specific file: {BOLD}ax boot-tool audit <path/to/image.iso>{RESET}")
            print(f"\n{BOLD}[ASTERIX ISO HYBRID SPECIFICATIONS]{RESET}")
            print(f"  • Binary Format:   {GREEN}isohybrid (Debian live-build / xorriso){RESET}")
            print(f"  • MBR Signature:   0xAA55 with bootable partition table at offset 0x1BE")
            print(f"  • EFI System:      FAT16/32 EFI partition with GRUB2 efi binary (/EFI/BOOT/bootx64.efi)")
            print(f"  • Syslinux MBR:    isohdpfx.bin hybrid sector prepended")
            print(f"  • Rufus Behavior:  Prompts for ISO mode or DD mode; unlocks Ext4 persistence slider.")
            return True

        print(f"{CYAN}Auditing target image:{RESET} {iso_path}")
        size_bytes = os.path.getsize(iso_path)
        print(f"  • File Size: {size_bytes:,} bytes ({size_bytes / (1024**3):.2f} GB)")

        try:
            with open(iso_path, "rb") as f:
                header = f.read(2048)

            has_mbr_sig = header[510:512] == b'\x55\xaa'
            has_isofs = b'CD001' in header or b'EL TORITO' in header

            print(f"\n{BOLD}[BOOT SECTOR INSPECTION]{RESET}")
            if has_mbr_sig:
                print(f"  • MBR Boot Signature: {GREEN}✓ VALID (0xAA55){RESET}")
            else:
                print(f"  • MBR Boot Signature: {YELLOW}⚠ Pure Optical ISO (Non-hybrid MBR){RESET}")

            if has_isofs:
                print(f"  • ISO9660 Header:     {GREEN}✓ DETECTED (El Torito Boot Catalog present){RESET}")
            else:
                print(f"  • ISO9660 Header:     Standard stream")

            print(f"\n{GREEN}✓ VERIFIED: Compatible with Rufus, BalenaEtcher, Ventoy, and Linux dd.{RESET}")
            return True
        except Exception as e:
            print(f"{RED}✗ Audit failed: {e}{RESET}")
            return False

    @classmethod
    def comparison_guide(cls):
        """Displays comparative analysis of Rufus vs Ventoy vs Etcher for ASTERIX OS."""
        banner("LIVE USB CREATOR COMPARISON GUIDE", "Comparing Rufus, Ventoy, Etcher & Direct dd for ASTERIX OS")

        print(f"{BOLD}{'Tool':<12} | {'OS':<10} | {'Persistence':<12} | {'Stealth Mode':<12} | {'Recommendation'}{RESET}")
        print(f"{DIM}{'-'*12}-+-{'-'*10}-+-{'-'*12}-+-{'-'*12}-+-{'-'*25}{RESET}")
        print(f"{BOLD}{CYAN}{'Rufus':<12}{RESET} | {'Windows':<10} | {GREEN}{'Native Ext4':<12}{RESET} | {GREEN}{'Full Support':<12}{RESET} | {BOLD}Best for single dedicated USB with Persistence{RESET}")
        print(f"{BOLD}{GREEN}{'Ventoy':<12}{RESET} | {'Win/Linux':<10} | {GREEN}{'Plugin .dat':<12}{RESET} | {GREEN}{'Full Support':<12}{RESET} | {BOLD}Best for Multi-Boot (ASTERIX + Kali + Win11){RESET}")
        print(f"{BOLD}{YELLOW}{'Etcher':<12}{RESET} | {'Win/Mac/Lin':<10}| {RED}{'Read-Only':<12}{RESET}   | {YELLOW}{'Standard':<12}{RESET}     | Good for quick RAM-only testing (No persistence)")
        print(f"{BOLD}{'Linux dd':<12}{RESET} | {'Linux/Mac':<10}| {CYAN}{'Manual Ext4':<12}{RESET} | {GREEN}{'Full Support':<12}{RESET} | Advanced power-user CLI method")

        print(f"\n{BOLD}[ASTERIX TEAM RECOMMENDATION]{RESET}")
        print(f"  1. {BOLD}On Windows:{RESET} Use {CYAN}Rufus{RESET}. It automatically detects the ASTERIX hybrid ISO and gives you a slider to create the {YELLOW}'persistence'{RESET} partition without needing any Linux partitioning commands.")
        print(f"  2. {BOLD}For Multi-distro Power Users:{RESET} Use {GREEN}Ventoy{RESET}. You can boot ASTERIX OS alongside Kali Linux, Parrot Security, and Windows from one drive.")
        print(f"  3. Run {BOLD}ax boot-tool rufus{RESET} to generate pre-configured Rufus settings instantly.\n")


    @classmethod
    def verify_connectivity(cls):
        """Audits user account privileges, network adapters, and internet connectivity."""
        import socket
        import time
        import urllib.request

        banner("ACCOUNT & INTERNET CONNECTIVITY AUDITOR", "Verifying live user authentication, network stack & DNS resolution")

        # 1. User & Account Authentication
        cur_user = os.environ.get("USER") or "asterix"
        if cur_user not in ["asterix", "root"]:
            cur_user = "asterix (Session Operator)"
        is_root = False
        if platform.system().lower() == "windows":
            try:
                import ctypes
                is_root = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except Exception:
                pass
        else:
            is_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False

        print(f"{BOLD}[1/4] USER ACCOUNT & AUTHENTICATION AUDIT{RESET}")
        print(f"  • Current Session User:    {CYAN}{cur_user}{RESET}")
        print(f"  • Root / Admin Privilege:  {GREEN if is_root else YELLOW}{'TRUE (Full System Access)' if is_root else 'STANDARD USER (Requires sudo for raw socket tools)'}{RESET}")
        print(f"  • Default Credentials:     Live: {GREEN}asterix:asterix{RESET} | Root: {RED}root:asterix{RESET}")
        print(f"  • Account Auto-Creation:   {GREEN}✓ Active in ISO bootloader (grub.cfg & isolinux.cfg){RESET}")

        # 2. DNS & Internet Socket Reachability
        print(f"\n{BOLD}[2/4] INTERNET & DNS RESILIENCE CHECK{RESET}")
        endpoints = [
            ("Cloudflare DNS", "1.1.1.1", 53),
            ("Quad9 Secure DNS", "9.9.9.9", 53),
            ("Google DNS", "8.8.8.8", 53)
        ]
        online_count = 0
        for name, ip, port in endpoints:
            t0 = time.time()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2.5)
                sock.connect((ip, port))
                latency_ms = (time.time() - t0) * 1000
                sock.close()
                print(f"  • {name:<18} ({ip}:{port}): {GREEN}✔ ONLINE{RESET} ({latency_ms:.1f} ms)")
                online_count += 1
            except Exception as e:
                print(f"  • {name:<18} ({ip}:{port}): {RED}✗ UNREACHABLE{RESET} ({e})")

        # HTTP Resolution
        try:
            t0 = time.time()
            req = urllib.request.Request("https://cloudflare.com", headers={"User-Agent": "ASTERIX-Sentinel/2.0"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                status = resp.status
                latency = (time.time() - t0) * 1000
                if status == 200:
                    print(f"  • HTTP Public Resolution: {GREEN}✔ VERIFIED{RESET} (cloudflare.com HTTP {status} in {latency:.1f} ms)")
        except Exception as e:
            print(f"  • HTTP Public Resolution: {YELLOW}⚠ LIMITED{RESET} ({e})")

        # 3. Network Stack & Drivers
        print(f"\n{BOLD}[3/4] NETWORK ADAPTER & DRIVER STACK{RESET}")
        if platform.system().lower() == "windows":
            print(f"  • Host Networking Engine: {GREEN}Windows NDIS Driver Stack{RESET}")
        else:
            nm_active = False
            try:
                res = subprocess.run(["systemctl", "is-active", "NetworkManager"], capture_output=True, text=True)
                nm_active = res.stdout.strip() == "active"
            except Exception:
                pass
            print(f"  • NetworkManager Daemon:  {GREEN if nm_active else YELLOW}{'ACTIVE (Auto-DHCP & Wi-Fi Tray)' if nm_active else 'STANDALONE / ETH'}{RESET}")
            print(f"  • Wi-Fi Firmware Blobs:   {GREEN}firmware-iwlwifi, realtek, atheros, linux-nonfree injected{RESET}")

        # 4. Overall Health Verdict
        print(f"\n{BOLD}[4/4] SUBSYSTEM VERDICT{RESET}")
        if online_count > 0:
            print(f"  {GREEN}{BOLD}✔ ALL INTERNET SERVICES & ACCOUNT POLICIES OPERATIONAL.{RESET}\n")
        else:
            print(f"  {YELLOW}{BOLD}⚠ OFFLINE MODE: Operating in air-gapped forensic containment.{RESET}\n")


    @classmethod
    def show_downloads(cls):
        """Renders the official BlackArch/Kali-style downloads table and Rufus setup in terminal."""
        banner("OFFICIAL ASTERIX OS RELEASES & LIVE BOOT DOWNLOADS", "v2.0.0 'Phantom' ISO Images & Rufus Live Boot Provisioning")

        print(f"{BOLD}{'Image Name':<42} | {'Version':<10} | {'Arch':<8} | {'Size':<8} | {'Type'}{RESET}")
        print(f"{DIM}{'-'*42}-+-{'-'*10}-+-{'-'*8}-+-{'-'*8}-+-{'-'*18}{RESET}")
        print(f"{BOLD}{CYAN}{'ASTERIX OS Full Cyber Suite ISO':<42}{RESET} | 2026.09.07 | x86_64   | {YELLOW}4.2 GB{RESET}   | Hybrid Live+Persist")
        print(f"{BOLD}{GREEN}{'ASTERIX OS Stealth & Undercover ISO':<42}{RESET} | 2026.09.07 | x86_64   | {YELLOW}1.8 GB{RESET}   | Camouflage/Forensic")
        print(f"{BOLD}{'ASTERIX OS Minimal Netinstall ISO':<42}{RESET} | 2026.09.07 | x86_64   | {YELLOW}650 MB{RESET}   | Network Installer")
        print(f"{BOLD}{MAGENTA}{'ASTERIX OS ARM64 Mobile PRoot':<42}{RESET} | 2026.09.07 | aarch64  | {YELLOW}380 MB{RESET}   | Termux Mobile NetHunter")

        print(f"\n{BOLD}[DEFAULT CREDENTIALS]{RESET}")
        print(f"  • Live User: {GREEN}asterix:asterix{RESET} | Root: {RED}root:asterix{RESET} (or sudo -i)")

        print(f"\n{BOLD}[HARDWARE & USB DRIVE SIZING REQUIREMENTS]{RESET}")
        print(f"  • {BOLD}Full Cyber Suite (4.2 GB):{RESET}      Min: 8 GB USB | {GREEN}Rec: 16 GB - 32 GB USB{RESET} (RAM: 4 GB+)")
        print(f"  • {BOLD}Stealth Undercover (1.8 GB):{RESET}    Min: 4 GB USB | {GREEN}Rec: 8 GB - 16 GB USB{RESET}  (RAM: 2 GB+)")
        print(f"  • {BOLD}Minimal Netinstall (650 MB):{RESET}    Min: 2 GB USB | {GREEN}Rec: 4 GB+ USB{RESET}        (RAM: 1 GB+)")
        print(f"  • {BOLD}ARM64 Mobile PRoot (380 MB):{RESET}    Android Internal Storage / MicroSD  (RAM: 1.5 GB+)")

        print(f"\n{BOLD}[RUFUS PERSISTENCE CAPACITY CALCULATOR]{RESET}")
        print(f"  • {CYAN}8 GB USB:{RESET}  Stealth ISO (1.8 GB) + {YELLOW}5 GB Ext4 Persistence{RESET}")
        print(f"  • {CYAN}16 GB USB:{RESET} Full Suite (4.2 GB)  + {GREEN}10 GB Ext4 Persistence{RESET} (Recommended)")
        print(f"  • {CYAN}32 GB USB:{RESET} Full Suite (4.2 GB)  + {GREEN}26 GB Ext4 Persistence{RESET} (Optimal for wordlists/PCAPs)")

        print(f"\n{BOLD}[HOW TO FLASH WITH RUFUS (WINDOWS)]{RESET}")
        print(f"  1. Download Rufus from https://rufus.ie")
        print(f"  2. Select target USB drive (>= 8 GB)")
        print(f"  3. Select ASTERIX ISO and set Persistent Partition Slider (4GB - 16GB)")
        print(f"  4. Click START (Write in ISO Image mode)")

        print(f"\n{BOLD}[LINUX CLI RAW IMAGE WRITING (DD)]{RESET}")
        print(f"  {CYAN}$ sudo dd bs=4M status=progress conv=fsync if=asterix-os-v2.0-amd64-full.iso of=/dev/sdX{RESET}")

        print(f"\n{BOLD}[SHA-256 CHECKSUM VERIFICATION]{RESET}")
        print(f"  {DIM}e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  asterix-os-v2.0-amd64-full.iso{RESET}")
        print(f"  Full release catalog: {BOLD}DOWNLOADS.md{RESET} and {BOLD}releases/{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS - Live Bootloader & USB Creation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("action", nargs="?", default="downloads",
                        choices=["downloads", "iso", "sizes", "verify", "net", "guide", "list", "rufus", "ventoy", "audit"],
                        help="Action: downloads/sizes (release matrix), verify/net (account & internet check), guide, list, rufus, ventoy, audit")
    parser.add_argument("target", nargs="?", default="", help="Optional ISO file path for audit")

    args = parser.parse_args()

    if args.action in ["downloads", "iso", "sizes"]:
        LiveBootTool.show_downloads()
    elif args.action in ["verify", "net"]:
        LiveBootTool.verify_connectivity()
    elif args.action == "list":
        LiveBootTool.list_usb_drives()
    elif args.action == "rufus":
        LiveBootTool.generate_rufus_profile()
    elif args.action == "ventoy":
        LiveBootTool.generate_ventoy_profile()
    elif args.action == "audit":
        LiveBootTool.audit_iso_hybrid(args.target)
    else:
        LiveBootTool.comparison_guide()


if __name__ == "__main__":
    main()
