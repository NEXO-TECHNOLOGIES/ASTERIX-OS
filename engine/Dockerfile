# =====================================================================
# ASTERIX OS - Dockerized ISO Build Environment
# =====================================================================
FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    live-build \
    debootstrap \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-efi \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    git \
    curl \
    wget \
    sudo \
    python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY packages.list /build/engine/packages.list
COPY build-iso.sh /build/engine/build-iso.sh

RUN chmod +x /build/engine/build-iso.sh

CMD ["/bin/bash", "-c", "cd /build/engine && ./build-iso.sh"]
