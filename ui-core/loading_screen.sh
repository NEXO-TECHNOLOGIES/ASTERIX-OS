#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS — Multi-Mode Cyber Linux Bootloader v5.0
# 3 distinct live boot themes in one script:
#   1) blackmirror  -> darker "Black Mirror" Linux boot
#   2) neon        -> neon cyberpunk KDE-style startup
#   3) stealth     -> next-gen stealth OS loader with motion + glow
# =====================================================================

R='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'; REVERSE='\033[7m'
FG_DARK='\033[38;5;238m'; FG_GRAY='\033[38;5;245m'; FG_LIGHT='\033[38;5;252m'
FG_GREEN='\033[38;5;46m'; FG_DARKGREEN='\033[38;5;22m'
FG_CYAN='\033[38;5;51m'; FG_SKY='\033[38;5;117m'
FG_MAGENTA='\033[38;5;201m'; FG_PURPLE='\033[38;5;141m'
FG_RED='\033[38;5;196m'; FG_ORANGE='\033[38;5;214m'
FG_YELLOW='\033[38;5;220m'; FG_WHITE='\033[38;5;231m'
BG_BLACK='\033[48;5;16m'; BG_DARK='\033[48;5;236m'; BG_NEON='\033[48;5;18m'
BG_DEEPBLUE='\033[48;5;17m'; BG_VIOLET='\033[48;5;54m'; BG_CYAN='\033[48;5;23m'; BG_INDIGO='\033[48;5;53m'
BG_STEALTH='\033[48;5;22m'; BG_ASH='\033[48;5;240m'

COLS=${COLUMNS:-$(tput cols 2>/dev/null || printf '92')}
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
DEFAULT_SETTINGS_FILE="${HOME}/.config/asterix/loading_screen.conf"
SETTINGS_FILE="${ASTERIX_LOADING_SETTINGS:-$DEFAULT_SETTINGS_FILE}"
if [[ -z "${ASTERIX_LOADING_SETTINGS}" ]] && [[ ! -d "$(dirname "$SETTINGS_FILE")" ]]; then
    SETTINGS_FILE="${SCRIPT_DIR}/loading_screen.conf"
fi
FAST=0
MODE='blackmirror'
PROFILE='medium'
PACKAGE_NAME='asterix'
PACKAGE_CATEGORY='general'
DEVICE_CLASS='desktop'
DEVICE_NAME='ASTERIX NODE'
USER_IDENTITY=''
BACKGROUND_THEME='neon'
BACKGROUND_STYLE='gradient'
BACKGROUND_INTENSITY='medium'
BOOT_SOUND_STYLE='pulse'
TELEMETRY_STYLE='standard'
LOGIN_THEME='default'

load_settings() {
    if [[ -f "$SETTINGS_FILE" ]]; then
        while IFS='=' read -r key value; do
            key="${key//[[:space:]]/}"
            value="${value#\"}"
            value="${value%\"}"
            case "$key" in
                MODE) MODE="$value" ;;
                PROFILE) PROFILE="$value" ;;
                PACKAGE_NAME) PACKAGE_NAME="$value" ;;
                PACKAGE_CATEGORY) PACKAGE_CATEGORY="$value" ;;
                DEVICE_CLASS) DEVICE_CLASS="$value" ;;
                DEVICE_NAME) DEVICE_NAME="$value" ;;
                USER_IDENTITY) USER_IDENTITY="$value" ;;
                BACKGROUND_THEME) BACKGROUND_THEME="$value" ;;
                BACKGROUND_STYLE) BACKGROUND_STYLE="$value" ;;
                BACKGROUND_INTENSITY) BACKGROUND_INTENSITY="$value" ;;
                BOOT_SOUND_STYLE) BOOT_SOUND_STYLE="$value" ;;
                TELEMETRY_STYLE) TELEMETRY_STYLE="$value" ;;
                LOGIN_THEME) LOGIN_THEME="$value" ;;
            esac
        done < "$SETTINGS_FILE"
    fi
}

save_settings() {
    mkdir -p "$(dirname "$SETTINGS_FILE")"
    cat > "$SETTINGS_FILE" <<EOF
MODE=${MODE}
PROFILE=${PROFILE}
PACKAGE_NAME=${PACKAGE_NAME}
PACKAGE_CATEGORY=${PACKAGE_CATEGORY}
DEVICE_CLASS=${DEVICE_CLASS}
DEVICE_NAME=${DEVICE_NAME}
USER_IDENTITY=${USER_IDENTITY}
BACKGROUND_THEME=${BACKGROUND_THEME}
BACKGROUND_STYLE=${BACKGROUND_STYLE}
BACKGROUND_INTENSITY=${BACKGROUND_INTENSITY}
BOOT_SOUND_STYLE=${BOOT_SOUND_STYLE}
TELEMETRY_STYLE=${TELEMETRY_STYLE}
LOGIN_THEME=${LOGIN_THEME}
EOF
}

show_settings() {
    echo "ASTERIX boot settings"
    echo "config file: ${SETTINGS_FILE}"
    echo "MODE=${MODE}"
    echo "PROFILE=${PROFILE}"
    echo "PACKAGE_NAME=${PACKAGE_NAME}"
    echo "PACKAGE_CATEGORY=${PACKAGE_CATEGORY}"
    echo "DEVICE_CLASS=${DEVICE_CLASS}"
    echo "DEVICE_NAME=${DEVICE_NAME}"
    echo "USER_IDENTITY=${USER_IDENTITY}"
    echo "BACKGROUND_THEME=${BACKGROUND_THEME}"
    echo "BACKGROUND_STYLE=${BACKGROUND_STYLE}"
    echo "BACKGROUND_INTENSITY=${BACKGROUND_INTENSITY}"
    echo "BOOT_SOUND_STYLE=${BOOT_SOUND_STYLE}"
    echo "TELEMETRY_STYLE=${TELEMETRY_STYLE}"
    echo "LOGIN_THEME=${LOGIN_THEME}"
}

