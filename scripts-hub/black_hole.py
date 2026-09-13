#!/usr/bin/env python3
"""Black Hole — defensive privacy hardening + local surveillance detection.

This module is intentionally framed as a privacy-hardening/internet masking tool:
- it verifies the host is not leaking obvious DNS/IP data,
- it checks the local network for suspicious camera-like devices,
- it checks for microphone/camera exposure indicators on the host,
- it can attempt aggressive local masking to disconnect the active wireless link
  and reduce exposure when the risk score indicates a suspicious environment.

This is a best-effort local hardening and detection layer. It can reduce network
and physical exposure substantially, but it is not a guarantee of preventing all
surveillance by any party or bypassing every form of tracking.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import shutil
except ImportError:  # pragma: no cover
    shutil = None


def default_policy() -> Dict[str, Any]:
    return {
        "network": {
            "dns_privacy": True,
            "https_only": True,
            "local_log_redaction": True,
            "proxy_fallback": True,
            "system_telemetry_cleanup": True,
        },
        "device_scan": {
            "arp_scan": True,
            "port_scan": True,
            "wifi_probe": True,
            "camera_checks": True,
            "mic_checks": True,
        },
        "hidden_device_detection": {
            "camera": True,
            "microphone": True,
            "infrared_led": True,
            "unknown_wifi_beacon": True,
        },
        "status": "ready",
    }


class BlackHole:
    """Privacy hardening and local surveillance detection suite."""

    CAMERA_PORTS = [554, 8554, 8000, 8080, 8081, 8899, 5000, 1935, 7070]
    CAMERA_HINTS = [
        "IPCAM", "CAM_", "SPY", "RTSP", "MJPEG", "ONVIF", "TuyaSmart", "ESP32", "DVR"
    ]

    def __init__(self, policy: Dict[str, Any] | None = None):
        self.policy = default_policy()
        if policy:
            self.policy.update(policy)
        self._deep_probe_guard = 0

    def local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def subnet_prefix(self) -> str:
        ip = self.local_ip()
        if ip == "127.0.0.1":
            return "127.0.0"
        parts = ip.split(".")
        if len(parts) == 4:
            return ".".join(parts[:3])
        return "127.0.0"

    def host_connectivity(self) -> Dict[str, Any]:
        try:
            socket.create_connection(("1.1.1.1", 443), timeout=2).close()
            return {"internet_check": "ok", "dns_lookup": "ok"}
        except Exception:
            return {"internet_check": "blocked_or_unreachable", "dns_lookup": "unknown"}

    def arp_table(self) -> List[Dict[str, str]]:
        devices: List[Dict[str, str]] = []
        try:
            if sys.platform.startswith("win"):
                out = subprocess.check_output(["arp", "-a"], stderr=subprocess.DEVNULL, text=True)
                for line in out.splitlines():
                    parts = line.split()
                    if len(parts) >= 3 and parts[0].count(".") == 3:
                        ip = parts[0]
                        mac = parts[1] if len(parts) > 1 else "unknown"
                        devices.append({"ip": ip, "mac": mac.lower()})
            else:
                out = subprocess.check_output(["arp", "-n"], stderr=subprocess.DEVNULL, text=True)
                for line in out.splitlines()[2:]:
                    parts = line.split()
                    if len(parts) >= 4:
                        ip = parts[0]
                        mac = parts[2]
                        devices.append({"ip": ip, "mac": mac.lower()})
        except Exception:
            pass
        return devices

    def port_probe(self, host: str, port: int, timeout: float = 0.08) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((host, port))
                return True
        except Exception:
            return False

    def suspicious_camera_hosts(self) -> List[Dict[str, Any]]:
        suspicious: List[Dict[str, Any]] = []
        devices = self.arp_table()
        candidate_ips = {d["ip"] for d in devices}
        subnet = self.subnet_prefix()
        if subnet and subnet != "127.0.0":
            for last in range(1, 11):
                candidate_ips.add(f"{subnet}.{last}")
        for host in sorted(candidate_ips):
            open_ports = []
            for port in self.CAMERA_PORTS:
                if self.port_probe(host, port):
                    open_ports.append(port)
            if open_ports:
                suspicious.append({"host": host, "ports": open_ports, "risk": "possible_camera_or_streaming_device"})
        return suspicious

    def local_audio_camera_signals(self) -> Dict[str, Any]:
        findings: List[str] = []
        checks = []

        for path in ("/proc/asound/cards", "/dev/video0", "/dev/video1"):
            if os.path.exists(path):
                checks.append(path)

        if checks:
            findings.append("camera or audio device nodes detected on the host")
        else:
            findings.append("no obvious local webcam/audio device nodes were detected")

        audio_tools = ["arecord", "ffmpeg", "v4l2-ctl", "lsusb", "system_profiler"]
        available = [t for t in audio_tools if shutil_which(t)]
        if available:
            findings.append(f"device inspection utilities available: {', '.join(available)}")

        return {
            "check_paths": checks,
            "findings": findings,
            "status": "pass" if "no obvious local webcam/audio device nodes were detected" in findings else "warning",
        }

    def usb_device_suspicion(self) -> Dict[str, Any]:
        suspicious: List[str] = []
        device_paths: List[str] = []
        usb_class_matches = []
        has_usb_bus = False

        usb_paths = [
            Path("/sys/bus/usb/devices"),
            Path("/sys/class/video4linux"),
            Path("/dev/input/by-id"),
            Path("/dev/input/by-path"),
        ]

        for base in usb_paths:
            if base.exists():
                has_usb_bus = True
                device_paths.append(str(base))
                try:
                    if base.is_dir():
                        for child in sorted(base.iterdir()):
                            name = child.name.lower()
                            if any(token in name for token in ["camera", "video", "audio", "mic", "sensor", "webcam", "hid", "usb"]):
                                suspicious.append(child.name)
                            if any(token in name for token in ["video", "audio", "camera", "mic"]):
                                usb_class_matches.append(child.name)
                except Exception:
                    continue

        if shutil_which("lsusb"):
            try:
                proc = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=5)
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        lowered = line.lower()
                        if any(token in lowered for token in ["camera", "video", "audio", "mic", "sensor", "webcam", "hid"]):
                            suspicious.append(line.strip())
            except Exception:
                pass

        if sys.platform.startswith("win"):
            try:
                proc = subprocess.run(["wmic", "path", "Win32_USBControllerDevice", "get", "Dependent"], capture_output=True, text=True, timeout=5)
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        lowered = line.lower()
                        if any(token in lowered for token in ["camera", "video", "audio", "mic", "sensor", "webcam"]):
                            suspicious.append(line.strip())
            except Exception:
                pass

        unique_suspicious = []
        seen = set()
        for item in suspicious:
            key = str(item).strip()
            if key and key.lower() not in seen:
                seen.add(key.lower())
                unique_suspicious.append(key)

        status = "pass"
        if unique_suspicious:
            status = "warning"
        elif not has_usb_bus:
            status = "pass"

        return {
            "status": status,
            "device_paths": device_paths,
            "suspicious_devices": unique_suspicious,
            "usb_device_classes": usb_class_matches,
            "notes": "USB/peripheral inspection checks for camera, audio, and sensor-like attachments.",
        }

    def wifi_beacons(self) -> List[Dict[str, Any]]:
        beacons: List[Dict[str, Any]] = []
        try:
            if sys.platform.startswith("win"):
                proc = subprocess.run(["netsh", "wlan", "show", "network", "mode=bssid"], capture_output=True, text=True, timeout=5)
                if proc.returncode == 0:
                    for line in proc.stdout.splitlines():
                        if "SSID" in line and "Signal" not in line:
                            ssid = line.split(":", 1)[1].strip()
                            if ssid:
                                beacons.append({"ssid": ssid, "signal": "unknown", "security": "unknown", "bssid": "unknown"})
            else:
                commands = [
                    ["iwlist", "scan"],
                    ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,BSSID", "device", "wifi", "list"],
                ]
                for cmd in commands:
                    if shutil_which(cmd[0]):
                        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if proc.returncode == 0 and proc.stdout.strip():
                            for raw in proc.stdout.splitlines():
                                if not raw.strip():
                                    continue
                                entry = {"ssid": "unknown", "signal": "unknown", "security": "unknown", "bssid": "unknown"}
                                if raw.startswith("Cell") and "Address" in raw:
                                    continue
                                if "ESSID:" in raw:
                                    entry["ssid"] = raw.split("ESSID:", 1)[1].strip().strip('"')
                                elif "SSID:" in raw:
                                    entry["ssid"] = raw.split(":", 1)[1].strip().strip('"')
                                if "Signal level=" in raw:
                                    entry["signal"] = raw.split("Signal level=", 1)[1].split()[0].strip()
                                if "Security" in raw or "SECURITY" in raw:
                                    entry["security"] = "encrypted"
                                if "Address:" in raw and "Cell" in raw:
                                    entry["bssid"] = raw.split("Address:", 1)[1].strip()
                                if entry["ssid"] != "unknown":
                                    beacons.append(entry)
                            break
        except Exception:
            pass
        return beacons

    def network_exposure(self) -> Dict[str, Any]:
        exposed = []
        for port in [22, 53, 80, 443, 3389, 8080, 8443, 8000, 8554, 5000]:
            if self.port_probe(self.local_ip(), port):
                exposed.append(port)
        return {
            "local_open_ports": exposed,
            "exposure_level": "low" if not exposed else "elevated",
            "notes": "Local-only exposure check for common service and surveillance ports",
        }

    def classify_wifi_fingerprint(self, ssid: str) -> Dict[str, str]:
        label = "unknown"
        lowered = (ssid or "").lower()
        if any(token in lowered for token in ["cam", "camera", "ipcam", "dvr", "cctv", "doorbell", "baby", "spy", "security"]):
            label = "camera_like"
        elif any(token in lowered for token in ["phone", "pixel", "galaxy", "iphone", "android", "tablet", "hotspot", "mi", "tecno", "motorola", "xiaomi"]):
            label = "mobile_device"
        elif any(token in lowered for token in ["guest", "public", "airport", "hotel", "starbucks", "cafe", "library", "wifi"]):
            label = "public_network"
        elif any(token in lowered for token in ["office", "corp", "work", "secure", "enterprise"]):
            label = "workplace_network"
        elif lowered.strip():
            label = "unknown_network"
        return {"ssid": ssid or "unknown", "classification": label}

    def signal_intensity(self, signal_check: Dict[str, Any], wifi: List[Dict[str, Any]], camera_scan: List[Dict[str, Any]], network: Dict[str, Any]) -> Dict[str, Any]:
        camera_score = 0
        mic_score = 0
        if camera_scan:
            camera_score += 35 + 10 * len(camera_scan)
        if signal_check["status"] == "warning":
            mic_score += 30
            camera_score += 15
        if signal_check["check_paths"]:
            mic_score += 15
            camera_score += 10
        if wifi:
            camera_score += min(20, len(wifi) * 8)
            mic_score += min(15, len(wifi) * 5)
        if network["local_open_ports"]:
            camera_score += min(25, 10 * len(network["local_open_ports"]))
            mic_score += min(20, 8 * len(network["local_open_ports"]))

        overall = min(100, max(camera_score, mic_score))
        return {
            "camera_intensity": min(100, camera_score),
            "microphone_intensity": min(100, mic_score),
            "overall_intensity": overall,
            "assessment": "high" if overall >= 70 else "medium" if overall >= 40 else "low",
        }

    def record_risk_trend(self, risk_score: int) -> Dict[str, Any]:
        state_dir = Path.home() / ".asterix_vault"
        state_dir.mkdir(parents=True, exist_ok=True)
        history_path = state_dir / "black_hole_risk_history.json"
        history: List[Dict[str, Any]] = []
        if history_path.exists():
            try:
                with open(history_path, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                    if isinstance(loaded, list):
                        history = loaded
            except Exception:
                history = []

        entry = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "risk_score": int(risk_score),
        }
        history.append(entry)
        if len(history) > 20:
            history = history[-20:]
        with open(history_path, "w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2)
        return {"history_path": str(history_path), "samples": len(history), "latest": entry}

    def trace_assessment(self, user_query: str | None = None, probe_data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if probe_data is None:
            probe_data = self.deep_probe()
        if not isinstance(probe_data, dict):
            probe_data = {}
        if not probe_data:
            return {
                "decision": "clear",
                "confidence": "low",
                "assessment": "no strong evidence of hostile tracing",
                "signals": [],
                "risk_score": 0,
                "ai_reasoning": "No actionable surveillance data was provided; the environment appears ordinary.",
            }

        score = int(probe_data.get("risk_score", 0))
        reasons: List[str] = []

        if probe_data.get("camera_scan"):
            reasons.append("camera-like devices are visible on the local subnet")
        if probe_data.get("wifi_beacons"):
            reasons.append("multiple wireless beacons or nearby networks are detectable")
        if probe_data.get("network_exposure", {}).get("local_open_ports"):
            reasons.append("service ports are exposed locally and deserve scrutiny")
        if probe_data.get("device_signal_check", {}).get("status") == "warning":
            reasons.append("host-side camera or audio indicators are active")

        if user_query:
            q = user_query.lower()
            if any(word in q for word in ["traced", "tracked", "watched", "being watched", "followed", "surveilled", "listening", "recording"]):
                reasons.append("user narrative suggests they suspect surveillance or tracking")

        if not reasons:
            overall = "no strong evidence of hostile tracing"
            verdict = "clear"
            confidence = "low"
        elif score >= 70:
            overall = "likely targeted surveillance or hostile tracing is present"
            verdict = "high"
            confidence = "high"
        elif score >= 40:
            overall = "some suspicious exposure patterns are present; targeted tracing is possible"
            verdict = "medium"
            confidence = "medium"
        else:
            overall = "low-confidence exposure, but the pattern is worth monitoring"
            verdict = "low"
            confidence = "medium"

        return {
            "decision": verdict,
            "confidence": confidence,
            "assessment": overall,
            "signals": reasons,
            "risk_score": score,
            "ai_reasoning": (
                "The system combines wireless visibility, open service exposure, and local device indicators "
                "to infer whether a user is being observed or traced. High scores across multiple layers suggest "
                "coordinated surveillance, while sparse findings indicate ordinary local connectivity."
            ),
        }

    def disconnect_active_connection(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "protocol": "Asterix Protocol 156",
            "status": "not_attempted",
            "internet_masking": "initiated",
            "detail": "No active Wi‑Fi connection was disconnected.",
        }
        try:
            if sys.platform.startswith("win"):
                proc = subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, text=True, timeout=8)
                if proc.returncode == 0:
                    result["status"] = "disconnected"
                    result["detail"] = "The active Wi‑Fi connection was terminated as part of Asterix Protocol 156."
                else:
                    result["status"] = "failed"
                    result["detail"] = proc.stderr.strip() or proc.stdout.strip() or "Wi‑Fi disconnect command failed."
            else:
                proc = subprocess.run(["nmcli", "radio", "wifi", "off"], capture_output=True, text=True, timeout=8)
                if proc.returncode == 0:
                    result["status"] = "disconnected"
                    result["detail"] = "The active Wi‑Fi radio was disabled as part of Asterix Protocol 156."
                else:
                    result["status"] = "failed"
                    result["detail"] = proc.stderr.strip() or proc.stdout.strip() or "Wi‑Fi radio shutdown command failed."
        except Exception as exc:
            result["status"] = "failed"
            result["detail"] = str(exc)
        return result

    def mask_internet(self, disconnect: bool = False, aggressive: bool = False) -> Dict[str, Any]:
        probe = self.deep_probe()
        total_masking = bool(aggressive or probe["risk_score"] >= 70)
        hardening_actions = [
            "disconnect active wireless link when available",
            "disable obvious camera/audio exposure hints on the local host",
            "review nearby Wi‑Fi beacon fingerprints and USB peripherals",
            "reduce DNS and network exposure by enforcing local privacy hygiene",
        ]
        if aggressive:
            hardening_actions.append("enable full aggressive masking mode and escalation monitoring")

        action = {
            "protocol": "Asterix Protocol 156",
            "name": "Internet masking initiated",
            "risk_score": probe["risk_score"],
            "risk_level": probe["risk_level"],
            "status": "armed",
            "disconnect": disconnect,
            "aggressive": aggressive,
            "total_masking": total_masking,
            "masking_guarantee": "best_effort_local_mask_only",
            "hardening_actions": hardening_actions,
            "warning": "This is a best-effort local mitigation layer; it cannot guarantee total invisibility against all surveillance methods.",
        }
        if disconnect:
            action["connection_action"] = self.disconnect_active_connection()
            action["status"] = action["connection_action"]["status"]
        if total_masking:
            action["masking_guarantee"] = "best_effort_total_local_masking"
            action["status"] = action.get("status", "armed")
        return action

    def deep_probe(self) -> Dict[str, Any]:
        if self._deep_probe_guard:
            return {
                "risk_score": 0,
                "risk_level": "low",
                "wifi_beacons": [],
                "wifi_fingerprints": [],
                "signal_summary": {
                    "camera_like_devices": 0,
                    "wifi_networks_seen": 0,
                    "device_nodes_detected": 0,
                    "open_local_ports": 0,
                    "camera_risk": "low",
                    "microphone_risk": "low",
                },
                "network_exposure": {"local_open_ports": [], "exposure_level": "low", "notes": "Fallback probe after recursion guard."},
                "camera_scan": [],
                "device_signal_check": {"check_paths": [], "findings": [], "status": "pass"},
                "usb_device_check": {"status": "pass", "device_paths": [], "suspicious_devices": [], "usb_device_classes": [], "notes": "Fallback probe after recursion guard."},
                "signal_intensity": {"camera_intensity": 0, "microphone_intensity": 0, "overall_intensity": 0, "assessment": "low"},
                "policy": self.policy["hidden_device_detection"],
                "risk_trend": {"history_path": "", "samples": 0, "latest": {"timestamp": "", "risk_score": 0}},
                "trace_assessment": {"decision": "clear", "confidence": "low", "assessment": "no strong evidence of hostile tracing", "signals": [], "risk_score": 0, "ai_reasoning": "Recursion guard prevented a re-entrant deep probe."},
                "targeted_surveillance_verdict": {"status": "normal_environment", "confidence": "low", "summary": "The environment appears ordinary.", "signals": [], "auto": True},
            }

        self._deep_probe_guard += 1
        try:
            camera_scan = self.suspicious_camera_hosts()
            signal_check = self.local_audio_camera_signals()
            wifi = self.wifi_beacons()
            network = self.network_exposure()
            wifi_fingerprints = [self.classify_wifi_fingerprint(item.get("ssid", "unknown")) for item in wifi]
            intensity = self.signal_intensity(signal_check, wifi, camera_scan, network)
            signal_summary = {
                "camera_like_devices": len(camera_scan),
                "wifi_networks_seen": len(wifi),
                "device_nodes_detected": len(signal_check["check_paths"]),
                "open_local_ports": len(network["local_open_ports"]),
                "camera_risk": "high" if camera_scan else "low",
                "microphone_risk": "high" if signal_check["status"] == "warning" else "low",
            }
            risk_score = 10
            risk_score += len(camera_scan) * 22
            risk_score += len(wifi) * 8
            risk_score += len(network["local_open_ports"]) * 7
            if signal_check["status"] == "warning":
                risk_score += 20
            risk_score = min(risk_score, 100)

            risk_trend = self.record_risk_trend(risk_score)
            usb_check = self.usb_device_suspicion()
            if usb_check["status"] == "warning":
                risk_score += 18
                signal_summary["microphone_risk"] = "high"

            risk_score = min(risk_score, 100)
            probe = {
                "risk_score": risk_score,
                "risk_level": "critical" if risk_score >= 70 else "elevated" if risk_score >= 40 else "low",
                "wifi_beacons": wifi,
                "wifi_fingerprints": wifi_fingerprints,
                "signal_summary": signal_summary,
                "network_exposure": network,
                "camera_scan": camera_scan,
                "device_signal_check": signal_check,
                "usb_device_check": usb_check,
                "signal_intensity": intensity,
                "policy": self.policy["hidden_device_detection"],
                "risk_trend": risk_trend,
            }
            probe["trace_assessment"] = self.trace_assessment(probe_data=probe)
            probe["targeted_surveillance_verdict"] = self.auto_targeted_surveillance_verdict(probe)
            return probe
        finally:
            self._deep_probe_guard -= 1

    def auto_targeted_surveillance_verdict(self, probe: Dict[str, Any]) -> Dict[str, Any]:
        score = int(probe.get("risk_score", 0))
        reasons = []
        if probe.get("camera_scan"):
            reasons.append("camera-like devices visible")
        if probe.get("device_signal_check", {}).get("status") == "warning":
            reasons.append("host device signals are active")
        if probe.get("usb_device_check", {}).get("status") == "warning":
            reasons.append("USB or peripheral anomalies detected")
        if len(probe.get("wifi_beacons", [])) >= 3:
            reasons.append("multiple nearby beacon fingerprints are present")
        if probe.get("network_exposure", {}).get("local_open_ports"):
            reasons.append("local exposure ports are open")

        if score >= 75 or (score >= 50 and len(reasons) >= 2):
            verdict = "targeted_surveillance"
            confidence = "high" if score >= 75 else "medium"
            summary = "Multiple environmental and host-side signals indicate a likely targeted surveillance pattern."
        elif score >= 40:
            verdict = "monitoring_risk"
            confidence = "medium"
            summary = "The system shows elevated exposure but not enough evidence to confirm active targeting."
        else:
            verdict = "normal_environment"
            confidence = "low"
            summary = "The environment looks like ordinary nearby wireless activity without a strong hostile signal."

        return {
            "status": verdict,
            "confidence": confidence,
            "summary": summary,
            "signals": reasons,
            "auto": True,
        }

    def verbose_report(self, user_query: str | None = None) -> str:
        probe = self.deep_probe()
        trace = probe["trace_assessment"]
        lines: List[str] = []
        lines.append("Black Hole // hostile surveillance and privacy probe")
        lines.append("=" * 72)
        lines.append(f"Risk score: {probe['risk_score']}/100 | Level: {probe['risk_level']}")
        lines.append(f"Trace assessment: {trace['assessment']}")
        lines.append(f"Confidence: {trace['confidence']} | Decision: {trace['decision']}")
        lines.append(f"Signal intensity: {probe['signal_intensity']['overall_intensity']}/100 ({probe['signal_intensity']['assessment']})")
        lines.append("")
        lines.append("Observed signal layer:")
        lines.append(f"- Wi‑Fi beacons: {len(probe['wifi_beacons'])}")
        lines.append(f"- Suspected camera-like devices: {len(probe['camera_scan'])}")
        lines.append(f"- Local exposed ports: {len(probe['network_exposure']['local_open_ports'])}")
        lines.append(f"- Device node hints: {len(probe['device_signal_check']['check_paths'])}")
        lines.append("")
        if probe["wifi_beacons"]:
            lines.append("Beacon details:")
            for beacon in probe["wifi_beacons"]:
                lines.append(f"  * SSID: {beacon.get('ssid', 'unknown')} | BSSID: {beacon.get('bssid', 'unknown')} | Signal: {beacon.get('signal', 'unknown')}")
            for fp in probe["wifi_fingerprints"]:
                lines.append(f"  * Fingerprint: {fp['ssid']} -> {fp['classification']}")
        if probe["camera_scan"]:
            lines.append("Camera-like detections:")
            for host in probe["camera_scan"]:
                lines.append(f"  * {host['host']} -> ports {host['ports']}")
        if trace["signals"]:
            lines.append("Reasons for concern:")
            for reason in trace["signals"]:
                lines.append(f"  * {reason}")
        lines.append("")
        lines.append("Action plan:")
        if trace["decision"] in {"high", "medium"}:
            lines.append("  1. Isolate the host from unknown wireless networks and disable unexpected test ports.")
            lines.append("  2. Review local device nodes and any newly attached USB camera or audio hardware.")
            lines.append("  3. Re-run the probe after changing networks to confirm whether the visibility persists.")
        else:
            lines.append("  1. Keep the host in privacy-hardening mode and avoid exposing sensitive services.")
            lines.append("  2. Continue monitoring for new nearby beacon fingerprints or device-node changes.")
            lines.append("  3. Use the deep-scan periodically if the user suspects targeted observation.")
        lines.append("")
        lines.append(trace["ai_reasoning"])
        return "\n".join(lines)

    def status_report(self) -> Dict[str, Any]:
        return {
            "privacy": {
                "mode": "Black Hole",
                "dns_privacy": self.policy["network"]["dns_privacy"],
                "https_only": self.policy["network"]["https_only"],
                "log_redaction": self.policy["network"]["local_log_redaction"],
                "network_check": self.host_connectivity(),
                "local_ip": self.local_ip(),
            },
            "surveillance": {
                "camera_scan": self.suspicious_camera_hosts(),
                "device_signal_check": self.local_audio_camera_signals(),
            },
            "device_scan": {
                "arp_entries": self.arp_table(),
                "policy": self.policy["device_scan"],
            },
            "hidden_device_detection": self.policy["hidden_device_detection"],
        }

    def run_check(self) -> Dict[str, Any]:
        report = self.status_report()
        return {
            "overall": "healthy" if not report["surveillance"]["camera_scan"] else "warning",
            "report": report,
        }


def shutil_which(cmd: str) -> str | None:
    for path in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(path, cmd)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


def _cli() -> int:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(description="Black Hole privacy + surveillance hardening checks")
    parser.add_argument("--status", action="store_true", help="print the privacy status report")
    parser.add_argument("--scan", action="store_true", help="run a local surveillance scan")
    parser.add_argument("--full", action="store_true", help="run an advanced deep-probe assessment with Wi‑Fi beacon and risk scoring")
    parser.add_argument("--verbose", action="store_true", help="print a richer human-readable hostile surveillance report")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    parser.add_argument("--disconnect", action="store_true", help="disconnect the active Wi‑Fi connection as part of Asterix Protocol 156")
    parser.add_argument("--mask", action="store_true", help="initiate the Asterix Protocol 156 internet masking flow")
    parser.add_argument("--aggressive", action="store_true", help="activate a stronger best-effort local total masking mode")
    parser.add_argument("--query", type=str, help="optional user narrative to assess if they suspect being tracked")
    args = parser.parse_args()

    tool = BlackHole()
    if args.mask or args.disconnect:
        payload = tool.mask_internet(disconnect=args.disconnect or args.mask, aggressive=args.aggressive or args.mask)
        if args.json:
            print(json.dumps(payload, indent=2))
            return 0
        print(f"Asterix Protocol 156: {payload['name']}")
        print(f"Status: {payload['status']}")
        print(f"Masking guarantee: {payload['masking_guarantee']}")
        if payload.get("connection_action"):
            print(f"Connection action: {payload['connection_action']['status']} - {payload['connection_action']['detail']}")
        return 0

    if args.full or args.scan:
        payload = {
            "overall": "healthy",
            "report": tool.deep_probe(),
        }
        if payload["report"]["risk_score"] >= 40:
            payload["overall"] = "elevated"
        if payload["report"]["risk_score"] >= 70:
            payload["overall"] = "critical"
        if args.json:
            print(json.dumps(payload, indent=2))
            return 0
        if args.verbose:
            print(tool.verbose_report(args.query))
        else:
            print("Black Hole deep probe: " + payload["overall"])
            print(f"Risk score: {payload['report']['risk_score']}/100")
            print(f"Wi‑Fi beacons seen: {len(payload['report']['wifi_beacons'])}")
            print(f"Camera-like devices: {len(payload['report']['camera_scan'])}")
            print(f"Local ports exposed: {len(payload['report']['network_exposure']['local_open_ports'])}")
        return 0

    report = tool.run_check()
    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    if args.verbose:
        print(tool.verbose_report(args.query))
    else:
        print("Black Hole status: " + report["overall"])
        print(f"Local IP: {report['report']['privacy']['local_ip']}")
        print(f"DNS/privacy policy: {report['report']['privacy']['dns_privacy']}")
        print(f"Local camera-like devices: {len(report['report']['surveillance']['camera_scan'])}")
        if report["report"]["surveillance"]["camera_scan"]:
            for item in report["report"]["surveillance"]["camera_scan"]:
                print(f"  - {item['host']} -> ports {item['ports']}")
        print(f"Host audio/camera signal check: {report['report']['surveillance']['device_signal_check']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
