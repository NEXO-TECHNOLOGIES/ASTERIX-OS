#!/usr/bin/env python3
"""Discover likely RTSP/ONVIF surveillance endpoints on the local network.

This helper is used when the user does not already know the IP of a monitoring
camera or stream endpoint. It inspects the local subnet for common surveillance
ports and reports likely hosts without requiring a manual target IP.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
from typing import Any, Dict, List, Tuple


DEFAULT_PORTS = [554, 8554, 8000, 8081, 8899, 3702, 80, 8080]


def local_ipv4() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def subnet_for_local_host(cidr_prefix: int = 24) -> str:
    ip = local_ipv4()
    try:
        return str(ipaddress.ip_network(f"{ip}/{cidr_prefix}", strict=False))
    except Exception:
        return "127.0.0.0/8"


def port_probe(host: str, port: int, timeout: float = 0.25) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((host, port))
            return True
    except Exception:
        return False


def rtsp_banner_probe(host: str, port: int, timeout: float = 0.8) -> Dict[str, Any]:
    payload = (
        b"OPTIONS rtsp://%s:%d RTSP/1.0\r\n"
        b"CSeq: 1\r\n"
        b"User-Agent: ASTERIX-ShadowCam/1.0\r\n\r\n"
    ) % (host.encode(), port)
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.settimeout(timeout)
            s.sendall(payload)
            data = s.recv(2048)
            text = data.decode("latin-1", errors="replace")
            return {"host": host, "port": port, "banner": text.strip(), "open": True}
    except Exception:
        return {"host": host, "port": port, "banner": "", "open": False}


def discover_hosts(subnet: str, ports: List[int] | None = None) -> Dict[str, Any]:
    ports = ports or DEFAULT_PORTS
    try:
        net = ipaddress.ip_network(subnet, strict=False)
    except ValueError:
        net = ipaddress.ip_network("127.0.0.0/8", strict=False)

    hits: List[Dict[str, Any]] = []
    for host_int in list(net.hosts())[:254]:
        host = str(host_int)
        if host.endswith(".1") and host.startswith("127."):
            continue
        open_ports: List[int] = []
        for port in ports:
            if port_probe(host, port, timeout=0.18):
                open_ports.append(port)
        if open_ports:
            details = {"host": host, "ports": open_ports, "likely_camera_or_stream": False}
            for port in open_ports:
                banner = rtsp_banner_probe(host, port)
                if banner["banner"]:
                    lower = banner["banner"].lower()
                    if "rtsp" in lower or "onvif" in lower or "server" in lower or "options" in lower:
                        details["likely_camera_or_stream"] = True
            hits.append(details)

    return {
        "subnet": str(net),
        "hosts": hits,
        "summary": f"Found {len(hits)} likely camera/stream endpoint(s) on subnet {net}",
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Discover RTSP/ONVIF surveillance devices on the local network")
    parser.add_argument("--subnet", type=str, help="Subnet to scan, such as 192.168.1.0/24")
    parser.add_argument("--cidr", type=int, default=24, help="CIDR prefix to use when subnet is not specified")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args()

    subnet = args.subnet or subnet_for_local_host(args.cidr)
    result = discover_hosts(subnet)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Scanning subnet: {result['subnet']}")
        if not result["hosts"]:
            print("No likely camera or stream endpoints were found.")
            return 0
        for host in result["hosts"]:
            print(f"{host['host']} -> ports {host['ports']}" )
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
