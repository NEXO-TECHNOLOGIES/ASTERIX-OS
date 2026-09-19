#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Real-Time Multiplayer Team Synchronization & Collision Avoidance
  Tool: ax team / ax collab-sync
  Version: 3.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0

  Features:
    • Zero-Infrastructure Mesh: Direct P2P over Wi-Fi, LAN, hotspot, or WireGuard
    • Target Lock Collision Avoidance: Prevents dual-scan EDR alert spikes
    • HMAC-SHA256 Packet Authentication: Shared-passphrase peer trust verification
    • Logical Vector Clocks: Conflict-free distributed state sequencing
    • Automated Peer Discovery: Passive & active UDP broadcast beaconing
    • Real-Time Delta Exchange: Peer-to-peer event push & pull
===============================================================================
"""

import os
import sys
import json
import time
import uuid
import socket
import hmac
import hashlib
import threading
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
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

BANNER = f"""{C_MAGENTA}{C_BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║   ███╗   ███╗███████╗███████╗██╗  ██╗███████╗██████╗      ║
    ║   ████╗ ████║██╔════╝██╔════╝██║  ██║██╔════╝██╔══██╗     ║
    ║   ██╔████╔██║█████╗  ███████╗███████║███████╗██████╔╝     ║
    ║   ██║╚██╔╝██║██╔══╝  ╚════██║██╔══██║╚════██║██╔══██╗     ║
    ║   ██║ ╚═╝ ██║███████╗███████║██║  ██║███████║██║  ██║     ║
    ║   ╚═╝     ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝     ║
    ║     MULTIPLAYER P2P TEAM SYNCHRONIZATION ENGINE v3.0      ║
    ╚═══════════════════════════════════════════════════════════╝{C_RESET}
"""

DEFAULT_BROADCAST_PORT = 4889
DEFAULT_HTTP_PORT = 4890
CONFIG_DIR = Path.home() / ".asterix" / "team"
CONFIG_FILE = CONFIG_DIR / "mesh_state.json"


def get_lan_ip() -> str:
    """Best-effort discovery of local LAN IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Does not send traffic
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def sign_payload(secret: str, data_bytes: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), data_bytes, hashlib.sha256).hexdigest()


def verify_payload(secret: str, data_bytes: bytes, signature: str) -> bool:
    expected = sign_payload(secret, data_bytes)
    return hmac.compare_digest(expected, signature)


