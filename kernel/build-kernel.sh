#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KERNEL_VERSION="${KERNEL_VERSION:-6.6.13}"
KERNEL_URL="https://cdn.kernel.org/pub/linux/kernel/v6.x/linux-${KERNEL_VERSION}.tar.xz"
WORK_DIR="${WORK_DIR:-$ROOT_DIR/kernel-build}"
OUT_DIR="${OUT_DIR:-$WORK_DIR/out}"
CONFIG_FILE="${CONFIG_FILE:-$ROOT_DIR/kernel/configs/asterix-kernel.config}"
BUILD_THREADS="${BUILD_THREADS:-$(nproc 2>/dev/null || echo 4)}"
ARCH_NAME="$(uname -m)"

case "$ARCH_NAME" in
  x86_64|amd64)
    KERNEL_ARCH="x86_64"
    ;;
  aarch64|arm64)
    KERNEL_ARCH="arm64"
    ;;
  *)
    KERNEL_ARCH="$ARCH_NAME"
    ;;
esac

export DEBIAN_FRONTEND=noninteractive

echo "[ASTERIX KERNEL] Preparing custom linux build for ${ARCH_NAME}"

if [ "$(id -u)" -ne 0 ]; then
  echo "[ASTERIX KERNEL] Root privileges required to install build dependencies and generate initramfs." >&2
  exit 1
fi

apt-get update
apt-get install -y --no-install-recommends \
  build-essential bc curl ca-certificates git fakeroot \
  libssl-dev libelf-dev flex bison kmod cpio initramfs-tools

mkdir -p "$WORK_DIR" "$OUT_DIR"

if [ ! -d "$WORK_DIR/src" ]; then
  echo "[ASTERIX KERNEL] Downloading Linux ${KERNEL_VERSION} source"
  curl -fL "$KERNEL_URL" -o "$WORK_DIR/linux-${KERNEL_VERSION}.tar.xz"
  tar -xf "$WORK_DIR/linux-${KERNEL_VERSION}.tar.xz" -C "$WORK_DIR"
  mv "$WORK_DIR/linux-${KERNEL_VERSION}" "$WORK_DIR/src"
fi

if [ ! -f "$CONFIG_FILE" ]; then
  echo "[ASTERIX KERNEL] Missing config: $CONFIG_FILE" >&2
  exit 1
fi

cp "$CONFIG_FILE" "$WORK_DIR/src/.config"
cd "$WORK_DIR/src"
make olddefconfig
make -j"$BUILD_THREADS" bzImage modules

make modules_install INSTALL_MOD_PATH="$OUT_DIR/modules"

if [ -f "arch/${KERNEL_ARCH}/boot/bzImage" ]; then
  cp "arch/${KERNEL_ARCH}/boot/bzImage" "$OUT_DIR/vmlinuz-asterix"
elif [ -f "arch/${KERNEL_ARCH}/boot/Image" ]; then
  cp "arch/${KERNEL_ARCH}/boot/Image" "$OUT_DIR/vmlinuz-asterix"
else
  echo "[ASTERIX KERNEL] Kernel image not found after build." >&2
  exit 1
fi

cp .config "$OUT_DIR/asterix-kernel.config"
mkinitramfs -o "$OUT_DIR/initrd-asterix.img" "${KERNEL_VERSION}-asterix"

cat <<EOF
[ASTERIX KERNEL] Build complete.
  Kernel:  $OUT_DIR/vmlinuz-asterix
  Initramfs: $OUT_DIR/initrd-asterix.img
  Config:  $OUT_DIR/asterix-kernel.config
EOF
