#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Maximum-Tier Cyber Shell Environment
# Supercharges Bash and Zsh with FZF fuzzy search, Git status,
# one-touch domain launchers, and modern CLI tool aliases.
# =====================================================================

# Modern CLI Replacements & Aliases
if command -v eza >/dev/null 2>&1; then
    alias ls='eza --icons --group-directories-first'
    alias ll='eza -la --icons --group-directories-first --git'
    alias lt='eza --tree --level=2 --icons'
elif command -v exa >/dev/null 2>&1; then
    alias ls='exa --icons --group-directories-first'
    alias ll='exa -la --icons --group-directories-first --git'
fi

if command -v batcat >/dev/null 2>&1; then
    alias cat='batcat --paging=never --style=plain'
    alias bat='batcat'
elif command -v bat >/dev/null 2>&1; then
    alias cat='bat --paging=never --style=plain'
fi

if command -v fdfind >/dev/null 2>&1; then
    alias fd='fdfind'
fi

alias grep='grep --color=auto'
alias edit='nano'
alias ports='netstat -tulpn'
alias myip='curl -s ifconfig.me'
alias vault='cd /asterix_persistent'

# Developer Fast Compilers
run-rs() {
    if [ -z "$1" ]; then
        echo "Usage: run-rs <file.rs>"
        return 1
    fi
    out_bin="${1%.rs}"
    rustc -O "$1" -o "$out_bin" && ./"$out_bin"
}

run-c() {
    if [ -z "$1" ]; then
        echo "Usage: run-c <file.c>"
        return 1
    fi
    out_bin="${1%.c}"
    gcc -O2 "$1" -o "$out_bin" && ./"$out_bin"
}

run-py() {
    python3 "$@"
}

# Master Unified OS Toolchain: ax & asterix
if command -v ax >/dev/null 2>&1; then
    alias asterix='ax'
elif command -v asterix >/dev/null 2>&1; then
    alias ax='asterix'
elif [ -f /usr/local/bin/ax ]; then
    alias ax='/usr/local/bin/ax'
    alias asterix='/usr/local/bin/ax'
elif [ -f /etc/asterix/bin/ax ]; then
    alias ax='/etc/asterix/bin/ax'
    alias asterix='/etc/asterix/bin/ax'
fi

# ax System & Arsenal Maintenance Fast Shortcuts
alias ax-update='ax update'
alias ax-upgrade='ax upgrade'
alias ax-doctor='ax doctor'
alias ax-clean='ax clean'
alias ax-status='ax status'
alias ax-list='ax list'
alias ax-sysfetch='ax sysfetch'
alias as-update='ax update'
alias as-upgrade='ax upgrade'

# ax Tactical Cyber Warfare & Deception
alias ax-matrix='ax matrix'
alias ax-stealth='ax stealth'
alias ax-ghost='ax stealth'
alias ax-killswitch='ax killswitch'
alias ax-lockdown='ax killswitch'
alias ax-decoy='ax decoy'
alias ax-honeypot='ax decoy'
alias ax-payload='ax payload'
alias ax-revshell='ax payload'
alias ax-malware='ax malware-scan'
alias ax-tor='ax tor-status'
alias ax-quote='ax quote'

# ax Network & OSINT Reconnaissance
alias ax-ip='ax ip'
alias ax-ports='ax ports'
alias ax-ping='ax ping'
alias ax-scan='ax scan'
alias ax-netrecon='ax netrecon'
alias ax-subdomains='ax subdomains'
alias ax-banner='ax banner-grab'
alias ax-wifi='ax wifi-scan'
alias ax-sniff='ax sniff-live'
alias ax-speedtest='ax speedtest'
alias ax-mac='ax mac'
alias ax-webrecon='ax webrecon'
alias ax-dns='ax dns'
alias ax-whois='ax whois'
alias ax-traceroute='ax traceroute'
alias ax-arp='ax arp'
alias ax-conns='ax connections'
alias ax-traffic='ax traffic'

