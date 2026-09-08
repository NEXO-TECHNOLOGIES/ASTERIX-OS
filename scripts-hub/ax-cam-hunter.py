#!/usr/bin/env python3
"""
ASTERIX OS - Hotel & Privacy Counter-Surveillance Subsystem (ax cam-hunter)
Author: NEXO TECHNOLOGIES GROUP
100% Safe, Legal & Defensive Technical Surveillance Counter-Measures (TSCM).

Why Signal Jamming is Not Used:
  1. Legal: RF signal jamming is strictly illegal worldwide (violating FCC / ITU statutes),
     disrupts civilian & emergency 911 communications, and is a felony offense.
  2. Ineffective: Covert cameras and audio bugs frequently record locally to internal
     MicroSD cards or offline flash storage. Emitting radio jamming does NOT stop an offline
     spy camera or recorder from recording!
  3. The Professional Solution: Passive discovery, Wi-Fi IoT surveillance scanning,
     RTSP/ONVIF port auditing, RF beacon RSSI localization, and optical IR lens detection.
"""

import os
import sys
import socket
import subprocess
import re
import time
import argparse
from typing import List, Dict, Tuple, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RED = "\033[38;5;196m"
C_GREEN = "\033[38;5;46m"
C_YELLOW = "\033[38;5;220m"
C_CYAN = "\033[38;5;51m"
C_MAGENTA = "\033[38;5;201m"
C_GRAY = "\033[38;5;242m"
C_WHITE = "\033[38;5;231m"

KNOWN_CAM_PORTS = {
    554: "RTSP (Real-Time Video Streaming)",
    8554: "RTSP-Alt (Secondary Video Stream)",
    8000: "Hikvision / DVR Video Stream",
    8899: "ONVIF Device Management Service",
    3702: "WS-Discovery / ONVIF Discovery",
    1935: "RTMP (Live Streaming Video)",
    80: "HTTP (Web Management / IP Cam Portal)",
    8080: "HTTP-Alt (Webcam Admin Interface)",
    8081: "MJPEG Video Stream (Common in Mini Spy Cams)",
    8888: "IoT Camera Video Server",
    5000: "UPnP / IoT Media Server",
    7070: "RealMedia RTSP Video Port",
}

KNOWN_SPY_OUIS = {
    "18:fe:34": "Espressif Systems (ESP8266 Mini Wi-Fi Camera Module)",
    "24:0a:c4": "Espressif Systems (ESP32-CAM Covert Camera Module)",
    "30:ae:a4": "Espressif Systems (ESP32 IoT Spy Device)",
    "84:f3:eb": "Espressif Systems (ESP8266 IoT Surveillance)",
    "dc:4f:22": "Espressif Systems (ESP32 Module)",
    "a4:cf:12": "Espressif Systems (ESP32 Micro-Camera)",
    "60:01:94": "Tuya Smart (Generic White-Label Wi-Fi Hidden Cam)",
    "d8:1f:12": "Tuya Smart (Mini Wi-Fi Spy Camera)",
    "10:2c:6b": "Tuya Smart (Hidden Nanny Cam / Clock Cam)",
    "bc:dd:c2": "Tuya Smart (Pinhole Wi-Fi Module)",
    "00:12:12": "Hangzhou Xiongmai (XM IPCam / DVR Streamer)",
    "00:23:63": "Zhuhai Raysharp Technology (DVR/NVR Video)",
    "bc:5e:cd": "Hangzhou Hikvision Digital Technology",
    "c8:02:8f": "Hangzhou Hikvision Digital Technology",
    "44:19:b6": "Hangzhou Hikvision Digital Technology",
    "3c:ef:8c": "Zhejiang Dahua Technology (Covert IP Cam)",
    "90:02:a9": "Zhejiang Dahua Technology (IP Surveillance)",
    "e0:50:8b": "Zhejiang Dahua Technology",
    "ac:83:f3": "Shenzhen Reolink Innovation",
    "34:ce:00": "Wyze Labs (Smart Surveillance Camera)",
    "2c:aa:8e": "Wyze Labs (Mini Security Cam)",
    "00:0e:8f": "AMX Corporation (Audio/Video Surveillance)",
}

