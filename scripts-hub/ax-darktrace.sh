#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ASTERIX OS — ax-darktrace  (Dark Forensic & Telemetry Engine)          ║
# ║  Stealth memory triage · entropy scan · log anomaly · net telemetry     ║
# ║  100% defensive / forensic — no malware, no offensive payloads          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
# Usage:  ax darktrace [module]
#   modules:  all | mem | entropy | net | log | proc | cron | stealth | help

R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
FG_DARKGRAY='\033[38;5;237m'; FG_GRAY='\033[38;5;243m'
FG_GREEN='\033[38;5;46m';     FG_DKGREEN='\033[38;5;22m'
FG_CYAN='\033[38;5;51m'
FG_MAGENTA='\033[38;5;201m';  FG_PURPLE='\033[38;5;141m'
FG_RED='\033[38;5;196m';      FG_ORANGE='\033[38;5;208m'
FG_YELLOW='\033[38;5;220m';   FG_WHITE='\033[38;5;231m'

hrule() {
    local c="${1:-─}" col="${2:-$FG_CYAN}"
    local w; w=$(tput cols 2>/dev/null || echo 72)
    echo -e "${col}$(printf "%${w}s" | tr ' ' "$c")${R}"
}
header() {
    clear
    hrule "═" "$FG_MAGENTA"
    echo -e " ${FG_MAGENTA}${BOLD}[ ASTERIX DARKTRACE — FORENSIC TELEMETRY ENGINE ]${R}"
    echo -e " ${FG_GRAY}Stealth · Entropy · Memory · Network · Log Triage${R}"
    hrule "═" "$FG_MAGENTA"
    echo ""
}
ok()   { echo -e "  ${FG_GREEN}[✔]${R} $*"; }
warn() { echo -e "  ${FG_YELLOW}[!]${R} $*"; }
crit() { echo -e "  ${FG_RED}[✖]${R} $*"; }
info() { echo -e "  ${FG_CYAN}[*]${R} $*"; }

