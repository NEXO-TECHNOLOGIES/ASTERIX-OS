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

# ASTERIX One-Touch Domain Launchers
as-hub() { asterix "$@"; }
as-recon() { asterix --recon; }
as-web() { asterix --web-audit; }
as-exploit() { asterix --exploit; }
as-crack() { asterix --passwords; }
as-sniff() { asterix --sniffing; }
as-wifi() { asterix --wireless; }
as-forensic() { asterix --forensics; }
as-rev() { asterix --reverse; }
as-dev() { asterix --dev; }

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