interactive_settings_menu() {
    if [[ ! -t 0 || ! -t 1 ]]; then
        show_settings
        return 0
    fi

    echo "ASTERIX SETTINGS"
    echo "1) Background theme: ${BACKGROUND_THEME}"
    echo "2) Background style: ${BACKGROUND_STYLE}"
    echo "3) Background intensity: ${BACKGROUND_INTENSITY}"
    echo "4) Boot loading mode: ${MODE}"
    echo "5) Login theme: ${LOGIN_THEME}"
    echo "6) Save current settings"
    echo "7) Exit"
    printf "Choose option: "
    read -r choice

    case "$choice" in
        1)
            echo "Options: neon blackmirror stealth sunset ocean"
            printf "Set background theme: "
            read -r value
            [[ -n "$value" ]] && BACKGROUND_THEME="$value"
            ;;
        2)
            echo "Options: gradient wave"
            printf "Set background style: "
            read -r value
            [[ -n "$value" ]] && BACKGROUND_STYLE="$value"
            ;;
        3)
            echo "Options: low medium high"
            printf "Set background intensity: "
            read -r value
            [[ -n "$value" ]] && BACKGROUND_INTENSITY="$value"
            ;;
        4)
            echo "Options: blackmirror neon stealth random"
            printf "Set loading mode: "
            read -r value
            [[ -n "$value" ]] && MODE="$value"
            ;;
        5)
            echo "Options: default neon shadow stealth matrix"
            printf "Set login theme: "
            read -r value
            [[ -n "$value" ]] && LOGIN_THEME="$value"
            ;;
        6)
            save_settings
            echo "Saved to ${SETTINGS_FILE}"
            ;;
        *)
            echo "Exiting settings menu"
            ;;
    esac

    if [[ "$choice" != "7" && "$choice" != "*" ]]; then
        interactive_settings_menu
    fi
}

load_settings

for arg in "$@"; do
    case "$arg" in
        --fast) FAST=1 ;;
        --mode) shift; MODE="${1:-$MODE}" ;;
        --profile) shift; PROFILE="${1:-$PROFILE}" ;;
        --package) shift; PACKAGE_NAME="${1:-$PACKAGE_NAME}" ;;
        --category) shift; PACKAGE_CATEGORY="${1:-$PACKAGE_CATEGORY}" ;;
        --device) shift; DEVICE_NAME="${1:-$DEVICE_NAME}" ;;
        --device-class) shift; DEVICE_CLASS="${1:-$DEVICE_CLASS}" ;;
        --identity|--user|--name) shift; USER_IDENTITY="${1:-$USER_IDENTITY}" ;;
        --background|--bg|--theme) shift; BACKGROUND_THEME="${1:-$BACKGROUND_THEME}" ;;
        --background-style) shift; BACKGROUND_STYLE="${1:-$BACKGROUND_STYLE}" ;;
        --background-intensity) shift; BACKGROUND_INTENSITY="${1:-$BACKGROUND_INTENSITY}" ;;
        --settings|settings) interactive_settings_menu; exit 0 ;;
        --show-settings|--show) show_settings; exit 0 ;;
        --save-settings) save_settings; echo "Saved loading settings to ${SETTINGS_FILE}"; exit 0 ;;
        blackmirror|neon|stealth|random) MODE="$arg" ;;
        light|medium|heavy) PROFILE="$arg" ;;
        desktop|laptop|tablet|phone|server|gui|kde|plasma|workspace|ui|kernel|core|hypercore|system|boot|security|privacy|defender|hardened|media|audio|dev|tools|general) PACKAGE_CATEGORY="$arg" ;;
    esac
done

[[ -n "${CI:-}" ]] && FAST=1
_sleep() { [[ $FAST -eq 0 ]] && sleep "$1"; }

resolve_identity_name() {
    if [[ -n "${USER_IDENTITY}" ]]; then
        return
    fi

    USER_IDENTITY="${USER:-${USER_NAME:-asterix-user}}"
    if [[ -z "${USER_IDENTITY}" || "${USER_IDENTITY}" == "root" ]]; then
        USER_IDENTITY='asterix-user'
    fi

    if [[ -t 0 ]] && [[ "${USER_IDENTITY}" == "asterix-user" ]]; then
        printf '\033[2K\r\033[38;5;220mIdentity name: \033[0m' >&2
        IFS= read -r USER_IDENTITY
        if [[ -z "${USER_IDENTITY}" ]]; then
            USER_IDENTITY='asterix-user'
        fi
        printf '\n' >&2
    fi
}

_detect_device() {
    local chassis='' product='' sys_vendor='' model=''

    if command -v hostnamectl >/dev/null 2>&1; then
        chassis=$(hostnamectl 2>/dev/null | tr '[:upper:]' '[:lower:]' | grep -E 'chassis|hardware' || true)
        if [[ -n "$chassis" ]]; then
            if echo "$chassis" | grep -qiE 'laptop|notebook|tablet|convertible'; then
                DEVICE_CLASS='laptop'
            elif echo "$chassis" | grep -qiE 'desktop|tower|mini.*desktop|all in one'; then
                DEVICE_CLASS='desktop'
            fi
        fi
    fi

    if [[ -f /sys/class/dmi/id/chassis_type ]]; then
        chassis=$(tr -d '\n' < /sys/class/dmi/id/chassis_type)
        case "$chassis" in
            8|9|10|11|14|15|17|18)
                DEVICE_CLASS='laptop'
                ;;
            3|4|5|6|7|13)
                DEVICE_CLASS='desktop'
                ;;
        esac
    fi

    if [[ -f /sys/class/dmi/id/product_name ]]; then
        product=$(tr -d '\n' < /sys/class/dmi/id/product_name | tr '[:upper:]' '[:lower:]')
        case "$product" in
            *laptop*|*notebook*|*thinkpad*|*surface*|*xps*|*latitude*|*elitebook*|*book*|*chromebook*|*zenbook*)
                DEVICE_CLASS='laptop'
                DEVICE_NAME="$(tr -d '\n' < /sys/class/dmi/id/product_name)"
                ;;
            *)
                if [[ -z "$DEVICE_NAME" || "$DEVICE_NAME" == 'ASTERIX NODE' ]]; then
                    DEVICE_NAME="$(tr -d '\n' < /sys/class/dmi/id/product_name 2>/dev/null || printf 'ASTERIX NODE')"
                fi
                ;;
        esac
    fi

    if [[ -f /proc/device-tree/model ]]; then
        model=$(tr -d '\n' < /proc/device-tree/model | tr '[:upper:]' '[:lower:]')
        case "$model" in
            *laptop*|*notebook*|*book*|*surface*) DEVICE_CLASS='laptop' ;;
        esac
    fi

    case "$DEVICE_CLASS" in
        laptop)
            DEVICE_NAME="${DEVICE_NAME:-LAPTOP NODE}"
            ;;
        desktop)
            DEVICE_NAME="${DEVICE_NAME:-DESKTOP NODE}"
            ;;
        *)
            DEVICE_CLASS='desktop'
            DEVICE_NAME="${DEVICE_NAME:-DESKTOP NODE}"
            ;;
    esac
}

