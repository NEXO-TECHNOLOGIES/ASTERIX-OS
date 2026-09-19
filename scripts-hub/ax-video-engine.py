#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Cinematic Video Production Engine (1080p 60FPS)
  Tool: ax video-create / ax reel
  Version: 3.0.0
  Zero Dependencies: 100% Python Standard Library + FFmpeg
  SPDX-License-Identifier: MIT OR Apache-2.0

  Generates 5 Full HD Feature Showcase Videos + Master Showcase Compilation:
    1. 01_ATTACK_PATH_PATHFINDER_1080p.mp4
    2. 02_MULTIPLAYER_TEAM_SYNC_1080p.mp4
    3. 03_GHOST_EGRESS_DECOY_1080p.mp4
    4. 04_MOBILE_RF_SENSOR_SENTINEL_1080p.mp4
    5. 05_TAMPER_PROOF_EVIDENCE_VAULT_1080p.mp4
    6. ASTERIX_OS_BREAKTHROUGH_MASTER_SHOWCASE_1080p.mp4
===============================================================================
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any

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
C_CYAN    = "\033[96m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_RED     = "\033[91m"
C_MAGENTA = "\033[95m"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "assets" / "animations"
WALLPAPERS_DIR = BASE_DIR / "assets" / "wallpapers"
FONT_PATH = "C\\:/Windows/Fonts/consola.ttf" if sys.platform == "win32" else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_BOLD = "C\\:/Windows/Fonts/consolab.ttf" if sys.platform == "win32" else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

# Check for custom generated artwork or fallbacks
PATHFINDER_BG = Path("C:/Users/Baha/.gemini/antigravity/brain/7fbffb3c-4b96-4516-9e0f-8b17058ddcb4/pathfinder_showcase_1789597168728.jpg")
if not PATHFINDER_BG.exists():
    PATHFINDER_BG = WALLPAPERS_DIR / "ASTERIX_LINIX_01_Green_Hacker_1920x1080.png"

FEATURE_SPECS = [
    {
        "id": "01_ATTACK_PATH_PATHFINDER",
        "title": "ATTACK PATH PATHFINDER",
        "subtitle": "Autonomous DAG Attack Surface Synthesis & Shortest Path HUD",
        "command": "$ ax pathfinder demo --export-html reports/graph.html",
        "badge": "DAG GRAPH ENGINE v3.0",
        "badge_color": "0x00f0ff",
        "bg_image": str(PATHFINDER_BG).replace("\\", "/"),
        "telemetry": [
            "[+] Ingesting unified project.json model: 20 Nodes, 37 Directed Edges",
            "[*] Target Crown Jewel: corp-dc-01.aerospace.internal (10.0.20.5)",
            "[>] Shortest Attack Path: Attacker Entry -> Port 3389 -> Domain Controller",
            "[#] Lowest-Noise Stealth Path: Detection Noise Score 4.5 (Stealth)",
            "[!] Critical Chokepoint Identified: MS-WBT-SERVER (3389)",
            "[OK] Exported Standalone Cyber Graph HUD: reports/attack_path_graph.html"
        ],
        "audio_freq": 320
    },
    {
        "id": "02_MULTIPLAYER_TEAM_SYNC",
        "title": "MULTIPLAYER SQUAD SYNCHRONIZATION",
        "subtitle": "P2P Encrypted Mesh & Target Lock Collision Avoidance",
        "command": "$ ax team lock 10.0.20.5 --reason Active Kerberos Extraction",
        "badge": "P2P COLLAB MESH v3.0",
        "badge_color": "0x9d00ff",
        "bg_image": str(WALLPAPERS_DIR / "ASTERIX_LINIX_02_Purple_Galaxy_1920x1080.png").replace("\\", "/"),
        "telemetry": [
            "[+] Squad Mesh red-alpha initialized with HMAC-SHA256 Auth",
            "[*] Operator Callsign: ghost_lead | Node UUID: 1044b893...",
            "[LOCK] Target 10.0.20.5 LOCKED by ghost_lead for 30 minutes",
            "[ALERT] Collision Avoidance Active: Other squad members warned",
            "[>] Logical Vector Clock causality synchronized: ghost_lead = 2",
            "[OK] Zero Cloud Infra: Direct Wi-Fi / Hotspot P2P Delta Exchange"
        ],
        "audio_freq": 280
    },
    {
        "id": "03_GHOST_EGRESS_DECOY",
        "title": "GHOST EGRESS & DECOY BLENDING",
        "subtitle": "Dynamic Traffic Shaping & Benign Enterprise WAF Decoys",
        "command": "$ ax ghost decoy --count 5 --interval 1.0 --jitter 0.5",
        "badge": "GHOST EGRESS v3.0",
        "badge_color": "0x00ff9d",
        "bg_image": str(WALLPAPERS_DIR / "ASTERIX_LINIX_03_Neon_City_1920x1080.png").replace("\\", "/"),
        "telemetry": [
            "[*] Egress Network Posture: IPv6 SLAAC Privacy Addresses Active",
            "[*] Client Morphing: Chrome/Win -> Safari/macOS -> Firefox/Linux",
            "[>] Decoy 01: https://www.cloudflare.com/robots.txt (HTTP 200, 42ms)",
            "[>] Decoy 02: https://www.microsoft.com/robots.txt (HTTP 200, 58ms)",
            "[>] Decoy 03: https://kernel.org/releases.json (Gaussian Jitter: 0.44s)",
            "[OK] EDR/WAF Behavioral Heuristic Scoring Defeated: Enterprise Noise Blend"
        ],
        "audio_freq": 440
    },
    {
        "id": "04_MOBILE_RF_SENSOR_SENTINEL",
        "title": "MOBILE RF & WIRELESS SENSOR SENTINEL",
        "subtitle": "Passive BLE Tracker Hunter, Evil Twin & RF Jamming Auditor",
        "command": "$ ax radio status --defensive",
        "badge": "RF SENTINEL v3.0",
        "badge_color": "0xff0055",
        "bg_image": str(WALLPAPERS_DIR / "ASTERIX_LINIX_05_Red_Terminal_1920x1080.png").replace("\\", "/"),
        "telemetry": [
            "[RADIO] Passive BLE Sentinel: Apple AirTag / Find My Detected (5C:62:3A...)",
            "[ALERT] Evil Twin Hunter: Multi-BSSID conflict & downgrade probe",
            "[SHIELD] RF Jamming Audit: Threat Level NOMINAL (Zero continuous CW noise)",
            "[LOCK] 802.11w PMF Protection: Protected Management Frames Enforced",
            "[>] Ultrasonic Sensor Probe: 18 kHz - 22 kHz tracking band audited",
            "[OK] 100 PERCENT Passive Hardware Compliance (FCC/CE Non-Jamming)"
        ],
        "audio_freq": 220
    },
    {
        "id": "05_TAMPER_PROOF_EVIDENCE_VAULT",
        "title": "TAMPER-PROOF EVIDENCE VAULT",
        "subtitle": "Cryptographic RFC 3161 Timestamps & .axproof Verification Envelopes",
        "command": "$ ax evidence seal engagement_loot.pcap && ax evidence verify",
        "badge": "EVIDENCE PROOF v3.0",
        "badge_color": "0xffb800",
        "bg_image": str(WALLPAPERS_DIR / "ASTERIX_LINIX_07_Cyan_Core_1920x1080.png").replace("\\", "/"),
        "telemetry": [
            "[+] Cryptographic Artifact Binding: SHA-256 + SHA-512 Dual Digest",
            "[+] RFC 3161 Timestamp Token Bound: Microsecond UTC & Monotonic Clock",
            "[+] Hardware Attestation: Machine Fingerprint & Operator HMAC Signed",
            "[OK] VERIFICATION PASSED: CHAIN OF CUSTODY 100 PERCENT INTACT (.axproof)",
            "[ALERT] Forensic Tampering Sentinel: Bit-for-bit corruption instantly flagged",
            "[OK] Court-Admissible Forensic Verification Journal: evidence_ledger.json"
        ],
        "audio_freq": 380
    }
]


def render_feature_video(spec: Dict[str, Any], output_file: Path, duration: int = 7):
    """Renders a single high-impact 1080p 30fps MP4 feature video."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    bg_img = spec["bg_image"]
    title = spec["title"].replace("'", "").replace(":", "")
    subtitle = spec["subtitle"].replace("'", "").replace(":", "")
    command = spec["command"].replace("'", "").replace(":", r"\:")
    badge = spec["badge"].replace("'", "")
    badge_color = spec["badge_color"]
    freq = spec["audio_freq"]

    drawtext_filters = []
    
    # 1. Background glassmorphic container
    drawtext_filters.append("drawbox=x=60:y=60:w=1800:h=960:color=black@0.65:t=fill")
    drawtext_filters.append(f"drawbox=x=60:y=60:w=1800:h=960:color={badge_color}@0.8:t=3")
    
    # Header Box
    drawtext_filters.append("drawbox=x=60:y=60:w=1800:h=120:color=black@0.85:t=fill")
    drawtext_filters.append(f"drawbox=x=60:y=180:w=1800:h=2:color={badge_color}@0.9:t=fill")

    # Header Title & Subtitle
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='ASTERIX OS // {title}':fontcolor=white:fontsize=36:x=100:y=90"
    )
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_PATH}':text='{subtitle}':fontcolor=0x94a3b8:fontsize=20:x=100:y=140"
    )
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='[ {badge} ]':fontcolor={badge_color}:fontsize=24:x=1860-tw-40:y=105"
    )

    # Command Execution Terminal Box
    drawtext_filters.append("drawbox=x=100:y=210:w=1720:h=70:color=0x0f172a@0.9:t=fill")
    drawtext_filters.append("drawbox=x=100:y=210:w=1720:h=70:color=0x334155@0.8:t=1")
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='{command}':fontcolor=0x38bdf8:fontsize=24:x=130:y=232"
    )

    # Telemetry Rows
    start_y = 320
    step_y = 80
    for idx, line in enumerate(spec["telemetry"]):
        t_show = 0.6 + (idx * 0.7)
        l_color = "0x00ff9d" if "[OK]" in line or "[>]" in line else ("0x38bdf8" if "[+]" in line else ("0xff0055" if "[ALERT]" in line or "[LOCK]" in line else "0xe2e8f0"))
        cleaned_line = line.replace("'", "").replace("%", " PERCENT").replace(":", r"\:")
        
        drawtext_filters.append(
            f"drawbox=x=100:y={start_y + idx*step_y}:w=1720:h=60:color=0x090d13@0.75:t=fill:enable='gte(t,{t_show:.2f})'"
        )
        drawtext_filters.append(
            f"drawbox=x=100:y={start_y + idx*step_y}:w=6:h=60:color={badge_color}:t=fill:enable='gte(t,{t_show:.2f})'"
        )
        drawtext_filters.append(
            f"drawtext=fontfile='{FONT_PATH}':text='{cleaned_line}':fontcolor={l_color}:fontsize=22:x=130:y={start_y + idx*step_y + 18}:enable='gte(t,{t_show:.2f})'"
        )

    # Footer Watermarks
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='ASTERIX OS v3.0 // NEXT-GEN CYBERNETIC SECURITY PLATFORM':fontcolor=0x64748b:fontsize=16:x=100:y=980"
    )
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_PATH}':text='https\\://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS':fontcolor=0x00f0ff:fontsize=16:x=1860-tw-40:y=980"
    )

    # Subtle moving scanline
    drawtext_filters.append(
        "drawbox=x=60:y='mod(t*300, 960)+60':w=1800:h=4:color=white@0.12:t=fill"
    )

    vf_chain = ",".join(drawtext_filters)

    # Audio synthesis
    audio_filter = (
        f"sine=frequency={freq}:duration={duration},volume=0.15[s1];"
        f"sine=frequency={freq*1.5}:duration={duration},volume=0.08[s2];"
        f"anoisesrc=d={duration}:c=pink:r=44100:a=0.02[n];"
        f"[s1][s2][n]amix=inputs=3[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", bg_img,
        "-f", "lavfi", "-i", f"sine=frequency={freq}:duration={duration}",
        "-filter_complex",
        f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,{vf_chain}[vout];{audio_filter}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        str(output_file)
    ]

    print(f"{C_CYAN}[*] Rendering {output_file.name}...{C_RESET}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"{C_RED}[!] Error rendering {output_file.name}:\n{proc.stderr}{C_RESET}")
        return False

    print(f"{C_GREEN}[[OK]] Rendered: {output_file.name} ({os.path.getsize(output_file) // 1024} KB){C_RESET}")
    return True


def render_master_showcase(rendered_files: List[Path], master_output: Path):
    """Concatenates all individual showcase videos into a master feature trailer."""
    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for vid in rendered_files:
            abs_p = str(vid.resolve()).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c", "copy",
        str(master_output)
    ]

    print(f"\n{C_MAGENTA}{C_BOLD}[*] Assembling Master Compilation Showcase: {master_output.name}...{C_RESET}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if list_file.exists():
        list_file.unlink()

    if proc.returncode == 0 and master_output.exists():
        print(f"{C_GREEN}{C_BOLD}[[OK]] Master Compilation Trailer Rendered Successfully:{C_RESET}")
        print(f"     {master_output} ({os.path.getsize(master_output) // 1024} KB)")
        return True
    else:
        print(f"{C_RED}[!] Master concatenation error: {proc.stderr}{C_RESET}")
        return False


def main():
    print(f"\n{C_CYAN}{C_BOLD}==============================================================={C_RESET}")
    print(f"{C_CYAN}{C_BOLD}  ASTERIX OS — Autonomous Video Production Studio v3.0         {C_RESET}")
    print(f"{C_CYAN}{C_BOLD}  High-Definition 1080p 60FPS Video Generation for AI & Socials {C_RESET}")
    print(f"{C_CYAN}{C_BOLD}==============================================================={C_RESET}\n")

    if not shutil.which("ffmpeg"):
        print(f"{C_RED}[!] FFmpeg binary not found on system PATH. Aborting.{C_RESET}")
        sys.exit(1)

    rendered = []
    for spec in FEATURE_SPECS:
        out_path = OUTPUT_DIR / f"{spec['id']}_1080p.mp4"
        ok = render_feature_video(spec, out_path, duration=7)
        if ok:
            rendered.append(out_path)

    if len(rendered) == len(FEATURE_SPECS):
        master_file = OUTPUT_DIR / "ASTERIX_OS_BREAKTHROUGH_MASTER_SHOWCASE_1080p.mp4"
        render_master_showcase(rendered, master_file)

    print(f"\n{C_GREEN}{C_BOLD}[[OK]] All {len(rendered)} Feature Videos Generated in:{C_RESET}")
    print(f"     {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
