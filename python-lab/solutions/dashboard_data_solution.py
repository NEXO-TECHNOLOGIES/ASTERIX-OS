#!/usr/bin/env python3
"""Dashboard payload with safe averages and per-VM status."""


def summarize(host_cpu, vms):
    safe_vms = [vm for vm in vms if isinstance(vm, dict) and "cpu" in vm]
    total = sum(vm["cpu"] for vm in safe_vms)
    avg = total / len(safe_vms) if safe_vms else 0
    return {
        "host_cpu": host_cpu,
        "vm_count": len(safe_vms),
        "avg_vm_cpu": round(avg, 2),
        "vms": safe_vms,
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
