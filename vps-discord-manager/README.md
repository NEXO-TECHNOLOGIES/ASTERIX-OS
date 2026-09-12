# ASTERIX VPS Manager

A practical project that lets you create and manage Linux VPS instances on a host machine with KVM/libvirt and control them through a Discord bot or a local CLI.

## What it does

- installs KVM/libvirt support on Ubuntu/Debian server
- downloads a cloud image
- creates a VM with your desired CPU, RAM, and disk size
- provisions SSH access through cloud-init
- lets you manage the lifecycle from Discord or the command line
- exposes dashboard-style status, host diagnostics, and lifecycle controls
- includes SSH key registration and management
- supports snapshot creation and cleanup for safe VM maintenance
- includes backup/log cleanup operations for better host hygiene
- starts a local web dashboard with host status and per-VM cards
- supports automated nightly snapshots for all running VMs
- supports per-VM SSH key injection into the guest cloud-init config
- exposes a REST API for dashboard consumption and monitoring integrations
- includes a cleaner metrics-oriented dashboard ready for CPU/RAM graph expansion

## Project layout

```text
vps-discord-manager/
├── install.sh
├── create-vps.sh
├── vps_admin.py
├── discord_bot.py
├── .env.example
├── README.md
├── .gitignore
└── __pycache__/
```

## Quick start

### 1) Install the host dependencies

```bash
chmod +x install.sh
sudo ./install.sh
```

### 2) Create a Discord bot

Create a bot in the Discord Developer Portal and copy its token.

### 3) Create a local config

```bash
cp .env.example .env
```

Then edit `.env`:

```env
DISCORD_BOT_TOKEN=your_token_here
```

### 4) Start the bot

```bash
python3 discord_bot.py
```

### 5) Use commands in Discord

```text
!vps create demo-vps 2 4096 40
!vps list
!vps dashboard
!vps host-info
!vps status demo-vps
!vps start demo-vps
!vps stop demo-vps
!vps restart demo-vps
!vps ssh demo-vps
!vps ssh-key list
!vps ssh-key generate demo-key
!vps inject-key demo-vps demo-key
!vps snapshot create demo-vps snap-1
!vps snapshot list demo-vps
!vps nightly-snapshot
!vps cleanup all
!vps logs demo-vps
!vps destroy demo-vps
```

## Web dashboard

Start the local web UI:

```bash
python3 dashboard_app.py
```

Then open:

```text
http://localhost:8080
```

It shows:
- host OS and uptime
- memory and disk data
- VM cards with name, status, IP, CPU, and memory
- automatic refresh every 10 seconds

API endpoints:

```text
GET /api/status
GET /api/host
GET /api/vms
GET /api/metrics
```

## Nightly snapshot scheduling

The project installs a cron job at 02:00 daily that runs the nightly snapshot script automatically:

```bash
python3 nightly_snapshots.py
```

This creates snapshots for each running VM with a timestamped label.

## Local admin CLI

You can also manage VMs directly from the host:

```bash
python3 vps_admin.py list
python3 vps_admin.py dashboard
python3 vps_admin.py host-info
python3 vps_admin.py create demo-vps 2 4096 40
python3 vps_admin.py status demo-vps
python3 vps_admin.py ssh demo-vps
python3 vps_admin.py ssh-key list
python3 vps_admin.py inject-key demo-vps demo-key
python3 vps_admin.py snapshot create demo-vps snap-1
python3 vps_admin.py nightly-snapshot
python3 vps_admin.py cleanup all
python3 vps_admin.py logs demo-vps
```

## Notes

This setup is designed for a real Linux host machine with KVM support. It is meant for practical VM deployment and local infrastructure work, not as a fake demo.

## System requirements

- Ubuntu or Debian server
- virtualization enabled in BIOS/firmware
- root or sudo access
- KVM support

## Example host commands

```bash
virsh list --all
virsh net-list --all
virsh console demo-vps
virsh domifaddr demo-vps
```