# ──────────────────────────────────────────────────────────────────────
# MODULE 1: Memory Triage
# ──────────────────────────────────────────────────────────────────────
mod_mem() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ MEMORY TRIAGE ━━${R}\n"
    if [[ -f /proc/meminfo ]]; then
        local total avail swap_total swap_free dirty
        total=$(awk '/MemTotal/{printf "%.0f", $2/1024}' /proc/meminfo)
        avail=$(awk '/MemAvailable/{printf "%.0f", $2/1024}' /proc/meminfo)
        swap_total=$(awk '/SwapTotal/{printf "%.0f", $2/1024}' /proc/meminfo)
        swap_free=$(awk '/SwapFree/{printf "%.0f", $2/1024}' /proc/meminfo)
        dirty=$(awk '/Dirty/{printf "%.0f KB", $2}' /proc/meminfo)
        local used=$(( total - avail ))
        local pct=$(( used * 100 / (total + 1) ))
        printf "  ${FG_CYAN}RAM Total:${R}     %s MB\n"  "$total"
        printf "  ${FG_CYAN}RAM Used:${R}      %s MB (%s%%)\n" "$used" "$pct"
        printf "  ${FG_CYAN}RAM Available:${R} %s MB\n"  "$avail"
        printf "  ${FG_CYAN}Swap Total:${R}    %s MB\n"  "$swap_total"
        printf "  ${FG_CYAN}Swap Free:${R}     %s MB\n"  "$swap_free"
        printf "  ${FG_CYAN}Dirty Pages:${R}   %s\n"     "$dirty"
        (( pct > 85 )) && warn "Memory pressure HIGH — ${pct}% used"
        (( pct > 95 )) && crit "CRITICAL: Memory nearly exhausted!"
    else
        warn "/proc/meminfo not available in this environment"
    fi

    echo ""
    info "Scanning for anomalous large anonymous RWX memory regions..."
    if [[ -d /proc ]]; then
        local found=0
        for pid in /proc/[0-9]*/maps; do
            [[ -r "$pid" ]] || continue
            local name; name=$(basename "$(dirname "$pid")")
            while IFS= read -r line; do
                if echo "$line" | grep -qE '^\S+ rwx' && echo "$line" | grep -qE '\s+\(deleted\)|\s+$'; then
                    local start end
                    start=$(echo "$line" | cut -d- -f1)
                    end=$(echo "$line" | cut -d- -f2 | cut -d' ' -f1)
                    local size=$(( 16#$end - 16#$start ))
                    if (( size > 52428800 )); then
                        warn "PID ${name}: large anon rwx region ${size} bytes at 0x${start}"
                        found=1
                    fi
                fi
            done < "$pid" 2>/dev/null
        done
        (( found == 0 )) && ok "No large anonymous RWX memory regions detected"
    fi
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 2: Shannon Entropy Scanner
# ──────────────────────────────────────────────────────────────────────
mod_entropy() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ ENTROPY SCANNER ━━${R}\n"
    info "Scanning common binary locations for high-entropy (packed/encrypted) files..."
    local dirs=("/usr/local/bin" "/usr/bin" "/tmp" "/var/tmp" "/dev/shm")
    local found=0
    for dir in "${dirs[@]}"; do
        [[ -d "$dir" ]] || continue
        for f in "$dir"/*; do
            [[ -f "$f" && -r "$f" && -x "$f" ]] || continue
            local ent
            ent=$(dd if="$f" bs=4096 count=4 2>/dev/null | od -An -tu1 | tr ' ' '\n' | \
                awk 'NF{c[$1]++;n++} END{
                    for(b in c){p=c[b]/n; e-=p*log(p)/log(2)}
                    printf "%.2f", e
                }' 2>/dev/null || echo "0")
            if awk "BEGIN{exit !($ent > 7.2)}" 2>/dev/null; then
                warn "HIGH ENTROPY (${ent} bits): $f"
                found=1
            fi
        done
    done
    (( found == 0 )) && ok "No high-entropy executables detected in scanned paths"

    echo ""
    info "Checking /tmp and /dev/shm for hidden executables..."
    local hidden=0
    for dir in /tmp /dev/shm /var/tmp; do
        [[ -d "$dir" ]] || continue
        while IFS= read -r -d '' f; do
            warn "Executable in temp dir: $f"
            hidden=1
        done < <(find "$dir" -maxdepth 3 -type f -executable -print0 2>/dev/null)
    done
    (( hidden == 0 )) && ok "No executables found in /tmp, /dev/shm, /var/tmp"
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 3: Network Telemetry
# ──────────────────────────────────────────────────────────────────────
mod_net() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ NETWORK TELEMETRY ━━${R}\n"
    info "Active listening ports:"
    if command -v ss &>/dev/null; then
        ss -tlunp 2>/dev/null | tail -n +2 | while IFS= read -r line; do
            echo -e "    ${FG_CYAN}${line}${R}"
        done
    elif command -v netstat &>/dev/null; then
        netstat -tlunp 2>/dev/null | tail -n +3 | head -20 | while IFS= read -r line; do
            echo -e "    ${FG_CYAN}${line}${R}"
        done
    else
        warn "ss/netstat not available — reading /proc/net/tcp"
        awk 'NR>1{
            split($2,a,":"); port=strtonum("0x"a[2])
            if($4=="0A") printf "  LISTEN  :%d\n", port
        }' /proc/net/tcp 2>/dev/null | sort -u
    fi

    echo ""
    info "Checking established connections for anomalies..."
    local suspicious=0
    if command -v ss &>/dev/null; then
        while IFS= read -r conn; do
            local rport; rport=$(echo "$conn" | awk '{print $6}' | cut -d: -f2)
            if [[ "$rport" =~ ^[0-9]+$ ]]; then
                if ! echo "80 443 22 53 8080 8443 8888 5353" | grep -qw "$rport"; then
                    warn "Unusual outbound connection: $conn"
                    suspicious=1
                fi
            fi
        done < <(ss -tnp state established 2>/dev/null | tail -n +2)
    fi
    (( suspicious == 0 )) && ok "No anomalous established connections detected"

    echo ""
    info "Network interface counters (errors/drops):"
    if [[ -f /proc/net/dev ]]; then
        awk 'NR>2{
            iface=$1; rx_bytes=$2; rx_err=$4; tx_bytes=$10; tx_err=$12
            if(rx_err+tx_err > 0)
                printf "  \033[38;5;220m[!] %s  RX_err=%s  TX_err=%s\033[0m\n", iface, rx_err, tx_err
            else
                printf "  \033[38;5;46m[OK]\033[0m %s  RX=%.1fMB TX=%.1fMB\n", iface, rx_bytes/1048576, tx_bytes/1048576
        }' /proc/net/dev
    fi
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 4: Log Anomaly Triage
# ──────────────────────────────────────────────────────────────────────
SUSPICIOUS_PATTERNS=(
    "Failed password" "authentication failure" "BREAK-IN ATTEMPT"
    "Invalid user" "Connection closed by" "Disconnected from"
    "sudo:" "su:" "COMMAND=" "segfault" "oom-kill" "Out of memory"
    "possible SYN flooding" "kernel: BUG" "kernel: WARNING"
    "rootkit" "suspicious" "unauthorized" "privilege escalation"
)

mod_log() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ LOG ANOMALY TRIAGE ━━${R}\n"
    local LOG_PATHS=(
        "/var/log/auth.log" "/var/log/secure" "/var/log/syslog"
        "/var/log/kern.log" "/var/log/dmesg" "/var/log/messages"
        "/data/data/com.termux/files/usr/var/log/dpkg.log"
    )
    local scanned=0 hits=0
    for log in "${LOG_PATHS[@]}"; do
        [[ -r "$log" ]] || continue
        scanned=$(( scanned + 1 ))
        info "Scanning: $log"
        for pattern in "${SUSPICIOUS_PATTERNS[@]}"; do
            local matches
            matches=$(grep -ic "$pattern" "$log" 2>/dev/null || echo 0)
            if (( matches > 0 )); then
                warn "[$matches hits] Pattern: '$pattern' in $log"
                grep -i "$pattern" "$log" 2>/dev/null | tail -3 | while IFS= read -r line; do
                    echo -e "      ${FG_GRAY}└ ${line}${R}"
                done
                hits=$(( hits + 1 ))
            fi
        done
    done
    echo ""
    (( scanned == 0 )) && warn "No standard log files found/readable in this environment"
    (( hits == 0 && scanned > 0 )) && ok "No suspicious patterns found in $scanned log file(s)"
    (( hits > 0 )) && crit "Found $hits suspicious pattern(s) across $scanned log file(s)"
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 5: Process Anomaly Scan
# ──────────────────────────────────────────────────────────────────────
mod_proc() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ PROCESS ANOMALY SCAN ━━${R}\n"
    info "Checking for processes running deleted binaries..."
    local deleted=0
    for pid in /proc/[0-9]*/exe; do
        [[ -L "$pid" ]] || continue
        local target; target=$(readlink "$pid" 2>/dev/null || echo "")
        if echo "$target" | grep -q "(deleted)"; then
            local pname; pname=$(cat "$(dirname "$pid")/comm" 2>/dev/null || echo "unknown")
            warn "PID $(basename "$(dirname "$pid")"): running deleted binary — $pname ($target)"
            deleted=1
        fi
    done
    (( deleted == 0 )) && ok "No processes running deleted executables"

    echo ""
    info "Top 5 CPU/RAM consumers:"
    if command -v ps &>/dev/null; then
        ps aux --no-header 2>/dev/null | sort -rk3 | head -5 | \
            awk '{printf "  \033[38;5;51m%-20s\033[0m PID:%-6s CPU:%s%%  MEM:%s%%\n", $11, $2, $3, $4}'
    fi
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 6: Cron & Persistence Audit
# ──────────────────────────────────────────────────────────────────────
mod_cron() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ CRON & PERSISTENCE AUDIT ━━${R}\n"
    local cron_paths=(
        "/etc/crontab" "/etc/cron.d" "/etc/cron.daily" "/etc/cron.hourly"
        "/etc/cron.weekly" "/var/spool/cron/crontabs"
        "/data/data/com.termux/files/usr/var/spool/cron/crontabs"
    )
    info "Scanning cron locations..."
    local found=0
    for path in "${cron_paths[@]}"; do
        if [[ -f "$path" && -r "$path" ]]; then
            echo -e "  ${FG_CYAN}$path:${R}"
            grep -v '^#\|^$' "$path" 2>/dev/null | while IFS= read -r line; do
                echo -e "    ${FG_YELLOW}$line${R}"
            done
            found=1
        elif [[ -d "$path" ]]; then
            for f in "$path"/*; do
                [[ -f "$f" && -r "$f" ]] || continue
                echo -e "  ${FG_CYAN}$f:${R}"
                grep -v '^#\|^$' "$f" 2>/dev/null | head -10 | while IFS= read -r line; do
                    echo -e "    ${FG_YELLOW}$line${R}"
                done
                found=1
            done
        fi
    done
    (( found == 0 )) && ok "No cron files found/readable in this environment"

    echo ""
    info "Checking shell startup files for anomalous entries..."
    local startup_files=("$HOME/.bashrc" "$HOME/.bash_profile" "$HOME/.profile"
                         "$HOME/.zshrc" "/etc/profile" "/etc/bash.bashrc")
    for f in "${startup_files[@]}"; do
        [[ -r "$f" ]] || continue
        if grep -qE 'curl|wget.*sh|bash -i|/dev/tcp|nc -e|python.*-c.*exec' "$f" 2>/dev/null; then
            crit "Suspicious entry in startup file: $f"
            grep -nE 'curl|wget.*sh|bash -i|/dev/tcp|nc -e|python.*-c.*exec' "$f" | \
                while IFS= read -r line; do echo -e "    ${FG_RED}$line${R}"; done
        else
            ok "$f — clean"
        fi
    done
}

# ──────────────────────────────────────────────────────────────────────
# MODULE 7: Stealth HUD (live telemetry overlay)
# ──────────────────────────────────────────────────────────────────────
mod_stealth() {
    echo -e "\n${FG_PURPLE}${BOLD}━━ STEALTH LIVE HUD ━━${R}"
    echo -e " ${FG_GRAY}(Press Ctrl+C to exit live mode)${R}\n"
    local iters=0 max_iters=120
    while (( iters < max_iters )); do
        local ts; ts=$(date '+%H:%M:%S')
        local load; load=$(cat /proc/loadavg 2>/dev/null | cut -d' ' -f1-3)
        local mem_free; mem_free=$(awk '/MemAvailable/{printf "%.0fMB",$2/1024}' /proc/meminfo 2>/dev/null || echo "?")
        local conn_count=0
        command -v ss &>/dev/null && conn_count=$(ss -tn state established 2>/dev/null | wc -l)
        local tcp_wait; tcp_wait=$(ss -tan 2>/dev/null | grep -c TIME-WAIT || echo 0)

        printf "\r ${FG_CYAN}[%s]${R} ${FG_WHITE}Load:${R} ${FG_YELLOW}%-12s${R} ${FG_WHITE}RAM Free:${R} ${FG_GREEN}%-8s${R} ${FG_WHITE}Conns:${R} ${FG_MAGENTA}%3s${R} ${FG_WHITE}TW:${R} ${FG_GRAY}%s${R}" \
            "$ts" "$load" "$mem_free" "$conn_count" "$tcp_wait"
        sleep 1
        iters=$(( iters + 1 ))
    done
    echo ""
}

# ──────────────────────────────────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────────────────────────────────
_show_menu() {
    header
    echo -e " ${FG_CYAN}[1]${R} ${FG_WHITE}Memory Triage${R}          ${FG_GRAY}— Large anon regions, RAM pressure, page stats${R}"
    echo -e " ${FG_CYAN}[2]${R} ${FG_WHITE}Entropy Scanner${R}        ${FG_GRAY}— Detect packed/encrypted binaries in key dirs${R}"
    echo -e " ${FG_CYAN}[3]${R} ${FG_WHITE}Network Telemetry${R}      ${FG_GRAY}— Listening ports, anomalous connections, IF stats${R}"
    echo -e " ${FG_CYAN}[4]${R} ${FG_WHITE}Log Anomaly Triage${R}     ${FG_GRAY}— Scan auth/syslog for brute-force & intrusion${R}"
    echo -e " ${FG_CYAN}[5]${R} ${FG_WHITE}Process Scan${R}           ${FG_GRAY}— Deleted-exe procs, resource hogs${R}"
    echo -e " ${FG_CYAN}[6]${R} ${FG_WHITE}Cron & Persistence${R}     ${FG_GRAY}— Crontab audit, startup file anomaly check${R}"
    echo -e " ${FG_CYAN}[7]${R} ${FG_WHITE}Stealth Live HUD${R}       ${FG_GRAY}— Live load/RAM/connections telemetry overlay${R}"
    echo -e " ${FG_CYAN}[A]${R} ${FG_WHITE}Run All Modules${R}        ${FG_GRAY}— Full forensic sweep (save output to report)${R}"
    echo -e " ${FG_CYAN}[0]${R} ${FG_RED}Exit DarkTrace${R}"
    echo ""
}

_run_all() {
    header
    local report="$HOME/asterix_persistent/darktrace-$(date +%Y%m%d-%H%M%S).report"
    mkdir -p "$(dirname "$report")" 2>/dev/null
    echo -e " ${FG_CYAN}[*] Running all modules — output: ${FG_YELLOW}$report${R}\n"
    {
        echo "=== ASTERIX DARKTRACE REPORT === $(date)"
        mod_mem; mod_entropy; mod_net; mod_log; mod_proc; mod_cron
        echo "=== END REPORT ==="
    } | tee "$report"
    echo ""
    ok "Report saved to: $report"
}

MODULE="${1:-}"
case "$MODULE" in
    mem|memory)     header; mod_mem  ;;
    entropy)        header; mod_entropy ;;
    net|network)    header; mod_net  ;;
    log|logs)       header; mod_log  ;;
    proc|process)   header; mod_proc ;;
    cron)           header; mod_cron ;;
    stealth|hud)    header; mod_stealth ;;
    all)            _run_all ;;
    help|--help|-h)
        header
        echo -e " ${FG_WHITE}USAGE:${R}  ax darktrace [module]"
        echo -e " ${FG_CYAN}MODULES:${R}  mem | entropy | net | log | proc | cron | stealth | all"
        ;;
    "")
        while true; do
            _show_menu
            read -rp "$(echo -e " ${FG_CYAN}${BOLD}DARKTRACE » ${R}")" choice
            case "$choice" in
                1) header; mod_mem;     read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                2) header; mod_entropy; read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                3) header; mod_net;     read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                4) header; mod_log;     read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                5) header; mod_proc;    read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                6) header; mod_cron;    read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                7) header; mod_stealth ;;
                [Aa]) _run_all;         read -rp $'\n\033[38;5;243mPress Enter...\033[0m' ;;
                0|q|exit) break ;;
                *) ;;
            esac
        done
        ;;
    *)
        echo -e "${FG_RED}[!] Unknown module: $MODULE${R}  (use: ax darktrace help)"
        exit 1
        ;;
esac