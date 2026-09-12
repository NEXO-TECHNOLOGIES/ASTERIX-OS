#!/usr/bin/env python3
"""Build a small dashboard payload from host and VM data."""


def summarize(host_cpu, vms):
    total = sum(vm["cpu"] for vm in vms)
    avg = total / len(vms) if vms else 0
    return {
        "host_cpu": host_cpu,
        "vm_count": len(vms),
        "avg_vm_cpu": avg,
        "vms": vms,
    }


def main():
    payload = summarize(42, [
        {"name": "web-01", "cpu": 15},
        {"name": "db-01", "cpu": 25},
        {"name": "api-01", "cpu": 20},
    ])
    print(payload)


if __name__ == "__main__":
    main()