_apply_package_profile() {
    local pkg="${PACKAGE_NAME,,}"
    local cat="${PACKAGE_CATEGORY,,}"

    _detect_device

    case "$pkg" in
        desktop|gui|kde|plasma|workspace|ui|desktop-env|asterix-desktop)
            MODE='neon'
            cat='desktop'
            ;;
        kernel|core|hypercore|system|boot|asterix-kernel|asterix-core)
            MODE='blackmirror'
            cat='kernel'
            ;;
        security|privacy|stealth|defender|hardened|asterix-defender|asterix-security|secure-chat)
            MODE='stealth'
            cat='security'
            ;;
        media|audio|video|stream|multimedia)
            MODE='neon'
            cat='media'
            ;;
        dev|tools|compiler|builder|code|sdk)
            MODE='blackmirror'
            cat='dev'
            ;;
        *)
            MODE="${MODE:-blackmirror}"
            ;;
    esac

    case "$cat" in
        desktop|gui|ui|kde|plasma)
            MODE='neon'
            BOOT_SOUND_STYLE='synth'
            TELEMETRY_STYLE='pulse'
            LOGIN_THEME='neon'
            ;;
        kernel|core|system|boot)
            MODE='blackmirror'
            BOOT_SOUND_STYLE='hollow'
            TELEMETRY_STYLE='spectral'
            LOGIN_THEME='shadow'
            ;;
        security|privacy|defender|stealth|hardened)
            MODE='stealth'
            BOOT_SOUND_STYLE='low'
            TELEMETRY_STYLE='stealth'
            LOGIN_THEME='stealth'
            ;;
        media|audio|video)
            MODE='neon'
            BOOT_SOUND_STYLE='pulse'
            TELEMETRY_STYLE='wave'
            LOGIN_THEME='neon'
            ;;
        dev|tools|compiler)
            MODE='blackmirror'
            BOOT_SOUND_STYLE='scan'
            TELEMETRY_STYLE='grid'
            LOGIN_THEME='matrix'
            ;;
        *)
            BOOT_SOUND_STYLE='pulse'
            TELEMETRY_STYLE='standard'
            LOGIN_THEME='default'
            ;;
    esac

    if [[ "$DEVICE_CLASS" == "laptop" ]]; then
        MODE='blackmirror'
        BOOT_SOUND_STYLE='low'
        TELEMETRY_STYLE='stealth'
        LOGIN_THEME='shadow'
    elif [[ "$DEVICE_CLASS" == "desktop" ]]; then
        MODE='neon'
        BOOT_SOUND_STYLE='synth'
        TELEMETRY_STYLE='pulse'
        LOGIN_THEME='neon'
    fi

    case "$PROFILE" in
        light)
            PROFILE='light'
            ;;
        heavy)
            PROFILE='heavy'
            ;;
        *)
            PROFILE='medium'
            ;;
    esac

    PACKAGE_CATEGORY="$cat"
    PACKAGE_NAME="${PACKAGE_NAME:-asterix}"
}

_play_boot_sound() {
    case "$BOOT_SOUND_STYLE" in
        synth)
            printf '\a'; sleep 0.05; printf '\a'; sleep 0.05; printf '\a';
            ;;
        hollow)
            printf '\a'; sleep 0.12; printf '\a';
            ;;
        low)
            printf '\a'; sleep 0.18; printf '\a'; sleep 0.1; printf '\a';
            ;;
        scan)
            printf '\a'; sleep 0.04; printf '\a'; sleep 0.04; printf '\a'; sleep 0.04; printf '\a';
            ;;
        *)
            printf '\a'; sleep 0.08; printf '\a';
            ;;
    esac
}

hrule() {
    local char="${1:--}" col="${2:-$FG_CYAN}" w="${3:-$COLS}"
    printf '%b\n' "${col}$(printf "%${w}s" | tr ' ' "$char")${R}"
}

set_bg() {
    local color="${1:-$BG_BLACK}"
    printf '%b' "${color}"
}

_background_cycle() {
    local palette=()
    case "$MODE" in
        blackmirror)
            palette=("$BG_BLACK" "$BG_DEEPBLUE" "$BG_VIOLET" "$BG_INDIGO" "$BG_DARK")
            ;;
        neon)
            palette=("$BG_NEON" "$BG_DEEPBLUE" "$BG_CYAN" "$BG_VIOLET" "$BG_BLACK")
            ;;
        stealth)
            palette=("$BG_STEALTH" "$BG_BLACK" "$BG_ASH" "$BG_DARK" "$BG_STEALTH")
            ;;
        *)
            palette=("$BG_BLACK" "$BG_DEEPBLUE" "$BG_VIOLET" "$BG_INDIGO" "$BG_DARK")
            ;;
    esac

    local i=0
    for color in "${palette[@]}"; do
        set_bg "$color"
        [[ $FAST -eq 0 ]] && sleep 0.08
        i=$(( i + 1 ))
    done
    set_bg "${palette[0]}"
}