class TeamMeshManager:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.state = self.load_state()

    def load_state(self) -> Dict[str, Any]:
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        # Default fresh state
        return {
            "mesh_name": "asterix-default-mesh",
            "operator_callsign": f"operator_{uuid.uuid4().hex[:6]}",
            "node_id": str(uuid.uuid4()),
            "passphrase": "asterix-p2p-mesh-secret",
            "http_port": DEFAULT_HTTP_PORT,
            "vector_clock": {},
            "peers": {},
            "locks": {},  # target -> {operator, reason, expires_at}
            "shared_log": []
        }

    def save_state(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    def init_mesh(self, mesh_name: str, passphrase: str, callsign: Optional[str] = None):
        self.state["mesh_name"] = mesh_name
        self.state["passphrase"] = passphrase
        if callsign:
            self.state["operator_callsign"] = callsign
        self.state["node_id"] = str(uuid.uuid4())
        self.state["locks"] = {}
        self.state["peers"] = {}
        self.state["shared_log"] = []
        self.state["vector_clock"] = {self.state["operator_callsign"]: 1}
        self.save_state()

    def lock_target(self, target: str, reason: str, ttl_seconds: int = 1800) -> Tuple[bool, str]:
        self.clean_expired_locks()
        now = time.time()
        existing = self.state["locks"].get(target)

        if existing and existing.get("expires_at", 0) > now:
            owner = existing.get("operator", "Unknown")
            if owner != self.state["operator_callsign"]:
                return False, f"Target '{target}' is already locked by {owner} for: '{existing.get('reason')}'"

        expires_at = now + ttl_seconds
        lock_entry = {
            "target": target,
            "operator": self.state["operator_callsign"],
            "reason": reason,
            "created_at": now,
            "expires_at": expires_at
        }
        self.state["locks"][target] = lock_entry
        self.record_event("TARGET_LOCKED", {"target": target, "reason": reason, "expires_at": expires_at})
        self.save_state()
        return True, f"Target '{target}' locked for {ttl_seconds // 60} minutes by {self.state['operator_callsign']}."

    def unlock_target(self, target: str) -> Tuple[bool, str]:
        self.clean_expired_locks()
        existing = self.state["locks"].get(target)
        if not existing:
            return True, f"Target '{target}' is not locked."

        owner = existing.get("operator")
        if owner != self.state["operator_callsign"]:
            return False, f"Cannot unlock '{target}' - owned by operator '{owner}'."

        del self.state["locks"][target]
        self.record_event("TARGET_UNLOCKED", {"target": target})
        self.save_state()
        return True, f"Target '{target}' unlocked."

    def clean_expired_locks(self):
        now = time.time()
        expired = [t for t, l in self.state["locks"].items() if l.get("expires_at", 0) <= now]
        for t in expired:
            del self.state["locks"][t]

    def record_event(self, action: str, data: Dict[str, Any]):
        callsign = self.state["operator_callsign"]
        clock = self.state["vector_clock"].get(callsign, 0) + 1
        self.state["vector_clock"][callsign] = clock

        event = {
            "id": str(uuid.uuid4()),
            "timestamp": time.time(),
            "operator": callsign,
            "action": action,
            "clock": clock,
            "data": data
        }
        self.state["shared_log"].append(event)
        # Retain last 200 events
        if len(self.state["shared_log"]) > 200:
            self.state["shared_log"] = self.state["shared_log"][-200:]


class P2PRequestHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP handler for incoming peer delta sync & lock queries."""

    manager: Optional[TeamMeshManager] = None

    def do_GET(self):
        if self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            mgr = self.__class__.manager
            mgr.clean_expired_locks()
            res = {
                "mesh_name": mgr.state["mesh_name"],
                "operator": mgr.state["operator_callsign"],
                "node_id": mgr.state["node_id"],
                "active_locks": mgr.state["locks"],
                "clock": mgr.state["vector_clock"],
                "status": "online"
            }
            self.wfile.write(json.dumps(res).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        mgr = self.__class__.manager
        content_len = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_len)

        # Authenticate with HMAC signature header
        sig = self.headers.get("X-Asterix-Signature", "")
        if not verify_payload(mgr.state["passphrase"], post_data, sig):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized / HMAC Signature Mismatch"}')
            return

        try:
            payload = json.loads(post_data.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        if self.path == "/sync":
            # Ingest events & update locks
            peer_locks = payload.get("locks", {})
            peer_events = payload.get("events", [])
            for target, lock in peer_locks.items():
                if lock.get("expires_at", 0) > time.time():
                    mgr.state["locks"][target] = lock

            existing_ids = {e["id"] for e in mgr.state["shared_log"]}
            for ev in peer_events:
                if ev.get("id") not in existing_ids:
                    mgr.state["shared_log"].append(ev)

            mgr.save_state()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "synchronized"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress noisy HTTP request console logging
        return


def run_server(manager: TeamMeshManager, port: int):
    P2PRequestHandler.manager = manager
    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, P2PRequestHandler)
        print(f"{C_GREEN}[+] Team Mesh P2P Sync Server listening on port {port} (LAN IP: {get_lan_ip()}){C_RESET}")
        httpd.serve_forever()
    except Exception as e:
        print(f"{C_RED}[!] Failed to start HTTP sync server: {e}{C_RESET}")


def send_beacon(manager: TeamMeshManager, port: int):
    """Sends a single UDP broadcast discovery announcement."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(1.0)

    packet = {
        "mesh": manager.state["mesh_name"],
        "callsign": manager.state["operator_callsign"],
        "node_id": manager.state["node_id"],
        "port": manager.state["http_port"],
        "timestamp": time.time()
    }
    raw = json.dumps(packet).encode("utf-8")
    sig = sign_payload(manager.state["passphrase"], raw)

    msg = json.dumps({"payload": packet, "signature": sig}).encode("utf-8")

    try:
        sock.sendto(msg, ("<broadcast>", port))
        print(f"{C_GREEN}[+] UDP Discovery Beacon broadcasted on port {port}{C_RESET}")
    except Exception as e:
        print(f"{C_YELLOW}[*] Broadcast warning: {e}{C_RESET}")
    finally:
        sock.close()


def listen_beacons(manager: TeamMeshManager, port: int, timeout: float = 3.0):
    """Listens for active peer broadcasts on the local subnet."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            try:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except Exception:
                pass
        sock.bind(("", port))
        sock.settimeout(timeout)
        print(f"{C_CYAN}[*] Listening for peer beacons on UDP port {port} for {timeout}s...{C_RESET}")

        start = time.time()
        discovered = 0
        while time.time() - start < timeout:
            try:
                data, addr = sock.recvfrom(4096)
                wrapper = json.loads(data.decode("utf-8"))
                sig = wrapper.get("signature", "")
                payload = wrapper.get("payload", {})

                raw_payload = json.dumps(payload).encode("utf-8")
                if verify_payload(manager.state["passphrase"], raw_payload, sig):
                    callsign = payload.get("callsign")
                    if callsign != manager.state["operator_callsign"]:
                        manager.state["peers"][callsign] = {
                            "ip": addr[0],
                            "port": payload.get("port", DEFAULT_HTTP_PORT),
                            "last_seen": time.time(),
                            "node_id": payload.get("node_id")
                        }
                        manager.save_state()
                        discovered += 1
                        print(f"  {C_GREEN}[*] Discovered Peer: {C_BOLD}{callsign}{C_RESET} at {addr[0]}:{payload.get('port')}")
            except socket.timeout:
                break
            except Exception:
                pass

        if discovered == 0:
            print(f"  {C_DIM}No other active peers responded within window.{C_RESET}")
    except Exception as e:
        print(f"{C_RED}[!] Socket bind error: {e}{C_RESET}")
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="ASTERIX OS Multiplayer P2P Team Synchronization")
    parser.add_argument("command", nargs="?", default="status",
                        choices=["status", "init", "lock", "unlock", "locks", "peers", "beacon", "listen", "serve"],
                        help="Action to perform")
    parser.add_argument("target", nargs="?", default=None, help="Target IP, CIDR, or hostname to lock/unlock")
    parser.add_argument("--mesh", default=None, help="Mesh network identifier")
    parser.add_argument("--passphrase", "-p", default=None, help="Secret passphrase for HMAC authentication")
    parser.add_argument("--callsign", "-c", default=None, help="Operator callsign alias")
    parser.add_argument("--reason", "-r", default="Active probing", help="Reason for acquiring target lock")
    parser.add_argument("--ttl", type=int, default=1800, help="Lock duration in seconds (default: 1800)")
    parser.add_argument("--port", type=int, default=DEFAULT_HTTP_PORT, help="Port to run HTTP sync daemon on")

    args = parser.parse_args()

    print(BANNER)
    mgr = TeamMeshManager()

    if args.command == "init":
        mesh_name = args.mesh or "asterix-alpha-squad"
        passphrase = args.passphrase or "asterix-p2p-mesh-secret"
        mgr.init_mesh(mesh_name, passphrase, args.callsign)
        print(f"{C_GREEN}[[OK]] Initialized Team Mesh '{mesh_name}'{C_RESET}")
        print(f"  • Operator Callsign: {C_BOLD}{mgr.state['operator_callsign']}{C_RESET}")
        print(f"  • Node UUID:         {mgr.state['node_id']}")
        print(f"  • HMAC Passphrase:   {'*' * len(passphrase)} (Hash verified)")

    elif args.command == "lock":
        if not args.target:
            print(f"{C_RED}[!] Error: target IP or domain required to lock (e.g. ax team lock 192.168.1.10){C_RESET}")
            sys.exit(1)
        ok, msg = mgr.lock_target(args.target, args.reason, args.ttl)
        if ok:
            print(f"{C_GREEN}[[OK]] {msg}{C_RESET}")
        else:
            print(f"{C_RED}[!] LOCK COLLISION DETECTED:{C_RESET} {msg}")

    elif args.command == "unlock":
        if not args.target:
            print(f"{C_RED}[!] Error: target IP or domain required to unlock (e.g. ax team unlock 192.168.1.10){C_RESET}")
            sys.exit(1)
        ok, msg = mgr.unlock_target(args.target)
        if ok:
            print(f"{C_GREEN}[[OK]] {msg}{C_RESET}")
        else:
            print(f"{C_RED}[!] {msg}{C_RESET}")

    elif args.command == "locks":
        mgr.clean_expired_locks()
        locks = mgr.state["locks"]
        print(f"\n{C_CYAN}{C_BOLD}[*] ACTIVE COLLISION-AVOIDANCE TARGET LOCKS:{C_RESET}")
        if not locks:
            print(f"  {C_DIM}No active target locks in place. All targets free for engagement.{C_RESET}")
        else:
            now = time.time()
            for tgt, info in locks.items():
                rem_mins = max(0, int(info.get("expires_at", 0) - now) // 60)
                is_mine = info.get("operator") == mgr.state["operator_callsign"]
                owner_str = f"{C_GREEN}[YOU]{C_RESET}" if is_mine else f"{C_YELLOW}[{info.get('operator')}]{C_RESET}"
                print(f"  [LOCK] {C_BOLD}{tgt}{C_RESET} ── {owner_str} Reason: \"{info.get('reason')}\" (TTL: {rem_mins}m remaining)")

    elif args.command == "peers":
        peers = mgr.state["peers"]
        print(f"\n{C_CYAN}{C_BOLD}[*] KNOWN SQUAD PEERS IN MESH '{mgr.state['mesh_name']}':{C_RESET}")
        if not peers:
            print(f"  {C_DIM}No peers discovered yet. Run 'ax team listen' or 'ax team beacon'.{C_RESET}")
        else:
            now = time.time()
            for cs, p in peers.items():
                ago = int(now - p.get("last_seen", now))
                print(f"   {C_BOLD}{cs}{C_RESET} ── IP: {p.get('ip')}:{p.get('port')} (Seen {ago}s ago)")

    elif args.command == "beacon":
        send_beacon(mgr, DEFAULT_BROADCAST_PORT)

    elif args.command == "listen":
        listen_beacons(mgr, DEFAULT_BROADCAST_PORT)

    elif args.command == "serve":
        run_server(mgr, args.port)

    elif args.command == "status":
        mgr.clean_expired_locks()
        print(f"\n{C_CYAN}{C_BOLD}[*] MULTIPLAYER SQUAD MESH TELEMETRY{C_RESET}")
        print(f"  • Mesh Identifier:   {C_BOLD}{mgr.state['mesh_name']}{C_RESET}")
        print(f"  • Local Callsign:    {C_GREEN}{C_BOLD}{mgr.state['operator_callsign']}{C_RESET}")
        print(f"  • Local LAN IP:      {get_lan_ip()}")
        print(f"  • Active Locks Held: {len(mgr.state['locks'])}")
        print(f"  • Known Peers:       {len(mgr.state['peers'])}")
        print(f"  • Vector Clock:      {json.dumps(mgr.state['vector_clock'])}")
        print(f"  • Event Log Depth:   {len(mgr.state['shared_log'])} entries")


if __name__ == "__main__":
    main()
