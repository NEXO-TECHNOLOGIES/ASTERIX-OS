#!/usr/bin/env python3
"""
ASTERIX OS - Secure Localhost Chatting Vault v2.0
Zero-Knowledge, End-to-End Encrypted (E2EE), Ephemeral In-Memory Chat Vault.
Supports Direct 1-on-1 and Multi-User Group Chats with Admin Controls.
Built-In 3-Strike Intrusion Detection System (IDS) & OS Counter-Attack Alerting.

Zero external dependencies (pure Python 3 standard library).
"""

import sys
import os
import json
import time
import secrets
import hashlib
import threading
import queue
import socket
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse

# Colors
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE   = "\033[38;5;231m"
C_GRAY    = "\033[38;5;244m"

DEFAULT_PORT = 8765
DEFAULT_HOST = "127.0.0.1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR  = os.path.join(BASE_DIR, "web")

ROOMS = {}
ROOMS_LOCK = threading.Lock()

FAILED_LOGINS = {}
FAILED_LOCK = threading.Lock()

RATE_LIMITS = {}
RATE_LOCK = threading.Lock()

def check_rate_limit(ip, max_requests=120, window=60.0):
    now = time.time()
    with RATE_LOCK:
        history = RATE_LIMITS.setdefault(ip, [])
        history = [t for t in history if now - t < window]
        if len(history) >= max_requests:
            return False
        history.append(now)
        RATE_LIMITS[ip] = history
        return True

def hash_password(password, salt_hex):
    salt_bytes = bytes.fromhex(salt_hex)
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 100000).hex()

def trigger_intruder_alert(ip, port, room_id, attempt_count):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"\n{C_RED}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_RED}║{C_WHITE}{C_BOLD}  🚨 [ALERT] ASTERIX CAUGHT A THIEF SNOOPING INTO THE PRIVATE CHAT!       {C_RESET}{C_RED}║{C_RESET}")
    print(f"{C_RED}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}TARGET INTRUDER IP :{C_RESET} {C_RED}{C_BOLD}{ip}{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}INTRUDER PORT      :{C_RESET} {C_WHITE}{port}{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}TARGETED VAULT ROOM:{C_RESET} {C_CYAN}{room_id}{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}FAILED ATTEMPTS    :{C_RESET} {C_RED}{attempt_count} consecutive unauthorized attempts{C_RESET}")
    print(f"  {C_YELLOW}{C_BOLD}DETECTION TIMESTAMP:{C_RESET} {C_GRAY}{ts}{C_RESET}\n")
    print(f"  {C_WHITE}{C_BOLD}ELIMINATE THE TARGET USING PREINSTALLED ASTERIX OS TOOLS:{C_RESET}")
    print(f"    {C_CYAN}• ax nmap -sV -O {ip}{C_RESET}           {C_GRAY}Audit attacker operating system & open attack surfaces{C_RESET}")
    print(f"    {C_CYAN}• ax killswitch{C_RESET}                     {C_GRAY}Instant host isolation / sever network connections{C_RESET}")
    print(f"    {C_CYAN}• ax decoy {port}{C_RESET}                       {C_GRAY}Deploy honeypot listener to trap & log further probes{C_RESET}")
    print(f"    {C_CYAN}• ax traceroute {ip}{C_RESET}                {C_GRAY}Map adversary hops, ISP origin & geolocation{C_RESET}")
    print(f"    {C_CYAN}• ax stealth{C_RESET}                        {C_GRAY}Engage ghost mode: wipe session caches & RAM traces{C_RESET}")
    print(f"{C_RED}──────────────────────────────────────────────────────────────────────────{C_RESET}\n")

    with ROOMS_LOCK:
        for r_id, room in ROOMS.items():
            for c_id, client in room["clients"].items():
                try:
                    client["queue"].put_nowait({
                        "type": "intrusion_alert",
                        "attacker_ip": ip,
                        "attacker_port": port,
                        "target_room": room_id,
                        "attempts": attempt_count,
                        "timestamp": time.time()
                    })
                except Exception:
                    pass