_typewriter_echo() {
    local text="$1" color="${2:-$FG_CYAN}" delay="${3:-0.012}"
    local i ch
    for (( i=0; i<${#text}; i++ )); do
        ch="${text:$i:1}"
        printf '%b%s' "$color" "$ch"
        [[ $FAST -eq 0 ]] && sleep "$delay"
    done
    printf '%b' "$R"
}

_scanlines() {
    local line
    for (( line=0; line<${LINES:-32}; line++ )); do
        printf '%b' "$FG_DARK"
        printf '%*s\n' "$COLS" '' | tr ' ' '─'
        [[ $FAST -eq 0 ]] && sleep 0.008
    done
    printf '%b' "$R"
}

_glitch_burst() {
    local i
    for (( i=0; i<5; i++ )); do
        local x=$(( RANDOM % 20 + 5 ))
        local y=$(( RANDOM % 8 + 2 ))
        printf '\n'
        printf '\033[%dG' "$x"
        printf '%b' "$FG_MAGENTA"
        printf '%*s' "$y" '' | tr ' ' '▒'
        printf '%b' "$R"
        [[ $FAST -eq 0 ]] && sleep 0.05
    done
}

_spinner_frame() {
    local idx="$1"
    local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    printf '%b%s%b' "$FG_CYAN" "${frames[$idx]}" "$R"
}

_draw_spinner() {
    local i
    for (( i=0; i<10; i++ )); do
        printf '\r  %b' "$FG_CYAN"
        _spinner_frame "$i"
        printf ' %bLOADING ASTERIX ...%b' "$FG_WHITE" "$R"
        [[ $FAST -eq 0 ]] && sleep 0.05
    done
}

_resolve_background_theme() {
    case "$BACKGROUND_THEME" in
        blackmirror|midnight|void)
            BACKGROUND_THEME='blackmirror'
            BACKGROUND_STYLE='gradient'
            ;;
        neon|cyber|plasma)
            BACKGROUND_THEME='neon'
            BACKGROUND_STYLE='wave'
            ;;
        stealth|hush|shadow)
            BACKGROUND_THEME='stealth'
            BACKGROUND_STYLE='wave'
            ;;
        sunset|solar|amber)
            BACKGROUND_THEME='sunset'
            BACKGROUND_STYLE='gradient'
            ;;
        ocean|aqua|deep)
            BACKGROUND_THEME='ocean'
            BACKGROUND_STYLE='wave'
            ;;
        *)
            BACKGROUND_THEME='neon'
            BACKGROUND_STYLE='wave'
            ;;
    esac

    case "$BACKGROUND_INTENSITY" in
        low|soft) BACKGROUND_INTENSITY='low' ;;
        high|strong) BACKGROUND_INTENSITY='high' ;;
        *) BACKGROUND_INTENSITY='medium' ;;
    esac
}

_render_fullscreen_gradient() {
    local rows="${LINES:-38}"
    local cols="${COLS:-120}"
    local palette=(18 19 20 21 27 45 51 57 93 105 117 201 213 219)
    local r c idx

    _resolve_background_theme

    case "$BACKGROUND_THEME" in
        blackmirror)
            palette=(16 17 18 19 20 53 54 57 93 117 201 219)
            ;;
        neon)
            palette=(18 19 20 21 27 45 51 57 93 105 117 201 213 219)
            ;;
        stealth)
            palette=(22 23 24 16 17 18 19 20 28 29 30 31 54)
            ;;
        sunset)
            palette=(52 58 94 166 214 208 202 196 190 178)
            ;;
        ocean)
            palette=(17 18 19 20 23 24 25 27 30 45 51 57 63)
            ;;
    esac

    if [[ "$BACKGROUND_INTENSITY" == "low" ]]; then
        palette=(18 19 20 21 27 45)
    elif [[ "$BACKGROUND_INTENSITY" == "high" ]]; then
        palette=(17 18 19 20 27 45 51 57 63 93 117 201 213 219 226)
    fi

    printf '\033[H\033[2J'
    for (( r=0; r<rows; r++ )); do
        for (( c=0; c<cols; c++ )); do
            idx=$(( (r + c) % ${#palette[@]} ))
            printf '\033[48;5;%sm ' "${palette[idx]}"
        done
        printf '\033[0m\n'
    done
    printf '\033[0m'
}

_render_neon_wave() {
    local rows="${LINES:-38}"
    local cols="${COLS:-120}"
    local r c wave_char wave_color='45'
    _resolve_background_theme

    case "$BACKGROUND_THEME" in
        blackmirror)
            wave_color='21'
            ;;
        neon)
            wave_color='45'
            ;;
        stealth)
            wave_color='34'
            ;;
        sunset)
            wave_color='214'
            ;;
        ocean)
            wave_color='51'
            ;;
    esac

    for (( r=0; r<rows; r++ )); do
        printf '\033[%d;1H' $(( r + 1 ))
        for (( c=0; c<cols; c++ )); do
            wave_char=' '
            if (( (c + r*2) % 13 < 3 )); then
                wave_char='~'
                printf '\033[38;5;%sm%s' "$wave_color" "$wave_char"
            elif (( (c + r*3) % 17 < 2 )); then
                wave_char='·'
                printf '\033[38;5;%sm%s' "$(( wave_color + 20 ))" "$wave_char"
            else
                printf ' '
            fi
        done
        printf '\033[0m'
        [[ $FAST -eq 0 ]] && sleep 0.015
    done
    printf '\033[0m'
}

_play_welcome_overlay() {
    local rows="${LINES:-38}"
    local cols="${COLS:-120}"
    local center=$(( cols / 2 - 18 ))
    local tag="DEVICE: ${DEVICE_NAME} | TYPE: ${DEVICE_CLASS}"
    local pulse_delay=0.18

    case "$PROFILE" in
        light)
            pulse_delay=0.12
            ;;
        heavy)
            pulse_delay=0.24
            ;;
        *)
            pulse_delay=0.18
            ;;
    esac

    clear
    _resolve_background_theme
    if [[ "$BACKGROUND_STYLE" == "gradient" ]]; then
        _render_fullscreen_gradient
    else
        _render_neon_wave
    fi

    printf '\033[H'
    printf '\033[%d;1H' $(( rows / 4 ))
    printf '\033[38;5;45m\033[1m%s\033[0m\n' "$(printf '%*s' "$cols" '' | tr ' ' ' ')"

    printf '\033[%d;1H' $(( rows / 2 - 2 ))
    printf '\033[38;5;255m\033[1m%*s\033[0m\n' "$cols" '' | tr ' ' ' '
    printf '\033[%d;%dH' $(( rows / 2 - 1 )) "$center"
    printf '\033[38;5;51m\033[1mASTERIX OS\033[0m'
    printf '\033[%d;%dH' $(( rows / 2 + 1 )) "$(( center - 4 ))"
    printf '\033[38;5;213mHYPERCORE EDITION\033[0m'

    printf '\033[%d;%dH' $(( rows / 2 + 4 )) "$(( center - 10 ))"
    _typewriter_echo "INITIALIZING ${PACKAGE_NAME^^} FOR ${USER_IDENTITY^^}" "$FG_CYAN" 0.025
    printf '\n'
    for (( i=0; i<4; i++ )); do
        printf '\033[%d;%dH' $(( rows / 2 + 6 + i )) "$(( center - 14 ))"
        printf '\033[38;5;153m>\033[0m '
        printf '\033[38;5;87m%s\033[0m' "SYSTEM ${i} ONLINE"
        [[ $FAST -eq 0 ]] && sleep "$pulse_delay"
    done

    printf '\033[%d;%dH' $(( rows - 4 )) "$(( cols / 2 - 18 ))"
    printf '\033[38;5;220m[%s : package=%s : profile=%s]\033[0m' "$tag" "$PACKAGE_NAME" "$PROFILE"
    printf '\033[0m'
}

