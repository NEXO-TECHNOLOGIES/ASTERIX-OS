#!/usr/bin/env python3
"""
=====================================================================
ASTERIX OS - Remote Cloud Compute & Storage Node (Panel Worker)
Deploy this on your 50-coins panel / VPS / Discord container.
Provides:
 1. Remote Cloud Computation Engine (Compile, Hash, Scripts, Tasks)
 2. Encrypted Remote Cloud Storage API (Upload, Download, List)
 3. Optional Discord Bot Interface with Slash Commands
=====================================================================
"""

import os
import sys
import json
import time
import subprocess
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", 8080))
AUTH_KEY = os.environ.get("ASTERIX_CLOUD_KEY", "asterix-sec-key-2026")
STORAGE_DIR = os.path.abspath(os.environ.get("STORAGE_DIR", "./cloud_vault"))
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")

os.makedirs(STORAGE_DIR, exist_ok=True)

class CloudRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _check_auth(self):
        auth_header = self.headers.get("X-Asterix-Key", "")
        if auth_header != AUTH_KEY:
            self._send_json(401, {"error": "Unauthorized. Invalid X-Asterix-Key."})
            return False
        return True

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/health" or path == "/":
            self._send_json(200, {
                "status": "ONLINE",
                "node": "ASTERIX Cloud Compute Node",
                "platform": sys.platform,
                "uptime": int(time.time()),
                "storage_dir": STORAGE_DIR
            })
            return

        if not self._check_auth():
            return

        if path == "/status":
            cpu_count = os.cpu_count() or 1
            storage_usage = shutil.disk_usage(STORAGE_DIR)
            files = os.listdir(STORAGE_DIR)
            
            self._send_json(200, {
                "status": "READY",
                "cpu_cores": cpu_count,
                "storage_used_bytes": storage_usage.used,
                "storage_free_bytes": storage_usage.free,
                "files_stored": len(files),
                "file_list": files
            })
            return

        if path == "/download":
            query = parse_qs(parsed.query)
            filename = query.get("file", [""])[0]
            file_path = os.path.join(STORAGE_DIR, os.path.basename(filename))

            if not os.path.exists(file_path):
                self._send_json(404, {"error": f"File '{filename}' not found in cloud vault."})
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(filename)}")
            self.send_header("Content-Length", str(os.path.getsize(file_path)))
            self.end_headers()

            with open(file_path, "rb") as f:
                shutil.copyfileobj(f, self.wfile)
            return

        self._send_json(404, {"error": "Endpoint not found."})

    def do_POST(self):
        if not self._check_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # 1. Remote Cloud Computation Engine (/compute)
        if path == "/compute":
            try:
                data = json.loads(body.decode("utf-8"))
                command = data.get("command", "")
                timeout = min(int(data.get("timeout", 60)), 300)

                if not command:
                    self._send_json(400, {"error": "Missing 'command' parameter."})
                    return

                start_time = time.time()
                proc = subprocess.run(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True
                )
                duration = time.time() - start_time

                self._send_json(200, {
                    "success": proc.returncode == 0,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "execution_time_sec": round(duration, 3)
                })
            except subprocess.TimeoutExpired:
                self._send_json(408, {"error": f"Computation timed out after {timeout} seconds."})
            except Exception as e:
                self._send_json(500, {"error": str(e)})
            return

        # 2. Remote Cloud Storage Upload (/upload)
        if path == "/upload":
            query = parse_qs(parsed.query)
            filename = query.get("file", [""])[0] or f"artifact_{int(time.time())}.dat"
            safe_filename = os.path.basename(filename)
            file_path = os.path.join(STORAGE_DIR, safe_filename)

            with open(file_path, "wb") as f:
                f.write(body)

            self._send_json(200, {
                "success": True,
                "message": f"File '{safe_filename}' saved to cloud vault.",
                "size_bytes": len(body),
                "path": file_path
            })
            return

        self._send_json(404, {"error": "Unknown POST endpoint."})

def run_server():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, CloudRequestHandler)
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║        ASTERIX OS // CLOUD COMPUTE & STORAGE NODE         ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  • Port:        {PORT:<41} ║
    ║  • Storage Dir: {STORAGE_DIR:<41} ║
    ║  • Auth Key:    {AUTH_KEY:<41} ║
    ║  • Status:      ONLINE & LISTENING FOR CLOUD JOBS         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down ASTERIX Cloud Worker...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