# ax Defense, Hardening & Forensics
alias ax-hash='ax hash'
alias ax-shred='ax shred'
alias ax-rootkit='ax rootkit'
alias ax-trace='ax trace'
alias ax-vuln='ax vuln'
alias ax-packet='ax packet'
alias ax-logwatch='ax logwatch'
alias ax-firewall='ax firewall'
alias ax-audit='ax audit'
alias ax-suid='ax suid'
alias ax-certs='ax certs'
alias ax-docker='ax docker-audit'
alias ax-exif='ax exif'
alias ax-kernel='ax kernel-hardening'
alias ax-fim-init='ax fim-init'
alias ax-fim-check='ax fim-check'
alias ax-auth='ax auth-audit'
alias ax-secrets='ax git-secrets'
alias ax-cis='ax cis-audit'
alias ax-tls='ax tls-audit'

# ax Crypto, Encoding & Passwords
alias ax-encrypt='ax encrypt'
alias ax-decrypt='ax decrypt'
alias ax-b64enc='ax b64enc'
alias ax-b64dec='ax b64dec'
alias ax-hexenc='ax hexenc'
alias ax-hexdec='ax hexdec'
alias ax-genpass='ax genpass'
alias ax-entropy='ax entropy'
alias ax-qr='ax qr'

# ax System, Workspace & Desktop HUD
alias ax-cpu='ax cpu'
alias ax-disk='ax disk'
alias ax-mem='ax mem'
alias ax-service='ax service'
alias ax-ps='ax ps'
alias ax-bench='ax benchmark'
alias ax-env='ax env'
alias ax-top='ax top'
alias ax-backup='ax backup'
alias ax-loot='ax loot'
alias ax-wp='ax wallpaper'
alias ax-hud='ax hud'
alias ax-scaffold='ax scaffold'
alias ax-compress='ax compress'
alias ax-extract='ax extract'
alias ax-bigfiles='ax find-large'
alias ax-pstree='ax pstree'
alias ax-env-audit='ax env-audit'

# Network Intelligence & Telemetry
alias ax-ip-geo='ax ip-geo'
alias ax-net-route='ax net-route'
alias ax-listening='ax listening'
alias ax-cron-audit='ax cron-audit'

# Crypto, Certs & Encoding
alias ax-cert-create='ax cert-create'
alias ax-json='ax json-format'

# System Power & I/O Telemetry
alias ax-disk-io='ax disk-io'
alias ax-uptime='ax uptime-stats'
alias ax-battery='ax battery'
alias ax-pkg-verify='ax pkg-verify'

# Advanced Offensive & Forensics (v2.8.0)
alias ax-ssh-audit='ax ssh-audit'
alias ax-arp-detect='ax arp-detect'
alias ax-hexdump='ax hexdump'
alias ax-strings='ax strings-scan'
alias ax-shadow-audit='ax shadow-audit'
alias ax-usb-audit='ax usb-audit'
alias ax-dmesg='ax dmesg-watch'
alias ax-neigh='ax net-neighbors'
alias ax-nft='ax nft-rules'
alias ax-strace='ax syscall-trace'
alias ax-lsof='ax open-files'
alias ax-escape='ax container-escape'
alias ax-knock='ax port-knock'
alias ax-memmap='ax mem-regions'

