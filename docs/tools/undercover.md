# 🕶️ `undercover` — Terminal Camouflage & Visual Disguise

A privacy utility that disguises the terminal environment by suppressing cyber banners and reformatting shell prompts to blend into public or corporate environments.

---

## 📌 Usage

```bash
ax undercover [on|off|status]
```

---

## ⚙️ How It Works

- **Stealth Camouflage (`ax undercover on`)**:
  - Sets a persistent marker at `~/.asterix_undercover`.
  - Suppresses all ASCII art banners and cybersecurity logos across `bin/ax` and diagnostic tools.
  - Changes the shell prompt to a standard, non-descript command prompt (`C:\Users\Admin>` on Windows emulation or `user@ubuntu:~$` on POSIX).
- **Normal Mode (`ax undercover off`)**:
  - Removes the stealth marker and restores the full cyberpunk visual interface.

---

## 🔍 Technical Implementation
- Implemented in `scripts-hub/ax-undercover.py` using 100% Python Standard Library.
- Does not modify OS binaries or violate operating system integrity.