SUSPICIOUS_SSID_PATTERNS = [
    r"^CAM[_\-0-9a-zA-Z]+$",
    r"^IPCAM[_\-0-9a-zA-Z]+$",
    r"^HD[\-_]?MINI[\-_]?CAM.*$",
    r"^SPY[\-_]?CAM.*$",
    r"^TuyaSmart[_\-0-9a-zA-Z]+$",
    r"^MD81S[_\-0-9a-zA-Z]+$",
    r"^Care[_\-]?Cam[_\-0-9a-zA-Z]+$",
    r"^V380[_\-0-9a-zA-Z]+$",
    r"^LookCam[_\-0-9a-zA-Z]+$",
    r"^HDWiFiCam[_\-0-9a-zA-Z]+$",
    r"^iCookyCam[_\-0-9a-zA-Z]+$",
    r"^Mini[\-_]?DV[_\-0-9a-zA-Z]+$",
]


def banner(title: str, subtitle: str):
    print(f"\n{C_BOLD}{C_CYAN}========================================================================={C_RESET}")
    print(f"{C_BOLD}{C_CYAN}  ASTERIX OS :: {title.upper()}{C_RESET}")
    print(f"{C_DIM}  {subtitle}{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}========================================================================={C_RESET}\n")


def print_jammer_doctrine():
    """Explains why RF jamming is illegal, hazardous, and ineffective vs TSCM."""
    banner("HOTEL & TRAVEL ANTI-SURVEILLANCE DOCTRINE", "Why Signal Jamming Fails & How Real Counter-Surveillance Works")
    print(f"{C_BOLD}[THE REALITY OF SIGNAL JAMMING VS. COVERT CAMERAS]{C_RESET}")
    print(f"  {C_RED}{C_BOLD}✖ WHY RF JAMMING IS ILLEGAL & HARMFUL:{C_RESET}")
    print(f"    • Emitting radio frequency interference violates telecommunications laws worldwide (FCC, ITU).")
    print(f"    • It indiscriminately blocks life-critical emergency communications (911/112 cellular calls,")
    print(f"      hospital equipment, aviation, and emergency responder dispatch).")
    print(f"    • Standard PC and smartphone wireless chips physically lack RF amplification to emit jamming.")
    print()
    print(f"  {C_YELLOW}{C_BOLD}⚠ WHY RF JAMMING DOES NOT STOP HIDDEN CAMERAS:{C_RESET}")
    print(f"    • Over 70% of covert spy cameras (smoke detector cams, clock cams, USB chargers) record directly")
    print(f"      to {C_BOLD}internal MicroSD cards or offline flash memory{C_RESET}.")
    print(f"    • Jamming the airwaves does {C_RED}NOT{C_RESET} stop a camera from recording video to an SD card!")
    print(f"    • If a camera does stream, jamming alerts the attacker and locks your own devices out.")
    print()
    print(f"  {C_GREEN}{C_BOLD}✔ THE PROFESSIONAL SOVEREIGN SOLUTION (TSCM AUDITING):{C_RESET}")
    print(f"    • {C_BOLD}1. LAN IoT Video Sweep:{C_RESET} Detect active IP cameras streaming over the hotel Wi-Fi.")
    print(f"    • {C_BOLD}2. Hardware Vendor OUI Audit:{C_RESET} Flag Espressif (ESP32-CAM) & Tuya covert modules.")
    print(f"    • {C_BOLD}3. Passive RF & BLE Beacon Sweep:{C_RESET} Scan for ad-hoc camera APs without transmitting.")
    print(f"    • {C_BOLD}4. Optical Retro-Reflection Test:{C_RESET} Spot curved pinhole lenses using flashlight retro-glare.")
    print(f"    • {C_BOLD}5. Infrared Night-Vision Inspection:{C_RESET} Spot night-vision IR LEDs invisible to human eyes.\n")


