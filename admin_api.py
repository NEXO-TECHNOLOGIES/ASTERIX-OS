from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

VM_CATALOG = [
    {"name": "vps-prod-01", "region": "us-east", "cpu": "8 vCPU", "ram": "32 GB", "status": "Running", "progress": 88, "image": "Ubuntu 24.04 LTS", "sshKey": "operator@asterix"},
    {"name": "vps-dev-03", "region": "eu-west", "cpu": "4 vCPU", "ram": "16 GB", "status": "Scaling", "progress": 62, "image": "Debian 12", "sshKey": "ci-bot@dev"},
    {"name": "edge-node-09", "region": "ap-south", "cpu": "6 vCPU", "ram": "24 GB", "status": "Healthy", "progress": 74, "image": "Fedora 40", "sshKey": "edge-gateway"},
    {"name": "sandbox-12", "region": "local", "cpu": "2 vCPU", "ram": "8 GB", "status": "Paused", "progress": 34, "image": "Ubuntu 24.04 LTS", "sshKey": "operator@asterix"},
    {"name": "demo-k8s-01", "region": "us-central", "cpu": "12 vCPU", "ram": "48 GB", "status": "Ready", "progress": 91, "image": "Custom ISO", "sshKey": "ci-bot@dev"},
    {"name": "backup-vm-02", "region": "us-east", "cpu": "4 vCPU", "ram": "16 GB", "status": "Queued", "progress": 48, "image": "Debian 12", "sshKey": "new-key"}
]

KEY_CATALOG = [
    {"name": "operator@asterix", "fingerprint": "SHA256:tQx3Qf...7zM"},
    {"name": "ci-bot@dev", "fingerprint": "SHA256:6Vxy8K...pFO"},
    {"name": "edge-gateway", "fingerprint": "SHA256:Hmp9kL...Q1L"}
]

SNAPSHOT_CATALOG = [
    {"name": "prod-snapshot-01", "created": "2026-09-12 09:15", "size": "14 GB", "status": "Verified"},
    {"name": "edge-snapshot-02", "created": "2026-09-11 21:42", "size": "8 GB", "status": "Ready"},
    {"name": "sandbox-snapshot-04", "created": "2026-09-10 18:01", "size": "4 GB", "status": "Queued"}
]


def send_json(handler, status, payload):
    data = json.dumps(payload).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(data)))
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.end_headers()
    handler.wfile.write(data)


class AdminAPIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/admin':
            send_json(self, 200, {
                'vms': VM_CATALOG,
                'keys': KEY_CATALOG,
                'snapshots': SNAPSHOT_CATALOG
            })
            return
        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get('Content-Length', '0'))
        body = self.rfile.read(length).decode('utf-8') if length else '{}'

        try:
            payload = json.loads(body) if body else {}
        except json.JSONDecodeError:
            payload = {}

        if self.path.startswith('/api/vm/'):
            segments = self.path.split('/')
            if len(segments) >= 5 and segments[3] and segments[4] in {'start', 'stop', 'reboot'}:
                vm_name = segments[3]
                for vm in VM_CATALOG:
                    if vm['name'] == vm_name:
                        vm['status'] = {'start': 'Running', 'stop': 'Stopped', 'reboot': 'Rebooting'}[segments[4]]
                        vm['progress'] = {'start': 88, 'stop': 22, 'reboot': 66}[segments[4]]
                        break
                send_json(self, 200, {'vms': VM_CATALOG})
                return

        if self.path == '/api/snapshot':
            name = payload.get('name', f"snapshot-{len(SNAPSHOT_CATALOG) + 1}")
            created = payload.get('created', '2026-09-12 00:00')
            size = payload.get('size', '2 GB')
            status = payload.get('status', 'Queued')
            SNAPSHOT_CATALOG.insert(0, {'name': name, 'created': created, 'size': size, 'status': status})
            send_json(self, 201, {'snapshots': SNAPSHOT_CATALOG})
            return

        self.send_error(404)

    def do_DELETE(self):
        if self.path.startswith('/api/vm/'):
            vm_name = self.path.split('/')[3]
            VM_CATALOG[:] = [vm for vm in VM_CATALOG if vm['name'] != vm_name]
            send_json(self, 200, {'vms': VM_CATALOG})
            return

        if self.path.startswith('/api/snapshot/'):
            snapshot_name = self.path.split('/')[3]
            SNAPSHOT_CATALOG[:] = [snapshot for snapshot in SNAPSHOT_CATALOG if snapshot['name'] != snapshot_name]
            send_json(self, 200, {'snapshots': SNAPSHOT_CATALOG})
            return

        self.send_error(404)


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8765), AdminAPIHandler)
    print('ASTERIX admin API running on http://0.0.0.0:8765')
    server.serve_forever()
