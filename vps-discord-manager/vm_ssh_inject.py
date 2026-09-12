#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
KEY_DIR = PROJECT_ROOT / "ssh-keys"


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    return result.returncode, stdout, stderr


def ensure_key(name):
    KEY_DIR.mkdir(parents=True, exist_ok=True)
    pub_path = KEY_DIR / f"{name}.pub"
    if not pub_path.exists():
        key_path = KEY_DIR / name
        code, out, err = run_command(["bash", "-lc", f"ssh-keygen -t ed25519 -N '' -f '{key_path}' >/dev/null 2>&1"])
        if code != 0:
            return 1, "", err or "Unable to generate SSH key."
        return 0, pub_path.read_text().strip(), ""
    return 0, pub_path.read_text().strip(), ""


def inject_key(vm_name, key_name):
    code, pubkey, err = ensure_key(key_name)
    if code != 0:
        return code, "", err

    user_data_path = PROJECT_ROOT / f"{vm_name}-user-data"
    if user_data_path.exists():
        existing = user_data_path.read_text()
        if pubkey in existing:
            return 0, f"Key already configured for {vm_name}.", ""

    shell_block = f"\n  - {pubkey}\n"
    payload = """
#cloud-config
users:
  - default
  - name: admin
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: [adm, sudo]
    lock_passwd: false
    ssh_authorized_keys:
      - {pubkey}
package_update: true
package_upgrade: true
packages:
  - curl
  - git
  - openssh-server
runcmd:
  - systemctl enable --now ssh
""".strip()

    user_data_path.write_text(payload + "\n")
    return 0, f"Injected key '{key_name}' into VM config for {vm_name}.", ""


def main():
    parser = argparse.ArgumentParser(description="Inject an SSH key into a VM cloud-init config")
    parser.add_argument("vm_name")
    parser.add_argument("key_name", nargs="?", default="default")
    args = parser.parse_args()

    code, out, err = inject_key(args.vm_name, args.key_name)
    if out:
        print(out)
    if err:
        print(err)
    return code


if __name__ == "__main__":
    sys.exit(main())