# ASTERIX One-Touch Domain Launchers
as-hub() { ax "$@"; }
as-recon() { ax recon "$@"; }
as-web() { ax web "$@"; }
as-exploit() { ax exploit "$@"; }
as-crack() { ax crack "$@"; }
as-sniff() { ax sniff "$@"; }
as-wifi() { ax wifi "$@"; }
as-forensic() { ax forensics "$@"; }
as-rev() { ax rev "$@"; }
as-dev() { ax dev "$@"; }
as-portal() {
    if [ -f /etc/asterix/ui-core/asterix-web-portal.sh ]; then
        /etc/asterix/ui-core/asterix-web-portal.sh
    elif [ -f ui-core/asterix-web-portal.sh ]; then
        ./ui-core/asterix-web-portal.sh
    else
        asterix-web-portal
    fi
}
as-discord() {
    if [ -f /etc/asterix/ui-core/asterix-discord.sh ]; then
        /etc/asterix/ui-core/asterix-discord.sh "$@"
    elif [ -f ui-core/asterix-discord.sh ]; then
        ./ui-core/asterix-discord.sh "$@"
    else
        asterix-discord "$@"
    fi
}
as-cloud() {
    if [ -f /etc/asterix/ui-core/asterix-cloud.sh ]; then
        /etc/asterix/ui-core/asterix-cloud.sh "$@"
    elif [ -f ui-core/asterix-cloud.sh ]; then
        ./ui-core/asterix-cloud.sh "$@"
    else
        asterix-cloud "$@"
    fi
}

# Native C Systems Utilities Shortcuts
alias as-sysinfo='asterix-sysinfo'
alias as-memview='asterix-memview'
alias as-netprobe='asterix-netprobe'
alias as-hasher='asterix-hasher'
alias as-shredder='asterix-shredder'
alias as-proctrace='asterix-proctrace'
alias as-rootkit='asterix-rootkit-detect'
alias as-syscall='asterix-syscall-mon'
alias as-envdump='asterix-env-dump'

# Native C++ Cyber Utilities
alias as-packetcraft='asterix-packetcraft'
alias as-vulnscan='asterix-vulnscan'
alias as-logwatch='asterix-logwatch'

# x86-64 Pure Assembly & Go Engines
alias as-rawinfo='asterix-raw-info'
alias as-webrecon='asterix-webrecon'

# Scripts Hub Shortcuts
alias as-netrecon='/etc/asterix/scripts-hub/net-recon.sh'
alias as-cleanup='/etc/asterix/scripts-hub/secure-cleanup.sh'
alias as-backup='/etc/asterix/scripts-hub/backup-cloud.sh'
as-scaffold() { /etc/asterix/scripts-hub/dev-bootstrap.sh "$@"; }

# Launch Instant Quad-Grid Workspace
as-quad() {
    if [ -f /etc/asterix/asterix.tmux.conf ]; then
        tmux -f /etc/asterix/asterix.tmux.conf new-session \; split-window -h \; split-window -v \; select-pane -t 0 \; split-window -v \; select-layout tiled
    elif [ -f ui-core/asterix.tmux.conf ]; then
        tmux -f ui-core/asterix.tmux.conf new-session \; split-window -h \; split-window -v \; select-pane -t 0 \; split-window -v \; select-layout tiled
    else
        tmux new-session \; split-window -h \; split-window -v \; select-pane -t 0 \; split-window -v \; select-layout tiled
    fi
}

# FZF Fuzzy Integration (History, Files, Dirs)
if command -v fzf >/dev/null 2>&1; then
    eval "$(fzf --bash 2>/dev/null || true)"
fi

# Zoxide Smart Navigation Integration
if command -v zoxide >/dev/null 2>&1; then
    eval "$(zoxide init bash 2>/dev/null || true)"
fi

# Cyberpunk Terminal Prompt (PS1)
_asterix_git_branch() {
    git branch 2>/dev/null | sed -e '/^[^*]/d' -e 's/* \(.*\)/ (\1)/'
}

if [ "$UID" -eq 0 ]; then
    USER_COLOR="\[\033[38;5;196m\]"
    USER_TAG="root"
else
    USER_COLOR="\[\033[38;5;51m\]"
    USER_TAG="\u"
fi

PS1="${USER_COLOR}┌──(${USER_TAG}@asterix-sec)─[\[\033[38;5;220m\]\w\[\033[38;5;201m\]\$(_asterix_git_branch)${USER_COLOR}]\n└──╼ \[\033[38;5;46m\]❯\[\033[0m\] "