_draw_telemetry() {
    local cpu="$1" mem="$2" net="$3"
    local cpu_bar cpu_blank mem_bar mem_blank net_bar net_blank
    local fill='█' empty='░' label_color="$FG_GREEN"

    case "$TELEMETRY_STYLE" in
        pulse)
            fill='▉'; empty='▢'; label_color="$FG_CYAN" ;;
        spectral)
            fill='▓'; empty='▒'; label_color="$FG_MAGENTA" ;;
        stealth)
            fill='▌'; empty='·'; label_color="$FG_GREEN" ;;
        wave)
            fill='━'; empty='·'; label_color="$FG_YELLOW" ;;
        grid)
            fill='▦'; empty='□'; label_color="$FG_SKY" ;;
        *)
            fill='█'; empty='░'; label_color="$FG_GREEN" ;;
    esac

    cpu_bar=$(( cpu * 18 / 100 ))
    cpu_blank=$(( 18 - cpu_bar ))
    mem_bar=$(( mem * 18 / 100 ))
    mem_blank=$(( 18 - mem_bar ))
    net_bar=$(( net * 18 / 100 ))
    net_blank=$(( 18 - net_bar ))

    printf '  %bCPU  %b%s%b%s %b\n' "$FG_YELLOW" "$label_color" "$(printf '%*s' "$cpu_bar" '' | tr ' ' "$fill")" "$FG_DARK" "$(printf '%*s' "$cpu_blank" '' | tr ' ' "$empty")" "$R"
    printf '  %bRAM  %b%s%b%s %b\n' "$FG_YELLOW" "$label_color" "$(printf '%*s' "$mem_bar" '' | tr ' ' "$fill")" "$FG_DARK" "$(printf '%*s' "$mem_blank" '' | tr ' ' "$empty")" "$R"
    printf '  %bNET  %b%s%b%s %b\n' "$FG_YELLOW" "$label_color" "$(printf '%*s' "$net_bar" '' | tr ' ' "$fill")" "$FG_DARK" "$(printf '%*s' "$net_blank" '' | tr ' ' "$empty")" "$R"
}

_glitch_char() {
    local ch="$1" intensity="$2"
    local glyphs=(' ' '#' '@' '%' '!' '?' '0' '1' 'X' '<' '>' '█' '▓' '▒' '▄' '■')
    if (( RANDOM % 100 < intensity )); then
        printf '%s' "${glyphs[$(( RANDOM % ${#glyphs[@]} ))]}"
    else
        printf '%s' "$ch"
    fi
}

_glitch_line() {
    local s="$1" intensity="$2" out=""
    for (( i=0; i<${#s}; i++ )); do
        out+="$( _glitch_char "${s:$i:1}" "$intensity" )"
    done
    printf '%s' "$out"
}

pick_mode() {
    if [[ "$MODE" == "random" ]]; then
        local list=(blackmirror neon stealth)
        MODE="${list[$(( RANDOM % ${#list[@]} ))]}"
    fi
}

BANNER_BLACK=(
"      █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗ ███████╗"
"     ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔═══██╗██╔════╝"
"     ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║   ██║███████╗"
"     ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║   ██║╚════██║"
"     ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╔╝███████║"
"     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝"
"                                 // HYPERCORE SYSTEMS //"
"                        [ AETHER-LINK • KERNEL SYNCHRONIZATION ]"
)

BANNER_NEON=(
"      █████╗ ███╗   ██╗ █████╗ ██╗  ██╗██╗   ██╗███╗   ███╗ ██████╗ ███████╗"
"     ██╔══██╗████╗  ██║██╔══██╗██║  ██║██║   ██║████╗ ████║██╔═══██╗██╔════╝"
"     ███████║██╔██╗ ██║███████║███████║██║   ██║██╔████╔██║██║   ██║███████╗"
"     ██╔══██║██║╚██╗██║██╔══██║██╔══██║██║   ██║██║╚██╔╝██║██║   ██║╚════██║"
"     ██║  ██║██║ ╚████║██║  ██║██║  ██║╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████║"
"     ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝"
"                               // PLASMA // SIGNAL // CYBER //"
"                     [ KDE-CLASS • QUANTUM DESKTOP DOCK ONLINE ]"
)

BANNER_STEALTH=(
"        ░█████╗░██████╗░██╗░░░██╗██████╗░███████╗███████╗██╗███╗░░██╗"
"        ██╔══██╗██╔══██╗██║░░░██║██╔══██╗██╔════╝██╔════╝██║████╗░██║"
"        ███████║██████╔╝██║░░░██║██████╔╝█████╗░░█████╗░░██║██╔██╗██║"
"        ██╔══██║██╔══██╗██║░░░██║██╔═══╝░██╔══╝░░██╔══╝░░██║██║╚████║"
"        ██║░░██║██║░░██║╚██████╔╝██║░░░░░███████╗███████╗██║██║░╚███║"
"        ╚═╝░░╚═╝╚═╝░░╚═╝░╚═════╝░╚═╝░░░░░╚══════╝╚══════╝╚═╝╚═╝░░╚══╝"
"                              // AETHER HUSH //"
"                          [ SILENT KERNEL • LOW-TRACE MODE ]"
)

_banner_phase() {
    local colors=()
    local ints=()
    case "$MODE" in
        blackmirror)
            colors=("$FG_RED" "$FG_MAGENTA" "$FG_CYAN" "$FG_GREEN" "$FG_SKY")
            ints=(38 20 12 6 3)
            ;;
        neon)
            colors=("$FG_CYAN" "$FG_SKY" "$FG_MAGENTA" "$FG_YELLOW" "$FG_GREEN")
            ints=(30 22 16 10 5)
            ;;
        stealth)
            colors=("$FG_GRAY" "$FG_DARKGREEN" "$FG_GREEN" "$FG_CYAN" "$FG_LIGHT")
            ints=(16 12 8 5 2)
            ;;
        *)
            colors=("$FG_RED" "$FG_MAGENTA" "$FG_CYAN" "$FG_GREEN" "$FG_SKY")
            ints=(38 20 12 6 3)
            ;;
    esac

    [[ $FAST -eq 1 ]] && ints=(0 0 0 0 0)

    local banner_ref="BANNER_BLACK"
    [[ "$MODE" == "neon" ]] && banner_ref="BANNER_NEON"
    [[ "$MODE" == "stealth" ]] && banner_ref="BANNER_STEALTH"

    local bg_palette=("$BG_BLACK" "$BG_DEEPBLUE" "$BG_VIOLET" "$BG_INDIGO" "$BG_DARK")
    [[ "$MODE" == "neon" ]] && bg_palette=("$BG_NEON" "$BG_DEEPBLUE" "$BG_CYAN" "$BG_VIOLET" "$BG_BLACK")
    [[ "$MODE" == "stealth" ]] && bg_palette=("$BG_STEALTH" "$BG_BLACK" "$BG_ASH" "$BG_DARK" "$BG_STEALTH")

    for idx in 0 1 2 3 4; do
        set_bg "${bg_palette[$idx]}"
        [[ $FAST -eq 0 ]] && clear
        echo -e "${colors[$idx]}${BOLD}"
        for line in "${!banner_ref}[@]"; do
            printf '  %s\n' "$(_glitch_line "$line" "${intens[$idx]}")"
        done
        echo -e "${R}"
        _sleep 0.08
    done
    set_bg "${bg_palette[0]}"
}

