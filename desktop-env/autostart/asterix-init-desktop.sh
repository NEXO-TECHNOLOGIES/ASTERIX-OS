#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - Desktop Environment Initializer
# Sets wallpaper, starts HUD overlay, and enables compositor
# =====================================================================

# 1. Apply ASTERIX custom wallpaper
WALLPAPER="/etc/asterix/assets/wallpapers/asterix-main-wallpaper.png"
if [ -f "$WALLPAPER" ]; then
    feh --bg-scale "$WALLPAPER" 2>/dev/null || true
    # XFCE wallpaper setting fallback
    if command -v xfconf-query >/dev/null 2>&1; then
        xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/workspace0/last-image -s "$WALLPAPER" 2>/dev/null || true
    fi
fi

# 2. Start desktop compositor for transparent windows & shadows
if command -v picom >/dev/null 2>&1; then
    picom --backend glx --vsync -b 2>/dev/null || picom -b 2>/dev/null || true
fi

# 3. Start ASTERIX Desktop HUD (Conky)
HUD_CONF="/etc/asterix/desktop-env/conky/asterix-hud.conkyrc"
if [ -f "$HUD_CONF" ] && command -v conky >/dev/null 2>&1; then
    killall conky 2>/dev/null || true
    conky -c "$HUD_CONF" -d 2>/dev/null || true
fi

# 4. Start NetworkManager System Tray Applet (Wi-Fi, Ethernet & VPN Applet)
if command -v nm-applet >/dev/null 2>&1; then
    pgrep -x nm-applet >/dev/null || nm-applet --indicator &
fi
