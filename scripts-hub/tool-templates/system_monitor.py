#!/usr/bin/env python3
"""System monitor CLI tool template for ASTERIX AI training."""

import argparse
import json
import os
import time
from typing import Dict, List


def read_cpu_usage() -> Dict:
    try:
        with open('/proc/stat', 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('cpu '):
                    parts = line.split()
                    user = int(parts[1])
                    nice = int(parts[2])
                    system = int(parts[3])
                    idle = int(parts[4])
                    total = user + nice + system + idle
                    return {
                        'user': user,
                        'nice': nice,
                        'system': system,
                        'idle': idle,
                        'total': total,
                    }
    except Exception:
        return {}
    return {}


def read_memory_usage() -> Dict:
    mem = {}
    try:
        with open('/proc/meminfo', 'r', encoding='utf-8') as f:
            for line in f:
                key, value = line.split(':', 1)
                mem[key.strip()] = int(value.strip().split()[0])
    except Exception:
        return mem
    return mem


def list_processes() -> List[Dict]:
    processes = []
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue
        stat_path = f'/proc/{pid}/stat'
        try:
            with open(stat_path, 'r', encoding='utf-8') as f:
                data = f.read().split()
                if len(data) >= 22:
                    cmd = data[1].strip('()')
                    processes.append({'pid': int(pid), 'name': cmd, 'state': data[2]})
        except Exception:
            pass
    return processes


def build_report() -> Dict:
    return {
        'timestamp': time.time(),
        'cpu': read_cpu_usage(),
        'memory': read_memory_usage(),
        'processes': list_processes()[:20],
    }


def main():
    parser = argparse.ArgumentParser(description='Monitor Linux system health and running processes.')
    parser.add_argument('--json', action='store_true', help='print output as JSON')
    parser.add_argument('--interval', type=float, default=1.0, help='sleep interval between polls')
    parser.add_argument('--count', type=int, default=1, help='number of samples to print')
    args = parser.parse_args()

    for i in range(args.count):
        report = build_report()
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"Sample {i + 1}: {len(report['processes'])} processes active")
            print(f"Memory: {report['memory'].get('MemTotal', 0)} KB total")
        if i + 1 < args.count:
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
