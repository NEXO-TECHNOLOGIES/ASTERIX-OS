# =====================================================================
# ASTERIX OS - Media & Visual Asset Vault
# =====================================================================

Place your custom visual assets here. The ASTERIX OS build engine and
Rust loader will automatically pick them up and bind them into the OS.

---

## 📁 Directory Structure & Supported Formats

### 1. `assets/wallpapers/`
* **Purpose:** High-resolution wallpapers for the desktop environment and terminal backgrounds.
* **Supported Formats:** `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`
* **Recommended Resolution:** 1920x1080 or 3840x2160 (4K)
* **Default Names:**
  - `asterix-main-wallpaper.png` (Default OS Desktop Background)
  - `asterix-terminal-bg.png` (Terminal transparent background)

### 2. `assets/animations/`
* **Purpose:** Boot loading animation video or sequence frames.
* **Supported Formats:** 
  - Video: `.mp4`, `.webm`, `.mkv`
  - Animated: `.gif`
  - Frame Sequences: `frame_001.png`, `frame_002.png`, etc.
* **Integration:**
  - Plymouth boot splash engine converts videos/GIFs into high-FPS boot sequences.
  - Rust terminal loader parses frames for TrueColor terminal splash playback.

### 3. `assets/iso-branding/`
* **Purpose:** GRUB bootloader splash screen, ISO icons, and banner logos.
* **Supported Formats:** `.png`, `.svg`, `.ico`
* **Default Names:**
  - `grub-splash.png` (640x480 or 1024x768 PNG for boot menu)
  - `os-icon.png` (Logo icon)

---

## 🚀 How to Drop Your Assets
Simply drag and drop your files into these folders:
```
ASTERIX OS/
└── assets/
    ├── wallpapers/      <--- Drop your ISO background images here
    ├── animations/      <--- Drop your loading animation video/GIF here
    └── iso-branding/    <--- Drop your icons / logos here
```
When you run `build-iso.sh` or `asterix-loader`, the build system will automatically embed them!