_show_side_panel() {
    local pct="$1" mode="$2"
    local used=$(( pct * 48 / 100 ))
    local rem=$(( 48 - used ))

    printf '  %s%s%s %s%3d%%%s\n' \
        "${FG_CYAN}" "[${mode}]" "${R}" \
        "${FG_YELLOW}" "$pct" "${R}"
    printf '  %s' "${FG_GREEN}"
    printf '%*s' "$used" '' | tr ' ' '▓'
    printf '%s' "${FG_DARK}"
    printf '%*s' "$rem" '' | tr ' ' '░'
    printf '%s\n' "${R}"
}

BOOT_STEPS=(
    "KERNEL_INIT:Booting ASTERIX Hypercore v4.9.0-sec"
    "MEMORY_MAP:Locking DMA rings and page tables"
    "QUANTUM_VAULT:Initialization of ChaCha20 + AES-256-GCM"
    "CALL_GATE:Syscall hardening and eBPF anchors"
    "PERSIST_MOUNT:Mounting persistent AETHER volume"
    "CONTAINER_SYNC:Rootless Debian runtime handshake"
    "NET_SENTINEL:TCP/UDP port sentinel online"
    "CRYPTO_CORE:ARX-512 and AXCIPH02 cores active"
    "ANOMALY_LAB:DarkTrace + LogHunter scanning"
    "AUXILIARY_AUDIT:Guard sensors and kernel telemetry"
    "MASTER_SHELL:ASTERIX control plane operational"
)

_step_meter() {
    local pct="$1" w=26
    local done=$(( pct * w / 100 ))
    local left=$(( w - done ))
    printf '%b%s%b%s' "$FG_CYAN" "$(printf '%*s' "$done" '' | tr ' ' '█')" "$FG_DARK" "$(printf '%*s' "$left" '' | tr ' ' '░')"
}

_run_boot() {
    local total="${#BOOT_STEPS[@]}" count=0 delay=0.07
    [[ $FAST -eq 1 ]] && delay=0.004

    _play_boot_sound
    echo ""
    hrule '═' "$FG_CYAN"
    case "$MODE" in
        blackmirror)
            printf ' %b%-80s%b\n' "$FG_WHITE" "[ ASTERIX BLACK MIRROR BOOTLINE — LIVE KERNEL PREP ]" "$R"
            ;;
        neon)
            printf ' %b%-80s%b\n' "$FG_CYAN" "[ ASTERIX KDE-STYLE CYBER STARTUP — PLASMA LINK ACTIVE ]" "$R"
            ;;
        stealth)
            printf ' %b%-80s%b\n' "$FG_GREEN" "[ ASTERIX STEALTH CORE BOOTLINE — LOW-TRACE SYSTEM ONLINE ]" "$R"
            ;;
        *)
            printf ' %b%-80s%b\n' "$FG_WHITE" "[ ASTERIX HYPERCORE BOOTLINE — LIVE SYSTEM INITIALIZATION ]" "$R"
            ;;
    esac
    hrule '═' "$FG_CYAN"
    echo ""

    for item in "${BOOT_STEPS[@]}"; do
        IFS=':' read -r key desc <<< "$item"
        count=$(( count + 1 ))
        local pct=$(( count * 100 / total ))

        if (( count % 2 == 0 )); then
            _background_cycle
        fi

        if (( RANDOM % 100 < 25 )); then
            _glitch_burst
        fi

        for p in 22 48 73 100; do
            printf '\r  %b[%b%-18s%b]%b %-34s %b %3d%% %b' \
                "$FG_CYAN" "$BOLD" "$key" "$R" "$FG_CYAN" "$desc" \
                "$(_step_meter "$p")" "$p" "$R"
            [[ $FAST -eq 0 ]] && sleep 0.012
        done

        printf '\r  %b[%b%-18s%b]%b %-34s %b %s%b\n' \
            "$FG_CYAN" "$BOLD" "$key" "$R" "$FG_CYAN" "$desc" "$FG_GREEN" "[ OK ]" "$R"
        _sleep "$delay"

        if (( count % 3 == 0 || count == total )); then
            printf '  %bCORE %b[%s] %b%3d%%%b\n' \
                "$FG_GRAY" "$FG_CYAN" "$(printf '%*s' $(( pct * 42 / 100 )) '' | tr ' ' '▓')$(printf '%*s' $(( 42 - pct * 42 / 100 )) '' | tr ' ' '░')" "$FG_YELLOW" "$pct" "$R"
        fi
    done

    echo ""
    _show_side_panel 38 "MEM"
    _show_side_panel 68 "CPU"
    _show_side_panel 92 "NET"
    echo ""
}

