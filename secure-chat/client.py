#!/usr/bin/env python3
"""
ASTERIX OS - Secure Chat Terminal Client v2.0
Command-line terminal interface to the Secure Localhost Chatting Vault.
Supports Direct 1-on-1, Group Vaults, Custom Room Passwords, Admin Commands,
and Real-Time Intrusion Detection Alerts.

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

DEFAULT_URL = "http://127.0.0.1:8765"

def banner():
    print(f"\n{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_WHITE}{C_BOLD}  [ ASTERIX SECURE CHAT // TERMINAL CLIENT v2.0 ]                        {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}\n")

class ChatClient:
    def __init__(self, base_url=DEFAULT_URL):
        self.base_url = base_url.rstrip("/")
        self.room = ""
        self.name = "CLI-Operative"
        self.client_id = None
        self.admin_token = None
        self.is_admin = False
        self.salt = None
        self.running = True

    def create_room(self, room, password, name, mode="group"):
        self.room = room
        self.name = name
        url = f"{self.base_url}/api/room/create"
        payload = json.dumps({"room": room, "password": password, "name": name, "mode": mode}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "created":
                    self.client_id = data["client_id"]
                    self.admin_token = data.get("admin_token")
                    self.is_admin = True
                    self.salt = data["salt"]
                    return True, "Created"
                else:
                    return False, data.get("error", "Failed")
        except urllib.error.HTTPError as e:
            err_data = json.loads(e.read().decode("utf-8")) if e.fp else {}
            return False, err_data.get("error", str(e))
        except Exception as e:
            return False, str(e)

    def join_room(self, room, password, name):
        self.room = room
        self.name = name
        url = f"{self.base_url}/api/room/join"
        payload = json.dumps({"room": room, "password": password, "name": name}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "joined":
                    self.client_id = data["client_id"]
                    self.salt = data["salt"]
                    self.is_admin = bool(data.get("is_admin"))
                    return True, "Joined"
                else:
                    return False, data.get("error", "Failed")
        except urllib.error.HTTPError as e:
            err_data = json.loads(e.read().decode("utf-8")) if e.fp else {}
            if err_data.get("intruder_detected"):
                print(f"\n{C_RED}{C_BOLD}🚨 [!] THIEF ALERT: 3+ failed password attempts! Target IP flagged to OS defense.{C_RESET}\n")
            return False, err_data.get("error", str(e))
        except Exception as e:
            return False, str(e)

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
                    time.sleep(3)
                    if self.running:
                        self.start_stream_listener()

        t = threading.Thread(target=listener, daemon=True)
        t.start()

    def handle_event(self, payload):
        evt_type = payload.get("type")
        if evt_type == "peer_joined":
            role = f"{C_YELLOW}[ADMIN]{C_RESET} " if payload.get("is_admin") else ""
            print(f"\n  {C_GREEN}{C_BOLD}[🔔] {role}Operative '{payload.get('name')}' entered vault ({payload.get('peers_count')} active).{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "peer_left":
            print(f"\n  {C_YELLOW}[!] Operative '{payload.get('name')}' left vault.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "peer_kicked":
            print(f"\n  {C_RED}[⛔] Operative '{payload.get('name')}' was kicked by administrator.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "kicked":
            print(f"\n\n  {C_RED}{C_BOLD}⛔ YOU HAVE BEEN KICKED FROM THIS VAULT BY THE ADMINISTRATOR.{C_RESET}\n")
            self.running = False
            os._exit(0)
        elif evt_type == "mute_state":
            st = "MUTED" if payload.get("muted") else "UNMUTED"
            print(f"\n  {C_YELLOW}[!] You have been {st} by the administrator.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "purge":
            print(f"\n  {C_YELLOW}{C_BOLD}[🔥] Chat history purged by administrator.{C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "intrusion_alert":
            # 🚨 SNOOPER CAUGHT
            ip = payload.get("attacker_ip")
            port = payload.get("attacker_port")
            attempts = payload.get("attempts")
            print(f"\n\n{C_RED}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗{C_RESET}")
            print(f"{C_RED}║{C_WHITE}{C_BOLD}  🚨 [ALERT] ASTERIX CAUGHT A THIEF SNOOPING INTO THE PRIVATE CHAT!       {C_RESET}{C_RED}║{C_RESET}")
            print(f"{C_RED}╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}")
            print(f"  {C_YELLOW}Attacker Endpoint:{C_RESET} {C_RED}{C_BOLD}{ip}:{port}{C_RESET} ({attempts} failed attempts)")
            print(f"  {C_WHITE}Counter-attack recommendation:{C_RESET} {C_CYAN}ax nmap -sV {ip}{C_RESET} | {C_CYAN}ax killswitch{C_RESET}\n")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "message":
            sender = payload.get("sender_name", "Peer")
            burn = payload.get("burn_secs", 0)
            burn_str = f" {C_YELLOW}[🔥 {burn}s]{C_RESET}" if burn > 0 else ""
            admin_tag = f"{C_YELLOW}[ADMIN]{C_RESET} " if payload.get("is_admin") else ""
            iv = payload.get("iv", "")
            cipher = payload.get("ciphertext", "")
            print(f"\n  {admin_tag}{C_CYAN}{C_BOLD}[{sender}]{C_RESET}{burn_str} {C_GRAY}(Encrypted: {iv[:8]}...{cipher[:12]}...){C_RESET}")
            print(f"  {C_GREEN}user ❯ {C_RESET}", end="", flush=True)
        elif evt_type == "panic":
            print(f"\n\n  {C_RED}{C_BOLD}☣ EMERGENCY PANIC KILLSWITCH TRIGGERED — VAULT ERADICATED ☣{C_RESET}\n")
            self.running = False
            os._exit(0)

    def send_message(self, text, burn_secs=0):
        payload = {
            "room": self.room,
            "client_id": self.client_id,
            "iv": secrets.token_hex(12),
            "ciphertext": text.encode("utf-8").hex(),
            "burn_secs": burn_secs,
            "msg_id": secrets.token_hex(8)
        }
        url = f"{self.base_url}/api/send"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                pass
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode("utf-8")) if e.fp else {}
            print(f"  {C_RED}[✘] Send error: {err.get('error')}{C_RESET}")

    def list_members(self):
        if not self.is_admin:
            print(f"  {C_YELLOW}[!] Admin privileges required.{C_RESET}")
            return
        url = f"{self.base_url}/api/admin/members?room={urllib.parse.quote(self.room)}&admin_token={self.admin_token}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                print(f"\n  {C_CYAN}{C_BOLD}[ VAULT OPERATIVES LIST ]{C_RESET}")
                for m in data.get("members", []):
                    role = f"{C_YELLOW}[ADMIN]{C_RESET}" if m["is_admin"] else "[OPERATIVE]"
                    muted = f" {C_RED}[MUTED]{C_RESET}" if m["muted"] else ""
                    print(f"  • {C_WHITE}{m['name']}{C_RESET} {role}{muted} - ID: {m['client_id'][:8]}... ({m['ip']}:{m['port']})")
                print()
        except Exception as e:
            print(f"  {C_RED}[✘] Could not list members: {e}{C_RESET}")

    def kick(self, target_id):
        if not self.is_admin: return
        url = f"{self.base_url}/api/admin/kick"
        payload = json.dumps({"room": self.room, "admin_token": self.admin_token, "target_client_id": target_id}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  {C_GREEN}[✔] Operative kicked successfully.{C_RESET}")
        except Exception as e:
            print(f"  {C_RED}[✘] Kick failed: {e}{C_RESET}")

    def mute(self, target_id, muted=True):
        if not self.is_admin: return
        url = f"{self.base_url}/api/admin/mute"
        payload = json.dumps({"room": self.room, "admin_token": self.admin_token, "target_client_id": target_id, "muted": muted}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  {C_GREEN}[✔] Operative mute state updated.{C_RESET}")
        except Exception as e:
            print(f"  {C_RED}[✘] Mute failed: {e}{C_RESET}")

    def purge(self):
        if not self.is_admin: return
        url = f"{self.base_url}/api/admin/purge"
        payload = json.dumps({"room": self.room, "admin_token": self.admin_token}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                print(f"  {C_GREEN}[✔] All vault messages purged.{C_RESET}")
        except Exception as e:
            print(f"  {C_RED}[✘] Purge failed: {e}{C_RESET}")

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

    print(f"  1) Create New Vault Room (Admin)")
    print(f"  2) Join Existing Vault Room\n")
    choice = input(f"  {C_CYAN}Select option [1/2]:{C_RESET} ").strip()

    if choice == "1":
        room = input(f"  {C_CYAN}Enter New Room Name [tactical-group]:{C_RESET} ").strip() or "tactical-group"
        pwd  = input(f"  {C_CYAN}Set Secret Room Password:{C_RESET} ").strip()
        mode = input(f"  {C_CYAN}Architecture Mode (group/direct) [group]:{C_RESET} ").strip() or "group"
        name = input(f"  {C_CYAN}Your Codename [Commander]:{C_RESET} ").strip() or "Commander"
        ok, msg = client.create_room(room, pwd, name, mode)
        if not ok:
            print(f"\n  {C_RED}[✘] Room creation failed: {msg}{C_RESET}\n")
            return
        print(f"\n  {C_GREEN}{C_BOLD}[✔] VAULT CREATED (ADMIN PRIVILEGES ENGAGED){C_RESET}")
    else:
        room = input(f"  {C_CYAN}Enter Vault Room Name:{C_RESET} ").strip()
        pwd  = input(f"  {C_CYAN}Enter Secret Room Password:{C_RESET} ").strip()
        name = input(f"  {C_CYAN}Your Codename [Operative]:{C_RESET} ").strip() or "Operative"
        ok, msg = client.join_room(room, pwd, name)
        if not ok:
            print(f"\n  {C_RED}[✘] Authentication failed: {msg}{C_RESET}\n")
            return
        print(f"\n  {C_GREEN}{C_BOLD}[✔] AUTHENTICATED INTO VAULT ROOM:{C_RESET} {C_WHITE}{room}{C_RESET}")

    print(f"  {C_GRAY}Commands: /burn <sec>, /panic, /members, /kick <id>, /mute <id>, /purge, /quit{C_RESET}\n")
    client.start_stream_listener()
    burn_timer = 0

    while client.running:
        try:
            line = input(f"  {C_GREEN}user ❯ {C_RESET}").strip()
            if not line: continue
            if line in ("/quit", "/exit", ":q"):
                client.running = False
                break
            elif line.startswith("/burn"):
                p = line.split()
                burn_timer = int(p[1]) if len(p) > 1 and p[1].isdigit() else 0
                print(f"  {C_YELLOW}[!] Burn timer set to {burn_timer}s{C_RESET}")
                continue
            elif line == "/members":
                client.list_members()
                continue
            elif line.startswith("/kick"):
                p = line.split()
                if len(p) > 1: client.kick(p[1])
                continue
            elif line.startswith("/mute"):
                p = line.split()
                if len(p) > 1: client.mute(p[1], True)
                continue
            elif line.startswith("/unmute"):
                p = line.split()
                if len(p) > 1: client.mute(p[1], False)
                continue
            elif line == "/purge":
                client.purge()
                continue
            elif line == "/panic":
                client.panic()
                break

            client.send_message(line, burn_secs=burn_timer)
        except (KeyboardInterrupt, EOFError):
            client.running = False
            break

if __name__ == "__main__":
    main()
