#!/data/data/com.termux/files/usr/bin/bash
# =====================================================================
# ASTERIX OS — Mobile Debian Rootless Subsystem & Folder Engine CLI
# Zero-crash PRoot wrapper with hardened directories, multi-DNS,
# APT sandbox fix, and resilient folder creation.
# =====================================================================

set -e

CYAN='\033[38;5;51m'
GREEN='\033[38;5;46m'
YELLOW='\033[38;5;220m'
RED='\033[38;5;196m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASTERIX_ROOT="$(dirname "$SCRIPT_DIR")"

find_python() {
    for cand in python3 python py \
        "/data/data/com.termux/files/usr/bin/python3" \
        "/usr/bin/python3" \
        "/usr/local/bin/python3"; do
        if command -v "$cand" >/dev/null 2>&1; then
            if "$cand" -c "import sys; print(sys.version_info[0])" 2>/dev/null | grep -q "3"; then
                echo "$cand"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON_BIN="$(find_python || true)"
ENGINE="${ASTERIX_ROOT}/scripts-hub/ax-debian-manager.py"
[ -f "$ENGINE" ] || ENGINE="$HOME/ASTERIX-OS/scripts-hub/ax-debian-manager.py"
[ -f "$ENGINE" ] || ENGINE="/opt/ASTERIX-OS/scripts-hub/ax-debian-manager.py"

# If Python engine is available, dispatch to it
if [ -n "$PYTHON_BIN" ] && [ -f "$ENGINE" ]; then
    exec "$PYTHON_BIN" "$ENGINE" "$@"
fi

# Fallback Bash implementation if Python is not yet installed
PERSIST="${HOME}/asterix_persistent"
[ -d "$HOME/.asterix_storage" ] && PERSIST="${HOME}/.asterix_storage"
mkdir -p "$PERSIST"/{projects,scans,loot,captures,reports,notes,scripts,payloads,wordlists,workspace} 2>/dev/null || true

cmd="${1:-shell}"
shift || true

case "$cmd" in
    shell|login)
        echo -e "${CYAN}${BOLD}[*] Launching Debian Rootless Environment...${NC}"
        proot_args=("--link2symlink" "--bind" "${ASTERIX_ROOT}:/opt/ASTERIX-OS" "--bind" "${PERSIST}:/asterix_persistent")
        [ -d "/sdcard" ] && [ -w "/sdcard" ] && proot_args+=("--bind" "/sdcard:/sdcard")
        exec proot-distro login "${proot_args[@]}" debian -- "$@"
        ;;
    folder|dir|mkdir)
        action="${1:-list}"
        shift || true
        case "$action" in
            create|new)
                target_name="$1"
                if [ -z "$target_name" ]; then
                    echo -e "${RED}Error: Specify folder name: debian-rootless folder create <name>${NC}"
                    exit 1
                fi
                dest="$PERSIST/projects/$target_name"
                mkdir -p "$dest"/{scans,loot,notes,reports,scripts} 2>/dev/null || true
                chmod -R 755 "$dest" 2>/dev/null || true
                echo -e "${GREEN}✔ Created resilient folder:${NC} $dest"
                ;;
            *)
                echo -e "${CYAN}Persistent Folders at: $PERSIST${NC}"
                ls -la "$PERSIST"
                ;;
        esac
        ;;
    doctor|check)
        echo -e "${CYAN}[*] Debian Rootless Quick Diagnostic:${NC}"
        which proot proot-distro 2>/dev/null || echo -e "${RED}[!] proot-distro missing. Run: pkg install proot proot-distro${NC}"
        [ -d "$PREFIX/var/lib/proot-distro/installed-rootfs/debian" ] && echo -e "${GREEN}[✔] Debian Rootfs installed${NC}" || echo -e "${YELLOW}[!] Debian Rootfs missing${NC}"
        ;;
    fix|repair)
        echo -e "${CYAN}[*] Repairing Debian Rootless Configuration...${NC}"
        deb_root="$PREFIX/var/lib/proot-distro/installed-rootfs/debian"
        if [ -d "$deb_root" ]; then
            # Fix resolv.conf
            printf "nameserver 1.1.1.1\nnameserver 8.8.8.8\nnameserver 9.9.9.9\n" > "$deb_root/etc/resolv.conf" 2>/dev/null || true
            # Fix APT Sandbox user
            mkdir -p "$deb_root/etc/apt/apt.conf.d"
            printf 'APT::Sandbox::User "root";\nAcquire::Languages "none";\n' > "$deb_root/etc/apt/apt.conf.d/99termux-rootless" 2>/dev/null || true
            # Fix policy-rc.d
            mkdir -p "$deb_root/usr/sbin"
            printf '#!/bin/sh\nexit 101\n' > "$deb_root/usr/sbin/policy-rc.d" 2>/dev/null || true
            chmod 755 "$deb_root/usr/sbin/policy-rc.d" 2>/dev/null || true
            # Fix /dev/shm and /tmp
            mkdir -p "$deb_root/dev/shm" "$deb_root/tmp" 2>/dev/null || true
            chmod 1777 "$deb_root/dev/shm" "$deb_root/tmp" 2>/dev/null || true
            echo -e "${GREEN}[✔] Rootless Debian configuration repaired.${NC}"
        fi
        ;;
    *)
        echo "Usage: debian-rootless [shell|run|folder|doctor|fix]"
        ;;
esac