_final_splash() {
    hrule '═' "$FG_MAGENTA"
    case "$MODE" in
        blackmirror)
            local msg="[*] ALL CRITICAL SUBSYSTEMS ONLINE: BLACK MIRROR MODE STABLE"
            ;;
        neon)
            local msg="[*] ALL CRITICAL SUBSYSTEMS ONLINE: NEON KDE MODE STABLE"
            ;;
        stealth)
            local msg="[*] ALL CRITICAL SUBSYSTEMS ONLINE: STEALTH HYPERCORE STABLE"
            ;;
        *)
            local msg="[*] ALL CRITICAL SUBSYSTEMS ONLINE: ASTERIX HYPERCORE STABLE"
            ;;
    esac

    if [[ $FAST -eq 0 ]]; then
        local out=''
        for (( i=0; i<${#msg}; i++ )); do
            out+="${msg:$i:1}"
            printf '\r %b%s%b' "$FG_GREEN" "$out" "$R"
            sleep 0.012
        done
        echo ""
    else
        echo -e " ${FG_GREEN}${BOLD}${msg}${R}"
    fi

    case "$MODE" in
        blackmirror)
            echo -e " ${FG_YELLOW}Environment:${R}  ${FG_GREEN}Darktrace path • Silent monitor mesh active${R}"
            echo -e " ${FG_YELLOW}Runtime:${R}      ${FG_CYAN}Rust daemons online • Secure shell layer armed${R}"
            echo -e " ${FG_YELLOW}Status:${R}       ${FG_MAGENTA}SPECTRAL LINK ACTIVE • KERNEL HANDSHAKE CONFIRMED${R}"
            ;;
        neon)
            echo -e " ${FG_YELLOW}Environment:${R}  ${FG_GREEN}KDE Plasma shell • Neon telemetry mesh active${R}"
            echo -e " ${FG_YELLOW}Runtime:${R}      ${FG_CYAN}System pulse synced • Dashboard glow stable${R}"
            echo -e " ${FG_YELLOW}Status:${R}       ${FG_MAGENTA}AETHER-DOCK ONLINE • DESKTOP SIGNAL LOCKED${R}"
            ;;
        stealth)
            echo -e " ${FG_YELLOW}Environment:${R}  ${FG_GREEN}Low-trace root • Evasive kernel path active${R}"
            echo -e " ${FG_YELLOW}Runtime:${R}      ${FG_CYAN}Signal noise masked • Ghost routes synchronized${R}"
            echo -e " ${FG_YELLOW}Status:${R}       ${FG_MAGENTA}HUSH MODE ACTIVE • KERNEL SHADOW CONFIRMED${R}"
            ;;
    esac

    echo ""
    printf '  %b' "$FG_MAGENTA"
    for i in 1 2 3 4 5; do printf '◉ '; sleep 0.08; done
    printf '%b\n' "$R"
    echo -e " ${FG_CYAN}${BOLD}KERNEL READY${R}"
    echo -e " ${FG_YELLOW}ASTERIX OS — hypercore boot handshake complete${R}"
    echo ""
    _draw_telemetry 68 74 82
    echo ""
    printf '%b\n' "${FG_CYAN}"
    _typewriter_echo "login: ASTERIX OS // user: ${USER_IDENTITY}" "$FG_CYAN" 0.008
    printf '%b\n' "$R"
    _typewriter_echo "welcome to the AETHER shell, ${USER_IDENTITY}" "$FG_GREEN" 0.01
    printf '%b\n' "$R"
    printf '%b' "$FG_WHITE"
    printf "  ${USER_IDENTITY}@asterix:~$ "
    sleep 0.2
    printf '%b' "$FG_CYAN"
    printf 'systemctl start astx.desktop\n'
    printf '%b\n' "$R"
    hrule '═' "$FG_MAGENTA"
    echo ""
}

