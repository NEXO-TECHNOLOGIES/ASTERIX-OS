#!/usr/bin/env python3
import json
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ASTERIX VPS Dashboard</title>
  <style>
    :root {
      --bg: #07111f;
      --panel: #101d2e;
      --panel-2: #15273d;
      --accent: #5eead4;
      --accent-2: #7dd3fc;
      --text: #e6f1ff;
      --muted: #9db7d3;
      --warn: #fbbf24;
      --danger: #f87171;
      --good: #4ade80;
      --shadow: rgba(10, 18, 32, 0.6);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Segoe UI, Tahoma, sans-serif;
      background: linear-gradient(180deg, var(--bg), #0e1d2d 55%, #091522);
      color: var(--text);
    }
    .shell {
      width: min(1200px, calc(100% - 32px));
      margin: 24px auto;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 18px 20px;
      background: rgba(16, 29, 46, 0.85);
      border: 1px solid rgba(94, 234, 212, 0.15);
      border-radius: 18px;
      box-shadow: 0 12px 40px var(--shadow);
      margin-bottom: 20px;
    }
    .header h1 {
      margin: 0;
      font-size: clamp(20px, 3vw, 34px);
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    .pill {
      padding: 8px 14px;
      border-radius: 999px;
      background: rgba(94, 234, 212, 0.12);
      color: var(--accent);
      border: 1px solid rgba(94, 234, 212, 0.25);
      font-size: 12px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 18px;
    }
    .panel {
      background: linear-gradient(180deg, rgba(21, 39, 61, 0.95), rgba(12, 24, 38, 0.95));
      border-radius: 16px;
      border: 1px solid rgba(125, 211, 252, 0.15);
      box-shadow: 0 12px 32px var(--shadow);
      padding: 18px;
    }
    .host-box {
      margin-bottom: 18px;
    }
    .host-box h2, .card h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .stat {
      font-size: 13px;
      color: var(--text);
      line-height: 1.8;
      white-space: pre-wrap;
    }
    .card {
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: "";
      position: absolute;
      inset: 0 auto auto 0;
      width: 100%;
      height: 4px;
      background: linear-gradient(90deg, var(--accent), var(--accent-2));
    }
    .vm-name {
      font-weight: 700;
      font-size: 22px;
      margin-bottom: 10px;
    }
    .badge {
      display: inline-block;
      padding: 5px 10px;
      font-size: 12px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.12);
      margin-bottom: 12px;
    }
    .running { background: rgba(74, 222, 128, 0.14); color: var(--good); }
    .stopped { background: rgba(248, 113, 113, 0.12); color: var(--danger); }
    .meta { color: var(--muted); font-size: 13px; line-height: 1.9; }
    .empty {
      color: var(--muted);
      padding: 16px;
      border: 1px dashed rgba(157, 183, 211, 0.35);
      border-radius: 12px;
      margin-top: 12px;
    }
    @media (max-width: 680px) {
      .header { flex-direction: column; gap: 12px; align-items: flex-start; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="header">
      <h1>ASTERIX VPS</h1>
      <div class="pill" id="timestamp">loading...</div>
    </div>

    <div class="panel host-box">
      <h2>Host status</h2>
      <div id="host-status" class="stat">loading host metrics...</div>
    </div>

    <div class="grid" id="vm-grid"></div>
  </div>

  <script>
    const vmGrid = document.getElementById('vm-grid');
    const hostStatus = document.getElementById('host-status');
    const timestamp = document.getElementById('timestamp');

    function renderHost(data) {
      const details = [
        data.os || 'OS: unknown',
        data.kernel || 'Kernel: unknown',
        data.uptime || 'Uptime: unknown',
        data.memory || 'Memory: unknown',
        data.disk || 'Disk: unknown',
        data.libvirt || 'Libvirt: unknown'
      ];
      hostStatus.textContent = details.join('\n');
    }

    function renderVMs(vms) {
      if (!vms || !vms.length) {
        vmGrid.innerHTML = '<div class="empty">No VMs are currently registered.</div>';
        return;
      }

      vmGrid.innerHTML = vms.map(vm => `
        <div class="panel card">
          <div class="vm-name">${vm.name}</div>
          <div class="badge ${vm.state === 'running' ? 'running' : 'stopped'}">${vm.state}</div>
          <div class="meta">
            CPU: ${vm.cpu || 'unknown'}<br>
            Memory: ${vm.memory || 'unknown'}<br>
            IP: ${vm.ip || 'pending'}<br>
            Domain: ${vm.domain || 'n/a'}
          </div>
        </div>
      `).join('');
    }

    async function refresh() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        renderHost(data.host);
        renderVMs(data.vms);
        timestamp.textContent = new Date().toLocaleTimeString();
      } catch (error) {
        vmGrid.innerHTML = '<div class="empty">Unable to load VPS data right now.</div>';
        hostStatus.textContent = 'Dashboard error: ' + error.message;
      }
    }

    refresh();
    setInterval(refresh, 10000);
  </script>
</body>
</html>
"""


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    return result.returncode, stdout, stderr


def parse_vm_list():
    code, out, err = run_command(["bash", "-lc", "virsh list --all 2>&1 || true"])
    lines = [line.strip() for line in (out or err).splitlines() if line.strip()]
    if len(lines) < 3:
        return []

    vms = []
    for line in lines[2:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        if parts[0].lower() == "id":
            continue
        try:
            identifier = int(parts[0])
        except ValueError:
            identifier = None
        name = parts[1]
        state = parts[2] if len(parts) > 2 else "unknown"
        vms.append({"id": identifier, "name": name, "state": state.lower()})
    return vms


def get_vm_details(name):
    code, info, err = run_command(["bash", "-lc", f"virsh dominfo {name} 2>&1 || true"])
    memory = "unknown"
    cpu = "unknown"
    state = "unknown"
    domain = "n/a"

    for line in (info or err).splitlines():
        if line.lower().startswith("state:"):
            state = line.split(":", 1)[1].strip()
        elif line.lower().startswith("cpu(s):"):
            cpu = line.split(":", 1)[1].strip()
        elif line.lower().startswith("max memory:"):
            memory = line.split(":", 1)[1].strip().split()[0] + " MB"
        elif line.lower().startswith("name:"):
            domain = line.split(":", 1)[1].strip()

    code2, ip_output, err2 = run_command(["bash", "-lc", f"virsh domifaddr {name} 2>&1 || true"])
    ip = "pending"
    if ip_output:
        lines = [line.strip() for line in ip_output.splitlines() if line.strip()]
        for line in reversed(lines):
            bits = line.split()
            if len(bits) >= 4 and bits[0].startswith("vnet"):
                ip = bits[-1]
                break
            if len(bits) >= 4 and bits[-1].count('.') == 3:
                ip = bits[-1]
                break

    return {
        "name": name,
        "state": state.lower() if state.lower() in {"running", "paused", "shutdown", "shut off", "crashed", "blocked"} else "unknown",
        "cpu": cpu,
        "memory": memory,
        "ip": ip,
        "domain": domain,
    }


def get_host_status():
    sections = {
        "os": "OS: unknown",
        "kernel": "Kernel: unknown",
        "uptime": "Uptime: unknown",
        "memory": "Memory: unknown",
        "disk": "Disk: unknown",
        "libvirt": "Libvirt: unknown",
    }

    code, uname_out, _ = run_command(["bash", "-lc", "uname -a 2>/dev/null || true"])
    if uname_out:
        sections["kernel"] = f"Kernel: {uname_out.split()[0]} {uname_out.split()[2]}"

    code, os_out, _ = run_command(["bash", "-lc", "cat /etc/os-release 2>/dev/null | sed -n '1,4p' || true"])
    if os_out:
        os_labels = []
        for line in os_out.splitlines():
            if line.startswith("NAME=") or line.startswith("PRETTY_NAME="):
                os_labels.append(line.split("=", 1)[1].strip().strip('"'))
        sections["os"] = "OS: " + " | ".join(os_labels) if os_labels else sections["os"]

    code, uptime_out, _ = run_command(["bash", "-lc", "uptime 2>/dev/null || true"])
    if uptime_out:
        sections["uptime"] = "Uptime: " + uptime_out

    code, mem_out, _ = run_command(["bash", "-lc", "free -m 2>/dev/null || true"])
    if mem_out:
        parts = mem_out.splitlines()
        if len(parts) >= 2:
            sections["memory"] = "Memory: " + parts[1].replace("\t", " | ")

    code, disk_out, _ = run_command(["bash", "-lc", "df -h / 2>/dev/null || true"])
    if disk_out:
        lines = [line for line in disk_out.splitlines() if line.strip()]
        if len(lines) >= 2:
            sections["disk"] = "Disk: " + lines[1].replace("\t", " | ")

    code, libvirt_out, _ = run_command(["bash", "-lc", "systemctl is-active libvirtd 2>/dev/null || true"])
    if libvirt_out:
        sections["libvirt"] = "Libvirt: " + libvirt_out
    else:
        sections["libvirt"] = "Libvirt: not detected"

    return sections


def collect_dashboard_payload():
    vm_rows = parse_vm_list()
    vms = []
    for row in vm_rows:
        detail = get_vm_details(row["name"])
        vms.append({
            "name": detail["name"],
            "state": detail["state"],
            "cpu": detail["cpu"],
            "memory": detail["memory"],
            "ip": detail["ip"],
            "domain": detail["domain"],
        })

    payload = {
        "host": get_host_status(),
        "vms": vms,
    }
    return payload


class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(collect_dashboard_payload()).encode())
            return

        if parsed.path == "/api/host":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(get_host_status()).encode())
            return

        if parsed.path == "/api/vms":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(parse_vm_list()).encode())
            return

        if parsed.path == "/api/metrics":
            payload = {
                "host": get_host_status(),
                "vms": [get_vm_details(vm["name"]) for vm in parse_vm_list()],
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())
            return

        if parsed.path in {"/", "/index.html"}:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
            return

        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        return


def main():
    host = "0.0.0.0"
    port = 8080
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"ASTERIX VPS dashboard running on http://{host}:{port}")
    print("REST endpoints: /api/status, /api/host, /api/vms, /api/metrics")
    server.serve_forever()


if __name__ == "__main__":
    main()