def get_local_ip_and_subnet() -> Tuple[Optional[str], Optional[str]]:
    """Retrieves current active local IP address and /24 subnet base."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.0)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        parts = local_ip.split(".")
        subnet = f"{parts[0]}.{parts[1]}.{parts[2]}"
        return local_ip, subnet
    except Exception:
        return None, None


def get_arp_devices() -> List[Dict[str, str]]:
    """Parses operating system ARP table to find live IPs and MAC addresses."""
    devices = []
    try:
        if sys.platform == "win32":
            output = subprocess.check_output(["arp", "-a"], universal_newlines=True, stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    ip = parts[0]
                    mac = parts[1].lower().replace("-", ":")
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) and re.match(r"^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$", mac):
                        if not ip.startswith("224.") and not ip.startswith("239.") and not ip.endswith(".255"):
                            devices.append({"ip": ip, "mac": mac})
        else:
            output = subprocess.check_output(["arp", "-n"], universal_newlines=True, stderr=subprocess.DEVNULL)
            for line in output.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    ip = parts[0]
                    mac = parts[2].lower()
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) and re.match(r"^([0-9a-f]{2}[:-]){5}([0-9a-f]{2})$", mac):
                        devices.append({"ip": ip, "mac": mac})
    except Exception:
        pass
    return devices


def test_port(ip: str, port: int, timeout: float = 0.4) -> bool:
    """Tests if a specific TCP port is open on a target device."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def scan_network_for_cameras(quick: bool = False):
    """Scans the local network for hidden cameras, video streamers and IoT surveillance."""
    banner("LOCAL NETWORK SURVEILLANCE & CAMERA SCANNER", "Passive & Active IoT Streaming Video Device Discovery")
    local_ip, subnet = get_local_ip_and_subnet()

    if not local_ip or not subnet:
        print(f"  {C_RED}[!] No active network interface detected. Ensure Wi-Fi/Ethernet is connected.{C_RESET}\n")
        return

    print(f"  {C_CYAN}[*] Active Host IP:{C_RESET}     {C_BOLD}{local_ip}{C_RESET}")
    print(f"  {C_CYAN}[*] Target Subnet Range:{C_RESET} {C_BOLD}{subnet}.1 - {subnet}.254{C_RESET}")
    print(f"  {C_CYAN}[*] Probing Surveillance Ports:{C_RESET} RTSP(554/8554), ONVIF(8000/8899), HTTP-Cam(80/8080/8081)\n")

    arp_devs = get_arp_devices()
    print(f"  {C_BOLD}[+] Step 1: Evaluating {len(arp_devs)} Cached Devices in Local ARP Table...{C_RESET}")

    suspicious_findings = []

    for dev in arp_devs:
        ip = dev["ip"]
        mac = dev["mac"]
        oui_prefix = mac[:8]
        vendor_match = KNOWN_SPY_OUIS.get(oui_prefix, None)

        # Probe surveillance ports
        open_ports = []
        for port, service_desc in KNOWN_CAM_PORTS.items():
            if test_port(ip, port, timeout=0.25):
                open_ports.append((port, service_desc))

        is_suspicious = bool(vendor_match) or any(p in [554, 8554, 8000, 8899, 8081] for p, _ in open_ports)

        if is_suspicious:
            suspicious_findings.append({
                "ip": ip,
                "mac": mac,
                "vendor": vendor_match or "Generic / Unregistered Hardware",
                "open_ports": open_ports
            })
            print(f"  {C_RED}{C_BOLD}[ALERT: SUSPICIOUS SURVEILLANCE DEVICE DETECTED]{C_RESET}")
            print(f"    • IP Address:   {C_BOLD}{C_WHITE}{ip}{C_RESET}")
            print(f"    • MAC Address:  {C_YELLOW}{mac}{C_RESET}")
            print(f"    • Hardware OUI: {C_RED}{vendor_match or 'Unknown'}{C_RESET}")
            for p, desc in open_ports:
                print(f"    • Active Port:  {C_GREEN}{p}/TCP{C_RESET} ({desc})")
            print()
        else:
            print(f"    {C_GRAY}• Clean device: {ip:<15} | MAC: {mac} | Vendor: Clean/Standard{C_RESET}")

    if not arp_devs or not quick:
        print(f"\n  {C_BOLD}[+] Step 2: Probing Common Gateway & High-Probability IoT IP Range...{C_RESET}")
        candidate_ips = [f"{subnet}.1", f"{subnet}.2", f"{subnet}.100", f"{subnet}.101", f"{subnet}.200"]
        for cand_ip in candidate_ips:
            if cand_ip == local_ip:
                continue
            open_ports = []
            for port, service_desc in [(554, "RTSP"), (8000, "ONVIF/DVR"), (8081, "MJPEG-Cam")]:
                if test_port(cand_ip, port, timeout=0.2):
                    open_ports.append((port, service_desc))
            if open_ports:
                print(f"  {C_RED}[!] Streaming Video Port Open on {cand_ip}: {open_ports}{C_RESET}")

    print(f"\n{C_BOLD}[NETWORK SCAN SUMMARY]{C_RESET}")
    if suspicious_findings:
        print(f"  {C_RED}{C_BOLD}⚠ WARNING: {len(suspicious_findings)} suspicious video or surveillance device(s) identified on this network!{C_RESET}")
        print(f"  {C_YELLOW}Recommendation: Inspect the physical room, check open ports with VLC (rtsp://<IP>:554/live), or disconnect.{C_RESET}\n")
    else:
        print(f"  {C_GREEN}{C_BOLD}✔ No streaming video endpoints or known spy camera MACs found on this Wi-Fi network.{C_RESET}\n")


