# ==============================================================================
# ASTERIX OS — Desktop Docker Testing & Sandbox Environment
# Target Architectures: linux/amd64, linux/arm64
# Base: Debian 12 (Bookworm)
# ==============================================================================

FROM debian:bookworm-slim

LABEL maintainer="NEXO TECHNOLOGIES GROUP <security@asterixos.org>"
LABEL description="ASTERIX OS Desktop Sandbox & Cross-Platform Verification Container"

ENV DEBIAN_FRONTEND=noninteractive
ENV TERM=xterm-256color
ENV LANG=C.UTF-8
ENV ASTERIX_DIR=/opt/ASTERIX-OS
ENV PATH="/opt/ASTERIX-OS/bin:${PATH}"

# Install Core Debian Prerequisites & Security Tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    ca-certificates \
    curl \
    wget \
    git \
    python3 \
    python3-minimal \
    iproute2 \
    iputils-ping \
    dnsutils \
    netcat-openbsd \
    socat \
    nmap \
    tcpdump \
    procps \
    sudo \
    tar \
    gzip \
    file \
    && rm -rf /var/lib/apt/lists/*

# Configure APT Rootless & Init Policies (PRoot & Container Parity)
RUN mkdir -p /etc/apt/apt.conf.d /usr/sbin \
    && echo 'APT::Sandbox::User "root";' > /etc/apt/apt.conf.d/99termux-rootless \
    && printf '#!/bin/sh\nexit 101\n' > /usr/sbin/policy-rc.d \
    && chmod 755 /usr/sbin/policy-rc.d

# Create asterix non-root user with passwordless sudo
RUN useradd -m -s /bin/bash -u 1000 asterix \
    && echo "asterix ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/asterix \
    && chmod 0440 /etc/sudoers.d/asterix

# Configure Persistent Volume Structure
RUN mkdir -p /asterix_persistent/{projects,scans,loot,captures,reports,notes,scripts,payloads,wordlists,workspace} \
    && chown -R asterix:asterix /asterix_persistent

# Set working directory
WORKDIR /opt/ASTERIX-OS

# Copy ASTERIX OS codebase into container image
COPY . /opt/ASTERIX-OS

# Fix permissions and setup symlink for master ax CLI
RUN chmod +x /opt/ASTERIX-OS/bin/ax \
    && ln -sf /opt/ASTERIX-OS/bin/ax /usr/local/bin/ax \
    && chown -R asterix:asterix /opt/ASTERIX-OS

USER asterix
WORKDIR /home/asterix

VOLUME ["/asterix_persistent", "/opt/ASTERIX-OS"]

CMD ["/bin/bash"]
