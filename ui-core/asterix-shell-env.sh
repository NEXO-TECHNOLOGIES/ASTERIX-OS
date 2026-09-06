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
alias ax-darktrace='ax darktrace'
alias ax-shadowcam='ax shadowcam'
alias ax-dark-engine='ax dark-engine'
alias ax-log-hunter='ax log-hunter'

# ASTERIX Anti-Network Attack & Defense Suite
alias ax-antinet='ax anti-net'
alias ax-antiemail='ax anti-email'
alias ax-antiarp='ax anti-arp'
alias ax-antisyn='ax anti-syn'
alias ax-antidns='ax anti-dns'
alias ax-antiscan='ax anti-scan'
alias ax-antirev='ax anti-rev'

# ASTERIX External Packages & THUNDER Defender
alias ax-pkg='ax pkg'
alias ax-pkgsync='ax pkg sync'
alias ax-pkgstatus='ax pkg status'
alias ax-thunder='ax thunder'
alias thunder='ax thunder'
alias ax-iprotator='ax ip-rotator'
alias iprotator='ax ip-rotator'
alias ax-wscan='ax wscan'
alias wscan='ax wscan'
alias ax-lightning='ax lightning'
alias lightning='ax lightning'
alias ax-defender='ax defender'
alias defender='ax defender'
alias ax-firewall='ax firewall'
alias ax-isolate='ax isolate'
alias ax-quarantine='ax quarantine'
alias ax-game='ax game'
alias game='ax game'
alias ax-overdrive='ax overdrive'
alias overdrive='ax overdrive'
alias apex-overdrive='ax overdrive'
alias ax-snapshot='ax snapshot'
alias snapshot='ax snapshot'
alias ax-restore='ax snapshot restore'
alias ax-events='ax event-log'
alias ax-eventlog='ax event-log'
alias ax-sfc='ax sfc'
alias sfc='ax sfc'
alias ax-taskmgr='ax taskmgr'
alias taskmgr='ax taskmgr'
alias ax-secpol='ax secpol'
alias secpol='ax secpol'
alias ax-sandbox='ax sandbox'
alias sandbox='ax sandbox'
alias ax-applocker='ax applocker'
alias applocker='ax applocker'
alias ax-bitlocker='ax bitlocker'
alias bitlocker='ax bitlocker'
alias ax-credguard='ax cred-guard'
alias credguard='ax cred-guard'
alias ax-exploitguard='ax exploit-guard'
alias exploitguard='ax exploit-guard'
alias ax-undercover='ax undercover'
alias undercover='ax undercover'
alias ax-nuke='ax nuke'
alias nuke='ax nuke'
alias ax-tweaks='ax tweaks'
alias tweaks='ax tweaks'
alias ax-forensic='ax forensic-mode'
alias forensic='ax forensic-mode'
alias ax-rfaudit='ax rf-audit'
alias rfaudit='ax rf-audit'

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

# Deep Core Root & Kernel Hardening (v2.9.0)
alias ax-kmod='ax kmod-audit'
alias ax-ghost='ax deleted-procs'
alias ax-cap='ax cap-audit'
alias ax-ebpf='ax ebpf-audit'
alias ax-persistence='ax root-persistence'
alias ax-seccomp='ax seccomp-audit'
alias ax-ttysnoop='ax tty-snoop'
alias ax-kexec='ax kexec-lockdown'
alias ax-memprotect='ax mem-protect'
alias ax-mountaudit='ax mount-hardening'
alias ax-ipc='ax ipc-audit'
alias ax-dmesg-exploit='ax dmesg-exploit'
alias ax-rootjail='ax root-jail'
alias ax-coredump='ax core-dump-audit'