def scan_wireless_beacons():
    """Scans for unassociated Wi-Fi camera APs and covert ad-hoc transmitters."""
    banner("WIRELESS RF & AD-HOC BEACON SWEEP", "Passive Detection of P2P & Covert Wi-Fi Camera Access Points")
    print(f"  {C_CYAN}[*] Sweeping airwaves for ad-hoc spy camera SSIDs (CAM_*, IPCAM_*, TuyaSmart_*)...{C_RESET}\n")

    found_beacons = []

    try:
        if sys.platform == "win32":
            output = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=bssid"], universal_newlines=True, stderr=subprocess.DEVNULL)
            current_ssid = ""
            for line in output.splitlines():
                line = line.strip()
                if line.startswith("SSID") and ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        current_ssid = parts[1].strip()
                elif line.startswith("Signal") and ":" in line:
                    sig = line.split(":", 1)[1].strip()
                    if current_ssid:
                        found_beacons.append({"ssid": current_ssid, "signal": sig})
                        current_ssid = ""
        else:
            # Linux iw / nmcli scan
            if subprocess.call(["which", "nmcli"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                output = subprocess.check_output(["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"], universal_newlines=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    parts = line.split(":")
                    if len(parts) >= 2 and parts[0]:
                        found_beacons.append({"ssid": parts[0], "signal": f"{parts[1]}%"})
    except Exception as e:
        print(f"  {C_YELLOW}[!] Could not query wireless adapter ({e}). Skipping live Wi-Fi probe.{C_RESET}\n")

    covert_hits = []
    for b in found_beacons:
        ssid = b["ssid"]
        sig = b["signal"]
        for pat in SUSPICIOUS_SSID_PATTERNS:
            if re.match(pat, ssid, re.IGNORECASE):
                covert_hits.append(b)
                break

    if covert_hits:
        print(f"  {C_RED}{C_BOLD}[CRITICAL WARNING: COVERT AD-HOC CAMERA ACCESS POINT DETECTED]{C_RESET}")
        for hit in covert_hits:
            print(f"    • Suspicious SSID: {C_BOLD}{C_WHITE}{hit['ssid']}{C_RESET}")
            print(f"    • Signal Strength: {C_GREEN}{hit['signal']}{C_RESET} (Hotter signal = closer physical proximity)")
            print(f"    • Threat Profile:  Ad-hoc Wi-Fi camera broadcasting its own setup/streaming beacon.")
        print()
    else:
        print(f"  {C_GREEN}✔ Audited {len(found_beacons)} wireless networks in range. Zero covert camera SSIDs detected.{C_RESET}\n")


def print_optical_and_ir_guide():
    """Renders the comprehensive Technical Surveillance Counter-Measures (TSCM) Hotel Guide."""
    banner("HOTEL & AIRBNB PHYSICAL INSPECTION FIELD GUIDE", "Optical Reflection, Infrared LED & Hardware Inspection Checklist")

    print(f"{C_BOLD}{C_CYAN}── STEP 1: THE INFRARED (IR) NIGHT-VISION TEST ─────────────────────────{C_RESET}")
    print(f"  Many covert cameras use 850nm or 940nm Infrared LEDs for recording in the dark.")
    print(f"  Human eyes cannot see IR light, but smartphone digital sensors DO pick it up as bright purple/white light.")
    print()
    print(f"  {C_BOLD}Procedure:{C_RESET}")
    print(f"  1. Close all blinds and turn off {C_BOLD}ALL lights{C_RESET} in the hotel room so it is pitch black.")
    print(f"  2. Open the camera app on your smartphone or laptop (the front selfie camera usually has NO IR filter).")
    print(f"  3. Slowly pan your camera across the room, focusing on clocks, ceiling vents, and mirrors.")
    print(f"  4. {C_YELLOW}Result:{C_RESET} If you see a pulsing or steady glowing purple/white light that is invisible to your naked eye,")
    print(f"     you have found an active infrared surveillance illuminator!\n")

    print(f"{C_BOLD}{C_CYAN}── STEP 2: THE OPTICAL RETRO-REFLECTION (FLASHLIGHT PINHOLE) TEST ──────{C_RESET}")
    print(f"  Camera lenses are made of curved optical glass or plastic. When light shines directly into them,")
    print(f"  they retro-reflect light back to the source (creating a bright red/blue reflection pinpoint).")
    print()
    print(f"  {C_BOLD}Procedure:{C_RESET}")
    print(f"  1. Hold a bright flashlight or smartphone flash directly next to your eye (at pupil level).")
    print(f"  2. Scan systematically from 2–5 feet away, inspecting all small holes (2mm to 5mm).")
    print(f"  3. Look for a tiny, razor-sharp bright glint of light reflecting back into your eye.\n")

    print(f"{C_BOLD}{C_CYAN}── STEP 3: HIGH-RISK HOTEL HIDING SPOT CHECKLIST ───────────────────────{C_RESET}")
    hotspots = [
        ("Smoke Detectors & Sprinklers", "Top culprit in hotels. Check for tiny unaligned pinholes or extra LEDs."),
        ("Alarm Clocks & Radios", "Look through the tinted glass faceplate with your flashlight."),
        ("USB Wall Charger Bricks", "Check fake chargers plugged into wall outlets facing beds or desks."),
        ("Two-Way Mirrors", "Finger test: Place your fingernail against the glass. If there is a gap between nail and reflection, it is genuine. If your nail touches its own reflection directly with NO gap, it is a two-way mirror!"),
        ("Air Conditioning & Heating Vents", "Look between vent grates for mounted lenses or micro wires."),
        ("Tissue Boxes & Desk Lamps", "Inspect seams, power cords, and hollow plastic housings."),
        ("Bathroom Hooks & Shower Heads", "Check coat hooks on the back of bathroom doors for optical pinholes.")
    ]
    for spot, desc in hotspots:
        print(f"  {C_BOLD}• {spot:<32}{C_RESET} : {desc}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS - Hotel & Travel Anti-Surveillance Suite (ax cam-hunter)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("mode", nargs="?", default="hotel", choices=["hotel", "scan", "rf", "guide", "doctrine", "all"],
                        help="Audit mode: hotel (full audit), scan (network cameras), rf (wireless beacons), guide (optical inspection), doctrine (jammer analysis)")
    parser.add_argument("--quick", action="store_true", help="Perform high-speed quick sweep")

    args = parser.parse_args()

    if args.mode in ["doctrine"]:
        print_jammer_doctrine()
    elif args.mode in ["guide"]:
        print_optical_and_ir_guide()
    elif args.mode in ["scan"]:
        scan_network_for_cameras(quick=args.quick)
    elif args.mode in ["rf"]:
        scan_wireless_beacons()
    elif args.mode in ["hotel", "all"]:
        print_jammer_doctrine()
        scan_network_for_cameras(quick=args.quick)
        scan_wireless_beacons()
        print_optical_and_ir_guide()


if __name__ == "__main__":
    main()
