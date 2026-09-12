#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

if ! command -v sudo >/dev/null 2>&1; then
  echo "sudo is required. Please install it first."
  exit 1
fi

echo "[1/6] Updating package lists..."
sudo apt-get update

echo "[2/6] Installing KVM, libvirt, and required virtualization tools..."
sudo apt-get install -y \
  qemu-system qemu-utils \
  libvirt-daemon-system libvirt-clients \
  virtinst cloud-image-utils \
  bridge-utils dnsmasq net-tools \
  curl git python3 python3-pip cron

echo "[3/6] Enabling libvirt service..."
sudo systemctl enable --now libvirtd

if ! id -nG "$(whoami)" | grep -qw "libvirt"; then
  echo "Adding current user to libvirt and kvm groups..."
  sudo usermod -aG libvirt "$(whoami)"
  sudo usermod -aG kvm "$(whoami)"
fi

echo "[4/6] Installing Python Discord bot dependency..."
python3 -m pip install --user discord.py python-dotenv

echo "[5/6] Creating project directories..."
mkdir -p /opt/asterix-vps
mkdir -p /var/lib/asterix-vps
mkdir -p /var/lib/asterix-vps/backup
mkdir -p /var/lib/asterix-vps/snapshots
mkdir -p /var/lib/asterix-vps/logs

cat > /etc/profile.d/asterix-vps.sh <<'EOF'
export ASTERIX_VPS_DIR="/var/lib/asterix-vps"
export PATH="$PATH:/opt/asterix-vps"
EOF

chmod +x /etc/profile.d/asterix-vps.sh

PROJECT_DIR="$(pwd)"
CRON_LINE="0 2 * * * cd '$PROJECT_DIR' && python3 nightly_snapshots.py >> /var/lib/asterix-vps/logs/nightly-snapshots.log 2>&1"
( crontab -l 2>/dev/null | grep -Fv "nightly_snapshots.py"; echo "$CRON_LINE" ) | crontab -

echo "[6/6] Installing cron job for nightly snapshots..."

cat <<'EOF'

══════════════════════════════════════════════════
ASTERIX VPS Manager setup complete.

Next steps:
  1. Log out and log back in.
  2. Copy the project files into /opt/asterix-vps
  3. Edit .env with your Discord bot token
  4. Run: python3 discord_bot.py
  5. Start the dashboard with: python3 dashboard_app.py

Useful host commands:
  virsh list --all
  virsh net-list --all
  virsh console <vm-name>

Nightly snapshot cron job is installed at 02:00 daily.
EOF
