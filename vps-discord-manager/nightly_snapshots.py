#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    return result.returncode, stdout, stderr


def main():
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    code, out, err = run_command(["bash", "-lc", "virsh list --name --state-running 2>/dev/null || true"])
    if code != 0 and not out:
        print(err or "Unable to list running VMs.")
        return 1

    names = [line.strip() for line in out.splitlines() if line.strip()]
    if not names:
        print("No running VMs found. No nightly snapshot created.")
        return 0

    for name in names:
        label = f"nightly-{stamp}"
        snapshot_cmd = [
            "bash",
            "-lc",
            f"virsh snapshot-create-as --domain {name} --name {label} --description 'Nightly snapshot {stamp}' 2>&1 || true",
        ]
        snap_code, snap_out, snap_err = run_command(snapshot_cmd)
        payload = snap_out or snap_err or "snapshot created"
        print(f"{name}: {payload}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
