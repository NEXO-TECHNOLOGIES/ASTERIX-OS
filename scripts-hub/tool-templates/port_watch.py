#!/usr/bin/env python3
"""CLI tool template to watch open ports and report changes."""

import argparse
import json
import socket
import time


def port_is_open(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def main():
    parser = argparse.ArgumentParser(description='Watch a port on a target host.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--interval', type=float, default=1.0)
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    for i in range(args.count):
        open_state = port_is_open(args.host, args.port)
        payload = {
            'host': args.host,
            'port': args.port,
            'open': open_state,
            'iteration': i + 1,
        }
        if args.json:
            print(json.dumps(payload))
        else:
            print(f"{args.host}:{args.port} -> {'OPEN' if open_state else 'CLOSED'}")
        if i + 1 < args.count:
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
