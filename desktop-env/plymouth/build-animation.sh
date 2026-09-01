#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Plymouth Boot Animation Builder
# Extracts PNG frames from the loading animation MP4, generates
# the Plymouth theme script, and packages the complete theme.
# Run this ONCE on your build machine before running build-iso.sh
# =====================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Check assets/animations first, then fallback to iso-images
if [ -f "${PROJECT_ROOT}/assets/animations/ASTERIX_LINIX_INTERACTIVE_LOADING_15SEC_1920x1080.mp4" ]; then
    ANIM_SRC="${PROJECT_ROOT}/assets/animations/ASTERIX_LINIX_INTERACTIVE_LOADING_15SEC_1920x1080.mp4"
elif [ -f "${PROJECT_ROOT}/iso-images/ASTERIX_LINIX_INTERACTIVE_LOADING_15SEC_1920x1080.mp4" ]; then
    ANIM_SRC="${PROJECT_ROOT}/iso-images/ASTERIX_LINIX_INTERACTIVE_LOADING_15SEC_1920x1080.mp4"
else
    # Find any mp4 in assets/animations
    ANIM_SRC=$(find "${PROJECT_ROOT}/assets/animations" -name "*.mp4" 2>/dev/null | head -n 1)
fi

THEME_DIR="${SCRIPT_DIR}"
FRAMES_DIR="${THEME_DIR}/frames"

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
    ___   _____ ______ ______ ____     ____  __  __
   /   | / ___//_  __// ____// __ \   / __ \/ / / /
  / /| | \__ \  / /  / __/  / /_/ /  / / / / / / / 
 / ___ |___/ / / /  / /___ / _, _/  / /_/ / /_/ /  
/_/  |_/____/ /_/  /_____//_/ |_|   \____/\____/   
     PLYMOUTH BOOT ANIMATION BUILDER
EOF
echo -e "${NC}"

if ! command -v ffmpeg >/dev/null 2>&1; then
    echo -e "${RED}[!] ffmpeg not found. Install it first:${NC}"
    echo "    sudo apt install ffmpeg"
    exit 1
fi

if [ ! -f "${ANIM_SRC}" ]; then
    echo -e "${RED}[!] Animation source not found: ${ANIM_SRC}${NC}"
    echo -e "${YELLOW}[*] Expected: iso-images/ASTERIX_LINIX_INTERACTIVE_LOADING_15SEC_1920x1080.mp4${NC}"
    exit 1
fi

echo -e "${YELLOW}[*] Extracting frames from animation...${NC}"
rm -rf "${FRAMES_DIR}"
mkdir -p "${FRAMES_DIR}"

# Extract at 24fps, scale to 1920x1080, output as 8-bit PNG
ffmpeg -i "${ANIM_SRC}" \
    -vf "fps=24,scale=1920:1080:flags=lanczos" \
    -pix_fmt rgb24 \
    "${FRAMES_DIR}/frame_%04d.png" \
    -hide_banner -loglevel error

FRAME_COUNT=$(ls "${FRAMES_DIR}"/frame_*.png 2>/dev/null | wc -l)
echo -e "${GREEN}[✔] Extracted ${FRAME_COUNT} frames at 24fps${NC}"

echo -e "${YELLOW}[*] Generating Plymouth theme script...${NC}"

cat << PLYMOUTH_SCRIPT > "${THEME_DIR}/asterix.script"
/*
 * ASTERIX OS - Plymouth Boot Animation Theme Script
 * Frame-based animation driven from extracted MP4 frames.
 */

FRAME_COUNT  := ${FRAME_COUNT};
FRAME_RATE   := 24;
frame_index  := 0;
last_time    := 0;

fun refresh_callback()
{
    now := Plymouth.GetTime();
    delta := now - last_time;

    if (delta >= (1.0 / FRAME_RATE)) {
        last_time := now;
        frame_index := (frame_index + 1) % FRAME_COUNT;
    }

    sprite.SetImage(frames[frame_index]);
}

/*
 * Pre-load all frames into the sprite array.
 * Plymouth caches these in GPU memory for smooth playback.
 */
for (i = 0; i < FRAME_COUNT; i++) {
    num_str := i + 1;
    if (i + 1 < 10)
        num_str := "000" + (i + 1);
    else if (i + 1 < 100)
        num_str := "00" + (i + 1);
    else if (i + 1 < 1000)
        num_str := "0" + (i + 1);

    frames[i] := Image("frames/frame_" + num_str + ".png");
}

/* Center the animation sprite on screen */
screen_width  := Window.GetWidth();
screen_height := Window.GetHeight();
sprite        := Sprite();
sprite.SetImage(frames[0]);
sprite.SetX((screen_width  - frames[0].GetWidth())  / 2);
sprite.SetY((screen_height - frames[0].GetHeight()) / 2);
sprite.SetZ(1);

Plymouth.SetRefreshFunction(refresh_callback);
PLYMOUTH_SCRIPT

echo -e "${YELLOW}[*] Generating Plymouth theme metadata...${NC}"

cat << 'META' > "${THEME_DIR}/asterix.plymouth"
[Plymouth Theme]
Name=ASTERIX OS
Description=ASTERIX OS cybernetic boot animation
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/asterix
ScriptFile=/usr/share/plymouth/themes/asterix/asterix.script
META

echo -e "${YELLOW}[*] Generating Plymouth install hook...${NC}"

cat << 'HOOK' > "${THEME_DIR}/install-plymouth.sh"
#!/usr/bin/env bash
set -e

THEME_SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_DEST="/usr/share/plymouth/themes/asterix"

mkdir -p "${THEME_DEST}/frames"
cp "${THEME_SRC}/asterix.plymouth" "${THEME_DEST}/"
cp "${THEME_SRC}/asterix.script"   "${THEME_DEST}/"
cp "${THEME_SRC}"/frames/*.png     "${THEME_DEST}/frames/"

update-alternatives --install \
    /usr/share/plymouth/themes/default.plymouth \
    default.plymouth \
    "${THEME_DEST}/asterix.plymouth" \
    100

update-alternatives --set \
    default.plymouth \
    "${THEME_DEST}/asterix.plymouth" || true

plymouth-set-default-theme asterix
update-initramfs -u 2>/dev/null || true

echo "[✔] ASTERIX Plymouth theme installed successfully."
HOOK
chmod +x "${THEME_DIR}/install-plymouth.sh"

echo -e "${GREEN}${BOLD}"
echo "[✔] Plymouth theme built successfully!"
echo "    Frames:      ${FRAME_COUNT} PNG files in desktop-env/plymouth/frames/"
echo "    Theme:       desktop-env/plymouth/asterix.plymouth"
echo "    Script:      desktop-env/plymouth/asterix.script"
echo "    Install:     Run install-plymouth.sh inside the live chroot"
echo -e "${NC}"