_login_screen() {
    clear
    set_bg "$BG_BLACK"

    case "$LOGIN_THEME" in
        neon)
            echo -e "${FG_CYAN}${BOLD}"
            printf '  %*s\n' "$(( COLS / 2 + 12 ))" ' ░▒▓██▓▒░ '
            printf '  %*s\n' "$(( COLS / 2 + 6 ))" 'ASTERIX OS'
            printf '  %*s\n' "$(( COLS / 2 + 5 ))" 'Hypercore Edition'
            echo -e "${R}"
            echo -e "  ${FG_GREEN}Kernel:${R} ${FG_WHITE}v4.9.0-sec${R}"
            echo -e "  ${FG_YELLOW}User:${R} ${FG_CYAN}${USER_IDENTITY}${R}"
            echo -e "  ${FG_MAGENTA}Session:${R} ${FG_WHITE}AETHER secure shell${R}"
            echo ""
            printf '  %b' "$FG_CYAN"
            _typewriter_echo "login: " "$FG_CYAN" 0.02
            printf '%b' "$FG_GREEN"
            printf '%s\n' "$USER_IDENTITY"
            printf '%b' "$FG_CYAN"
            _typewriter_echo "password: " "$FG_CYAN" 0.02
            printf '%b' "$FG_GREEN"
            printf '********\n'
            printf '%b\n' "$R"
            echo -e "  ${FG_GREEN}[ OK ] Login accepted${R}"
            echo -e "  ${FG_YELLOW}Welcome back to the hypercore desktop, ${USER_IDENTITY}.${R}"
            echo ""
            _draw_spinner
            echo ""
            echo -e "  ${FG_MAGENTA}ASTERIX OS ready${R}"
            ;;
        shadow)
            echo -e "${FG_WHITE}${BOLD}"
            printf '  %*s\n' "$(( COLS / 2 + 10 ))" '◈ ASTERIX HYPERCORE ◈'
            printf '  %*s\n' "$(( COLS / 2 + 7 ))" 'secure login shell'
            echo -e "${R}"
            echo -e "  ${FG_RED}Kernel:${R} ${FG_WHITE}v4.9.0-sec${R}"
            echo -e "  ${FG_YELLOW}User:${R} ${FG_CYAN}${USER_IDENTITY}${R}"
            echo -e "  ${FG_MAGENTA}Session:${R} ${FG_WHITE}kernel-guarded${R}"
            echo ""
            printf '  %b' "$FG_RED"
            _typewriter_echo "login: " "$FG_RED" 0.02
            printf '%b' "$FG_WHITE"
            printf '%s\n' "$USER_IDENTITY"
            printf '%b' "$FG_RED"
            _typewriter_echo "password: " "$FG_RED" 0.02
            printf '%b' "$FG_WHITE"
            printf '********\n'
            printf '%b\n' "$R"
            echo -e "  ${FG_GREEN}[ SECURE ] verified${R}"
            echo -e "  ${FG_YELLOW}Welcome back to the hidden kernel surface, ${USER_IDENTITY}.${R}"
            ;;
        stealth)
            echo -e "${FG_GREEN}${BOLD}"
            printf '  %*s\n' "$(( COLS / 2 + 10 ))" '── AETHER HUSH ──'
            printf '  %*s\n' "$(( COLS / 2 + 8 ))" 'low-trace session'
            echo -e "${R}"
            echo -e "  ${FG_GREEN}Kernel:${R} ${FG_WHITE}v4.9.0-sec${R}"
            echo -e "  ${FG_YELLOW}User:${R} ${FG_CYAN}${USER_IDENTITY}${R}"
            echo -e "  ${FG_MAGENTA}Session:${R} ${FG_WHITE}ghost-mode shell${R}"
            echo ""
            printf '  %b' "$FG_GREEN"
            _typewriter_echo "login: " "$FG_GREEN" 0.02
            printf '%b' "$FG_WHITE"
            printf '%s\n' "$USER_IDENTITY"
            printf '%b' "$FG_GREEN"
            _typewriter_echo "password: " "$FG_GREEN" 0.02
            printf '%b' "$FG_WHITE"
            printf '********\n'
            printf '%b\n' "$R"
            echo -e "  ${FG_GREEN}[ OK ] Session concealed${R}"
            echo -e "  ${FG_YELLOW}Welcome back to the stealth desktop, ${USER_IDENTITY}.${R}"
            ;;
        matrix)
            echo -e "${FG_GREEN}${BOLD}"
            printf '  %*s\n' "$(( COLS / 2 + 10 ))" '░▒▓ DEV MATRIX ▓▒░'
            printf '  %*s\n' "$(( COLS / 2 + 8 ))" 'compiler shell'
            echo -e "${R}"
            echo -e "  ${FG_GREEN}Kernel:${R} ${FG_WHITE}v4.9.0-sec${R}"
            echo -e "  ${FG_YELLOW}User:${R} ${FG_CYAN}${USER_IDENTITY}${R}"
            echo -e "  ${FG_MAGENTA}Session:${R} ${FG_WHITE}build-lab${R}"
            echo ""
            printf '  %b' "$FG_GREEN"
            _typewriter_echo "login: " "$FG_GREEN" 0.02
            printf '%b' "$FG_WHITE"
            printf '%s\n' "$USER_IDENTITY"
            printf '%b' "$FG_GREEN"
            _typewriter_echo "password: " "$FG_GREEN" 0.02
            printf '%b' "$FG_WHITE"
            printf '********\n'
            printf '%b\n' "$R"
            echo -e "  ${FG_GREEN}[ READY ] build environment online${R}"
            echo -e "  ${FG_YELLOW}Welcome back to the dev surface, ${USER_IDENTITY}.${R}"
            ;;
        *)
            echo -e "${FG_CYAN}${BOLD}"
            printf '  %*s\n' "$(( COLS / 2 + 12 ))" ' ░▒▓██▓▒░ '
            printf '  %*s\n' "$(( COLS / 2 + 6 ))" 'ASTERIX OS'
            printf '  %*s\n' "$(( COLS / 2 + 5 ))" 'Hypercore Edition'
            echo -e "${R}"
            echo -e "  ${FG_GREEN}Kernel:${R} ${FG_WHITE}v4.9.0-sec${R}"
            echo -e "  ${FG_YELLOW}User:${R} ${FG_CYAN}${USER_IDENTITY}${R}"
            echo -e "  ${FG_MAGENTA}Session:${R} ${FG_WHITE}AETHER secure shell${R}"
            echo ""
            printf '  %b' "$FG_CYAN"
            _typewriter_echo "login: " "$FG_CYAN" 0.02
            printf '%b' "$FG_GREEN"
            printf '%s\n' "$USER_IDENTITY"
            printf '%b' "$FG_CYAN"
            _typewriter_echo "password: " "$FG_CYAN" 0.02
            printf '%b' "$FG_GREEN"
            printf '********\n'
            printf '%b\n' "$R"
            echo -e "  ${FG_GREEN}[ OK ] Login accepted${R}"
            echo -e "  ${FG_YELLOW}Welcome back to the hypercore desktop, ${USER_IDENTITY}.${R}"
            echo ""
            _draw_spinner
            echo ""
            echo -e "  ${FG_MAGENTA}ASTERIX OS ready${R}"
            ;;
    esac
}

resolve_identity_name
_apply_package_profile
pick_mode
set_bg "$BG_BLACK"
clear
_play_welcome_overlay
case "$MODE" in
    blackmirror)
        printf '%b\n' "${FG_CYAN}${BOLD}"
        for line in "${BANNER_BLACK[@]}"; do printf '  %s\n' "$line"; done
        printf '%b\n' "$R"
        ;;
    neon)
        printf '%b\n' "${FG_CYAN}${BOLD}"
        for line in "${BANNER_NEON[@]}"; do printf '  %s\n' "$line"; done
        printf '%b\n' "$R"
        ;;
    stealth)
        printf '%b\n' "${FG_GREEN}${BOLD}"
        for line in "${BANNER_STEALTH[@]}"; do printf '  %s\n' "$line"; done
        printf '%b\n' "$R"
        ;;
    *)
        printf '%b\n' "${FG_CYAN}${BOLD}"
        for line in "${BANNER_BLACK[@]}"; do printf '  %s\n' "$line"; done
        printf '%b\n' "$R"
        ;;
esac
_run_boot
_final_splash
_login_screen