# ASTERIX One-Touch Domain Launchers (ax-* and asterix-*)
ax-hub() { ax "$@"; }
ax-recon() { ax recon "$@"; }
ax-web() { ax web "$@"; }
ax-exploit() { ax exploit "$@"; }
ax-crack() { ax crack "$@"; }
ax-sniff() { ax sniff "$@"; }
ax-wifi() { ax wifi "$@"; }
ax-forensic() { ax forensics "$@"; }
ax-rev() { ax rev "$@"; }
ax-dev() { ax dev "$@"; }
ax-portal() {
    if [ -f /etc/asterix/ui-core/asterix-web-portal.sh ]; then
        /etc/asterix/ui-core/asterix-web-portal.sh
    elif [ -f ui-core/asterix-web-portal.sh ]; then
        ./ui-core/asterix-web-portal.sh
    else
        asterix-web-portal
    fi
}
ax-discord() {
    if [ -f /etc/asterix/ui-core/asterix-discord.sh ]; then
        /etc/asterix/ui-core/asterix-discord.sh "$@"
    elif [ -f ui-core/asterix-discord.sh ]; then
        ./ui-core/asterix-discord.sh "$@"
    else
        asterix-discord "$@"
    fi
}
ax-cloud() {
    if [ -f /etc/asterix/ui-core/asterix-cloud.sh ]; then
        /etc/asterix/ui-core/asterix-cloud.sh "$@"
    elif [ -f ui-core/asterix-cloud.sh ]; then
        ./ui-core/asterix-cloud.sh "$@"
    else
        asterix-cloud "$@"
    fi
}

# Full "asterix-*" form aliases
alias asterix-hub='ax-hub'
alias asterix-recon='ax-recon'
alias asterix-web='ax-web'
alias asterix-exploit='ax-exploit'
alias asterix-darktrace='ax darktrace'
alias asterix-shadowcam='ax shadowcam'
alias asterix-dark-engine='ax dark-engine'
alias asterix-log-hunter='ax log-hunter'
alias asterix-crack='ax-crack'
alias asterix-sniff='ax-sniff'
alias asterix-wifi='ax-wifi'
alias asterix-forensic='ax-forensic'
alias asterix-rev='ax-rev'
alias asterix-dev='ax-dev'
alias asterix-portal='ax-portal'
alias asterix-discord='ax-discord'
alias asterix-cloud='ax-cloud'
alias asterix-quad='ax-quad'

# Backward-compatibility fallback (as-*)
alias as-hub='ax-hub'
alias as-recon='ax-recon'
alias as-web='ax-web'
alias as-exploit='ax-exploit'
alias as-crack='ax-crack'
alias as-sniff='ax-sniff'
alias as-wifi='ax-wifi'
alias as-forensic='ax-forensic'
alias as-rev='ax-rev'
alias as-dev='ax-dev'
alias as-portal='ax-portal'
alias as-discord='ax-discord'
alias as-cloud='ax-cloud'
alias as-quad='ax-quad'

# Native C Systems Utilities Shortcuts (ax-* and asterix-*)
alias ax-sysinfo='asterix-sysinfo'
alias ax-memview='asterix-memview'
alias ax-netprobe='asterix-netprobe'
alias ax-hasher='asterix-hasher'
alias ax-shredder='asterix-shredder'
alias ax-proctrace='asterix-proctrace'
alias ax-rootkit='asterix-rootkit-detect'
alias ax-syscall='asterix-syscall-mon'
alias ax-envdump='asterix-env-dump'

# Native C++ Cyber Utilities
alias ax-packetcraft='asterix-packetcraft'
alias ax-vulnscan='asterix-vulnscan'
alias ax-logwatch='asterix-logwatch'

# x86-64 Pure Assembly & Go Engines
alias ax-rawinfo='asterix-raw-info'
alias ax-cipher='asterix-cipher-asm'
alias ax-webrecon='asterix-webrecon'

# Pure Rust Security & Systems Engines Suite
alias ax-bininspect='asterix-bin-inspector'
alias ax-sentinel='asterix-net-sentinel'
alias ax-crypto='asterix-crypto-core'
alias ax-sysmon='asterix-sys-mon'
alias ax-guard='asterix-guard-engine'
alias asterix-bininspect='asterix-bin-inspector'
alias asterix-sentinel='asterix-net-sentinel'
alias asterix-crypto='asterix-crypto-core'
alias asterix-sysmon='asterix-sys-mon'
alias asterix-guard='asterix-guard-engine'
alias asterix-cipher='asterix-cipher-asm'

# Scripts Hub Shortcuts
alias ax-netrecon='/etc/asterix/scripts-hub/net-recon.sh'
alias ax-cleanup='/etc/asterix/scripts-hub/secure-cleanup.sh'
alias ax-backup='/etc/asterix/scripts-hub/backup-cloud.sh'
ax-scaffold() { /etc/asterix/scripts-hub/dev-bootstrap.sh "$@"; }
alias asterix-scaffold='ax-scaffold'

# Launch Instant Quad-Grid Workspace
ax-quad() {
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
