#!/usr/bin/env python3
"""Local HTTP service for ASTERIX project-safe tool generation and approval."""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tool_generator import approve_tool, generate_safe_tool, load_registry

HOST = "127.0.0.1"
PORT = 8765


class ToolRegistryHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send_json({"status": "ok"}, 200)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/tool-registry":
            self._send_json({"status": "not_found"}, 404)
            return
        registry = load_registry()
        self._send_json({"tools": registry.get("tools", []), "pending": registry.get("pending", []), "approved": registry.get("approved", [])})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/tool-registry":
            self._send_json({"status": "not_found"}, 404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except json.JSONDecodeError:
            self._send_json({"status": "invalid_json", "error": "Malformed JSON body"}, 400)
            return

        tool_name = str(payload.get("tool_name") or "").strip()
        if payload.get("approve") is True and tool_name:
            entry = approve_tool(tool_name)
            if entry.get("status") == "not_found":
                self._send_json({"status": "not_found", "tool_name": tool_name}, 404)
                return
            self._send_json({"status": "approved", "tool": entry})
            return

        tool_type = str(payload.get("tool_type") or "dashboard").strip() or "dashboard"
        description = str(payload.get("description") or "Project-safe ASTERIX internal tool").strip() or "Project-safe ASTERIX internal tool"
        project_scope = str(payload.get("project_scope") or "project").strip() or "project"

        generated = generate_safe_tool(tool_type, description, categories=[tool_type.lower()], project_scope=project_scope)
        if generated.get("status") == "created" and payload.get("approve") is True:
            approved = approve_tool(generated["file_name"].replace(".py", ""))
            generated["approval"] = approved.get("status", "approved")
            generated["approved"] = approved.get("status", "approved") == "approved"
        self._send_json(generated)


def main():
    server = HTTPServer((HOST, PORT), ToolRegistryHandler)
    print(f"ASTERIX tool registry service listening on http://{HOST}:{PORT}/api/tool-registry")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
