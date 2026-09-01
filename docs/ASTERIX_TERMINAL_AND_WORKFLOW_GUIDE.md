# ASTERIX OS Terminal Master Guide
### Multi-Terminals, Live Splitting, Scrolling & Custom Backgrounds

This guide details session management, terminal multiplexing, scrollback buffers, and custom background themes in ASTERIX OS.

---

## 1. Window & Tab Management

### ASTERIX Desktop Terminal Shortcuts
| Action | Shortcut | Description |
| :--- | :--- | :--- |
| **New Tab** | `Ctrl + Shift + T` | Opens a new tab within the current window |
| **New Window** | `Ctrl + Shift + N` | Spawns an independent terminal window |
| **Switch Tabs** | `Alt + [1..9]` or `Ctrl + PageDown` | Cycles across active tabs |
| **Close Tab** | `Ctrl + Shift + W` | Terminates active tab session |
| **Toggle Fullscreen** | `F11` | Fullscreen terminal view |

---

## 2. Terminal Multiplexing (Pane Splitting)

Run concurrent operations (e.g. packet sniffing alongside network scans) in a single window using the integrated ASTERIX Tmux environment.

### ASTERIX Multiplexer Commands (Prefix: `Ctrl + A`)

1. **Start Workspace:**
   ```bash
   tmux -f /etc/asterix/asterix.tmux.conf
   ```
2. **Vertical Split (Side-by-Side):**
   * Press `Ctrl + A`, then `|`
3. **Horizontal Split (Top-to-Bottom):**
   * Press `Ctrl + A`, then `-`
4. **Pane Navigation:**
   * Click directly on any pane with the mouse, or use `Alt + Arrow Keys`
5. **New Tab:**
   * Press `Ctrl + A`, then `c`

---

## 3. Terminal Scrollback Navigation

### Mouse Scroll
* Mouse wheel scrolling is enabled by default in all ASTERIX sessions (`set -g mouse on`). Scrolling anywhere inside a pane activates the 50,000-line history buffer.

### Keyboard Scrollback
* **Page Scroll:** `Shift + PageUp` / `Shift + PageDown`
* **Buffer Inspect Mode:** Press `Ctrl + A` then `[`. Use arrow keys or Page keys to review log output. Press `q` to return to the active prompt.

---

## 4. Custom Background Configuration

### Terminal Background Image:
1. Open terminal preferences: **Edit** -> **Preferences** -> **Appearance**.
2. Select **Background Image** and point to:
   `/etc/asterix/assets/wallpapers/asterix-terminal-bg.png`
3. Adjust opacity to `0.85` for optimal contrast.

### Desktop Wallpaper:
1. Right-click desktop -> **Desktop Settings**.
2. Select **Background** -> **Add Image** and select:
   `/etc/asterix/assets/wallpapers/asterix-main-wallpaper.png`
3. Set style to **Zoomed** or **Centered**.

---

## 5. Mobile Session Controls (Termux Engine)

* **New Session:** Swipe from left edge and tap **NEW SESSION**.
* **Switch Session:** Tap the session ID in the left navigation drawer.
* **Scroll Buffer:** Drag with single finger vertically.
