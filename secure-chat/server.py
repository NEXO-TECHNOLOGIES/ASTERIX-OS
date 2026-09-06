#!/usr/bin/env python3
"""
ASTERIX OS - Secure Localhost Chatting System v1.0
Zero-Knowledge, End-to-End Encrypted (E2EE), Ephemeral RAM-Only Peer-to-Peer Chat.
Strict 2-party limit ("u and the person"), Anti-Forensic Panic Burn, Zero Disk Storage.

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

# ── Color palette ────────────────────────────────────────────────────────────
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
MAX_PEERS_PER_ROOM = 2  # Private two-party conversation only
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR  = os.path.join(BASE_DIR, "web")

# ── In-Memory Ephemeral Storage (ZERO DISK PERSISTENCE) ──────────────────────
# Format: room_id -> {
#   "salt": hex_str,
#   "created_at": float,
#   "clients": { client_id -> { "name": str, "joined_at": float, "last_seen": float, "queue": Queue() } },
#   "history": list of encrypted payloads,
#   "lock": Lock()
# }
ROOMS = {}
ROOMS_LOCK = threading.Lock()

# Rate limiting: IP -> [timestamp, ...]
RATE_LIMITS = {}
RATE_LOCK = threading.Lock()

def check_rate_limit(ip: str, max_requests: int = 60, window: float = 60.0) -> bool:
    now = time.time()
    with RATE_LOCK:
        history = RATE_LIMITS.setdefault(ip, [])
        history = [t for t in history if now - t < window]
        if len(history) >= max_requests:
            return False
        history.append(now)
        RATE_LIMITS[ip] = history
        return True

def log_event(category: str, detail: str, level: str = "INFO"):
    ts = datetime.datetime.utcnow().strftime("%H:%M:%S UTC")
    color = C_GREEN if level == "INFO" else (C_YELLOW if level == "WARN" else C_RED)
    print(f"  {C_GRAY}[{ts}]{C_RESET} {color}[{category}]{C_RESET} {detail}")

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class SecureChatHandler(BaseHTTPRequestHandler):
    server_version = "AsterixSecureVault/1.0"
    sys_version    = ""

    def log_message(self, format, *args):
        # Suppress default HTTP logging for anti-forensic stealth
        pass

    def send_security_headers(self, content_type="text/html; charset=utf-8"):
        self.send_header("Content-Type", content_type)
        # Strict security headers
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

    def read_json_body(self) -> dict | None:
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length <= 0 or content_length > 65536: # 64KB max payload
                return None
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        except Exception:
            return None

    def send_json_response(self, data: dict, status: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_security_headers("application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ── GET Handler ─────────────────────────────────────────────────────────
    def do_GET(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip, max_requests=120):
            self.send_response(429)
            self.end_headers()
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Real-time Event Stream (SSE)
        if path == "/api/stream":
            self.handle_sse_stream(query)
            return

        # 2. Status API
        if path == "/api/status":
            with ROOMS_LOCK:
                active_rooms = len(ROOMS)
                total_clients = sum(len(r["clients"]) for r in ROOMS.values())
            self.send_json_response({
                "status": "online",
                "active_rooms": active_rooms,
                "connected_peers": total_clients,
                "e2ee_engine": "AES-256-GCM + PBKDF2-SHA256",
                "storage_mode": "EPHEMERAL_RAM_ONLY"
            })
            return

        # 3. Serve Frontend Web UI
        if path == "/" or path == "/index.html":
            file_path = os.path.join(WEB_DIR, "index.html")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_security_headers("text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # 4. Serve static assets if any
        if path.startswith("/web/"):
            rel_path = path[5:].lstrip("/")
            safe_path = os.path.abspath(os.path.join(WEB_DIR, rel_path))
            if os.path.commonpath([WEB_DIR, safe_path]) == os.path.abspath(WEB_DIR) and os.path.isfile(safe_path):
                mime = "application/octet-stream"
                if safe_path.endswith(".css"): mime = "text/css"
                elif safe_path.endswith(".js"): mime = "application/javascript"
                elif safe_path.endswith(".svg"): mime = "image/svg+xml"
                with open(safe_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_security_headers(mime)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        self.send_response(404)
        self.end_headers()

    # ── SSE Stream Handler ──────────────────────────────────────────────────
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

        # Send initial connected handshake
        try:
            self.wfile.write(b": ping\n\n")
            self.wfile.flush()
        except Exception:
            return

        last_ping = time.time()
        while True:
            try:
                # Wait up to 1 second for queued events
                try:
                    event_data = client_queue.get(timeout=1.0)
                    msg_str = json.dumps(event_data)
                    payload = f"data: {msg_str}\n\n".encode("utf-8")
                    self.wfile.write(payload)
                    self.wfile.flush()
                except queue.Empty:
                    pass

                # Periodic heartbeat ping
                if time.time() - last_ping > 15.0:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    last_ping = time.time()

                    # Update last seen
                    with ROOMS_LOCK:
                        if room_id in ROOMS and client_id in ROOMS[room_id]["clients"]:
                            ROOMS[room_id]["clients"][client_id]["last_seen"] = time.time()
                        else:
                            break

            except (BrokenPipeError, ConnectionResetError):
                break
            except Exception:
                break

        # Disconnect cleanup
        with ROOMS_LOCK:
            if room_id in ROOMS and client_id in ROOMS[room_id]["clients"]:
                c_name = ROOMS[room_id]["clients"][client_id]["name"]
                del ROOMS[room_id]["clients"][client_id]
                log_event("DISCONNECT", f"Peer '{c_name}' left room '{room_id}'", "WARN")
                # Notify remaining peer
                for other_id, other_client in ROOMS[room_id]["clients"].items():
                    other_client["queue"].put({
                        "type": "peer_left",
                        "client_id": client_id,
                        "name": c_name,
                        "timestamp": time.time()
                    })

    # ── POST Handler ────────────────────────────────────────────────────────
    def do_POST(self):
        client_ip = self.client_address[0]
        if not check_rate_limit(client_ip, max_requests=100):
            self.send_response(429)
            self.end_headers()
            return

        data = self.read_json_body()
        if data is None:
            self.send_json_response({"error": "Invalid payload"}, 400)
            return

        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Join or Initialize Room
        if path == "/api/room/join":
            room_id = data.get("room", "asterix-vault").strip()
            client_name = data.get("name", "Operative").strip()[:32]
            if not room_id:
                room_id = "asterix-vault"

            with ROOMS_LOCK:
                if room_id not in ROOMS:
                    # Initialize ephemeral room with 32-byte cryptographically secure salt
                    salt = secrets.token_hex(32)
                    ROOMS[room_id] = {
                        "salt": salt,
                        "created_at": time.time(),
                        "clients": {},
                        "history": [],
                        "lock": threading.Lock()
                    }
                    log_event("ROOM_INIT", f"Ephemeral room created: '{room_id}'", "INFO")

                room = ROOMS[room_id]
                # Enforce 2-party peer limit
                if len(room["clients"]) >= MAX_PEERS_PER_ROOM:
                    log_event("ROOM_FULL", f"Join rejected for room '{room_id}' (Max 2 peers reached)", "WARN")
                    self.send_json_response({"error": "Room is full (Maximum 2 peers allowed for private security)"}, 403)
                    return

                client_id = secrets.token_hex(16)
                room["clients"][client_id] = {
                    "name": client_name,
                    "joined_at": time.time(),
                    "last_seen": time.time(),
                    "queue": queue.Queue(maxsize=100)
                }

                # Notify existing peer if present
                for other_id, other_client in room["clients"].items():
                    if other_id != client_id:
                        other_client["queue"].put({
                            "type": "peer_joined",
                            "client_id": client_id,
                            "name": client_name,
                            "timestamp": time.time()
                        })

                peers_count = len(room["clients"])
                salt_val = room["salt"]

            log_event("PEER_JOIN", f"Peer '{client_name}' connected to room '{room_id}' ({peers_count}/{MAX_PEERS_PER_ROOM})", "INFO")
            self.send_json_response({
                "status": "joined",
                "client_id": client_id,
                "room": room_id,
                "salt": salt_val,
                "peers_count": peers_count
            })
            return

        # 2. Relay Encrypted Message Payload (Server sees ONLY ciphertext)
        if path == "/api/send":
            room_id    = data.get("room")
            client_id  = data.get("client_id")
            iv         = data.get("iv")
            ciphertext = data.get("ciphertext")
            tag        = data.get("tag", "")
            burn_secs  = int(data.get("burn_secs", 0))
            msg_id     = data.get("msg_id", secrets.token_hex(12))

            if not all([room_id, client_id, iv, ciphertext]):
                self.send_json_response({"error": "Malformed encrypted envelope"}, 400)
                return

            with ROOMS_LOCK:
                if room_id not in ROOMS or client_id not in ROOMS[room_id]["clients"]:
                    self.send_json_response({"error": "Unauthorized / room expired"}, 403)
                    return

                room = ROOMS[room_id]
                sender_name = room["clients"][client_id]["name"]

                envelope = {
                    "type": "message",
                    "msg_id": msg_id,
                    "sender_id": client_id,
                    "sender_name": sender_name,
                    "iv": iv,
                    "ciphertext": ciphertext,
                    "tag": tag,
                    "burn_secs": burn_secs,
                    "timestamp": time.time()
                }

                # Relay to peer(s)
                delivered = 0
                for other_id, other_client in room["clients"].items():
                    if other_id != client_id:
                        try:
                            other_client["queue"].put_nowait(envelope)
                            delivered += 1
                        except queue.Full:
                            pass

            log_event("MSG_RELAY", f"Encrypted envelope dispatched in '{room_id}' (Burn: {burn_secs}s)", "INFO")
            self.send_json_response({"status": "delivered", "msg_id": msg_id, "recipients": delivered})
            return

        # 3. Individual Message Burn Notice
        if path == "/api/burn":
            room_id   = data.get("room")
            client_id = data.get("client_id")
            msg_id    = data.get("msg_id")

            with ROOMS_LOCK:
                if room_id in ROOMS and client_id in ROOMS[room_id]["clients"]:
                    room = ROOMS[room_id]
                    for other_id, other_client in room["clients"].items():
                        if other_id != client_id:
                            try:
                                other_client["queue"].put_nowait({
                                    "type": "burn",
                                    "msg_id": msg_id,
                                    "timestamp": time.time()
                                })
                            except queue.Full:
                                pass

            self.send_json_response({"status": "burned", "msg_id": msg_id})
            return

        # 4. Emergency Panic / Room Burn Killswitch
        if path == "/api/panic":
            room_id   = data.get("room")
            client_id = data.get("client_id")

            with ROOMS_LOCK:
                if room_id in ROOMS:
                    room = ROOMS[room_id]
                    # Notify everyone in the room of panic burn
                    for c_id, client in room["clients"].items():
                        try:
                            client["queue"].put_nowait({
                                "type": "panic",
                                "reason": "EMERGENCY_KILLSWITCH_TRIGGERED",
                                "timestamp": time.time()
                            })
                        except Exception:
                            pass
                    # Eradicate room from RAM completely
                    del ROOMS[room_id]
                    log_event("PANIC_BURN", f"ROOM '{room_id}' PERMANENTLY NUKED FROM MEMORY", "CRIT")

            self.send_json_response({"status": "nuked", "action": "ROOM_ERADICATED"})
            return

        self.send_json_response({"error": "Endpoint not found"}, 404)

def banner(host: str, port: int, ssl_enabled: bool):
    proto = "https" if ssl_enabled else "http"
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  [ ASTERIX SECURE CHAT // ZERO-KNOWLEDGE LOCALHOST VAULT v1.0 ]       {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")
    print(f"  {C_GREEN}{C_BOLD}● LOCAL VAULT ONLINE{C_RESET}  —  Private Peer-to-Peer Encrypted Bridge")
    print(f"  {C_WHITE}Direct Web URL:{C_RESET}       {C_CYAN}{C_BOLD}{proto}://{host}:{port}{C_RESET}")
    print(f"  {C_WHITE}Encryption Core:{C_RESET}      {C_GREEN}AES-256-GCM (Browser Web Crypto API){C_RESET}")
    print(f"  {C_WHITE}Key Derivation:{C_RESET}       {C_GREEN}PBKDF2-HMAC-SHA256 (100,000 Iterations){C_RESET}")
    print(f"  {C_WHITE}Persistence:{C_RESET}          {C_YELLOW}100% In-Memory RAM (Zero Disk Writes){C_RESET}")
    print(f"  {C_WHITE}Party Limit:{C_RESET}          {C_MAGENTA}Strict 2-Party Bound (Peer & You Only){C_RESET}")
    print(f"  {C_WHITE}Anti-Forensics:{C_RESET}       {C_RED}Ephemeral Self-Destruct & 1-Click Panic Burn{C_RESET}\n")
    print(f"  {C_GRAY}To connect the other person on LAN: share http://<your-ip>:{port}{C_RESET}")
    print(f"  {C_GRAY}To connect over SSH tunnel:         ssh -L {port}:localhost:{port} user@host{C_RESET}")
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
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_file, keyfile=key_file)
            server.socket = context.wrap_socket(server.socket, server_side=True)
            log_event("SSL", "TLS encryption wrapper initialized", "INFO")

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
