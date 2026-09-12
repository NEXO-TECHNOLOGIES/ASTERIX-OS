#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import nightly_snapshots
import vm_ssh_inject

PROJECT_ROOT = Path(__file__).resolve().parent
CREATE_SCRIPT = PROJECT_ROOT / "create-vps.sh"
KEY_DIR = PROJECT_ROOT / "ssh-keys"
BACKUP_DIR = PROJECT_ROOT / "backups"
SNAPSHOT_DIR = PROJECT_ROOT / "snapshots"
LOG_DIR = PROJECT_ROOT / "logs"


def ensure_project_dirs():
    for directory in (KEY_DIR, BACKUP_DIR, SNAPSHOT_DIR, LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def run_command(command):
    result = subprocess.run(command, capture_output=True, text=True)
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    return result.returncode, stdout, stderr


def list_vms():
    return run_command(["bash", "-lc", "virsh list --all"])


def get_vm_status(name):
    return run_command(["bash", "-lc", f"virsh dominfo {name} 2>&1 || virsh list --all | grep {name} || true"])


def get_vm_ip(name):
    code, out, err = run_command(["bash", "-lc", f"virsh domifaddr {name} 2>&1 || true"])
    if out:
        return out.strip()
    return err.strip() or "IP not available yet"


def create_vm(name, cpu, ram, disk):
    if not CREATE_SCRIPT.exists():
        return 1, "", f"VM creation script not found: {CREATE_SCRIPT}"
    return run_command(["bash", str(CREATE_SCRIPT), name, str(cpu), str(ram), str(disk)])


def start_vm(name):
    return run_command(["bash", "-lc", f"virsh start {name} 2>&1 || true"])


def stop_vm(name):
    return run_command(["bash", "-lc", f"virsh shutdown {name} 2>/dev/null || virsh destroy {name} 2>&1 || true"])


def restart_vm(name):
    return run_command(["bash", "-lc", f"virsh reboot {name} 2>&1 || true"])


def destroy_vm(name):
    return run_command(["bash", "-lc", f"virsh destroy {name} >/dev/null 2>&1 || true; virsh undefine {name} --remove-all-storage >/dev/null 2>&1 || true; virsh list --all | grep {name} || true"])


def ssh_command(name):
    _, out, err = get_vm_ip(name)
    if "IP not available yet" in out or not out:
        return 1, "", f"No IP available for {name} yet. Wait a moment and run status again."
    ip = out.splitlines()[-1].split()[-1] if out and out.splitlines()[-1].split() else None
    if not ip:
        return 1, "", f"Unable to determine IP for {name}."
    return 0, f"ssh admin@{ip}", ""


def vm_logs(name):
    code, out, err = run_command(["bash", "-lc", f"virsh dominfo {name} 2>&1 || true; echo '---'; virsh domifaddr {name} 2>&1 || true"])
    return code, out or err, ""


def host_info():
    checks = [
        ["bash", "-lc", "uname -a"],
        ["bash", "-lc", "cat /etc/os-release 2>/dev/null || lsb_release -a 2>/dev/null || true"],
        ["bash", "-lc", "uptime"],
        ["bash", "-lc", "free -m"],
        ["bash", "-lc", "df -h /"],
        ["bash", "-lc", "lsblk 2>/dev/null || true"],
        ["bash", "-lc", "systemctl is-active libvirtd 2>/dev/null || true"],
    ]
    sections = []
    for cmd in checks:
        code, out, err = run_command(cmd)
        body = out or err or "No data available"
        sections.append(body)
    return "\n\n---\n\n".join(sections)


def dashboard():
    ensure_project_dirs()
    code, out, err = list_vms()
    content = out or err or "No VMs found."
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    entries = []
    for line in lines:
        if line.lower().startswith("id") or line.startswith("---") or line.startswith("Name"):
            continue
        if not line:
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        vm_name = parts[1] if parts[0].isdigit() else parts[0]
        status_line = get_vm_status(vm_name)[1]
        ip_line = get_vm_ip(vm_name)
        state = "running" if "running" in status_line.lower() else "stopped"
        entries.append(f"[{vm_name}] state={state} | ip={ip_line if ip_line and 'IP not available yet' not in ip_line else 'pending'}")

    if not entries:
        return "No VMs found."
    return "\n".join(entries)


def ssh_key_manage(args):
    ensure_project_dirs()
    if args.subcommand == "list":
        files = sorted(KEY_DIR.glob("*.pub"))
        if not files:
            return 0, "No SSH keys registered.", ""
        return 0, "\n".join(str(p.name) for p in files), ""

    if args.subcommand == "generate":
        name = args.name
        key_path = KEY_DIR / name
        if key_path.exists() or (key_path.with_suffix(".pub")).exists():
            return 1, "", f"A key named {name} already exists."
        code, out, err = run_command(["bash", "-lc", f"ssh-keygen -t ed25519 -N '' -f '{key_path}' >/dev/null 2>&1"]) 
        pub = key_path.with_suffix(".pub")
        if pub.exists():
            return code, f"Generated SSH key: {pub.name}", err
        return code, out, err or "Unable to generate key."

    if args.subcommand == "show":
        key_file = KEY_DIR / f"{args.name}.pub"
        if not key_file.exists():
            return 1, "", f"Key not found: {args.name}"
        return 0, key_file.read_text().strip(), ""

    if args.subcommand == "add":
        source = Path(args.source)
        if not source.exists():
            return 1, "", f"Source key file not found: {source}"
        target = KEY_DIR / f"{args.name}.pub"
        target.write_text(source.read_text().strip() + "\n")
        return 0, f"Added key for {args.name}.", ""

    if args.subcommand == "remove":
        target = KEY_DIR / f"{args.name}.pub"
        if target.exists():
            target.unlink()
        private_key = KEY_DIR / args.name
        if private_key.exists():
            private_key.unlink()
        return 0, f"Removed key entry for {args.name}.", ""

    return 1, "", "Unsupported SSH key command."


def snapshot_manage(args):
    ensure_project_dirs()
    if args.subcommand == "create":
        label = args.label or f"{args.name}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        return run_command(["bash", "-lc", f"virsh snapshot-create-as --domain {args.name} --name {label} --description 'ASTERIX snapshot created {datetime.utcnow().isoformat()}' 2>&1 || true"])

    if args.subcommand == "list":
        return run_command(["bash", "-lc", f"virsh snapshot-list {args.name} 2>&1 || true"])

    if args.subcommand == "delete":
        if not args.label:
            return 1, "", "Please specify a snapshot name. Example: snapshot delete my-vm snap-1"
        return run_command(["bash", "-lc", f"virsh snapshot-delete --domain {args.name} --snapshotname {args.label} 2>&1 || true"])

    if args.subcommand == "cleanup":
        cleaned = []
        for folder in (BACKUP_DIR, SNAPSHOT_DIR, LOG_DIR):
            code, out, err = run_command(["bash", "-lc", f"find '{folder}' -type f -mtime +7 -delete 2>/dev/null || true"])
            cleaned.append(f"{folder}: {'ok' if code == 0 else 'warning'}")
        return 0, "\n".join(cleaned), ""

    return 1, "", "Unsupported snapshot subcommand."


def cleanup_manage(args):
    ensure_project_dirs()
    target = (args.target or "all").lower()
    if target in {"all", "backups"}:
        run_command(["bash", "-lc", f"find '{BACKUP_DIR}' -type f -mtime +7 -delete 2>/dev/null || true"])
    if target in {"all", "snapshots"}:
        run_command(["bash", "-lc", f"find '{SNAPSHOT_DIR}' -type f -mtime +7 -delete 2>/dev/null || true"])
    if target in {"all", "logs"}:
        run_command(["bash", "-lc", f"find '{LOG_DIR}' -type f -mtime +14 -delete 2>/dev/null || true"])
    return 0, f"Cleanup finished for target: {target}", ""


def build_parser():
    parser = argparse.ArgumentParser(description="ASTERIX VPS admin CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all VMs")
    subparsers.add_parser("help", help="Print help")
    subparsers.add_parser("dashboard", help="Show a compact VM dashboard")
    subparsers.add_parser("host-info", help="Display host resource information")

    create = subparsers.add_parser("create", help="Create a new VM")
    create.add_argument("name")
    create.add_argument("cpu", nargs="?", default="2")
    create.add_argument("ram", nargs="?", default="4096")
    create.add_argument("disk", nargs="?", default="40")

    status = subparsers.add_parser("status", help="Show VM details")
    status.add_argument("name")

    for action in ("start", "stop", "restart", "destroy"):
        item = subparsers.add_parser(action, help=f"{action.title()} a VM")
        item.add_argument("name")

    ssh = subparsers.add_parser("ssh", help="Get SSH command for a VM")
    ssh.add_argument("name")

    logs = subparsers.add_parser("logs", help="Show VM summary/log info")
    logs.add_argument("name")

    ssh_key = subparsers.add_parser("ssh-key", help="Manage SSH keys")
    ssh_key_sub = ssh_key.add_subparsers(dest="subcommand", required=True)
    ssh_key_sub.add_parser("list", help="List registered SSH keys")
    gen = ssh_key_sub.add_parser("generate", help="Generate an SSH key")
    gen.add_argument("name")
    show = ssh_key_sub.add_parser("show", help="Show a registered SSH key")
    show.add_argument("name")
    add = ssh_key_sub.add_parser("add", help="Register an existing public key")
    add.add_argument("name")
    add.add_argument("source")
    remove = ssh_key_sub.add_parser("remove", help="Remove a registered SSH key")
    remove.add_argument("name")

    snapshot = subparsers.add_parser("snapshot", help="Manage VM snapshots")
    snapshot_sub = snapshot.add_subparsers(dest="subcommand", required=True)
    snap_create = snapshot_sub.add_parser("create", help="Create a VM snapshot")
    snap_create.add_argument("name")
    snap_create.add_argument("label", nargs="?", default=None)
    snap_list = snapshot_sub.add_parser("list", help="List VM snapshots")
    snap_list.add_argument("name")
    snap_delete = snapshot_sub.add_parser("delete", help="Delete a VM snapshot")
    snap_delete.add_argument("name")
    snap_delete.add_argument("label")
    snapshot_sub.add_parser("cleanup", help="Clean old snapshot data")

    cleanup = subparsers.add_parser("cleanup", help="Clean stale backups, snapshots, or logs")
    cleanup.add_argument("target", nargs="?", default="all")

    snapshot_job = subparsers.add_parser("nightly-snapshot", help="Create nightly snapshots for all running VMs")

    key_inject = subparsers.add_parser("inject-key", help="Inject an SSH key into a VM config")
    key_inject.add_argument("vm_name")
    key_inject.add_argument("key_name", nargs="?", default="default")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return 0

    if args.command == "list":
        code, out, err = list_vms()
        print(out or err or "No VMs found.")
        return code

    if args.command == "dashboard":
        print(dashboard())
        return 0

    if args.command == "host-info":
        print(host_info())
        return 0

    if args.command == "create":
        code, out, err = create_vm(args.name, args.cpu, args.ram, args.disk)
        print(out or err or "Creation process initiated.")
        return code

    if args.command == "status":
        code, out, err = get_vm_status(args.name)
        ip_info = get_vm_ip(args.name)
        print((out or err or "VM not found.") + (f"\n---\n{ip_info}" if ip_info else ""))
        return code

    if args.command == "start":
        code, out, err = start_vm(args.name)
        print(out or err or f"VM {args.name} started.")
        return code

    if args.command == "stop":
        code, out, err = stop_vm(args.name)
        print(out or err or f"VM {args.name} stopped.")
        return code

    if args.command == "restart":
        code, out, err = restart_vm(args.name)
        print(out or err or f"VM {args.name} restarted.")
        return code

    if args.command == "destroy":
        code, out, err = destroy_vm(args.name)
        print(out or err or f"VM {args.name} destroyed.")
        return code

    if args.command == "ssh":
        code, out, err = ssh_command(args.name)
        if code == 0:
            print(out)
        else:
            print(err)
        return code

    if args.command == "logs":
        code, out, err = vm_logs(args.name)
        print(out or err or f"No log data for {args.name}.")
        return code

    if args.command == "ssh-key":
        code, out, err = ssh_key_manage(args)
        print(out or err or "SSH key operation complete.")
        return code

    if args.command == "snapshot":
        code, out, err = snapshot_manage(args)
        print(out or err or "Snapshot operation complete.")
        return code

    if args.command == "cleanup":
        code, out, err = cleanup_manage(args)
        print(out or err or "Cleanup complete.")
        return code

    if args.command == "nightly-snapshot":
        code, out, err = nightly_snapshots.run_command(["python3", str(PROJECT_ROOT / "nightly_snapshots.py")])
        print(out or err or "Nightly snapshots finished.")
        return code

    if args.command == "inject-key":
        code, out, err = vm_ssh_inject.inject_key(args.vm_name, args.key_name)
        print(out or err or "SSH key injection complete.")
        return code

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
