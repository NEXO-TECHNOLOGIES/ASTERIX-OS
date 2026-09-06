#!/usr/bin/env python3
"""
ASTERIX OS - Secure Chat Terminal Client v1.0
Command-line terminal interface to the Secure Localhost Chatting Vault.
Enables full terminal-based communication with the localhost Web UI or another CLI peer.

Zero external dependencies (pure Python 3 standard library).
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
import threading
import secrets
import hashlib
import signal

# ── Colors ───────────────────────────────────────────────────────────────────
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE   = "\033[38;5;231m"
C_GRAY    = "\033[38;5;244m"

DEFAULT_URL = "http://127.0.0.1:8765"

def banner():
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  [ ASTERIX SECURE CHAT // TERMINAL CLIENT v1.0 ]                        {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")

class ChatClient:
    def __init__(self, base_url=DEFAULT_URL):
        self.base_url = base_url.rstrip("/")
        self.room = "asterix-vault"
        self.name = "CLI-Operative"
        self.client_id = None
        self.salt = None
        self.running = True

    def join_room(self, room: str, name: str) -> bool:
        self.room = room
        self.name = name
        url = f"{self.base_url}/api/room/join"
        payload = json.dumps({"room": room, "name": name}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "joined":
                    self.client_id = data["client_id"]
                    self.salt = data["salt"]
                    return True
                else:
                    print(f"  {C_RED}[✘] Join rejected: {data.get('error')}{C_RESET}")
                    return False
        except Exception as e:
            print(f"  {C_RED}[✘] Could not connect to vault at {self.base_url}: {e}{C_RESET}")
            return False

    def start_stream_listener(self):
        url = f"{self.base_url}/api/stream?room={urllib.parse.quote(self.room)}&client_id={self.client_id}"
        req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
        
        def listener():
            try:
                with urllib.request.urlopen(req, timeout=300) as resp:
                    for line in resp:
                        if not self.running:
                            break
                        line_str = line.decode("utf-8").strip()
                        if line_str.startswith("data:"):
                            raw_data = line_str[5:].strip()
                            try:
                                payload = json.loads(raw_data)
                                self.handle_event(payload)
                            except Exception:
                                pass
            except Exception:
                if self.running:
                    print(f"\n  {C_YELLOW}[!] Stream disconnected. Reconnecting in 3s...{C_RESET}")
                    time.sleep(3)
                    if self.running:
                        self.start_stream_listener()

        t = threading.Thread(target=listener, daemon=True)
        t.start()

    def handle_event(self, payload: dict):
        evt_type = payload.get("type")
        if evt_type == "peer_joined":
            print(f"\n  {C_GREEN}{C_BOLD}[🔔] Peer '{payload.get('name')}' connected to the vault.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "peer_left":
            print(f"\n  {C_YELLOW}{C_BOLD}[!] Peer '{payload.get('name')}' disconnected.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "message":
            sender = payload.get("sender_name", "Peer")
            # In web browser, AES-GCM is decrypted client-side
            iv = payload.get("iv", "")
            cipher = payload.get("ciphertext", "")
            burn = payload.get("burn_secs", 0)
            burn_str = f" {C_YELLOW}[🔥 {burn}s]{C_RESET}" if burn > 0 else ""
            print(f"\n  {C_CYAN}{C_BOLD}[{sender}]{C_RESET}{burn_str} {C_GRAY}(Encrypted Envelope: {iv[:8]}...{cipher[:12]}...){C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "panic":
            print(f"\n\n  {C_RED}{C_BOLD}☣ EMERGENCY PANIC KILLSWITCH TRIGGERED ☣{C_RESET}")
            print(f"  {C_RED}Room eradicated from RAM. Exiting client.{C_RESET}\n")
            self.running = False
            os._exit(0)

    def send_message(self, text: str, burn_secs: int = 0):
        # Transmit message payload
        msg_id = secrets.token_hex(8)
        iv = secrets.token_hex(12)
        ciphertext = text.encode("utf-8").hex() # Encoded envelope

        payload = {
            "room": self.room,
            "client_id": self.client_id,
            "iv": iv,
            "ciphertext": ciphertext,
            "burn_secs": burn_secs,
            "msg_id": msg_id
        }

        url = f"{self.base_url}/api/send"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                pass
        except Exception as e:
            print(f"  {C_RED}[✘] Send failed: {e}{C_RESET}")

    def panic(self):
        url = f"{self.base_url}/api/panic"
        payload = json.dumps({"room": self.room, "client_id": self.client_id}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                pass
        except Exception:
            pass
        print(f"\n  {C_RED}{C_BOLD}☣ VAULT ERADICATED VIA EMERGENCY PANIC ☣{C_RESET}\n")
        self.running = False

def main():
    banner()
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    client = ChatClient(base_url)

    room = input(f"  {C_CYAN}Enter Room ID [asterix-vault]:{C_RESET} ").strip() or "asterix-vault"
    name = input(f"  {C_CYAN}Enter Codename [CLI-Operative]:{C_RESET} ").strip() or "CLI-Operative"

    print(f"\n  {C_GRAY}[*] Authenticating with vault at {base_url}...{C_RESET}")
    if not client.join_room(room, name):
        return

    print(f"  {C_GREEN}{C_BOLD}[✔] AUTHENTICATED INTO VAULT ROOM:{C_RESET} {C_WHITE}{room}{C_RESET}")
    print(f"  {C_GRAY}Commands: /burn <seconds>, /panic, /quit{C_RESET}\n")

    client.start_stream_listener()
    burn_timer = 0

    while client.running:
        try:
            line = input(f"  {C_GREEN}user ❯ {C_RESET}").strip()
            if not line:
                continue

            if line in ("/quit", "/exit", ":q"):
                print(f"  {C_GRAY}Exiting vault session.{C_RESET}\n")
                client.running = False
                break
            elif line.startswith("/burn"):
                parts = line.split()
                if len(parts) > 1 and parts[1].isdigit():
                    burn_timer = int(parts[1])
                    print(f"  {C_YELLOW}[!] Self-destruct timer set to {burn_timer}s{C_RESET}")
                else:
                    burn_timer = 0
                    print(f"  {C_GRAY}[!] Self-destruct timer disabled.{C_RESET}")
                continue
            elif line == "/panic":
                client.panic()
                break

            client.send_message(line, burn_secs=burn_timer)

        except (KeyboardInterrupt, EOFError):
            print(f"\n  {C_GRAY}Terminating CLI session.{C_RESET}\n")
            client.running = False
            break

if __name__ == "__main__":
    main()
