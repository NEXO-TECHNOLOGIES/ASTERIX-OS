#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Autonomous Attack Path Pathfinder & Surface DAG Synthesizer
  Tool: ax pathfinder / ax graph
  Version: 3.0.0
  Zero Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0

  Features:
    • Unified Data Model Ingestion: Ingests project.json (hosts, services, creds, findings)
    • Autonomous DAG Construction: Entry points, service bridges, cred pivots, crown jewels
    • Shortest Path Algorithm: Hop-optimized traversal to high-value assets
    • Lowest-Noise Algorithm: Dijkstra weighted by EDR/SIEM detection probability
    • Critical Chokepoint & Blast Radius Analysis: Identifies key pivot pivots
    • Standalone Interactive HTML/SVG Visualizer: Fully embedded dark-mode graph HUD
===============================================================================
"""

import os
import sys
import json
import time
import heapq
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple, Set

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

BANNER = f"""{C_CYAN}{C_BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║   ██████╗  █████╗ ████████╗██╗  ██╗███████╗██╗███╗   ██╗  ║
    ║   ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║██╔════╝██║████╗  ██║  ║
    ║   ██████╔╝███████║   ██║   ███████║█████╗  ██║██╔██╗ ██║  ║
    ║   ██╔═══╝ ██╔══██║   ██║   ██╔══██║██╔══╝  ██║██║╚██╗██║  ║
    ║   ██║     ██║  ██║   ██║   ██║  ██║██║     ██║██║ ╚████║  ║
    ║   ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝  ║
    ║     ATTACK PATH PATHFINDER & GRAPH SYNTHESIZER v3.0       ║
    ╚═══════════════════════════════════════════════════════════╝{C_RESET}
"""

class AttackGraph:
    """Directed Acyclic Graph modeling an attack surface and pivot relationships."""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.adjacency: Dict[str, List[Dict[str, Any]]] = {}

    def add_node(self, node_id: str, label: str, node_type: str, weight: float = 1.0, metadata: Optional[Dict[str, Any]] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "label": label,
                "type": node_type,  # entry, host, service, credential, finding, crown_jewel
                "weight": weight,
                "metadata": metadata or {}
            }
            self.adjacency[node_id] = []

    def add_edge(self, source: str, target: str, rel_type: str, cost: float = 1.0, noise: float = 2.0, description: str = ""):
        edge = {
            "source": source,
            "target": target,
            "relation": rel_type,
            "cost": cost,
            "noise": noise,
            "description": description
        }
        self.edges.append(edge)
        if source in self.adjacency:
            self.adjacency[source].append(edge)

    def compute_shortest_path(self, start_node: str, end_node: str) -> Optional[Tuple[List[str], float]]:
        """Dijkstra based on edge hop cost (shortest path)."""
        if start_node not in self.nodes or end_node not in self.nodes:
            return None

        distances = {nid: float("inf") for nid in self.nodes}
        previous = {nid: None for nid in self.nodes}
        distances[start_node] = 0.0

        pq = [(0.0, start_node)]

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            if curr_dist > distances[curr_node]:
                continue
            if curr_node == end_node:
                break

            for edge in self.adjacency.get(curr_node, []):
                neighbor = edge["target"]
                new_dist = curr_dist + edge["cost"]
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = curr_node
                    heapq.heappush(pq, (new_dist, neighbor))

        if distances[end_node] == float("inf"):
            return None

        path = []
        curr = end_node
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()
        return path, distances[end_node]

    def compute_lowest_noise_path(self, start_node: str, end_node: str) -> Optional[Tuple[List[str], float]]:
        """Dijkstra weighted by detection noise (stealthiest path)."""
        if start_node not in self.nodes or end_node not in self.nodes:
            return None

        noises = {nid: float("inf") for nid in self.nodes}
        previous = {nid: None for nid in self.nodes}
        noises[start_node] = 0.0

        pq = [(0.0, start_node)]

        while pq:
            curr_noise, curr_node = heapq.heappop(pq)
            if curr_noise > noises[curr_node]:
                continue
            if curr_node == end_node:
                break

            for edge in self.adjacency.get(curr_node, []):
                neighbor = edge["target"]
                new_noise = curr_noise + edge["noise"]
                if new_noise < noises[neighbor]:
                    noises[neighbor] = new_noise
                    previous[neighbor] = curr_node
                    heapq.heappush(pq, (new_noise, neighbor))

        if noises[end_node] == float("inf"):
            return None

        path = []
        curr = end_node
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()
        return path, noises[end_node]

    def find_chokepoints(self) -> List[Tuple[str, int]]:
        """Identifies nodes that appear most frequently on shortest paths between all entry points and crown jewels."""
        entry_nodes = [nid for nid, data in self.nodes.items() if data["type"] == "entry"]
        target_nodes = [nid for nid, data in self.nodes.items() if data["type"] == "crown_jewel"]

        node_appearance: Dict[str, int] = {nid: 0 for nid in self.nodes}

        for entry in entry_nodes:
            for target in target_nodes:
                res = self.compute_shortest_path(entry, target)
                if res:
                    path, _ = res
                    # Exclude start and end
                    for mid in path[1:-1]:
                        node_appearance[mid] = node_appearance.get(mid, 0) + 1

        sorted_chokepoints = sorted(node_appearance.items(), key=lambda x: x[1], reverse=True)
        return [cp for cp in sorted_chokepoints if cp[1] > 0]

    def calculate_blast_radius(self, node_id: str) -> List[str]:
        """Calculates all reachable downstream assets if a node is compromised."""
        visited = set()
        queue = [node_id]

        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                for edge in self.adjacency.get(curr, []):
                    nxt = edge["target"]
                    if nxt not in visited:
                        queue.append(nxt)

        visited.discard(node_id)
        return list(visited)


def build_graph_from_project(project_data: Dict[str, Any]) -> AttackGraph:
    """Constructs attack graph from unified ASTERIX project.json data model."""
    graph = AttackGraph()

    # Default external entry node
    entry_id = "attacker_entry"
    graph.add_node(entry_id, "External Attacker Entry", "entry", weight=0.0, metadata={"origin": "Internet / Perimeter"})

    hosts = project_data.get("hosts", [])
    credentials = project_data.get("credentials", [])
    findings = project_data.get("findings", [])

    # Map Hosts & Services
    for host in hosts:
        ip = host.get("ip", "unknown")
        hostname = host.get("hostname") or ip
        os_guess = host.get("os_guess", "Unknown OS")
        is_dc = "domain" in hostname.lower() or "dc" in hostname.lower() or "active" in os_guess.lower()
        is_db = "db" in hostname.lower() or "database" in hostname.lower() or "sql" in hostname.lower()
        
        host_type = "crown_jewel" if (is_dc or is_db) else "host"
        graph.add_node(ip, f"{hostname} ({ip})", host_type, metadata={"os": os_guess, "status": host.get("status", "up")})

        # Check for open ports
        ports = host.get("ports", [])
        for p in ports:
            port_num = p.get("port")
            service = p.get("service", "unknown")
            state = p.get("state", "open")
            if state != "open":
                continue

            service_node_id = f"{ip}:{port_num}"
            graph.add_node(service_node_id, f"{service.upper()} ({port_num}) on {ip}", "service", metadata=p)
            
            # Exposure edge
            if port_num in (80, 443, 8080, 8443, 22, 21, 25, 3389):
                # Publicly visible entry edge
                graph.add_edge(entry_id, service_node_id, "exposes", cost=1.0, noise=1.5, description="Perimeter exposed port")
            else:
                graph.add_edge(ip, service_node_id, "hosts_service", cost=0.5, noise=0.5, description="Host bound service")

            # Service gives access to host
            graph.add_edge(service_node_id, ip, "compromises_host", cost=1.5, noise=3.0, description="Service exploitation to shell")

    # Map Credentials
    for i, cred in enumerate(credentials):
        target = cred.get("target", "")
        user = cred.get("username", "user")
        ctype = cred.get("type", "plaintext")
        cred_id = f"cred_{i}_{user}"

        graph.add_node(cred_id, f"Cred: {user} ({ctype})", "credential", metadata=cred)

        # Edge from source host or finding to credential
        if target in graph.nodes:
            graph.add_edge(target, cred_id, "leaks_credential", cost=0.5, noise=1.0, description="Harvested credential")
        else:
            graph.add_edge(entry_id, cred_id, "initial_credential", cost=0.5, noise=1.0, description="Supplied auth material")

        # Edge from credential to target hosts where it can authenticate
        for h in hosts:
            hip = h.get("ip", "")
            # Low noise pivot via legitimate authentication
            graph.add_edge(cred_id, hip, "authenticates_to", cost=1.0, noise=1.0, description=f"Login as {user}")

    # Map Findings / Vulnerabilities
    for vuln in findings:
        vid = vuln.get("id", "vuln")
        title = vuln.get("title", "Finding")
        target = vuln.get("target", "")
        sev = vuln.get("severity", "medium").lower()

        # Weight and noise based on severity
        noise_map = {"critical": 2.5, "high": 4.0, "medium": 5.5, "low": 7.0, "info": 8.0}
        noise = noise_map.get(sev, 4.0)

        vuln_node_id = f"vuln_{vid}"
        graph.add_node(vuln_node_id, f"[{sev.upper()}] {title}", "finding", metadata=vuln)

        # Target links to vuln
        if target in graph.nodes:
            graph.add_edge(target, vuln_node_id, "has_vulnerability", cost=0.5, noise=1.0, description=f"CVE/Misconfig {vid}")
            # Vuln leads to elevated pivot on target or lateral crown jewel
            for h in hosts:
                hip = h.get("ip", "")
                if hip != target and ("domain" in h.get("hostname", "").lower() or sev == "critical"):
                    graph.add_edge(vuln_node_id, hip, "lateral_pivot", cost=2.0, noise=noise, description=f"Exploitation pivot via {vid}")

    return graph


def generate_demo_project() -> Dict[str, Any]:
    """Generates a realistic mock enterprise engagement for instant demonstration."""
    return {
        "engagement_id": "ENG-2026-DEMO",
        "client_name": "AeroSpace Global Systems",
        "mode": "engagement",
        "hosts": [
            {
                "ip": "198.51.100.10",
                "hostname": "web-edge-01.aerospace.internal",
                "os_guess": "Ubuntu Linux 22.04 LTS",
                "status": "up",
                "ports": [
                    {"port": 80, "proto": "tcp", "state": "open", "service": "http", "product": "nginx", "version": "1.24.0"},
                    {"port": 443, "proto": "tcp", "state": "open", "service": "https", "product": "nginx", "version": "1.24.0"},
                    {"port": 22, "proto": "tcp", "state": "open", "service": "ssh", "product": "OpenSSH", "version": "8.9"}
                ]
            },
            {
                "ip": "10.0.10.25",
                "hostname": "app-internal-node.aerospace.internal",
                "os_guess": "Debian Linux 12",
                "status": "up",
                "ports": [
                    {"port": 8080, "proto": "tcp", "state": "open", "service": "http-proxy", "product": "Tomcat", "version": "9.0"},
                    {"port": 22, "proto": "tcp", "state": "open", "service": "ssh", "product": "OpenSSH", "version": "9.2"}
                ]
            },
            {
                "ip": "10.0.20.5",
                "hostname": "corp-dc-01.aerospace.internal",
                "os_guess": "Windows Server 2022 Datacenter",
                "status": "up",
                "ports": [
                    {"port": 88, "proto": "tcp", "state": "open", "service": "kerberos", "product": "Microsoft Windows Kerberos"},
                    {"port": 389, "proto": "tcp", "state": "open", "service": "ldap", "product": "Active Directory LDAP"},
                    {"port": 445, "proto": "tcp", "state": "open", "service": "microsoft-ds", "product": "SMB"},
                    {"port": 3389, "proto": "tcp", "state": "open", "service": "ms-wbt-server", "product": "RDP"}
                ]
            },
            {
                "ip": "10.0.30.12",
                "hostname": "vault-db-prod.aerospace.internal",
                "os_guess": "Red Hat Enterprise Linux 9",
                "status": "up",
                "ports": [
                    {"port": 5432, "proto": "tcp", "state": "open", "service": "postgresql", "product": "PostgreSQL", "version": "15.3"},
                    {"port": 22, "proto": "tcp", "state": "open", "service": "ssh", "product": "OpenSSH", "version": "9.0"}
                ]
            }
        ],
        "credentials": [
            {
                "target": "198.51.100.10",
                "service": "ssh",
                "username": "deploy_user",
                "type": "plaintext",
                "hash_or_secret": "******"
            },
            {
                "target": "10.0.10.25",
                "service": "kerberos",
                "username": "svc_ad_sync",
                "type": "ntlm",
                "hash_or_secret": "aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0"
            }
        ],
        "findings": [
            {
                "id": "SEC-001",
                "title": "Reverse Proxy SSRF to Internal Cloud Metadata",
                "severity": "high",
                "target": "198.51.100.10:443",
                "cve": "CVE-2024-1182",
                "cvss_score": 8.6
            },
            {
                "id": "SEC-002",
                "title": "Unconstrained Kerberos Delegation on AD Sync Service",
                "severity": "critical",
                "target": "10.0.10.25",
                "cve": "CVE-2023-38146",
                "cvss_score": 9.8
            }
        ]
    }


def render_html_graph(graph: AttackGraph, shortest_path: Optional[List[str]], lowest_noise_path: Optional[List[str]], output_path: str):
    """Generates an embedded, zero-dependency interactive dark-mode HTML/SVG attack graph report."""
    nodes_json = json.dumps(graph.nodes)
    edges_json = json.dumps(graph.edges)
    sp_json = json.dumps(shortest_path or [])
    lp_json = json.dumps(lowest_noise_path or [])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ASTERIX OS — Autonomous Attack Path Pathfinder</title>
<style>
  :root {{
    --bg: #090d13;
    --card: #121824;
    --border: #233044;
    --cyan: #00f0ff;
    --green: #00ff9d;
    --pink: #ff0055;
    --yellow: #ffb800;
    --text: #e2e8f0;
    --muted: #64748b;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; }}
  body {{ background: var(--bg); color: var(--text); display: flex; flex-direction: column; height: 100vh; overflow: hidden; }}
  header {{
    background: var(--card);
    border-bottom: 1px solid var(--border);
    padding: 14px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .logo {{ font-size: 18px; font-weight: bold; color: var(--cyan); letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }}
  .badge {{ font-size: 11px; padding: 3px 8px; border-radius: 4px; background: rgba(0,240,255,0.15); color: var(--cyan); border: 1px solid var(--cyan); }}
  .controls {{ display: flex; gap: 10px; }}
  button {{
    background: #1a2333;
    color: var(--text);
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.2s;
  }}
  button:hover {{ border-color: var(--cyan); color: var(--cyan); }}
  button.active {{ background: rgba(0,240,255,0.2); border-color: var(--cyan); color: var(--cyan); }}
  .main-container {{ display: flex; flex: 1; position: relative; overflow: hidden; }}
  #graph-canvas {{ flex: 1; width: 100%; height: 100%; cursor: grab; background: radial-gradient(circle at 50% 50%, #111a28 0%, #090d13 100%); }}
  #graph-canvas:active {{ cursor: grabbing; }}
  .sidebar {{
    width: 360px;
    background: var(--card);
    border-left: 1px solid var(--border);
    padding: 20px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}
  .card {{
    background: #0d121c;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 14px;
  }}
  .card h3 {{ font-size: 13px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; letter-spacing: 0.5px; }}
  .node-title {{ font-size: 16px; font-weight: bold; color: var(--cyan); margin-bottom: 6px; }}
  .tag {{ display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; text-transform: uppercase; margin-bottom: 10px; }}
  .tag-entry {{ background: rgba(0,240,255,0.2); color: var(--cyan); }}
  .tag-host {{ background: rgba(100,116,139,0.3); color: #cbd5e1; }}
  .tag-service {{ background: rgba(255,184,0,0.2); color: var(--yellow); }}
  .tag-credential {{ background: rgba(0,255,157,0.2); color: var(--green); }}
  .tag-finding {{ background: rgba(255,0,85,0.2); color: var(--pink); }}
  .tag-crown_jewel {{ background: rgba(255,0,85,0.3); color: #ff3377; border: 1px solid #ff0055; }}
  .kv {{ display: flex; justify-content: space-between; font-size: 13px; padding: 4px 0; border-bottom: 1px solid #1a2333; }}
  .kv span:first-child {{ color: var(--muted); }}
  .path-legend {{ display: flex; flex-direction: column; gap: 8px; font-size: 13px; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; }}
</style>
</head>
<body>

<header>
  <div class="logo">
    <span>🕸️ ASTERIX OS</span>
    <span class="badge">PATHFINDER v3.0</span>
  </div>
  <div class="controls">
    <button id="btn-shortest" class="active" onclick="setHighlight('shortest')">⚡ Shortest Path</button>
    <button id="btn-stealth" onclick="setHighlight('stealth')">👻 Lowest Noise (Stealth)</button>
    <button id="btn-all" onclick="setHighlight('all')">🌐 Full Attack Surface</button>
    <button onclick="resetView()">🎯 Center HUD</button>
  </div>
</header>

<div class="main-container">
  <canvas id="graph-canvas"></canvas>
  <div class="sidebar">
    <div class="card">
      <h3>Active Objective</h3>
      <div id="objective-info">
        <div style="font-weight:bold; color:var(--text); margin-bottom:4px;">Target Crown Jewels</div>
        <div style="font-size:12px; color:var(--muted);">Domain Controller / Vault Database</div>
      </div>
    </div>

    <div class="card">
      <h3>Path Legend</h3>
      <div class="path-legend">
        <div class="legend-item"><div class="legend-dot" style="background:var(--cyan);"></div><span>Shortest Path (Fewest Hops)</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--green);"></div><span>Lowest Noise (Stealth Credential Pivot)</span></div>
        <div class="legend-item"><div class="legend-dot" style="background:var(--pink);"></div><span>Crown Jewel Assets</span></div>
      </div>
    </div>

    <div class="card" id="details-card">
      <h3>Node Telemetry</h3>
      <div id="details-content">
        <div style="color:var(--muted); font-size:13px;">Click on any node in the canvas to inspect attack vector attributes and pivot relations.</div>
      </div>
    </div>
  </div>
</div>

<script>
const nodes = {nodes_json};
const edges = {edges_json};
const shortestPath = {sp_json};
const lowestNoisePath = {lp_json};

let activeMode = 'shortest';
let selectedNode = null;

const canvas = document.getElementById('graph-canvas');
const ctx = canvas.getContext('2d');

let width, height;
let panX = 0, panY = 0, zoom = 1;
let isDragging = false, dragStart = {{ x: 0, y: 0 }};

// Simulation Layout Positions
const positions = {{}};
const nodeKeys = Object.keys(nodes);

function initLayout() {{
  const total = nodeKeys.length;
  const radius = Math.min(width, height) * 0.35;
  const cx = width / 2;
  const cy = height / 2;

  // Circular / layered layout
  nodeKeys.forEach((key, idx) => {{
    const type = nodes[key].type;
    let x, y;
    if (type === 'entry') {{
      x = cx - radius * 1.2;
      y = cy;
    }} else if (type === 'crown_jewel') {{
      x = cx + radius * 1.2;
      y = cy + (idx % 2 === 0 ? -60 : 60);
    }} else if (type === 'credential') {{
      x = cx;
      y = cy - radius * 0.7;
    }} else if (type === 'finding') {{
      x = cx;
      y = cy + radius * 0.7;
    }} else {{
      const angle = (idx / total) * Math.PI * 2;
      x = cx + Math.cos(angle) * radius * 0.7;
      y = cy + Math.sin(angle) * radius * 0.7;
    }}
    positions[key] = {{ x, y, vx: 0, vy: 0 }};
  }});
}}

function resize() {{
  width = canvas.width = canvas.parentElement.clientWidth;
  height = canvas.height = canvas.parentElement.clientHeight;
  if (Object.keys(positions).length === 0) {{
    initLayout();
  }}
  draw();
}}

window.addEventListener('resize', resize);

function getNodeColor(type) {{
  switch (type) {{
    case 'entry': return '#00f0ff';
    case 'crown_jewel': return '#ff0055';
    case 'credential': return '#00ff9d';
    case 'finding': return '#ff3366';
    case 'service': return '#ffb800';
    default: return '#64748b';
  }}
}}

function isEdgeInActivePath(src, dst) {{
  const activePath = activeMode === 'shortest' ? shortestPath : (activeMode === 'stealth' ? lowestNoisePath : null);
  if (!activePath) return false;
  for (let i = 0; i < activePath.length - 1; i++) {{
    if (activePath[i] === src && activePath[i+1] === dst) return true;
  }}
  return false;
}}

function isNodeInActivePath(nid) {{
  const activePath = activeMode === 'shortest' ? shortestPath : (activeMode === 'stealth' ? lowestNoisePath : null);
  if (!activePath) return true;
  return activePath.includes(nid);
}}

function draw() {{
  ctx.clearRect(0, 0, width, height);
  ctx.save();
  ctx.translate(panX, panY);
  ctx.scale(zoom, zoom);

  // Draw Edges
  edges.forEach(edge => {{
    const p1 = positions[edge.source];
    const p2 = positions[edge.target];
    if (!p1 || !p2) return;

    const inPath = isEdgeInActivePath(edge.source, edge.target);
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);

    if (inPath) {{
      ctx.strokeStyle = activeMode === 'shortest' ? '#00f0ff' : '#00ff9d';
      ctx.lineWidth = 3.5;
      ctx.shadowColor = ctx.strokeStyle;
      ctx.shadowBlur = 8;
    }} else {{
      ctx.strokeStyle = activeMode === 'all' ? 'rgba(100, 116, 139, 0.4)' : 'rgba(100, 116, 139, 0.15)';
      ctx.lineWidth = 1;
      ctx.shadowBlur = 0;
    }}
    ctx.stroke();
    ctx.shadowBlur = 0;
  }});

  // Draw Nodes
  nodeKeys.forEach(nid => {{
    const node = nodes[nid];
    const pos = positions[nid];
    if (!pos) return;

    const inPath = isNodeInActivePath(nid);
    const isSelected = selectedNode === nid;
    const baseColor = getNodeColor(node.type);

    ctx.beginPath();
    const r = node.type === 'crown_jewel' ? 18 : (node.type === 'entry' ? 16 : 12);
    ctx.arc(pos.x, pos.y, r, 0, Math.PI * 2);

    ctx.fillStyle = isSelected ? '#ffffff' : (inPath ? baseColor : 'rgba(100,116,139,0.3)');
    if (inPath || isSelected) {{
      ctx.shadowColor = baseColor;
      ctx.shadowBlur = isSelected ? 16 : 10;
    }} else {{
      ctx.shadowBlur = 0;
    }}
    ctx.fill();
    ctx.shadowBlur = 0;

    // Border
    ctx.strokeStyle = '#090d13';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Text Label
    ctx.fillStyle = inPath ? '#e2e8f0' : 'rgba(148, 163, 184, 0.4)';
    ctx.font = '11px Segoe UI, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(node.label, pos.x, pos.y + r + 14);
  }});

  ctx.restore();
}}

function setHighlight(mode) {{
  activeMode = mode;
  document.getElementById('btn-shortest').classList.toggle('active', mode === 'shortest');
  document.getElementById('btn-stealth').classList.toggle('active', mode === 'stealth');
  document.getElementById('btn-all').classList.toggle('active', mode === 'all');
  draw();
}}

function resetView() {{
  panX = 0;
  panY = 0;
  zoom = 1;
  draw();
}}

canvas.addEventListener('mousedown', e => {{
  isDragging = true;
  dragStart = {{ x: e.clientX - panX, y: e.clientY - panY }};

  // Node selection check
  const rect = canvas.getBoundingClientRect();
  const mouseX = (e.clientX - rect.left - panX) / zoom;
  const mouseY = (e.clientY - rect.top - panY) / zoom;

  let clicked = null;
  nodeKeys.forEach(nid => {{
    const pos = positions[nid];
    if (pos) {{
      const dist = Math.hypot(pos.x - mouseX, pos.y - mouseY);
      if (dist <= 20) clicked = nid;
    }}
  }});

  if (clicked) {{
    selectedNode = clicked;
    updateSidebar(nodes[clicked]);
  }}
  draw();
}});

window.addEventListener('mousemove', e => {{
  if (isDragging) {{
    panX = e.clientX - dragStart.x;
    panY = e.clientY - dragStart.y;
    draw();
  }}
}});

window.addEventListener('mouseup', () => {{ isDragging = false; }});
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
  zoom = Math.min(Math.max(0.3, zoom * zoomFactor), 3);
  draw();
}});

function updateSidebar(node) {{
  const detailsDiv = document.getElementById('details-content');
  let metaRows = '';
  for (const [k, v] of Object.entries(node.metadata || {{}})) {{
    metaRows += `<div class="kv"><span>${{k}}</span><span>${{typeof v === 'object' ? JSON.stringify(v) : v}}</span></div>`;
  }}

  detailsDiv.innerHTML = `
    <div class="node-title">${{node.label}}</div>
    <div class="tag tag-${{node.type}}">${{node.type}}</div>
    <div class="kv"><span>Identifier</span><span><code>${{node.id}}</code></span></div>
    <div class="kv"><span>Path Weight</span><span>${{node.weight}}</span></div>
    <div style="margin-top:12px; font-weight:bold; font-size:12px; color:var(--muted); text-transform:uppercase;">Attributes</div>
    ${{metaRows || '<div style="color:var(--muted); font-size:12px; margin-top:4px;">No custom attributes.</div>'}}
  `;
}}

resize();
</script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(description="ASTERIX OS Attack Path Pathfinder & Attack Surface Graph Synthesizer")
    parser.add_argument("command", nargs="?", default="demo", choices=["analyze", "paths", "chokepoints", "export-html", "demo"],
                        help="Action to perform (default: demo)")
    parser.add_argument("--project", "-p", default=None, help="Path to project.json file (default: active engagement or demo)")
    parser.add_argument("--export-html", "-o", default=None, help="File path to export interactive HTML visualizer")
    parser.add_argument("--crown-jewel", "-c", default=None, help="Target crown jewel node ID to compute path towards")

    args = parser.parse_args()

    print(BANNER)

    # Load Project Data
    project_data = None
    if args.project and os.path.exists(args.project):
        try:
            with open(args.project, "r", encoding="utf-8") as f:
                project_data = json.load(f)
            print(f"{C_GREEN}[+] Loaded project engagement data from: {args.project}{C_RESET}")
        except Exception as e:
            print(f"{C_RED}[!] Error reading {args.project}: {e}{C_RESET}")
            sys.exit(1)
    else:
        # Check if active engagement exists
        active_proj = os.path.expanduser("~/.asterix/engagements/active/project.json")
        if os.path.exists(active_proj):
            with open(active_proj, "r", encoding="utf-8") as f:
                project_data = json.load(f)
            print(f"{C_GREEN}[+] Loaded active engagement workspace: {active_proj}{C_RESET}")
        else:
            print(f"{C_YELLOW}[*] No active engagement specified. Initializing High-Fidelity Enterprise Demo Topology...{C_RESET}")
            project_data = generate_demo_project()

    # Construct DAG
    graph = build_graph_from_project(project_data)

    entry_nodes = [nid for nid, d in graph.nodes.items() if d["type"] == "entry"]
    cj_nodes = [nid for nid, d in graph.nodes.items() if d["type"] == "crown_jewel"]

    target_cj = args.crown_jewel or (cj_nodes[0] if cj_nodes else None)
    start_entry = entry_nodes[0] if entry_nodes else None

    # Compute paths
    shortest_path, sp_dist = (None, 0.0)
    lowest_noise_path, ln_noise = (None, 0.0)

    if start_entry and target_cj:
        res_sp = graph.compute_shortest_path(start_entry, target_cj)
        if res_sp:
            shortest_path, sp_dist = res_sp

        res_ln = graph.compute_lowest_noise_path(start_entry, target_cj)
        if res_ln:
            lowest_noise_path, ln_noise = res_ln

    if args.command in ("analyze", "demo"):
        print(f"\n{C_CYAN}{C_BOLD}[*] ATTACK SURFACE TOPOLOGY SYNTHESIS{C_RESET}")
        print(f"  • Total Surface Nodes:   {C_BOLD}{len(graph.nodes)}{C_RESET}")
        print(f"  • Directed Traversal Edges: {C_BOLD}{len(graph.edges)}{C_RESET}")
        print(f"  • Perimeter Entry Points: {C_BOLD}{len(entry_nodes)}{C_RESET}")
        print(f"  • Target Crown Jewels:    {C_BOLD}{len(cj_nodes)}{C_RESET}")

        print(f"\n{C_YELLOW}{C_BOLD}[+] IDENTIFIED CROWN JEWELS & OBJECTIVES:{C_RESET}")
        for cj in cj_nodes:
            meta = graph.nodes[cj].get("metadata", {})
            print(f"    🎯 {C_BOLD}{graph.nodes[cj]['label']}{C_RESET} (OS: {meta.get('os', 'N/A')})")

    if args.command in ("paths", "demo"):
        print(f"\n{C_CYAN}{C_BOLD}[*] COMPUTED ATTACK VECTOR TRAVERSALS:{C_RESET}")
        if shortest_path:
            print(f"\n  {C_CYAN}{C_BOLD}⚡ SHORTEST ATTACK PATH (Hops: {len(shortest_path)-1}, Cost: {sp_dist:.1f}){C_RESET}")
            for idx, nid in enumerate(shortest_path):
                arrow = " ──▶ " if idx < len(shortest_path) - 1 else ""
                print(f"    [{idx}] {graph.nodes[nid]['label']}{arrow}")
        else:
            print(f"  {C_YELLOW}[!] No direct path found to {target_cj}{C_RESET}")

        if lowest_noise_path:
            print(f"\n  {C_GREEN}{C_BOLD}👻 LOWEST-NOISE STEALTH PATH (Detection Noise Score: {ln_noise:.1f}){C_RESET}")
            for idx, nid in enumerate(lowest_noise_path):
                arrow = " ──▶ " if idx < len(lowest_noise_path) - 1 else ""
                print(f"    [{idx}] {graph.nodes[nid]['label']}{arrow}")

    if args.command in ("chokepoints", "demo"):
        chokepoints = graph.find_chokepoints()
        print(f"\n{C_MAGENTA}{C_BOLD}[*] CRITICAL NETWORK CHOKEPOINTS (High-Value Pivot Targets):{C_RESET}")
        if chokepoints:
            for nid, count in chokepoints[:5]:
                print(f"    🛡️  {C_BOLD}{graph.nodes[nid]['label']}{C_RESET} (Intersected in {count} optimal traversals)")
        else:
            print(f"    {C_DIM}None detected.{C_RESET}")

    # Export HTML
    out_html = args.export_html or ("reports/attack_path_graph.html" if args.command == "export-html" or args.command == "demo" else None)
    if out_html:
        render_html_graph(graph, shortest_path, lowest_noise_path, out_html)
        print(f"\n{C_GREEN}{C_BOLD}[✓] Exported Interactive Cyber Attack Graph Visualizer:{C_RESET}")
        print(f"    📄 {os.path.abspath(out_html)}")


if __name__ == "__main__":
    main()
