#!/usr/bin/env bash
set -euo pipefail

NAME="${1:-demo-vps}"
CPU="${2:-2}"
RAM_MB="${3:-4096}"
DISK_GB="${4:-40}"
BRIDGE="${5:-br0}"
IMAGE_URL="${6:-https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-amd64.img}"
SSH_KEY="${7:-$HOME/.ssh/id_ed25519.pub}"
WORKDIR="${ASTERIX_VPS_DIR:-/var/lib/asterix-vps}"

mkdir -p "$WORKDIR"

if [ ! -f "$SSH_KEY" ]; then
  mkdir -p "$HOME/.ssh"
  ssh-keygen -t ed25519 -N '' -f "$HOME/.ssh/id_ed25519" >/dev/null 2>&1 || true
  SSH_KEY="$HOME/.ssh/id_ed25519.pub"
fi

if [ ! -f "$SSH_KEY" ]; then
  echo "SSH key was not found and could not be generated."
  exit 1
fi

IMAGE_PATH="$WORKDIR/${NAME}-base.img"
DISK_PATH="$WORKDIR/${NAME}.qcow2"
USER_DATA="$WORKDIR/${NAME}-user-data"
META_DATA="$WORKDIR/${NAME}-meta-data"

if [ ! -f "$IMAGE_PATH" ]; then
  echo "[1/4] Downloading Ubuntu cloud image..."
  curl -L --fail --output "$IMAGE_PATH" "$IMAGE_URL"
fi

if [ ! -f "$DISK_PATH" ]; then
  echo "[2/4] Creating virtual disk..."
  qemu-img create -f qcow2 -b "$IMAGE_PATH" "$DISK_PATH" "${DISK_GB}G"
else
  echo "[2/4] Disk already exists for $NAME. Reusing it."
fi

cat > "$USER_DATA" <<EOF
#cloud-config
users:
  - default
  - name: admin
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: [adm, sudo]
    lock_passwd: false
    ssh_authorized_keys:
      - $(cat "$SSH_KEY")
package_update: true
package_upgrade: true
packages:
  - curl
  - git
  - htop
  - net-tools
  - openssh-server
runcmd:
  - systemctl enable --now ssh
EOF

cat > "$META_DATA" <<EOF
instance-id: ${NAME}
local-hostname: ${NAME}
EOF

NETWORK_ARG=""
if ip link show "$BRIDGE" >/dev/null 2>&1; then
  NETWORK_ARG="--network bridge=${BRIDGE},model=virtio"
else
  NETWORK_ARG="--network network=default,model=virtio"
fi

echo "[3/4] Starting VM creation for $NAME..."
virt-install \
  --name "$NAME" \
  --memory "$RAM_MB" \
  --vcpus "$CPU" \
  --disk "$DISK_PATH,format=qcow2,bus=virtio" \
  --import \
  --os-variant ubuntu24.04 \
  $NETWORK_ARG \
  --graphics none \
  --console pty,target_type=virtio \
  --cloud-init "user-data=${USER_DATA},meta-data=${META_DATA}" \
  --noautoconsole

echo "[4/4] VPS creation started."
echo "Use the following to monitor it:"
echo "  virsh list --all"
echo "  virsh console $NAME"