def log_event(category, detail, level="INFO"):
    ts = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
    color = C_GREEN if level == "INFO" else (C_YELLOW if level == "WARN" else C_RED)
    print(f"  {C_GRAY}[{ts}]{C_RESET} {color}[{category}]{C_RESET} {detail}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class SecureChatHandler(BaseHTTPRequestHandler):
    server_version = "AsterixSecureVault/2.0"
    sys_version    = ""

    def log_message(self, format, *args):
        pass

    def send_security_headers(self, content_type="text/html; charset=utf-8"):
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; "
                         "script-src 'self' 'unsafe-inline'; "
                         "style-src 'self' 'unsafe-inline'; "
                         "connect-src 'self' http: https: ws: wss:; "
                         "img-src 'self' data:; "
                         "object-src 'none'; "
                         "frame-ancestors 'none'; "
                         "base-uri 'self'; "
                         "form-action 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-XSS-Protection", "1; mode=block")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, private, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")

    def read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0 or content_length > 65536:
                return None
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        except Exception:
            return None

    def send_json_response(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_security_headers("application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip):
            self.send_response(429)
            self.end_headers()
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/stream":
            self.handle_sse_stream(query)
            return

        if path == "/api/status":
            with ROOMS_LOCK:
                active_rooms = len(ROOMS)
                total_clients = sum(len(r["clients"]) for r in ROOMS.values())
            self.send_json_response({
                "status": "online",
                "active_rooms": active_rooms,
                "connected_operatives": total_clients,
                "e2ee_engine": "AES-256-GCM + PBKDF2-SHA256 (100k iters)",
                "modes_supported": ["direct (1-on-1)", "group (multi-user)"],
                "ids_engine": "3-Strike Intrusion Defense System Active"
            })
            return

        if path == "/api/admin/members":
            room_id = query.get("room", [""])[0]
            admin_token = query.get("admin_token", [""])[0]
            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if not room or room["admin_token"] != admin_token:
                    self.send_json_response({"error": "Unauthorized admin access"}, 403)
                    return
                members = []
                for c_id, client in room["clients"].items():
                    members.append({
                        "client_id": c_id,
                        "name": client["name"],
                        "is_admin": client["is_admin"],
                        "ip": client["ip"],
                        "port": client["port"],
                        "muted": client["muted"],
                        "joined_at": client["joined_at"]
                    })
            self.send_json_response({"members": members, "room": room_id})
            return

        if path == "/" or path == "/index.html":
            file_path = os.path.join(WEB_DIR, "index.html")
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_security_headers("text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_response(404)
        self.end_headers()

    def handle_sse_stream(self, query):
        room_id = query.get("room", [""])[0]
        client_id = query.get("client_id", [""])[0]

        if not room_id or not client_id:
            self.send_response(400)
            self.end_headers()
            return

        with ROOMS_LOCK:
            room = ROOMS.get(room_id)
            if not room or client_id not in room["clients"]:
                self.send_response(403)
                self.end_headers()
                return
            client_queue = room["clients"][client_id]["queue"]

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache, no-transform")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()

        try:
            self.wfile.write(b": ping\n\n")
            self.wfile.flush()
        except Exception:
            return

        last_ping = time.time()
        while True:
            try:
                try:
                    event_data = client_queue.get(timeout=1.0)
                    msg_str = json.dumps(event_data)
                    payload = f"data: {msg_str}\n\n".encode("utf-8")
                    self.wfile.write(payload)
                    self.wfile.flush()
                except queue.Empty:
                    pass

                if time.time() - last_ping > 15.0:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    last_ping = time.time()

                    with ROOMS_LOCK:
                        if room_id in ROOMS and client_id in ROOMS[room_id]["clients"]:
                            ROOMS[room_id]["clients"][client_id]["last_seen"] = time.time()
                        else:
                            break

            except (BrokenPipeError, ConnectionResetError):
                break
            except Exception:
                break

        with ROOMS_LOCK:
            if room_id in ROOMS and client_id in ROOMS[room_id]["clients"]:
                c_name = ROOMS[room_id]["clients"][client_id]["name"]
                del ROOMS[room_id]["clients"][client_id]
                log_event("DISCONNECT", f"Operative '{c_name}' left room '{room_id}'", "WARN")
                for other_id, other_client in ROOMS[room_id]["clients"].items():
                    other_client["queue"].put({
                        "type": "peer_left",
                        "client_id": client_id,
                        "name": c_name,
                        "peers_count": len(ROOMS[room_id]["clients"]),
                        "timestamp": time.time()
                    })

    def do_POST(self):
        client_ip = self.client_address[0]
        client_port = self.client_address[1]

        if not check_rate_limit(client_ip):
            self.send_response(429)
            self.end_headers()
            return

        data = self.read_json_body()
        if data is None:
            self.send_json_response({"error": "Invalid payload"}, 400)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # ── 1. Create Room ──────────────────────────────────────────────────
        if path == "/api/room/create":
            room_id = data.get("room", "").strip() or f"vault-{secrets.token_hex(4)}"
            password = data.get("password", "")
            mode = data.get("mode", "group").lower()
            creator_name = data.get("name", "Commander").strip()[:32]

            if not password:
                self.send_json_response({"error": "A custom password is required to create a vault room"}, 400)
                return

            if mode not in ("direct", "group"):
                mode = "group"

            with ROOMS_LOCK:
                if room_id in ROOMS:
                    self.send_json_response({"error": f"Room '{room_id}' already exists. Choose a unique name or join it."}, 409)
                    return

                salt = secrets.token_hex(32)
                pwd_hash = hash_password(password, salt)
                admin_token = secrets.token_hex(24)
                client_id = secrets.token_hex(16)

                ROOMS[room_id] = {
                    "mode": mode,
                    "salt": salt,
                    "password_hash": pwd_hash,
                    "admin_token": admin_token,
                    "created_at": time.time(),
                    "clients": {
                        client_id: {
                            "name": creator_name,
                            "is_admin": True,
                            "ip": client_ip,
                            "port": client_port,
                            "muted": False,
                            "joined_at": time.time(),
                            "last_seen": time.time(),
                            "queue": queue.Queue(maxsize=100)
                        }
                    },
                    "history": [],
                    "lock": threading.Lock()
                }

            log_event("ROOM_CREATE", f"Vault '{room_id}' created [Mode: {mode.upper()}] by '{creator_name}' (Admin)", "INFO")
            self.send_json_response({
                "status": "created",
                "room": room_id,
                "mode": mode,
                "client_id": client_id,
                "admin_token": admin_token,
                "salt": salt,
                "is_admin": True,
                "peers_count": 1
            })
            return

        # ── 2. Join Room (with 3-Strike IDS) ─────────────────────────────────
        if path == "/api/room/join":
            room_id  = data.get("room", "").strip()
            password = data.get("password", "")
            name     = data.get("name", "Operative").strip()[:32]
            admin_token = data.get("admin_token", "")

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)

            if not room:
                self.send_json_response({"error": f"Room '{room_id}' does not exist. Please create it first."}, 404)
                return

            expected_hash = room["password_hash"]
            provided_hash = hash_password(password, room["salt"])

            if not secrets.compare_digest(expected_hash, provided_hash):
                with FAILED_LOCK:
                    entry = FAILED_LOGINS.setdefault(client_ip, {"count": 0, "last_port": client_port, "last_attempt": 0})
                    entry["count"] += 1
                    entry["last_port"] = client_port
                    entry["last_attempt"] = time.time()
                    fail_count = entry["count"]

                log_event("AUTH_FAIL", f"Failed attempt #{fail_count} from {client_ip}:{client_port} on '{room_id}'", "WARN")

                if fail_count >= 3:
                    trigger_intruder_alert(client_ip, client_port, room_id, fail_count)
                    self.send_json_response({
                        "error": f"🚨 INTRUSION ALERT: 3 consecutive password failures! Target {client_ip}:{client_port} logged to OS defense systems.",
                        "intruder_detected": True,
                        "attacker_ip": client_ip,
                        "attacker_port": client_port
                    }, 403)
                    return
                else:
                    remaining = 3 - fail_count
                    self.send_json_response({
                        "error": f"Invalid vault password. {remaining} attempt(s) remaining before security lockdown.",
                        "attempts_failed": fail_count
                    }, 401)
                    return

            with FAILED_LOCK:
                if client_ip in FAILED_LOGINS:
                    del FAILED_LOGINS[client_ip]

            with ROOMS_LOCK:
                if room["mode"] == "direct" and len(room["clients"]) >= 2:
                    self.send_json_response({"error": "Direct room is at maximum 2-party capacity."}, 403)
                    return

                client_id = secrets.token_hex(16)
                is_admin = bool(admin_token and secrets.compare_digest(room["admin_token"], admin_token))

                room["clients"][client_id] = {
                    "name": name,
                    "is_admin": is_admin,
                    "ip": client_ip,
                    "port": client_port,
                    "muted": False,
                    "joined_at": time.time(),
                    "last_seen": time.time(),
                    "queue": queue.Queue(maxsize=100)
                }

                for other_id, other_client in room["clients"].items():
                    if other_id != client_id:
                        other_client["queue"].put({
                            "type": "peer_joined",
                            "client_id": client_id,
                            "name": name,
                            "is_admin": is_admin,
                            "peers_count": len(room["clients"]),
                            "timestamp": time.time()
                        })

                peers_count = len(room["clients"])
                salt_val = room["salt"]
                room_mode = room["mode"]

            log_event("PEER_JOIN", f"'{name}' authenticated into '{room_id}' ({peers_count} operatives in room)", "INFO")
            self.send_json_response({
                "status": "joined",
                "client_id": client_id,
                "room": room_id,
                "mode": room_mode,
                "salt": salt_val,
                "is_admin": is_admin,
                "peers_count": peers_count
            })
            return

        # ── 3. Send Message ──────────────────────────────────────────────────
        if path == "/api/send":
            room_id    = data.get("room")
            client_id  = data.get("client_id")
            iv         = data.get("iv")
            ciphertext = data.get("ciphertext")
            tag        = data.get("tag", "")
            burn_secs  = int(data.get("burn_secs", 0))
            msg_id     = data.get("msg_id", secrets.token_hex(12))

            if not all([room_id, client_id, iv, ciphertext]):
                self.send_json_response({"error": "Malformed envelope"}, 400)
                return

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if not room or client_id not in room["clients"]:
                    self.send_json_response({"error": "Unauthorized session"}, 403)
                    return

                sender = room["clients"][client_id]
                if sender.get("muted"):
                    self.send_json_response({"error": "You are muted by the vault administrator"}, 403)
                    return

                envelope = {
                    "type": "message",
                    "msg_id": msg_id,
                    "sender_id": client_id,
                    "sender_name": sender["name"],
                    "is_admin": sender["is_admin"],
                    "iv": iv,
                    "ciphertext": ciphertext,
                    "tag": tag,
                    "burn_secs": burn_secs,
                    "timestamp": time.time()
                }

                delivered = 0
                for other_id, other_client in room["clients"].items():
                    if other_id != client_id:
                        try:
                            other_client["queue"].put_nowait(envelope)
                            delivered += 1
                        except queue.Full:
                            pass

            self.send_json_response({"status": "delivered", "msg_id": msg_id, "recipients": delivered})
            return

        # ── 4. Admin Action: Kick ─────────────────────────────────────────────
        if path == "/api/admin/kick":
            room_id = data.get("room")
            admin_token = data.get("admin_token")
            target_id = data.get("target_client_id")

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if not room or not secrets.compare_digest(room["admin_token"], admin_token or ""):
                    self.send_json_response({"error": "Unauthorized: Admin privileges required"}, 403)
                    return

                if target_id in room["clients"]:
                    target_name = room["clients"][target_id]["name"]
                    try:
                        room["clients"][target_id]["queue"].put_nowait({
                            "type": "kicked",
                            "reason": "Removed by vault administrator"
                        })
                    except Exception:
                        pass
                    del room["clients"][target_id]
                    log_event("ADMIN_KICK", f"Admin kicked '{target_name}' from '{room_id}'", "WARN")

                    for other_id, other_client in room["clients"].items():
                        other_client["queue"].put({
                            "type": "peer_kicked",
                            "name": target_name,
                            "peers_count": len(room["clients"]),
                            "timestamp": time.time()
                        })

            self.send_json_response({"status": "kicked", "target_id": target_id})
            return

        # ── 5. Admin Action: Mute / Unmute ────────────────────────────────────
        if path == "/api/admin/mute":
            room_id = data.get("room")
            admin_token = data.get("admin_token")
            target_id = data.get("target_client_id")
            mute_state = bool(data.get("muted", True))

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if not room or not secrets.compare_digest(room["admin_token"], admin_token or ""):
                    self.send_json_response({"error": "Unauthorized: Admin privileges required"}, 403)
                    return

                if target_id in room["clients"]:
                    room["clients"][target_id]["muted"] = mute_state
                    target_name = room["clients"][target_id]["name"]
                    try:
                        room["clients"][target_id]["queue"].put_nowait({
                            "type": "mute_state",
                            "muted": mute_state
                        })
                    except Exception:
                        pass
                    log_event("ADMIN_MUTE", f"Admin set muted={mute_state} for '{target_name}'", "INFO")

            self.send_json_response({"status": "updated", "muted": mute_state})
            return

        # ── 6. Admin Action: Purge Chat ───────────────────────────────────────
        if path == "/api/admin/purge":
            room_id = data.get("room")
            admin_token = data.get("admin_token")

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if not room or not secrets.compare_digest(room["admin_token"], admin_token or ""):
                    self.send_json_response({"error": "Unauthorized: Admin privileges required"}, 403)
                    return

                for c_id, client in room["clients"].items():
                    try:
                        client["queue"].put_nowait({"type": "purge", "timestamp": time.time()})
                    except Exception:
                        pass
                log_event("ADMIN_PURGE", f"Admin purged all chat messages in '{room_id}'", "WARN")

            self.send_json_response({"status": "purged"})
            return

        # ── 7. Burn Message ──────────────────────────────────────────────────
        if path == "/api/burn":
            room_id   = data.get("room")
            client_id = data.get("client_id")
            msg_id    = data.get("msg_id")

            with ROOMS_LOCK:
                room = ROOMS.get(room_id)
                if room and client_id in room["clients"]:
                    for other_id, other_client in room["clients"].items():
                        if other_id != client_id:
                            try:
                                other_client["queue"].put_nowait({"type": "burn", "msg_id": msg_id})
                            except queue.Full:
                                pass

            self.send_json_response({"status": "burned", "msg_id": msg_id})
            return

        # ── 8. Panic Killswitch ──────────────────────────────────────────────
        if path == "/api/panic":
            room_id   = data.get("room")
            client_id = data.get("client_id")

            with ROOMS_LOCK:
                if room_id in ROOMS:
                    room = ROOMS[room_id]
                    for c_id, client in room["clients"].items():
                        try:
                            client["queue"].put_nowait({"type": "panic", "timestamp": time.time()})
                        except Exception:
                            pass
                    del ROOMS[room_id]
                    log_event("PANIC_BURN", f"ROOM '{room_id}' PERMANENTLY NUKED FROM MEMORY", "CRIT")

            self.send_json_response({"status": "nuked"})
            return

        self.send_json_response({"error": "Endpoint not found"}, 404)

def banner(host, port, ssl_enabled):
    proto = "https" if ssl_enabled else "http"
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  [ ASTERIX SECURE CHAT // ZERO-KNOWLEDGE LOCALHOST VAULT v2.0 ]       {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")
    print(f"  {C_GREEN}{C_BOLD}● SECURE LOCAL VAULT ONLINE{C_RESET}  —  Direct & Group Encrypted Bridge")
    print(f"  {C_WHITE}Direct Web URL:{C_RESET}       {C_CYAN}{C_BOLD}{proto}://{host}:{port}{C_RESET}")
    print(f"  {C_WHITE}Encryption Core:{C_RESET}      {C_GREEN}AES-256-GCM + PBKDF2-SHA256 (Web Crypto API){C_RESET}")
    print(f"  {C_WHITE}Chat Architectures:{C_RESET}   {C_CYAN}Direct 1-on-1 (2 Peers) & Multi-User Group Vaults{C_RESET}")
    print(f"  {C_WHITE}Admin Controls:{C_RESET}       {C_YELLOW}Kick Members, Toggle Mute, Purge All Messages{C_RESET}")
    print(f"  {C_WHITE}Intrusion Defense:{C_RESET}    {C_RED}{C_BOLD}3-Strike IDS (Attacker IP/Port Log & Counter-Attack Alert){C_RESET}")
    print(f"  {C_WHITE}Anti-Forensics:{C_RESET}       {C_RED}100% In-Memory RAM, Burn Timers, 1-Click Panic Nuke{C_RESET}\n")
    print(f"  {C_GRAY}To invite others over LAN:          share http://<your-lan-ip>:{port}{C_RESET}")
    print(f"  {C_GRAY}To connect across internet/tunnel:  ssh -L {port}:localhost:{port} user@host{C_RESET}")
    print(f"  {C_GRAY}Press Ctrl+C to terminate vault and instantly erase all active rooms.{C_RESET}\n")
    print(f"{C_CYAN}──────────────────────────────────────────────────────────────────────────{C_RESET}\n")

def run_server(host=DEFAULT_HOST, port=DEFAULT_PORT, use_ssl=False, open_browser=False):
    server = ThreadedHTTPServer((host, port), SecureChatHandler)

    if use_ssl:
        cert_file = os.path.join(BASE_DIR, "cert.pem")
        key_file  = os.path.join(BASE_DIR, "key.pem")
        if not os.path.isfile(cert_file) or not os.path.isfile(key_file):
            print(f"  {C_YELLOW}[!] Generating ephemeral self-signed TLS certificate...{C_RESET}")
            os.system(f'openssl req -x509 -newkey rsa:2048 -keyout "{key_file}" -out "{cert_file}" -days 365 -nodes -subj "/CN=localhost" 2>/dev/null')
        if os.path.isfile(cert_file) and os.path.isfile(key_file):
            import ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
            server.socket = context.wrap_socket(server.socket, server_side=True)

    banner(host, port, use_ssl)

    if open_browser:
        proto = "https" if use_ssl else "http"
        url = f"{proto}://{host}:{port}"
        threading.Thread(target=lambda: (time.sleep(1.0), os.system(f'start {url}' if os.name == 'nt' else f'xdg-open {url} 2>/dev/null'))).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n  {C_RED}{C_BOLD}[!] TERMINATING SECURE CHAT VAULT...{C_RESET}")
        with ROOMS_LOCK:
            ROOMS.clear()
        print(f"  {C_GREEN}[✔] All RAM data, rooms, and keys permanently eradicated.{C_RESET}\n")
        server.server_close()

def main():
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    use_ssl = False
    open_browser = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ("--port", "-p") and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif arg in ("--host", "-h") and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif arg in ("--ssl", "-s"):
            use_ssl = True
            i += 1
        elif arg in ("--open", "-o"):
            open_browser = True
            i += 1
        elif arg == "--lan":
            host = "0.0.0.0"
            i += 1
        else:
            i += 1

    run_server(host=host, port=port, use_ssl=use_ssl, open_browser=open_browser)

if __name__ == "__main__":
    main()
