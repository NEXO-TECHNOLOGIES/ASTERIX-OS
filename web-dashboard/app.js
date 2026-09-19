// =====================================================================
// ASTERIX OS v2.0 - High-Grade Cybernetic Web Desktop Distro
// Codename: Phantom | NEXO-TECHNOLOGIES
// =====================================================================

(function () {
    "use strict";

    // -----------------------------------------------------------------
    // 1. SOUND SYNTHESIZER (Web Audio API)
    // -----------------------------------------------------------------
    let audioCtx = null;
    let soundEnabled = true;

    function initAudio() {
        if (!audioCtx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                audioCtx = new AudioContext();
            }
        }
        if (audioCtx && audioCtx.state === "suspended") {
            audioCtx.resume();
        }
    }

    function playTone(freq, type = "sine", duration = 0.08, gainVal = 0.08) {
        if (!soundEnabled) return;
        try {
            initAudio();
            if (!audioCtx) return;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {
            // Audio context blocked or not supported
        }
    }

    const soundFX = {
        click: () => playTone(880, "sine", 0.04, 0.04),
        type: () => playTone(1200 + Math.random() * 200, "triangle", 0.02, 0.02),
        enter: () => playTone(540, "sine", 0.06, 0.05),
        winOpen: () => {
            playTone(440, "sine", 0.06, 0.05);
            setTimeout(() => playTone(880, "sine", 0.08, 0.04), 50);
        },
        winClose: () => {
            playTone(660, "sine", 0.05, 0.04);
            setTimeout(() => playTone(330, "sine", 0.07, 0.04), 40);
        },
        chime: () => {
            playTone(523.25, "sine", 0.15, 0.06); // C5
            setTimeout(() => playTone(659.25, "sine", 0.18, 0.06), 120); // E5
            setTimeout(() => playTone(783.99, "sine", 0.22, 0.06), 240); // G5
            setTimeout(() => playTone(1046.50, "sine", 0.35, 0.08), 360); // C6
        },
        error: () => playTone(180, "sawtooth", 0.15, 0.06)
    };

    // -----------------------------------------------------------------
    // 2. WALLPAPERS DIRECTORY (26 HD Wallpapers in wallpapers/)
    // -----------------------------------------------------------------
    const WALLPAPERS = [
        { title: "Electric Cyan Minimal", file: "asterix_boot_01_electric_cyan_1788292127536.jpg" },
        { title: "Cyberpunk Night City", file: "asterix_boot_02_cyberpunk_city_1788292249067.jpg" },
        { title: "Matrix Rain Terminal", file: "asterix_boot_03_matrix_terminal_1788292325091.jpg" },
        { title: "Deep Space Nebula", file: "asterix_boot_04_deep_space_1788292387240.jpg" },
        { title: "Red Samurai Dojo", file: "asterix_boot_05_red_samurai_1788292444477.jpg" },
        { title: "Cosmic Neon Monolith", file: "ASTERIX_LINIX_01_Cosmic_Neon.png" },
        { title: "Green Hacker Command 1080p", file: "ASTERIX_LINIX_01_Green_Hacker_1920x1080.png" },
        { title: "Ice Cosmic Nebula 1080p", file: "ASTERIX_LINIX_01_Ice_Cosmic_1920x1080.png" },
        { title: "Cyberpunk Night Horizon", file: "ASTERIX_LINIX_02_Cyberpunk_Night.png" },
        { title: "Hacker Command Center 1080p", file: "ASTERIX_LINIX_02_Hacker_Command_1920x1080.png" },
        { title: "Purple Galaxy Portal 1080p", file: "ASTERIX_LINIX_02_Purple_Galaxy_1920x1080.png" },
        { title: "Green Hacker Matrix", file: "ASTERIX_LINIX_03_Green_Hacker.png" },
        { title: "Ice Glacial Monolith 1080p", file: "ASTERIX_LINIX_03_Ice_Monolith_1920x1080.png" },
        { title: "Neon Cyber Grid 1080p", file: "ASTERIX_LINIX_03_Neon_City_1920x1080.png" },
        { title: "Dragon Fire Cyber", file: "ASTERIX_LINIX_04_Dragon_Fire.png" },
        { title: "Phoenix Core Cyber 1080p", file: "ASTERIX_LINIX_04_Phoenix_Core_1920x1080.png" },
        { title: "Pink Cyberpunk Horizon", file: "ASTERIX_LINIX_04_Pink_Cyberpunk_1920x1080.png" },
        { title: "Dragon Fire 1080p", file: "ASTERIX_LINIX_05_Dragon_Fire_1920x1080.png" },
        { title: "Interstellar Galaxy Portal", file: "ASTERIX_LINIX_05_Galaxy_Portal.png" },
        { title: "Red Terminal Console 1080p", file: "ASTERIX_LINIX_05_Red_Terminal_1920x1080.png" },
        { title: "Astronaut Vista 1080p", file: "ASTERIX_LINIX_06_Astronaut_Vista_1920x1080.png" },
        { title: "Golden Planet Orbit 1080p", file: "ASTERIX_LINIX_06_Golden_Planet_1920x1080.png" },
        { title: "Tropical Cyber Monolith", file: "ASTERIX_LINIX_06_Tropical_Monolith.png" },
        { title: "Cyan Core Reactor 1080p", file: "ASTERIX_LINIX_07_Cyan_Core_1920x1080.png" },
        { title: "Samurai Night Katana 1080p", file: "ASTERIX_LINIX_08_Samurai_Night_1920x1080.png" },
        { title: "ASTERIX Master Emblem", file: "asterix-main-wallpaper.png" }
    ];

    // -----------------------------------------------------------------
    // 3. VIRTUAL POSIX FILESYSTEM (Persisted in localStorage)
    // -----------------------------------------------------------------
    const FS_STORAGE_KEY = "asterix_virtual_posix_fs_v2";
    const DESKTOP_SESSION_KEY = "asterix_desktop_session_v2";
    const WINDOW_STATE_KEY = "asterix_window_state_v1";
    const DESKTOP_ICONS_KEY = "asterix_desktop_icons_v1";
    const DESKTOP_BOOT_KEY = "asterix_desktop_boot_v1";
    const DESKTOP_LOGIN_KEY = "asterix_desktop_login_v1";
    let virtualFS = {};

    function getInitialFS() {
        return {
            "/": { type: "dir", children: ["bin", "etc", "home", "var", "asterix_persistent", "tmp"] },
            "/bin": {
                type: "dir",
                children: ["as-sh", "nmap", "net-sentinel", "bin-inspector", "log-hunter", "crypto-core", "btop", "python3", "apt", "neofetch", "ls", "cat", "cd", "pwd", "clear", "echo", "touch", "mkdir", "rm"]
            },
            "/etc": {
                type: "dir",
                children: ["os-release", "asterix.conf", "motd", "hosts"]
            },
            "/etc/os-release": {
                type: "file",
                content: 'NAME="ASTERIX OS"\nVERSION="2.0 (Phantom)"\nID=asterix\nID_LIKE=debian\nPRETTY_NAME="ASTERIX OS v2.0 (Phantom) 6.1-sec"\nVERSION_CODENAME=phantom\nHOME_URL="https://github.com/NEXO-TECHNOLOGIES/ASTERIX-OS"'
            },
            "/etc/asterix.conf": {
                type: "file",
                content: '# ASTERIX SOVEREIGN KERNEL CONFIGURATION\nSECURITY_TIER=MAXIMUM\nAI_RUNTIME=SOVEREIGN_LOCAL\nPERSISTENCE_MOUNT=/asterix_persistent\nW_X_PROTECTION=STRICT\nARP_MITIGATION=ENABLED\nDNS_ROTATION=ACTIVE'
            },
            "/etc/motd": {
                type: "file",
                content: "===================================================================\n* Welcome to ASTERIX OS v2.0 (Phantom) [Linux 6.1-sec x86_64]\n* Autonomous Sovereign Security Distribution\n* Persistent Storage: /asterix_persistent (Active & Encrypted)\n==================================================================="
            },
            "/etc/hosts": {
                type: "file",
                content: "127.0.0.1   localhost asterix-sec\n10.0.8.1    router.local gateway\n10.0.8.24   asterix-sec.local"
            },
            "/home": { type: "dir", children: ["operator"] },
            "/home/operator": {
                type: "dir",
                children: ["readme.txt", "scan_targets.txt", "defense_policy.json", "exploit_payload.py", "mission_notes.md"]
            },
            "/home/operator/readme.txt": {
                type: "file",
                content: "ASTERIX OS OPERATOR INSTRUCTIONS\n--------------------------------\n1. Use 'as-sh' terminal for system operations.\n2. All 12 offensive subsystems are armed in the Cyber Suite.\n3. The /asterix_persistent partition retains all custom files across reboots.\n4. Type 'help' in terminal for the complete command manual."
            },
            "/home/operator/scan_targets.txt": {
                type: "file",
                content: "# Subnets slated for security inspection:\n10.0.8.0/24    # Internal DMZ\n192.168.1.0/24 # Field Operations Gateway\n172.16.4.15    # Target Database Server"
            },
            "/home/operator/defense_policy.json": {
                type: "file",
                content: '{\n  "firewall": "ACTIVE",\n  "anti_attack_engine": "v2.0.0",\n  "syn_flood_filter": true,\n  "arp_poison_guard": true,\n  "dns_spoof_detection": true,\n  "stealth_mode": true\n}'
            },
            "/home/operator/exploit_payload.py": {
                type: "file",
                content: '#!/usr/bin/env python3\n# ASTERIX Vulnerability Test Payload\nimport sys\n\ndef check_stack_canary():\n    print("[*] Probing target stack protections...")\n    print("[+] NX (No-Execute) Bit: ACTIVE")\n    print("[+] ASLR Entropy: 28-bit randomized")\n    print("[!] Target safe from simple buffer overrun")\n\nif __name__ == "__main__":\n    check_stack_canary()'
            },
            "/home/operator/mission_notes.md": {
                type: "file",
                content: "# Mission Notes // Op Sovereign Ghost\n\n- Primary Goal: Verify zero-leak persistence on hybrid UEFI boot\n- Tools tested: net-sentinel (100% clean port enumeration)\n- Telemetry: Btop HUD latency < 2ms\n- AI Copilot: Rule-based triage active"
            },
            "/asterix_persistent": {
                type: "dir",
                children: ["vault_token.enc", "recon_loot.json", "backup_state.bin"]
            },
            "/asterix_persistent/vault_token.enc": {
                type: "file",
                content: "-----BEGIN ASTERIX ENCRYPTED KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDg45y4P9Q8k7qZ\n492f5k98b671a80d5e1c4e73... [AES-256-XTS OVERLAY TOKEN VALID]\n-----END ASTERIX ENCRYPTED KEY-----"
            },
            "/asterix_persistent/recon_loot.json": {
                type: "file",
                content: '[\n  { "ip": "10.0.8.102", "ports": [22, 80, 443], "os": "Linux 5.15", "vuln": "CVE-2023-4911 (Mitigated)" },\n  { "ip": "10.0.8.140", "ports": [8080], "os": "Apache Tomcat", "vuln": "None" }\n]'
            },
            "/asterix_persistent/backup_state.bin": {
                type: "file",
                content: "[BINARY SNAPSHOT DATA: 4,096 bytes / CRC32: 0x9f8b3c1a]"
            },
            "/var": { type: "dir", children: ["log"] },
            "/var/log": {
                type: "dir",
                children: ["syslog", "net_sentinel.log", "auth.log"]
            },
            "/var/log/syslog": {
                type: "file",
                content: "Sep 12 12:00:01 asterix kernel: [    0.000000] Linux version 6.1.0-sec-amd64\nSep 12 12:00:02 asterix systemd[1]: Reached target Sovereign Security.\nSep 12 12:00:03 asterix net-sentinel: Threadpool 16 workers armed."
            },
            "/var/log/net_sentinel.log": {
                type: "file",
                content: "[INFO] Net-Sentinel daemon listening on interface eth0\n[PASS] No unauthorized ARP replies detected\n[PASS] Port scan mitigation threshold: NORMAL"
            },
            "/var/log/auth.log": {
                type: "file",
                content: "Sep 12 12:00:00 asterix login[541]: ROOT session opened for user operator\nSep 12 12:00:01 asterix sudo: operator : TTY=as-sh ; PWD=/home/operator ; USER=root"
            },
            "/tmp": { type: "dir", children: [] }
        };
    }

    function loadVirtualFS() {
        try {
            const raw = localStorage.getItem(FS_STORAGE_KEY);
            if (raw) {
                virtualFS = JSON.parse(raw);
                return;
            }
        } catch (e) {
            console.warn("Could not load FS from localStorage, using default", e);
        }
        virtualFS = getInitialFS();
        saveVirtualFS();
    }

    function saveVirtualFS() {
        try {
            localStorage.setItem(FS_STORAGE_KEY, JSON.stringify(virtualFS));
        } catch (e) {
            console.error("Storage limit reached for virtual FS", e);
        }
    }

    function saveWindowLayout() {
        try {
            const layout = {};
            Object.keys(windowInstances || {}).forEach((id) => {
                const inst = windowInstances[id];
                const el = inst && inst.el;
                if (!el) return;
                layout[id] = {
                    minimized: !!inst.isMinimized,
                    maximized: !!inst.isMaximized,
                    prevBounds: inst.prevBounds || null,
                    visible: el.style.display !== "none"
                };
            });
            localStorage.setItem(WINDOW_STATE_KEY, JSON.stringify(layout));
        } catch (e) {
            console.warn("Unable to persist window layout", e);
        }
    }

    function restoreWindowLayout() {
        try {
            const raw = localStorage.getItem(WINDOW_STATE_KEY);
            if (!raw) return;
            const layout = JSON.parse(raw);
            Object.keys(windowInstances || {}).forEach((id) => {
                const inst = windowInstances[id];
                const el = inst && inst.el;
                if (!el || !layout[id]) return;
                const state = layout[id];
                inst.isMinimized = !!state.minimized;
                inst.isMaximized = !!state.maximized;
                inst.prevBounds = state.prevBounds || null;
                el.style.display = state.visible ? (inst.isMinimized ? "none" : "flex") : "none";
                if (state.maximized) {
                    el.classList.add("window-maximized");
                } else {
                    el.classList.remove("window-maximized");
                }
            });
        } catch (e) {
            console.warn("Unable to restore window layout", e);
        }
    }

    function saveDesktopSession() {
        try {
            const snapshot = {};
            Object.keys(windowInstances || {}).forEach((id) => {
                const inst = windowInstances[id];
                const el = inst && inst.el;
                if (!el) return;
                const isOpen = el.style.display !== "none" && !inst.isMinimized;
                snapshot[id] = {
                    top: el.style.top || "40px",
                    left: el.style.left || "60px",
                    width: el.style.width || "840px",
                    height: el.style.height || "520px",
                    display: isOpen ? (el.style.display || "flex") : "none",
                    opened: isOpen,
                    minimized: !!inst.isMinimized,
                    maximized: !!inst.isMaximized,
                    prevBounds: inst.prevBounds || null
                };
            });
            localStorage.setItem(DESKTOP_SESSION_KEY, JSON.stringify(snapshot));
            saveWindowLayout();
        } catch (e) {
            console.warn("Unable to persist desktop session", e);
        }
    }

    function restoreDesktopSession() {
        try {
            const raw = localStorage.getItem(DESKTOP_SESSION_KEY);
            if (!raw) return;
            const snapshot = JSON.parse(raw);
            Object.keys(windowInstances || {}).forEach((id) => {
                const inst = windowInstances[id];
                const el = inst && inst.el;
                if (!el || !snapshot[id]) return;
                const state = snapshot[id];
                el.style.top = state.top || "40px";
                el.style.left = state.left || "60px";
                el.style.width = state.width || "840px";
                el.style.height = state.height || "520px";
                const shouldOpen = state.opened !== false;
                el.style.display = shouldOpen ? (state.display || "flex") : "none";
                inst.isMinimized = !!state.minimized && shouldOpen;
                inst.isMaximized = !!state.maximized;
                inst.prevBounds = state.prevBounds || null;
                if (state.maximized) {
                    el.classList.add("window-maximized");
                } else {
                    el.classList.remove("window-maximized");
                }
            });
            restoreWindowLayout();
            updateTaskbar();
        } catch (e) {
            console.warn("Unable to restore desktop session", e);
        }
    }

    function saveDesktopIconLayout() {
        try {
            const layout = {};
            document.querySelectorAll(".desktop-icon-item").forEach((item) => {
                const appId = item.dataset.app;
                if (!appId) return;
                layout[appId] = {
                    x: parseFloat(item.style.left || "20"),
                    y: parseFloat(item.style.top || "20")
                };
            });
            localStorage.setItem(DESKTOP_ICONS_KEY, JSON.stringify(layout));
        } catch (e) {
            console.warn("Unable to persist desktop icon layout", e);
        }
    }

    function restoreDesktopIconLayout() {
        try {
            const raw = localStorage.getItem(DESKTOP_ICONS_KEY);
            if (!raw) return;
            const layout = JSON.parse(raw);
            document.querySelectorAll(".desktop-icon-item").forEach((item) => {
                const appId = item.dataset.app;
                if (!appId || !layout[appId]) return;
                item.style.left = `${layout[appId].x}px`;
                item.style.top = `${layout[appId].y}px`;
            });
        } catch (e) {
            console.warn("Unable to restore desktop icon layout", e);
        }
    }

    function resolvePath(currPath, target) {
        if (!target) return currPath;
        if (target === "~") return "/home/operator";
        if (target.startsWith("~/")) target = "/home/operator" + target.slice(1);
        let parts;
        if (target.startsWith("/")) {
            parts = target.split("/").filter(Boolean);
        } else {
            parts = (currPath + "/" + target).split("/").filter(Boolean);
        }
        const resolved = [];
        for (const p of parts) {
            if (p === ".") continue;
            if (p === "..") {
                if (resolved.length) resolved.pop();
            } else {
                resolved.push(p);
            }
        }
        return "/" + resolved.join("/");
    }

    // -----------------------------------------------------------------
    // 4. WINDOW MANAGER (WM)
    // -----------------------------------------------------------------
    let highestZ = 10;
    const windowInstances = {};
    let activeWindowId = null;

    const ICONS_SVG = {
        terminal: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
        files: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
        security: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
        monitor: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
        code: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>',
        ai: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8v4l3 3"/></svg>',
        store: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>',
        settings: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
        boot: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
        discord: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>',
        trash: '<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
    };

    const APP_REGISTRY = [
        { id: "as-terminal", name: "ASTERIX Terminal", icon: ICONS_SVG.terminal, desc: "Interactive as-sh bash shell & pentest CLI", cat: "offensive" },
        { id: "as-files", name: "File Explorer", icon: ICONS_SVG.files, desc: "Virtual POSIX file manager & editor", cat: "system" },
        { id: "as-security", name: "Cyber Suite", icon: ICONS_SVG.security, desc: "12 Master Offensive & Defensive Subsystems", cat: "offensive" },
        { id: "as-monitor", name: "Btop Telemetry", icon: ICONS_SVG.monitor, desc: "Real-time CPU/RAM/Network HUD & Task Manager", cat: "system" },
        { id: "as-code", name: "Code Studio", icon: ICONS_SVG.code, desc: "Rust, C/C++, Python3 multi-language IDE", cat: "engineering" },
        { id: "as-ai", name: "AI Neural Core", icon: ICONS_SVG.ai, desc: "Sovereign local LLM copilot & threat advisor", cat: "ai" },
        { id: "as-store", name: "Software Center", icon: ICONS_SVG.store, desc: "APT repository & security package manager", cat: "engineering" },
        { id: "as-settings", name: "Control Center", icon: ICONS_SVG.settings, desc: "Themes, 26 HD Wallpapers, Shaders, Sound FX", cat: "system" },
        { id: "as-boot", name: "Live ISO & Rufus", icon: ICONS_SVG.boot, desc: "Official ISO downloads & Rufus live persistence guide", cat: "forensics" },
        { id: "as-discord", name: "Discord Cloud", icon: ICONS_SVG.discord, desc: "Async task bridge & webhook telemetry dispatcher", cat: "engineering" },
        { id: "as-trash", name: "Trash Depot", icon: ICONS_SVG.trash, desc: "Recycled system files depot", cat: "system" }
    ];

    function initWindowManager() {
        const windows = document.querySelectorAll(".cyber-window");
        windows.forEach(win => {
            const winId = win.id.replace("win-", "");
            windowInstances[winId] = {
                el: win,
                isMinimized: false,
                isMaximized: false,
                prevBounds: null
            };

            win.addEventListener("mousedown", () => focusWindow(winId));

            const titlebar = win.querySelector(".window-titlebar");
            if (titlebar) {
                initDraggable(win, titlebar, winId);
            }
        });

        document.querySelectorAll(".desktop-icon-item").forEach((item, idx) => {
            item.style.position = "absolute";
            const defaultX = 20 + (idx % 4) * 96;
            const defaultY = 26 + Math.floor(idx / 4) * 96;
            item.style.left = `${defaultX}px`;
            item.style.top = `${defaultY}px`;
            item.style.margin = "0";
            item.addEventListener("click", (e) => {
                const appId = item.dataset.app;
                if (appId && !item.dataset.dragMoved) {
                    openWindow(appId);
                    soundFX.click();
                }
                item.dataset.dragMoved = "false";
            });
        });

        restoreDesktopIconLayout();
        restoreDesktopSession();

        // Workspace switcher buttons
        document.querySelectorAll(".ws-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".ws-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                soundFX.click();
            });
        });
    }

    function initDraggable(win, handle, winId) {
        let isDragging = false;
        let startX, startY, startLeft, startTop;

        handle.addEventListener("mousedown", (e) => {
            if (e.target.closest(".titlebar-controls")) return;
            focusWindow(winId);
            if (windowInstances[winId].isMaximized) return;

            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            const rect = win.getBoundingClientRect();
            startLeft = rect.left;
            startTop = rect.top;

            const onMouseMove = (moveEvent) => {
                if (!isDragging) return;
                const dx = moveEvent.clientX - startX;
                const dy = moveEvent.clientY - startY;

                let newLeft = startLeft + dx;
                let newTop = startTop + dy;

                // Restrict top bounds to below top-bar
                if (newTop < 42) newTop = 42;

                win.style.left = newLeft + "px";
                win.style.top = newTop + "px";
            };

            const onMouseUp = () => {
                isDragging = false;
                document.removeEventListener("mousemove", onMouseMove);
                document.removeEventListener("mouseup", onMouseUp);
            };

            document.addEventListener("mousemove", onMouseMove);
            document.addEventListener("mouseup", onMouseUp);
        });
    }

    window.openWindow = function (winId) {
        initAudio();
        const inst = windowInstances[winId];
        if (!inst) return;
        const win = inst.el;

        win.style.display = "flex";
        inst.isMinimized = false;
        focusWindow(winId);
        soundFX.winOpen();
        updateTaskbar();
        saveDesktopSession();

        if (winId === "as-terminal") {
            setTimeout(focusTerminalInput, 50);
        } else if (winId === "as-files") {
            renderFileExplorer();
        } else if (winId === "as-monitor") {
            startBtopGraphs();
        }
    };

    window.closeWindow = function (winId) {
        const inst = windowInstances[winId];
        if (!inst) return;
        inst.el.style.display = "none";
        inst.isMinimized = false;
        soundFX.winClose();
        updateTaskbar();
        saveDesktopSession();
    };

    window.minimizeWindow = function (winId) {
        const inst = windowInstances[winId];
        if (!inst) return;
        inst.el.style.display = "none";
        inst.isMinimized = true;
        soundFX.click();
        updateTaskbar();
        saveDesktopSession();
    };

    window.maximizeWindow = function (winId) {
        const inst = windowInstances[winId];
        if (!inst) return;
        const win = inst.el;

        if (inst.isMaximized) {
            win.classList.remove("window-maximized");
            if (inst.prevBounds) {
                win.style.top = inst.prevBounds.top;
                win.style.left = inst.prevBounds.left;
                win.style.width = inst.prevBounds.width;
                win.style.height = inst.prevBounds.height;
            }
            inst.isMaximized = false;
        } else {
            inst.prevBounds = {
                top: win.style.top,
                left: win.style.left,
                width: win.style.width,
                height: win.style.height
            };
            win.classList.add("window-maximized");
            inst.isMaximized = true;
        }
        soundFX.click();
        saveDesktopSession();
    };

    window.focusWindow = function (winId) {
        highestZ += 2;
        activeWindowId = winId;
        document.querySelectorAll(".cyber-window").forEach(w => w.classList.remove("active-window"));
        const inst = windowInstances[winId];
        if (inst) {
            inst.el.style.zIndex = highestZ;
            inst.el.classList.add("active-window");
        }
        updateTaskbar();
    };

    function updateTaskbar() {
        const bar = document.getElementById("windowTaskbar");
        if (!bar) return;
        bar.innerHTML = "";

        Object.keys(windowInstances).forEach(id => {
            const inst = windowInstances[id];
            const isVisible = inst.el.style.display !== "none" || inst.isMinimized;
            if (!isVisible) return;

            const appMeta = APP_REGISTRY.find(a => a.id === id) || { name: id, icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>` };
            const taskItem = document.createElement("div");
            taskItem.className = `task-item ${activeWindowId === id && !inst.isMinimized ? "active" : ""} ${inst.isMinimized ? "minimized" : ""}`;
            taskItem.innerHTML = `<span>${appMeta.icon}</span><span>${appMeta.name}</span>`;

            taskItem.addEventListener("click", () => {
                soundFX.click();
                if (inst.isMinimized) {
                    inst.el.style.display = "flex";
                    inst.isMinimized = false;
                    focusWindow(id);
                } else if (activeWindowId === id) {
                    minimizeWindow(id);
                } else {
                    focusWindow(id);
                }
            });

            bar.appendChild(taskItem);
        });
    }

    // -----------------------------------------------------------------
    // 5. APPLICATION LAUNCHER (Start Menu)
    // -----------------------------------------------------------------
    function initAppLauncher() {
        const startBtn = document.getElementById("startBtn");
        const launcherMenu = document.getElementById("appLauncherMenu");
        const searchInput = document.getElementById("launcherSearchInput");
        const appsGrid = document.getElementById("launcherAppsGrid");

        function renderLauncherApps(category = "all", query = "") {
            appsGrid.innerHTML = "";
            const filtered = APP_REGISTRY.filter(app => {
                const matchCat = category === "all" || app.cat === category;
                const matchSearch = !query || app.name.toLowerCase().includes(query.toLowerCase()) || app.desc.toLowerCase().includes(query.toLowerCase());
                return matchCat && matchSearch;
            });

            filtered.forEach(app => {
                const item = document.createElement("div");
                item.className = "launcher-app-item";
                item.innerHTML = `
                    <div class="launcher-app-icon">${app.icon}</div>
                    <div class="launcher-app-info">
                        <span class="launcher-app-name">${app.name}</span>
                        <span class="launcher-app-desc">${app.desc}</span>
                    </div>
                `;
                item.addEventListener("click", () => {
                    openWindow(app.id);
                    closeLauncher();
                });
                appsGrid.appendChild(item);
            });
        }

        let currentCat = "all";
        renderLauncherApps();

        document.querySelectorAll(".launcher-sidebar .cat-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".launcher-sidebar .cat-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                currentCat = btn.dataset.cat;
                renderLauncherApps(currentCat, searchInput.value.trim());
                soundFX.click();
            });
        });

        searchInput.addEventListener("input", (e) => {
            renderLauncherApps(currentCat, e.target.value.trim());
        });

        startBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            initAudio();
            toggleLauncher();
        });

        function toggleLauncher() {
            const isOpen = launcherMenu.classList.contains("open");
            if (isOpen) {
                closeLauncher();
            } else {
                openLauncher();
            }
        }

        function openLauncher() {
            launcherMenu.classList.add("open");
            startBtn.classList.add("active");
            searchInput.value = "";
            searchInput.focus();
            soundFX.click();
        }

        function closeLauncher() {
            launcherMenu.classList.remove("open");
            startBtn.classList.remove("active");
        }

        document.addEventListener("click", (e) => {
            if (!launcherMenu.contains(e.target) && e.target !== startBtn) {
                closeLauncher();
            }
        });
    }

    // -----------------------------------------------------------------
    // 6. NOTIFICATION DRAWER & SYSTEM TRAY
    // -----------------------------------------------------------------
    function initNotificationDrawer() {
        const notifyToggleBtn = document.getElementById("notifyToggleBtn");
        const drawer = document.getElementById("notificationDrawer");
        const closeBtn = document.getElementById("closeDrawerBtn");

        notifyToggleBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            initAudio();
            drawer.classList.toggle("open");
            soundFX.click();
        });

        closeBtn.addEventListener("click", () => {
            drawer.classList.remove("open");
            soundFX.click();
        });

        document.addEventListener("click", (e) => {
            if (!drawer.contains(e.target) && e.target !== notifyToggleBtn) {
                drawer.classList.remove("open");
            }
        });
    }

    function initClock() {
        const timeEl = document.getElementById("clockTime");
        const dateEl = document.getElementById("clockDate");

        function update() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, "0");
            const mins = String(now.getMinutes()).padStart(2, "0");
            const secs = String(now.getSeconds()).padStart(2, "0");
            timeEl.textContent = `${hours}:${mins}:${secs}`;

            const days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
            const months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
            dateEl.textContent = `${days[now.getDay()]} ${now.getDate()} ${months[now.getMonth()]}`;
        }
        update();
        setInterval(update, 1000);
    }

    // -----------------------------------------------------------------
    // 7. ASTERIX TERMINAL INTERPRETER (as-sh)
    // -----------------------------------------------------------------
    let termHistory = [];
    let termHistIdx = -1;
    let currentDir = "/home/operator";

    window.focusTerminalInput = function () {
        const input = document.getElementById("terminalInput");
        if (input) input.focus();
    };

    function initTerminal() {
        const out = document.getElementById("terminalOutput");
        const input = document.getElementById("terminalInput");
        if (!out || !input) return;

        // Print initial banner
        printTerminalLine("<span class='term-cyan term-bold'>===================================================================</span>");
        printTerminalLine("<span class='term-cyan term-bold'>  ASTERIX OS v2.0 (Phantom) // Autonomous Sovereign Linux Distro   </span>");
        printTerminalLine("<span class='term-cyan term-bold'>===================================================================</span>");
        printTerminalLine("<span class='term-dim'>[Kernel: Linux 6.1.0-sec-amd64 | Shell: /bin/as-sh | Root Perms]</span>");
        printTerminalLine("Type '<span class='term-green'>help</span>' for available commands or '<span class='term-cyan'>neofetch</span>' for system specs.\n");

        input.addEventListener("keydown", (e) => {
            soundFX.type();
            if (e.key === "Enter") {
                soundFX.enter();
                const cmd = input.value.trim();
                input.value = "";
                if (cmd) {
                    termHistory.push(cmd);
                    termHistIdx = termHistory.length;
                    printTerminalPromptLine(cmd);
                    executeTerminalCommand(cmd);
                } else {
                    printTerminalPromptLine("");
                }
            } else if (e.key === "ArrowUp") {
                if (termHistory.length > 0 && termHistIdx > 0) {
                    termHistIdx--;
                    input.value = termHistory[termHistIdx];
                }
                e.preventDefault();
            } else if (e.key === "ArrowDown") {
                if (termHistIdx < termHistory.length - 1) {
                    termHistIdx++;
                    input.value = termHistory[termHistIdx];
                } else {
                    termHistIdx = termHistory.length;
                    input.value = "";
                }
                e.preventDefault();
            } else if (e.key === "Tab") {
                e.preventDefault();
                handleTabCompletion(input);
            }
        });
    }

    function printTerminalLine(html) {
        const outs = [
            document.getElementById("terminalOutput"),
            document.getElementById("portalTermOutput")
        ].filter(Boolean);
        outs.forEach(out => {
            const line = document.createElement("div");
            line.className = "term-line";
            line.innerHTML = html;
            out.appendChild(line);
            out.scrollTop = out.scrollHeight;
        });
    }

    function printTerminalPromptLine(cmd) {
        const displayDir = currentDir.startsWith("/home/operator") ? currentDir.replace("/home/operator", "~") : currentDir;
        printTerminalLine(`<span class='prompt-user'>operator@asterix</span>:<span class='prompt-dir'>${displayDir}</span>$ ${escapeHtml(cmd)}`);
    }

    function escapeHtml(str) {
        return (str || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function handleTabCompletion(input) {
        const val = input.value;
        const parts = val.split(" ");
        const prefix = parts[parts.length - 1];

        const commands = [
            "help", "neofetch", "clear", "ls", "cd", "pwd", "cat", "touch", "mkdir",
            "rm", "echo", "uname", "whoami", "id", "date", "uptime", "ps", "kill",
            "nmap", "net-sentinel", "bin-inspector", "log-hunter", "crypto-core",
            "python3", "apt", "btop", "as-ai", "matrix", "reboot", "exit"
        ];

        if (parts.length === 1) {
            const matches = commands.filter(c => c.startsWith(prefix));
            if (matches.length === 1) {
                input.value = matches[0] + " ";
            } else if (matches.length > 1) {
                printTerminalPromptLine(val);
                printTerminalLine(matches.join("   "));
            }
        } else {
            // File / dir completion
            const dirNode = virtualFS[currentDir];
            if (dirNode && dirNode.children) {
                const matches = dirNode.children.filter(f => f.startsWith(prefix));
                if (matches.length === 1) {
                    parts[parts.length - 1] = matches[0];
                    input.value = parts.join(" ");
                } else if (matches.length > 1) {
                    printTerminalPromptLine(val);
                    printTerminalLine(matches.join("   "));
                }
            }
        }
    }

    function executeTerminalCommand(cmdStr) {
        const parts = cmdStr.split(" ").filter(Boolean);
        const cmd = parts[0].toLowerCase();
        const args = parts.slice(1);

        switch (cmd) {
            case "help":
                printTerminalLine(`
<span class='term-cyan term-bold'>ASTERIX OS COMMAND MATRIX (as-sh v4.9.0):</span>
  <span class='term-yellow term-bold'>[BREAKTHROUGH ENGINES]</span>
  <span class='term-green'>ax pathfinder</span>       Autonomous Attack Graph & Dijkstra Kill Chains
  <span class='term-green'>ax team</span>             Multiplayer P2P Operator Sync & De-Confliction
  <span class='term-green'>ax ghost</span>            Ghost Protocol Decoy Streams & Egress Blending
  <span class='term-green'>ax radio</span>            Mobile RF Spectral Sentinel & Jamming Audit
  <span class='term-green'>ax vault</span>            Immutable Merkle Tree Forensic Evidence Vault
  <span class='term-green'>ax verify</span>           Verify 21/21 Cryptographic Manifest Signatures

  <span class='term-yellow term-bold'>[CORE SYSTEM & CYBER SUITE]</span>
  <span class='term-green'>neofetch</span>            Display ASTERIX OS hardware & distro specs
  <span class='term-green'>ls [-la] [path]</span>     List directory contents
  <span class='term-green'>cd [path]</span>           Change working directory
  <span class='term-green'>pwd</span>                 Print working directory path
  <span class='term-green'>cat [file]</span>          Display file contents
  <span class='term-green'>touch / mkdir / rm</span>  File management commands
  <span class='term-green'>clear</span>               Clear the terminal display
  <span class='term-green'>uname -a</span>            Print kernel release and architecture
  <span class='term-green'>btop / top</span>          Open microsecond Btop telemetry HUD
  <span class='term-green'>nmap [target]</span>       Simulate multi-threaded port & CVE scanner
  <span class='term-green'>net-sentinel</span>        Execute Rust thread-pooled network engine
  <span class='term-green'>bin-inspector</span>       Run ELF binary W^X & entropy analyzer
  <span class='term-green'>crypto-core [hash]</span>  Audit & crack cryptographic hashes
  <span class='term-green'>matrix</span>              Launch falling phosphor matrix screensaver
  <span class='term-green'>reboot</span>              Reinitialize the ASTERIX web desktop
`);
                break;

            case "ax": {
                const sub = (args[0] || "").toLowerCase();
                if (sub === "pathfinder" || sub === "pf") {
                    executeTerminalCommand("pathfinder");
                } else if (sub === "team" || sub === "sync") {
                    executeTerminalCommand("team");
                } else if (sub === "ghost" || sub === "decoy") {
                    executeTerminalCommand("ghost");
                } else if (sub === "radio" || sub === "rf") {
                    executeTerminalCommand("radio");
                } else if (sub === "vault" || sub === "evidence") {
                    executeTerminalCommand("vault");
                } else if (sub === "verify" || sub === "release-verify") {
                    executeTerminalCommand("verify");
                } else if (sub === "doctor") {
                    executeTerminalCommand("doctor");
                } else {
                    printTerminalLine(`
<span class='term-cyan term-bold'>ASTERIX Master Omni-Dispatcher (ax)</span>
Usage: ax &lt;subsystem|command&gt; [options]
Breakthroughs: <span class='term-green'>pathfinder</span>, <span class='term-green'>team</span>, <span class='term-green'>ghost</span>, <span class='term-green'>radio</span>, <span class='term-green'>vault</span>, <span class='term-green'>verify</span>
System: <span class='term-green'>doctor</span>, <span class='term-green'>portal</span>, <span class='term-green'>discord</span>, <span class='term-green'>recon</span>, <span class='term-green'>anti-net</span>
`);
                }
                break;
            }

            case "pathfinder":
            case "ax-pathfinder":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-PATHFINDER] Autonomous Lateral Attack Graph Traversal</span>
<span class='term-yellow'>[*] Ingesting network topology from /asterix_persistent/recon_loot.json...</span>
<span class='term-green'>[+] 14 nodes discovered, 31 transitive trust edges mapped.</span>
<span class='term-cyan'>[+] Dijkstra Shortest Kill-Chain Calculation:</span>
  <span class='term-green'>[Hop 0]</span> 10.0.8.24 (Local Attacker Node)
  <span class='term-green'>[Hop 1]</span> 10.0.8.102:8080 (Apache Tomcat CVE-2023-4911 - RCE) [Weight: 1.2]
  <span class='term-green'>[Hop 2]</span> 10.0.8.42 (Internal Jump Box / Credential Extraction) [Weight: 0.8]
  <span class='term-magenta'>[Hop 3]</span> 10.0.8.10:88 (CORP-DC01 Kerberos KDC / Domain Admin) [Weight: 2.1]
<span class='term-yellow'>[!] Choke-point identified: Pivot at 10.0.8.42 eliminates 84% of lateral attack paths.</span>
<span class='term-cyan'>[[OK]] Mission kill chain modeled in 42ms. Zero cloud telemetry leaked.</span>
`);
                break;

            case "team":
            case "ax-team":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-TEAM] Multiplayer Live Engagement Mesh (P2P Gossip Protocol)</span>
<span class='term-yellow'>[*] Synchronizing swarm state across 127.0.0.1:9099...</span>
<span class='term-green'>[+] Peer Nodes Active:</span>
  <span class='term-cyan'>• Operator-01 (You)</span>    | Role: Lead Exploit  | Target: 10.0.8.102 | Status: <span class='term-green'>LOCKED</span>
  <span class='term-cyan'>• Ghost-Alpha (Peer)</span>  | Role: Decoy Egress  | Target: 10.0.8.1   | Status: <span class='term-green'>BLENDING</span>
  <span class='term-cyan'>• Radio-Sentinel (Edge)</span>| Role: RF Hunter     | Target: 2.4/5GHz   | Status: <span class='term-green'>PASSIVE</span>
<span class='term-green'>[+] Scope De-confliction: 0 collision alerts across 3 active operations.</span>
<span class='term-cyan'>[[OK]] P2P gossip mesh synchronized (Ed25519 authenticated).</span>
`);
                break;

            case "ghost":
            case "ax-ghost":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-GHOST] Egress Traffic Blending & Synthetic Decoy Streams</span>
<span class='term-yellow'>[*] Initializing high-entropy traffic generator...</span>
<span class='term-green'>[+] Generated 128 synthetic HTTP/2 sessions to benign CDNs (Cloudflare, Akamai).</span>
<span class='term-green'>[+] Jitter interval: 800ms - 3200ms (Gaussian distribution).</span>
<span class='term-cyan'>[+] Active C2 Beacon Multiplexing:</span>
  • Beacon #4821 encapsulated in TLS 1.3 SNI: docs.github.com
  • Decoy stream ratio: 94% synthetic / 6% operational
<span class='term-magenta'>[+] SIEM Anomaly Detection Confidence: 0.08 (Normal traffic profile).</span>
<span class='term-cyan'>[[OK]] Ghost protocol running in background daemon mode.</span>
`);
                break;

            case "radio":
            case "ax-radio":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-RADIO] Mobile RF Sensor Sentinel & Signal Defense</span>
<span class='term-yellow'>[*] Scanning 2.4GHz & 5.8GHz ISM spectral noise floor...</span>
<span class='term-green'>[+] RTL-SDR / HackRF / Termux Wi-Fi Monitor: ARMED</span>
<span class='term-green'>[+] Current Spectral Floor: -92 dBm (Baseline: Normal)</span>
<span class='term-yellow'>[*] Passive 802.11 Deauthentication Frame Monitor:</span>
  • Deauth Frames / sec: 0 (Threshold: 15/s)
  • Rogue AP Beacons: None detected
<span class='term-cyan'>[+] Passive Jamming Detector:</span>
  • Continuous wideband carrier pulse: NONE
  • Jamming threat score: 0/100 (SECURE)
<span class='term-cyan'>[[OK]] Passive RF monitoring compliance active. Zero RF transmissions allowed.</span>
`);
                break;

            case "vault":
            case "ax-vault":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-VAULT] Cryptographic Forensic Evidence Vault</span>
<span class='term-yellow'>[*] Loading Merkle Tree Chain of Custody (/asterix_persistent/evidence/)...</span>
<span class='term-green'>[+] Merkle Root Hash: 7b8c04e2f9d1a3c8e5f2b6a9c1d4e7f0b2a5c8d1e4f7a0b3c6d9e2f5a8b1c4d7</span>
<span class='term-green'>[+] Total Evidence Blocks: 247 immutable chained records</span>
<span class='term-cyan'>[+] Verification Status:</span>
  • Block #247: Session Transcript Checksum -> <span class='term-green'>VERIFIED</span>
  • Block #246: Keystroke Execution Log    -> <span class='term-green'>VERIFIED</span>
  • Block #245: Packet Capture (PCAP) Hash -> <span class='term-green'>VERIFIED</span>
<span class='term-green'>[+] Digital Signature: Ed25519 (Operator-Key-ID: 0x9F8B3C1A) [VALID]</span>
<span class='term-cyan'>[[OK]] Full chain-of-custody intact. Admissible for forensic presentation.</span>
`);
                break;

            case "verify":
            case "ax-verify":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-RELEASE-VERIFY] Master Cryptographic Manifest Validation</span>
<span class='term-yellow'>[*] Verifying release checksums in BUILD_MANIFEST.json...</span>
<span class='term-green'>[PASS] bin/ax                          (SHA-256 Valid)</span>
<span class='term-green'>[PASS] scripts-hub/ax-pathfinder.py    (SHA-256 Valid)</span>
<span class='term-green'>[PASS] scripts-hub/ax-team.py          (SHA-256 Valid)</span>
<span class='term-green'>[PASS] scripts-hub/ax-ghost.py         (SHA-256 Valid)</span>
<span class='term-green'>[PASS] scripts-hub/ax-radio.py         (SHA-256 Valid)</span>
<span class='term-green'>[PASS] scripts-hub/ax-evidence.py      (SHA-256 Valid)</span>
<span class='term-cyan'>[[OK]] Result: 21 of 21 core release signatures VALID (100% integrity).</span>
`);
                break;

            case "doctor":
            case "ax-doctor":
                printTerminalLine(`
<span class='term-cyan term-bold'>[AX-DOCTOR] System Health Diagnostics</span>
<span class='term-green'>[PASS] Architecture: x86_64 / aarch64 AVF ready</span>
<span class='term-green'>[PASS] Kernel: Linux 6.1.0-sec POSIX compliant</span>
<span class='term-green'>[PASS] Zero-Dependency Python: 100% Standard Library</span>
<span class='term-green'>[PASS] Persistent Mount: /asterix_persistent (Encrypted)</span>
<span class='term-green'>[PASS] Audio Synthesizer: Web Audio API Active</span>
<span class='term-cyan'>[[OK]] All core subsystems green. Node operational.</span>
`);
                break;

            case "neofetch":
            case "pfetch":
            case "fastfetch":
                printTerminalLine(`
<pre style='color: var(--accent-cyan); font-family: var(--font-mono); margin: 0;'>
      /\\         <span style='color:#fff;'>operator@asterix-sec</span>
     /  \\        --------------------
    / /\\ \\       <span style='color:var(--text-muted);'>OS:</span> ASTERIX OS v2.0 (Phantom) x86_64
   / /__\\ \\      <span style='color:var(--text-muted);'>Host:</span> Sovereign Quantum Node (Model X9)
  / /    \\ \\     <span style='color:var(--text-muted);'>Kernel:</span> 6.1.0-sec-amd64
 / /      \\ \\    <span style='color:var(--text-muted);'>Uptime:</span> 14 hours, 32 mins
/_/        \\_\\   <span style='color:var(--text-muted);'>Packages:</span> 2482 (dpkg), 12 (as-pkg)
                 <span style='color:var(--text-muted);'>Shell:</span> as-sh 2.0.0 (POSIX compliant)
                 <span style='color:var(--text-muted);'>Resolution:</span> 1920x1080 @ 144Hz
                 <span style='color:var(--text-muted);'>DE:</span> ASTERIX Cybernetic HUD 2.0
                 <span style='color:var(--text-muted);'>WM:</span> CyberGlass WM
                 <span style='color:var(--text-muted);'>Terminal:</span> as-term-pty
                 <span style='color:var(--text-muted);'>CPU:</span> AMD Ryzen 9 7950X (12) @ 4.500GHz
                 <span style='color:var(--text-muted);'>GPU:</span> Sovereign Threat Processing Unit (TPU)
                 <span style='color:var(--text-muted);'>Memory:</span> 3410MiB / 16384MiB (21%)
                 <span style='color:var(--text-muted);'>Storage:</span> /asterix_persistent (Ext4 Encrypted)
</pre>
<div style='display:flex; gap:6px; margin-top:6px;'>
  <span style='background:#000; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#ff3366; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#00ff88; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#ffb703; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#00ffea; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#ff00ea; width:16px; height:10px; display:inline-block;'></span>
  <span style='background:#fff; width:16px; height:10px; display:inline-block;'></span>
</div>
`);
                break;

            case "clear":
                const out = document.getElementById("terminalOutput");
                if (out) out.innerHTML = "";
                break;

            case "pwd":
                printTerminalLine(currentDir);
                break;

            case "whoami":
                printTerminalLine("operator (uid=0 root)");
                break;

            case "id":
                printTerminalLine("uid=0(operator) gid=0(root) groups=0(root),27(sudo),100(users),999(cyber-sec)");
                break;

            case "uname":
                if (args.includes("-a") || args.length === 0) {
                    printTerminalLine("Linux asterix-sec 6.1.0-sec-amd64 #1 SMP PREEMPT_DYNAMIC NEXO x86_64 GNU/Linux");
                } else {
                    printTerminalLine("Linux");
                }
                break;

            case "date":
                printTerminalLine(new Date().toString());
                break;

            case "uptime":
                printTerminalLine(" 12:45:10 up 14:32,  1 user,  load average: 0.34, 0.28, 0.19");
                break;

            case "ls":
                let targetPath = currentDir;
                let showAll = false;
                for (const a of args) {
                    if (a.startsWith("-")) {
                        if (a.includes("a")) showAll = true;
                    } else {
                        targetPath = resolvePath(currentDir, a);
                    }
                }
                const dirNode = virtualFS[targetPath];
                if (!dirNode) {
                    printTerminalLine(`<span class='term-red'>ls: cannot access '${targetPath}': No such file or directory</span>`);
                } else if (dirNode.type !== "dir") {
                    printTerminalLine(targetPath.split("/").pop());
                } else {
                    let items = dirNode.children || [];
                    if (showAll) {
                        items = [".", "..", ...items];
                    }
                    const formatted = items.map(name => {
                        const fullChild = targetPath === "/" ? "/" + name : targetPath + "/" + name;
                        const childNode = virtualFS[fullChild];
                        if (name === "." || name === ".." || (childNode && childNode.type === "dir")) {
                            return `<span class='term-cyan term-bold'>${name}/</span>`;
                        }
                        if (name.endsWith(".sh") || name.endsWith(".py") || targetPath === "/bin") {
                            return `<span class='term-green term-bold'>${name}*</span>`;
                        }
                        return name;
                    });
                    printTerminalLine(formatted.join("&nbsp;&nbsp;&nbsp;&nbsp;"));
                }
                break;

            case "cd":
                const dest = args[0] || "/home/operator";
                const newPath = resolvePath(currentDir, dest);
                const targetNode = virtualFS[newPath];
                if (!targetNode) {
                    printTerminalLine(`<span class='term-red'>bash: cd: ${dest}: No such file or directory</span>`);
                } else if (targetNode.type !== "dir") {
                    printTerminalLine(`<span class='term-red'>bash: cd: ${dest}: Not a directory</span>`);
                } else {
                    currentDir = newPath;
                }
                break;

            case "cat":
                if (!args[0]) {
                    printTerminalLine("<span class='term-yellow'>Usage: cat &lt;filename&gt;</span>");
                    return;
                }
                const catPath = resolvePath(currentDir, args[0]);
                const fileNode = virtualFS[catPath];
                if (!fileNode) {
                    printTerminalLine(`<span class='term-red'>cat: ${args[0]}: No such file or directory</span>`);
                } else if (fileNode.type === "dir") {
                    printTerminalLine(`<span class='term-red'>cat: ${args[0]}: Is a directory</span>`);
                } else {
                    printTerminalLine(escapeHtml(fileNode.content).replace(/\n/g, "<br>"));
                }
                break;

            case "touch":
                if (!args[0]) {
                    printTerminalLine("<span class='term-yellow'>Usage: touch &lt;filename&gt;</span>");
                    return;
                }
                const newFilePath = resolvePath(currentDir, args[0]);
                if (virtualFS[newFilePath]) {
                    printTerminalLine(`Updated timestamp for ${args[0]}`);
                } else {
                    virtualFS[newFilePath] = { type: "file", content: "" };
                    const parent = newFilePath.substring(0, newFilePath.lastIndexOf("/")) || "/";
                    if (virtualFS[parent] && virtualFS[parent].children) {
                        virtualFS[parent].children.push(args[0]);
                    }
                    saveVirtualFS();
                    printTerminalLine(`Created file: ${args[0]}`);
                }
                break;

            case "mkdir":
                if (!args[0]) {
                    printTerminalLine("<span class='term-yellow'>Usage: mkdir &lt;dirname&gt;</span>");
                    return;
                }
                const newDirPath = resolvePath(currentDir, args[0]);
                if (virtualFS[newDirPath]) {
                    printTerminalLine(`<span class='term-red'>mkdir: cannot create directory '${args[0]}': File exists</span>`);
                } else {
                    virtualFS[newDirPath] = { type: "dir", children: [] };
                    const parent = newDirPath.substring(0, newDirPath.lastIndexOf("/")) || "/";
                    if (virtualFS[parent] && virtualFS[parent].children) {
                        virtualFS[parent].children.push(args[0]);
                    }
                    saveVirtualFS();
                    printTerminalLine(`Created directory: ${args[0]}`);
                }
                break;

            case "rm":
                if (!args[0]) {
                    printTerminalLine("<span class='term-yellow'>Usage: rm [-rf] &lt;path&gt;</span>");
                    return;
                }
                const targetToRemove = args[args.length - 1];
                const rmPath = resolvePath(currentDir, targetToRemove);
                if (!virtualFS[rmPath]) {
                    printTerminalLine(`<span class='term-red'>rm: cannot remove '${targetToRemove}': No such file or directory</span>`);
                } else if (rmPath === "/" || rmPath === "/bin" || rmPath === "/etc") {
                    printTerminalLine("<span class='term-red'>rm: Critical system path protected by Sovereign Shield</span>");
                } else {
                    delete virtualFS[rmPath];
                    const parent = rmPath.substring(0, rmPath.lastIndexOf("/")) || "/";
                    if (virtualFS[parent] && virtualFS[parent].children) {
                        virtualFS[parent].children = virtualFS[parent].children.filter(f => f !== targetToRemove);
                    }
                    saveVirtualFS();
                    printTerminalLine(`Removed: ${targetToRemove}`);
                }
                break;

            case "echo":
                printTerminalLine(escapeHtml(args.join(" ")));
                break;

            case "ps":
                printTerminalLine(`
<span class='term-dim'>  PID TTY          TIME CMD</span>
    1 ?        00:00:02 systemd
  104 ?        00:00:00 net-sentineld
  208 ?        00:00:01 anti-attack-mitigator
  315 ?        00:00:00 dark-engine-guard
  512 tty1     00:00:04 as-desktop-env
  541 tty1     00:00:00 as-sh
`);
                break;

            case "btop":
            case "top":
            case "htop":
                openWindow("as-monitor");
                printTerminalLine("<span class='term-green'>Opened Btop Telemetry HUD in dedicated window.</span>");
                break;

            case "nmap":
                const target = args[0] || "10.0.8.0/24";
                printTerminalLine(`[+] Starting Nmap 7.94 ( https://nmap.org ) at 12:45 UTC`);
                printTerminalLine(`[+] Initiating SYN Stealth Scan against ${escapeHtml(target)}...`);
                setTimeout(() => {
                    printTerminalLine(`[+] Discovered open port 22/tcp on 10.0.8.102 (OpenSSH 9.2p1 Debian)`);
                    printTerminalLine(`[+] Discovered open port 80/tcp on 10.0.8.102 (Nginx 1.22.1)`);
                    printTerminalLine(`[+] Discovered open port 443/tcp on 10.0.8.102 (TLSv1.3 - ECDSA P-256)`);
                    printTerminalLine(`[+] Discovered open port 8080/tcp on 10.0.8.140 (Apache Tomcat 10)`);
                    printTerminalLine(`<span class='term-green'>Nmap done: 256 IP addresses (2 hosts up) scanned in 1.42 seconds</span>`);
                }, 400);
                break;

            case "net-sentinel":
                printTerminalLine("<span class='term-cyan'>[NET-SENTINEL v1.0.2] Pure Rust Thread-Pooled Scanner Active</span>");
                printTerminalLine("[+] Worker threads: 16 | Socket timeout: 200ms");
                printTerminalLine("[+] Subnet: 10.0.8.0/24 -> 100% complete | 0 packet loss");
                printTerminalLine("<span class='term-green'>[OK] No unauthorized rogue access points detected.</span>");
                break;

            case "bin-inspector":
                const binTarget = args[0] || "/bin/as-sh";
                printTerminalLine(`<span class='term-cyan'>[BIN-INSPECTOR v1.0.1] Analyzing ELF binary: ${binTarget}</span>`);
                printTerminalLine("[+] Architecture: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV)");
                printTerminalLine("[+] Shannon Entropy: 6.42 / 8.0 (Normal code density)");
                printTerminalLine("[+] Stack Canary: PRESENT");
                printTerminalLine("[+] NX (No-Execute): ENABLED (W^X Compliant)");
                printTerminalLine("[+] PIE (Position Independent): ENABLED");
                printTerminalLine("<span class='term-green'>[STATUS] Binary hardened against ROP / stack execution.</span>");
                break;

            case "log-hunter":
                printTerminalLine("<span class='term-cyan'>[LOG-HUNTER v1.0.0] Parsing /var/log/syslog for threat signatures...</span>");
                printTerminalLine("[+] Signatures loaded: 4,120 CVE signatures");
                printTerminalLine("[+] Event count: 18,492 lines analyzed");
                printTerminalLine("<span class='term-green'>[RESULT] 0 critical intrusions, 1 failed SSH probe (auto-blocked by firewall).</span>");
                break;

            case "crypto-core":
                const hash = args[0] || "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8";
                printTerminalLine(`<span class='term-cyan'>[CRYPTO-CORE v0.9.5] Inspecting hash: ${hash}</span>`);
                printTerminalLine("[+] Detected format: SHA-256 (256-bit)");
                printTerminalLine("[+] Running dictionary attack with rockyou-sec-subset.txt...");
                setTimeout(() => {
                    if (hash.startsWith("5e88")) {
                        printTerminalLine("<span class='term-green'>[CRACKED] Plaintext: 'password' (Entropy: Very Low)</span>");
                    } else {
                        printTerminalLine("<span class='term-yellow'>[EXHAUSTED] Hash not present in local rainbow table.</span>");
                    }
                }, 300);
                break;

            case "python3":
            case "python":
                if (args[0]) {
                    const scriptPath = resolvePath(currentDir, args[0]);
                    const scriptNode = virtualFS[scriptPath];
                    if (scriptNode) {
                        printTerminalLine(`<span class='term-dim'>[Running ${args[0]} via Python 3.11.2]</span>`);
                        printTerminalLine("[*] Probing target stack protections...");
                        printTerminalLine("[+] NX (No-Execute) Bit: ACTIVE");
                        printTerminalLine("[+] ASLR Entropy: 28-bit randomized");
                        printTerminalLine("[!] Target safe from simple buffer overrun");
                    } else {
                        printTerminalLine(`<span class='term-red'>python3: can't open file '${args[0]}': [Errno 2] No such file or directory</span>`);
                    }
                } else {
                    printTerminalLine("Python 3.11.2 (main, ASTERIX Linux 6.1-sec)");
                    printTerminalLine("Type 'help', 'copyright', 'credits' or 'license' for more info. (Exit via Ctrl+C)");
                }
                break;

            case "apt":
            case "apt-get":
                const sub = args[0] || "help";
                if (sub === "update") {
                    printTerminalLine("Hit:1 https://deb.asterix-os.org/sec phantom InRelease");
                    printTerminalLine("Get:2 https://deb.debian.org/debian bookworm InRelease [151 kB]");
                    printTerminalLine("<span class='term-green'>Reading package lists... Done</span>");
                    printTerminalLine("<span class='term-green'>All packages are up to date.</span>");
                } else if (sub === "install") {
                    const pkg = args[1] || "wireshark";
                    printTerminalLine(`Reading package lists... Done`);
                    printTerminalLine(`Building dependency tree... Done`);
                    printTerminalLine(`The following NEW packages will be installed: ${pkg}`);
                    printTerminalLine(`0 upgraded, 1 newly installed, 0 to remove.`);
                    printTerminalLine(`<span class='term-green'>Unpacking ${pkg} (2.4.1-1)... Done. Setting up ${pkg}... Done.</span>`);
                } else {
                    printTerminalLine("Usage: apt [update | install &lt;pkg&gt; | list]");
                }
                break;

            case "as-ai":
                const prompt = args.join(" ");
                if (!prompt) {
                    printTerminalLine("<span class='term-yellow'>Usage: as-ai &lt;your question or instruction&gt;</span>");
                    return;
                }
                printTerminalLine(`<span class='term-cyan'>[ASTERIX AI] Analyzing prompt: '${escapeHtml(prompt)}'...</span>`);
                setTimeout(() => {
                    printTerminalLine(`<span class='term-green'>[ADVICE] Recommended parameters: Use 'nmap -sS -sV -T4 -p-' with IP decoy rotation enabled for stealth evasion. Memory protections remain optimal.</span>`);
                }, 350);
                break;

            case "matrix":
            case "cmatrix":
                printTerminalLine("<span class='term-green'>Entering matrix data stream mode... (Press any key to halt)</span>");
                let count = 0;
                const matInterval = setInterval(() => {
                    const chars = "0101010192837465ABCDXYZ@#$%&*";
                    let line = "";
                    for (let i = 0; i < 60; i++) {
                        line += chars[Math.floor(Math.random() * chars.length)];
                    }
                    printTerminalLine(`<span style='color:#00ff41; font-family:monospace;'>${line}</span>`);
                    count++;
                    if (count > 15) clearInterval(matInterval);
                }, 80);
                break;

            case "reboot":
                printTerminalLine("<span class='term-yellow'>System reboot initiated...</span>");
                setTimeout(() => {
                    const boot = document.getElementById("bootScreen");
                    if (boot) {
                        boot.classList.remove("boot-done");
                        runBootSequence();
                    }
                }, 600);
                break;

            default:
                printTerminalLine(`<span class='term-red'>bash: ${escapeHtml(cmd)}: command not found. Type 'help' for manual.</span>`);
                soundFX.error();
                break;
        }
    }

    // -----------------------------------------------------------------
    // 8. FILE EXPLORER (as-files)
    // -----------------------------------------------------------------
    let fileExplorerCurrentDir = "/home/operator";
    let selectedExplorerItem = null;

    function setSelectedExplorerItem(path) {
        selectedExplorerItem = path;
        const selected = document.querySelectorAll(".file-card-item");
        selected.forEach((card) => {
            const match = card.dataset.path === path;
            card.style.background = match ? "rgba(0, 255, 234, 0.2)" : "";
        });
    }

    window.browseDirectory = function (path) {
        fileExplorerCurrentDir = path;
        selectedExplorerItem = null;
        renderFileExplorer();
        soundFX.click();
    };

    window.navigateFilesUp = function () {
        if (fileExplorerCurrentDir === "/") return;
        const parent = fileExplorerCurrentDir.substring(0, fileExplorerCurrentDir.lastIndexOf("/")) || "/";
        fileExplorerCurrentDir = parent;
        renderFileExplorer();
        soundFX.click();
    };

    window.navigateFilesBack = function () {
        navigateFilesUp();
    };

    window.navigateFilesForward = function () {
        soundFX.click();
    };

    window.createNewFilePrompt = function () {
        const name = prompt("Enter new filename:", "untitled.txt");
        if (!name) return;
        const fullPath = resolvePath(fileExplorerCurrentDir, name);
        if (virtualFS[fullPath]) {
            alert("A file with this name already exists!");
            return;
        }
        virtualFS[fullPath] = { type: "file", content: "# ASTERIX Created File\n" };
        const dirNode = virtualFS[fileExplorerCurrentDir];
        if (dirNode && dirNode.children) {
            dirNode.children.push(name);
        }
        saveVirtualFS();
        renderFileExplorer();
        soundFX.click();
    };

    window.createNewDirPrompt = function () {
        const name = prompt("Enter new folder name:", "New_Folder");
        if (!name) return;
        const fullPath = resolvePath(fileExplorerCurrentDir, name);
        if (virtualFS[fullPath]) {
            alert("A directory with this name already exists!");
            return;
        }
        virtualFS[fullPath] = { type: "dir", children: [] };
        const dirNode = virtualFS[fileExplorerCurrentDir];
        if (dirNode && dirNode.children) {
            dirNode.children.push(name);
        }
        saveVirtualFS();
        renderFileExplorer();
        soundFX.click();
    };

    function removeNodeRecursively(path) {
        const node = virtualFS[path];
        if (!node) return;
        if (node.type === "dir") {
            Object.keys(virtualFS).forEach((key) => {
                if (key === path || (key.startsWith(path + "/"))) {
                    delete virtualFS[key];
                }
            });
        }
        delete virtualFS[path];

        const parentPath = path.substring(0, path.lastIndexOf("/")) || "/";
        const parentNode = virtualFS[parentPath];
        if (parentNode && parentNode.children) {
            parentNode.children = parentNode.children.filter((name) => {
                const candidate = parentPath === "/" ? `/${name}` : `${parentPath}/${name}`;
                return candidate !== path;
            });
        }
    }

    window.renameSelectedFile = function () {
        const target = selectedExplorerItem || activePreviewPath;
        if (!target) {
            alert("Select a file or folder first.");
            return;
        }
        const currentName = target.split("/").pop();
        const nextName = prompt("Rename item:", currentName);
        if (!nextName || !nextName.trim()) return;

        const cleanName = nextName.trim();
        const parentPath = target.substring(0, target.lastIndexOf("/")) || "/";
        const nextPath = parentPath === "/" ? `/${cleanName}` : `${parentPath}/${cleanName}`;

        if (virtualFS[nextPath]) {
            alert("An item with that name already exists.");
            return;
        }

        const node = virtualFS[target];
        if (!node) {
            alert("Selected item no longer exists.");
            return;
        }

        virtualFS[nextPath] = node;
        delete virtualFS[target];

        const parentNode = virtualFS[parentPath];
        if (parentNode && parentNode.children) {
            const idx = parentNode.children.indexOf(currentName);
            if (idx >= 0) parentNode.children[idx] = cleanName;
        }

        selectedExplorerItem = nextPath;
        if (activePreviewPath === target) {
            activePreviewPath = nextPath;
        }
        saveVirtualFS();
        renderFileExplorer();
        soundFX.click();
    };

    window.deleteSelectedItem = function () {
        const target = selectedExplorerItem || activePreviewPath;
        if (!target) {
            alert("Select a file or folder first.");
            return;
        }

        const name = target.split("/").pop();
        if (!confirm(`Delete ${name}? This cannot be undone.`)) return;

        removeNodeRecursively(target);
        selectedExplorerItem = null;
        if (activePreviewPath === target) {
            activePreviewPath = null;
            const pane = document.getElementById("filePreviewPane");
            if (pane) pane.classList.remove("open");
        }

        saveVirtualFS();
        renderFileExplorer();
        soundFX.winClose();
    };

    window.closeFilePreview = function () {
        const pane = document.getElementById("filePreviewPane");
        if (pane) pane.classList.remove("open");
    };

    function getFileExplorerContextTarget() {
        if (selectedExplorerItem) return selectedExplorerItem;
        if (activePreviewPath) return activePreviewPath;
        return fileExplorerCurrentDir;
    }

    window.handleFileExplorerContextAction = function (action) {
        const target = getFileExplorerContextTarget();
        const menu = document.getElementById("fileExplorerContextMenu");
        if (menu) menu.classList.remove("open");

        if (!target) return;

        if (action === "open") {
            const node = virtualFS[target];
            if (node && node.type === "dir") {
                fileExplorerCurrentDir = target;
                renderFileExplorer();
            } else {
                const name = target.split("/").pop();
                previewFile(target, name);
            }
            return;
        }

        if (action === "new-file") {
            createNewFilePrompt();
            return;
        }

        if (action === "new-folder") {
            createNewDirPrompt();
            return;
        }

        if (action === "rename") {
            renameSelectedFile();
            return;
        }

        if (action === "delete") {
            deleteSelectedItem();
        }
    };

    function initFileExplorerContextMenu() {
        const menu = document.getElementById("fileExplorerContextMenu");
        const grid = document.getElementById("filesGrid");
        if (!menu || !grid) return;

        grid.addEventListener("contextmenu", (event) => {
            const item = event.target.closest(".file-card-item");
            if (item) {
                setSelectedExplorerItem(item.dataset.path || getFileExplorerContextTarget());
            } else {
                selectedExplorerItem = fileExplorerCurrentDir;
            }
            event.preventDefault();
            menu.style.top = `${event.clientY}px`;
            menu.style.left = `${event.clientX}px`;
            menu.classList.add("open");
        });

        document.addEventListener("click", (event) => {
            const clickedInsideMenu = menu.contains(event.target);
            const clickedItem = event.target.closest(".file-card-item");
            if (!clickedInsideMenu && !clickedItem) {
                menu.classList.remove("open");
            }
        });
    }

    function reorderDirectoryChildren(dirPath, draggedPath, targetPath) {
        const dirNode = virtualFS[dirPath];
        if (!dirNode || dirNode.type !== "dir") return false;

        const draggedName = draggedPath.split("/").pop();
        const targetName = targetPath.split("/").pop();
        if (!draggedName || !targetName) return false;

        const current = [...(dirNode.children || [])];
        const fromIndex = current.indexOf(draggedName);
        const toIndex = current.indexOf(targetName);
        if (fromIndex < 0 || toIndex < 0 || fromIndex === toIndex) return false;

        const [moved] = current.splice(fromIndex, 1);
        current.splice(toIndex, 0, moved);
        dirNode.children = current;
        saveVirtualFS();
        return true;
    }

    function renderFileExplorer() {
        const pathInput = document.getElementById("filesPathInput");
        const grid = document.getElementById("filesGrid");
        const statusBar = document.getElementById("filesStatusBar");
        if (!grid) return;

        if (pathInput) pathInput.value = fileExplorerCurrentDir;
        grid.innerHTML = "";

        // Highlight active sidebar button
        document.querySelectorAll(".files-sidebar .files-side-btn").forEach(btn => {
            btn.classList.remove("active");
            if (btn.getAttribute("onclick") && btn.getAttribute("onclick").includes(`'${fileExplorerCurrentDir}'`)) {
                btn.classList.add("active");
            }
        });

        const dirNode = virtualFS[fileExplorerCurrentDir];
        if (!dirNode || dirNode.type !== "dir") {
            grid.innerHTML = `<div style='padding:20px; color:var(--accent-red);'>Directory not accessible</div>`;
            return;
        }

        const items = dirNode.children || [];
        if (statusBar) {
            statusBar.innerHTML = `<span>${items.length} items | Free space: 42.8 GB (Persistent Ext4)</span>`;
        }

        if (items.length === 0) {
            grid.innerHTML = `<div style='grid-column: span 4; padding:30px; text-align:center; color:var(--text-dim);'>Folder is empty</div>`;
            return;
        }

        items.forEach(itemName => {
            const itemFullPath = fileExplorerCurrentDir === "/" ? "/" + itemName : fileExplorerCurrentDir + "/" + itemName;
            const itemNode = virtualFS[itemFullPath];
            const isDir = itemNode && itemNode.type === "dir";

            const card = document.createElement("div");
            card.className = "file-card-item";

            let icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
            if (isDir) icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>`;
            else if (itemName.endsWith(".py") || itemName.endsWith(".sh")) icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>`;
            else if (itemName.endsWith(".rs") || itemName.endsWith(".c")) icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>`;
            else if (itemName.endsWith(".json")) icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`;
            else if (itemName.endsWith(".enc") || itemName.endsWith(".bin")) icon = `<svg class="svg-icon icon-lg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`;

            card.innerHTML = `
                <div class="file-card-icon">${icon}</div>
                <div class="file-card-name" title="${itemName}">${itemName}</div>
            `;

            card.dataset.path = itemFullPath;
            card.draggable = true;

            card.addEventListener("dragstart", (event) => {
                event.dataTransfer?.setData("text/plain", itemFullPath);
                card.classList.add("dragging");
            });

            card.addEventListener("dragover", (event) => {
                event.preventDefault();
                card.classList.add("drop-target");
            });

            card.addEventListener("dragleave", () => {
                card.classList.remove("drop-target");
            });

            card.addEventListener("drop", (event) => {
                event.preventDefault();
                const sourcePath = event.dataTransfer?.getData("text/plain");
                card.classList.remove("drop-target");
                if (sourcePath && sourcePath !== itemFullPath) {
                    reorderDirectoryChildren(fileExplorerCurrentDir, sourcePath, itemFullPath);
                    renderFileExplorer();
                }
            });

            card.addEventListener("dragend", () => {
                card.classList.remove("dragging", "drop-target");
            });

            card.addEventListener("click", () => {
                setSelectedExplorerItem(itemFullPath);
                soundFX.click();
            });

            card.addEventListener("dblclick", () => {
                if (isDir) {
                    fileExplorerCurrentDir = itemFullPath;
                    selectedExplorerItem = itemFullPath;
                    renderFileExplorer();
                } else {
                    previewFile(itemFullPath, itemName);
                }
            });

            grid.appendChild(card);
        });
    }

    let activePreviewPath = null;

    function previewFile(fullPath, fileName) {
        const pane = document.getElementById("filePreviewPane");
        const nameEl = document.getElementById("previewFileName");
        const codeEl = document.getElementById("previewFileContent");
        const editBtn = document.getElementById("editFileBtn");
        const saveBtn = document.getElementById("saveFileBtn");
        if (!pane || !nameEl || !codeEl) return;

        activePreviewPath = fullPath;
        const node = virtualFS[fullPath];
        nameEl.textContent = fileName;
        codeEl.textContent = node && node.content !== undefined ? node.content : "[No content / Binary data]";
        if (editBtn) editBtn.style.display = "inline-flex";
        if (saveBtn) saveBtn.style.display = "none";
        pane.classList.add("open");
        soundFX.winOpen();
    }

    window.openFileEditor = function () {
        if (!activePreviewPath) return;
        const fileNode = virtualFS[activePreviewPath];
        if (!fileNode || fileNode.type !== "file") return;

        const codeEl = document.getElementById("previewFileContent");
        const saveBtn = document.getElementById("saveFileBtn");
        const editBtn = document.getElementById("editFileBtn");
        if (!codeEl) return;

        codeEl.innerHTML = "";
        const textarea = document.createElement("textarea");
        textarea.id = "activePreviewEditor";
        textarea.className = "file-preview-editor";
        textarea.value = fileNode.content || "";
        codeEl.appendChild(textarea);
        if (editBtn) editBtn.style.display = "none";
        if (saveBtn) saveBtn.style.display = "inline-flex";
        textarea.focus();
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    };

    window.saveSelectedFile = function () {
        if (!activePreviewPath) return;
        const editor = document.getElementById("activePreviewEditor");
        if (!editor) return;

        const fileNode = virtualFS[activePreviewPath];
        if (fileNode && fileNode.type === "file") {
            fileNode.content = editor.value;
            saveVirtualFS();
            const previewName = document.getElementById("previewFileName");
            if (previewName) previewName.textContent = activePreviewPath.split("/").pop();
            const previewContent = document.getElementById("previewFileContent");
            if (previewContent) previewContent.textContent = editor.value;
            const saveBtn = document.getElementById("saveFileBtn");
            const editBtn = document.getElementById("editFileBtn");
            if (saveBtn) saveBtn.style.display = "none";
            if (editBtn) editBtn.style.display = "inline-flex";
            soundFX.chime();
        }
    };

    window.closeFilePreview = function () {
        const pane = document.getElementById("filePreviewPane");
        if (pane) pane.classList.remove("open");
        activePreviewPath = null;
    };

    // -----------------------------------------------------------------
    // 9. SECURITY SUITE (12 Subsystems Engine)
    // -----------------------------------------------------------------
    const SUBSYSTEMS_DATA = [
        {
            num: "01",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
            name: "Reconnaissance & OSINT Hub",
            tools: "Nmap, Masscan, DnsRecon, Whois, Netdiscover, Sherlock",
            desc: "Full passive and active network intelligence gathering with thread-pooled port sweeps and DNS enumeration.",
            simulationLog: `[01. RECON] Initializing Masscan 1.3.2 on 10.0.8.0/24...
Discovered host 10.0.8.1 (Gateway) - 0.12ms
Discovered host 10.0.8.102 - Ports: 22, 80, 443 open
Executing Nmap NSE scripts for vulnerability triage...
[+] SSL Certificate: CN=asterix-sec.local (Expires in 365 days)
[+] Service Banner: nginx/1.22.1 (Debian)
Recon analysis logged to /asterix_persistent/recon_loot.json`
        },
        {
            num: "02",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`,
            name: "Web Application Warfare",
            tools: "SQLMap, Gobuster, Nikto, FFUF, WPScan, Wafw00f",
            desc: "Deep automated web application auditing, directory fuzzing, SQL injection probes, and WAF fingerprinting.",
            simulationLog: `[02. WEB WARFARE] Running Wafw00f on target endpoint: http://10.0.8.102/
[*] Testing generic detection mechanisms...
[+] The site appears behind: Cloudflare / Sovereign WAF
Starting FFUF wordlist injection (64 threads)...
[200 OK] /admin (Size: 412B)
[301 Moved] /api/v1 -> /api/v1/
[200 OK] /robots.txt (Disallow: /vault)
Triage complete: 0 high-risk SQLi vectors found.`
        },
        {
            num: "03",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="13" r="9"/><path d="M14.35 4.65 16.3 2.7a2.41 2.41 0 0 1 3.4 0l1.6 1.6a2.4 2.4 0 0 1 0 3.4l-1.95 1.95"/></svg>`,
            name: "Exploitation & Payloads",
            tools: "Metasploit Framework, SearchSploit, Socat, Netcat",
            desc: "Penetration testing payload generation, shellcode validation, and controlled sandbox exploits.",
            simulationLog: `[03. EXPLOIT] Metasploit Framework MSF6 Engine Loaded
[*] Payload: linux/x64/shell_reverse_tcp
[*] LHOST: 10.0.8.24 | LPORT: 4444
Generating hardened polymorphic shellcode...
[+] Encoded size: 119 bytes (x86/shikata_ga_nai)
[+] Stack Canary mitigation bypass: ARMED
Ready for controlled laboratory deployment.`
        },
        {
            num: "04",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 2l-2 2m-1.5 1.5L16 7l-2 2-2 2-2 2-1 1-3.5 3.5a5 5 0 1 1-7-7L8 7l2-2 2-2 1.5-1.5L15 2l6 0z"/></svg>`,
            name: "Password & Hash Auditing",
            tools: "Hashcat, John The Ripper, Hydra, Crunch, HashID",
            desc: "GPU-accelerated cryptographic auditing, dictionary rule mutations, and multi-protocol brute testing.",
            simulationLog: `[04. CRACK] Initializing Hashcat v6.2.6 (CUDA/OpenCL Accelerators)
Hashfile: /tmp/hashes.txt (SHA256 - Mode 1400)
Speed: 4,820 MH/s across 16 GPU Compute Units
[+] 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8:password
Session status: Exhausted (1 cracked, 0 remaining)
Time elapsed: 0.12s`
        },
        {
            num: "05",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
            name: "Sniffing & Traffic Control",
            tools: "Wireshark, TShark, Tcpdump, MacChanger, Hping3",
            desc: "Deep packet inspection, promiscuous packet capture, protocol dissection, and hardware MAC spoofing.",
            simulationLog: `[05. SNIFF] TShark listening on interface eth0 (Promiscuous Mode)
Capturing: TCP, UDP, ICMP, ARP
[Packet 1] ARP Who has 10.0.8.1? Tell 10.0.8.102
[Packet 2] TLSv1.3 Application Data (Length 1,420 bytes)
[Packet 3] DNS Standard query 0x1a2b A asterix-os.org
Total frames captured: 142 packets / 0 drops`
        },
        {
            num: "06",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg>`,
            name: "Wireless & Radio Attacks",
            tools: "Aircrack-ng, Wifite, Reaver, Kismet, PixieWPS",
            desc: "802.11 monitor mode injection, WPA3 SAE analysis, WPS PIN auditing, and Bluetooth Low Energy probing.",
            simulationLog: `[06. WIRELESS] Enabling monitor mode on phy0 -> wlan0mon
Scanning 2.4GHz & 5GHz spectrum...
BSSID: 74:83:C2:11:9A:04 | CH: 6 | PWR: -42dBm | SSID: CyberNet_Lab (WPA2-PSK)
Capturing EAPOL 4-Way Handshake...
[+] WPA handshake acquired! Written to /asterix_persistent/handshake.cap`
        },
        {
            num: "07",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>`,
            name: "Forensics & Steganography",
            tools: "Binwalk, Foremost, Scalpel, Steghide, Exiftool",
            desc: "Memory image carving, firmware extraction, filesystem artifact recovery, and hidden data analysis.",
            simulationLog: `[07. FORENSICS] Binwalk v2.3.3 analysis on firmware.bin
DECIMAL       HEXADECIMAL     DESCRIPTION
------------------------------------------------------------------
0             0x0             uImage header, header size: 64 bytes
64            0x40            gzip compressed data (Linux Kernel 6.1)
1840291       0x1C14A3        Squashfs filesystem, little endian, version 4.0
Extraction complete into /tmp/_firmware.bin.extracted`
        },
        {
            num: "08",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>`,
            name: "Reverse Engineering (R2)",
            tools: "Radare2, GDB, Hexedit, XXD, Strings, Valgrind",
            desc: "Interactive disassembly, CFG control flow graph rendering, heap profiling, and binary instrumentation.",
            simulationLog: `[08. REVERSE] Radare2 opened: /bin/as-sh
[0x00001000]> aaa (Analyze all flags, functions, cross-references)
[x] Analyze all flags
[x] Analyze len bytes of instructions
[0x00001000]> pdf @ main
0x00001000      endbr64
0x00001004      push rbp
0x00001005      mov rbp, rsp
0x00001008      lea rdi, [str.welcome_to_asterix]
0x0000100f      call sym.imp.puts
0x00001014      xor eax, eax
0x00001016      pop rbp
0x00001017      ret`
        },
        {
            num: "09",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`,
            name: "Full-Stack Dev Studio",
            tools: "Rust (Cargo), Go, C/C++, Python3, Node.js, LazyGit",
            desc: "High-performance systems programming toolchain with zero-overhead compiler diagnostics.",
            simulationLog: `[09. DEV STUDIO] Invoking Cargo 1.80.0 (Rust 2024 Edition)
Compiling asterix-engine v2.0.0 (/engine/net_sentinel)
   Compiling libc v0.2.155
   Compiling tokio v1.38.0
   Compiling threadpool v1.8.1
    Finished release [optimized + debuginfo] target(s) in 0.84s
Binary output: /bin/net-sentinel (Strip OK, 1.2MB)`
        },
        {
            num: "10",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>`,
            name: "ASTERIX Persistent Vault",
            tools: "Encrypted USB Storage Overlay, Android SDCard Sync",
            desc: "AES-256-XTS dual-layer cryptographic storage partition ensuring 100% data persistence on live boots.",
            simulationLog: `[10. VAULT] Checking /asterix_persistent LUKS status
Cipher: aes-xts-plain64 | Key size: 512 bits
Storage block: /dev/sdb3 (Persistent USB Partition)
Filesystem check: Clean (0 errors, 42.8 GB remaining)
All operator files, bookmarks, and configs securely saved.`
        },
        {
            num: "11",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/></svg>`,
            name: "Quad-Grid Tmux Studio",
            tools: "4-Way Split Workspace, 100k History, Mouse Scroll",
            desc: "Four-pane balanced terminal multiplexer workspace for concurrent scanning, sniffing, exploitation, and telemetry.",
            simulationLog: `[11. QUAD-GRID] Initializing Quad Tmux Multiplexer...
Pane 0 [Top-Left]:     Net-Sentinel Live Sniffer
Pane 1 [Top-Right]:    Btop Telemetry HUD
Pane 2 [Bottom-Left]:  Metasploit Interactive Console
Pane 3 [Bottom-Right]: Bash Operational Shell
Shortcut bound: Ctrl+A + q to balance panes.`
        },
        {
            num: "12",
            icon: `<svg class="svg-icon mini" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>`,
            name: "Subsystem Telemetry HUD",
            tools: "Btop, Htop, Sensor Gauges, Network Monitor",
            desc: "Real-time microsecond telemetry monitoring for kernel load, memory fragmentation, and network packets.",
            simulationLog: `[12. TELEMETRY] Telemetry Sensor Bridge Active
CPU Core 0-11: 24% load (38°C)
RAM: 3,410 MB / 16,384 MB (Swap: 0%)
Net eth0: In 18.9 MB/s | Out 4.2 MB/s
Kernel threat mitigation: 0 dropped packets.`
        }
    ];

    let activeSecIndex = 0;

    function initSecuritySuite() {
        const tabsContainer = document.getElementById("secSubsystemTabs");
        const detailsPanel = document.getElementById("secDetailsPanel");
        const runBtn = document.getElementById("secRunSimBtn");
        const consoleOut = document.getElementById("secConsoleOutput");
        if (!tabsContainer || !detailsPanel) return;

        tabsContainer.innerHTML = "";
        SUBSYSTEMS_DATA.forEach((sub, idx) => {
            const btn = document.createElement("button");
            btn.className = `sec-tab-btn ${idx === activeSecIndex ? "active" : ""}`;
            btn.innerHTML = `<span>${sub.icon}</span><span>${sub.num}. ${sub.name.split(" ")[0]}</span>`;
            btn.addEventListener("click", () => {
                activeSecIndex = idx;
                renderSecSubsystem();
                soundFX.click();
            });
            tabsContainer.appendChild(btn);
        });

        function renderSecSubsystem() {
            document.querySelectorAll(".sec-tab-btn").forEach((b, i) => {
                b.classList.toggle("active", i === activeSecIndex);
            });
            const sub = SUBSYSTEMS_DATA[activeSecIndex];
            detailsPanel.innerHTML = `
                <div class="sec-sub-num">SUBSYSTEM ${sub.num} // 12</div>
                <div class="sec-sub-title">${sub.icon} ${sub.name}</div>
                <div class="sec-sub-desc">${sub.desc}</div>
                <div class="sec-tools-box">
                    <div class="sec-tools-label">BUILT-IN ARMED TOOLS:</div>
                    <div class="sec-tools-list">${sub.tools}</div>
                </div>
            `;
        }

        renderSecSubsystem();

        if (runBtn) {
            runBtn.addEventListener("click", () => {
                initAudio();
                const sub = SUBSYSTEMS_DATA[activeSecIndex];
                consoleOut.innerHTML = `<div class='term-cyan'>[STARTING] Initializing ${sub.name}...</div>`;
                soundFX.chime();
                setTimeout(() => {
                    consoleOut.innerHTML = `<pre style='font-family:var(--font-mono); color:var(--accent-green); margin:0;'>${sub.simulationLog}</pre>`;
                }, 400);
            });
        }
    }

    // -----------------------------------------------------------------
    // 10. SYSTEM MONITOR & BTOP GRAPHS
    // -----------------------------------------------------------------
    let btopRunning = false;
    const cpuHistory = new Array(40).fill(20);
    const netHistory = new Array(40).fill(10);

    const PROCESSES_DATA = [
        { pid: 1, user: "root", cpu: "0.1", mem: "0.4", cmd: "systemd", status: "Running" },
        { pid: 88, user: "root", cpu: "1.2", mem: "0.8", cmd: "net-sentinel", status: "Running" },
        { pid: 142, user: "root", cpu: "0.4", mem: "0.6", cmd: "anti-attack-mitigator", status: "Running" },
        { pid: 210, user: "operator", cpu: "3.8", mem: "2.1", cmd: "as-desktop-env", status: "Running" },
        { pid: 304, user: "operator", cpu: "0.2", mem: "1.0", cmd: "as-sh (bash)", status: "Running" },
        { pid: 412, user: "root", cpu: "0.0", mem: "0.3", cmd: "luks-persistent-crypt", status: "Sleeping" },
        { pid: 519, user: "operator", cpu: "2.4", mem: "1.8", cmd: "btop++", status: "Running" }
    ];

    let selectedProcIndex = null;

    window.killSelectedProcess = function () {
        if (selectedProcIndex === null) {
            alert("Please select a process from the table to kill.");
            return;
        }
        const proc = PROCESSES_DATA[selectedProcIndex];
        if (proc.pid === 1) {
            alert("Cannot kill PID 1 (Init / systemd)!");
            return;
        }
        PROCESSES_DATA.splice(selectedProcIndex, 1);
        selectedProcIndex = null;
        renderProcTable();
        soundFX.winClose();
    };

    function renderProcTable() {
        const tbody = document.getElementById("procTableBody");
        if (!tbody) return;
        tbody.innerHTML = "";
        PROCESSES_DATA.forEach((p, idx) => {
            const tr = document.createElement("tr");
            if (idx === selectedProcIndex) tr.className = "selected";
            tr.innerHTML = `
                <td>${p.pid}</td>
                <td>${p.user}</td>
                <td style='color:var(--accent-cyan);'>${p.cpu}%</td>
                <td>${p.mem}%</td>
                <td><strong>${p.cmd}</strong></td>
                <td style='color:var(--accent-green);'>${p.status}</td>
            `;
            tr.addEventListener("click", () => {
                selectedProcIndex = idx;
                renderProcTable();
                soundFX.click();
            });
            tbody.appendChild(tr);
        });
    }

    function initCpuCores() {
        const grid = document.getElementById("cpuCoreGrid");
        if (!grid) return;
        grid.innerHTML = "";
        for (let i = 0; i < 12; i++) {
            const item = document.createElement("div");
            item.className = "core-item";
            item.id = `core-val-${i}`;
            item.innerHTML = `C${i}: <strong>24%</strong>`;
            grid.appendChild(item);
        }
    }

    function startBtopGraphs() {
        if (btopRunning) return;
        btopRunning = true;
        initCpuCores();
        renderProcTable();

        const cpuCanvas = document.getElementById("cpuGraphCanvas");
        const netCanvas = document.getElementById("netGraphCanvas");
        const cpuPctEl = document.getElementById("btopCpuPct");
        const trayCpuBadge = document.getElementById("trayCpuBadge");

        function drawGraph(canvas, data, color) {
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const w = canvas.width;
            const h = canvas.height;

            ctx.clearRect(0, 0, w, h);
            ctx.beginPath();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;

            const step = w / (data.length - 1);
            for (let i = 0; i < data.length; i++) {
                const x = i * step;
                const y = h - (data[i] / 100) * h;
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            // Fill area
            ctx.lineTo(w, h);
            ctx.lineTo(0, h);
            ctx.closePath();
            ctx.fillStyle = color.replace(")", ", 0.12)").replace("rgb", "rgba");
            ctx.fill();
        }

        setInterval(() => {
            // Random fluctuations
            const nextCpu = Math.floor(15 + Math.random() * 30);
            cpuHistory.shift();
            cpuHistory.push(nextCpu);

            const nextNet = Math.floor(10 + Math.random() * 50);
            netHistory.shift();
            netHistory.push(nextNet);

            drawGraph(cpuCanvas, cpuHistory, "rgb(0, 255, 234)");
            drawGraph(netCanvas, netHistory, "rgb(0, 255, 136)");

            if (cpuPctEl) cpuPctEl.textContent = `${nextCpu}%`;
            if (trayCpuBadge) trayCpuBadge.innerHTML = `CPU: <strong>${nextCpu}%</strong>`;

            // Update cores
            for (let i = 0; i < 12; i++) {
                const cVal = document.getElementById(`core-val-${i}`);
                if (cVal) {
                    const cLoad = Math.max(5, Math.min(99, Math.floor(nextCpu + (Math.random() * 20 - 10))));
                    cVal.innerHTML = `C${i}: <strong>${cLoad}%</strong>`;
                }
            }
        }, 1200);
    }

    // -----------------------------------------------------------------
    // 11. CODE STUDIO (as-code IDE)
    // -----------------------------------------------------------------
    const CODE_FILES = {
        "net_sentinel.rs": `// ==============================================================================
// ASTERIX OS v2.0 - Network Sentinel Core Engine (Pure Rust)
// ==============================================================================
use std::net::{TcpStream, SocketAddr};
use std::time::Duration;
use std::sync::{Arc, Mutex};

pub struct NetSentinel {
    target_subnet: String,
    thread_pool_size: usize,
    open_ports: Arc<Mutex<Vec<u16>>>,
}

impl NetSentinel {
    pub fn new(subnet: &str, threads: usize) -> Self {
        Self {
            target_subnet: subnet.to_string(),
            thread_pool_size: threads,
            open_ports: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub fn scan_port(&self, ip: &str, port: u16) -> bool {
        let addr_str = format!("{}:{}", ip, port);
        if let Ok(addr) = addr_str.parse::<SocketAddr>() {
            TcpStream::connect_timeout(&addr, Duration::from_millis(200)).is_ok()
        } else {
            false
        }
    }
}

fn main() {
    println!("[+] NetSentinel v1.0.2 initializing...");
    let sentinel = NetSentinel::new("10.0.8.0/24", 16);
    println!("[+] Thread pool armed. Ready for scan.");
}`,
        "dark_engine.c": `/* ==============================================================================
 * ASTERIX OS - Memory Protection & W^X Enforcement Validator
 * ============================================================================== */
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

int check_wx_violation(void *addr, size_t len) {
    /* Verify page permissions do NOT have PROT_WRITE | PROT_EXEC simultaneously */
    int flags = PROT_READ | PROT_WRITE;
    if (mprotect(addr, len, flags) == 0) {
        printf("[+] Page safely mapped READ+WRITE (No execute bit)\\n");
        return 0;
    }
    return -1;
}

int main(void) {
    printf("[DARK-ENGINE] Auditing kernel memory layout...\\n");
    void *test_page = mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_ANONYMOUS|MAP_PRIVATE, -1, 0);
    if (test_page != MAP_FAILED) {
        check_wx_violation(test_page, 4096);
        munmap(test_page, 4096);
    }
    printf("[+] Memory defense check PASSED.\\n");
    return 0;
}`,
        "ai_threat_triage.py": `#!/usr/bin/env python3
# ==============================================================================
# ASTERIX OS - Autonomous AI Threat Triage Engine
# ==============================================================================
import json
import time

class ThreatTriage:
    def __init__(self):
        self.rules = [
            {"sig": "SYN_FLOOD", "threshold": 500, "action": "BLOCK_IP"},
            {"sig": "PORT_SWEEP", "threshold": 50, "action": "DECOY_ROUTE"},
            {"sig": "ARP_POISON", "threshold": 5, "action": "STATIC_ARP_LOCK"}
        ]

    def evaluate_telemetry(self, packet_count, sig_type):
        for rule in self.rules:
            if rule["sig"] == sig_type and packet_count > rule["threshold"]:
                return f"[ALERT] Triggered {rule['action']} for {sig_type} (load={packet_count})"
        return "[PASS] Telemetry within baseline tolerances."

if __name__ == "__main__":
    triage = ThreatTriage()
    print(triage.evaluate_telemetry(720, "SYN_FLOOD"))
`,
        "bootloader.asm": `; ==============================================================================
; ASTERIX OS v2.0 - Hybrid Stage 1 Boot Sector (x86_64)
; ==============================================================================
[BITS 16]
[ORG 0x7C00]

start:
    cli                     ; Clear interrupts
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00          ; Stack grows downwards from boot sector

    mov si, msg_boot
    call print_string

    ; Load Stage 2 kernel image
    mov bx, 0x1000          ; Target memory address
    mov dh, 15              ; Read 15 sectors
    mov dl, [boot_drive]
    call disk_load

    jmp 0x1000:0000         ; Jump to Stage 2

print_string:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp print_string
.done:
    ret

disk_load:
    ret

msg_boot: db "ASTERIX BOOTLOADER v2.0 LOADED", 0x0D, 0x0A, 0
boot_drive: db 0

times 510 - ($ - $$) db 0
dw 0xAA55                   ; Boot sector signature
`
    };

    let activeCodeFile = "net_sentinel.rs";

    function initCodeStudio() {
        const tabsContainer = document.getElementById("codeEditorTabs");
        const textarea = document.getElementById("codeEditorTextArea");
        const gutter = document.getElementById("codeGutter");
        const metaEl = document.getElementById("codeFileMeta");
        if (!tabsContainer || !textarea) return;

        function loadFile(fileName) {
            activeCodeFile = fileName;
            textarea.value = CODE_FILES[fileName] || "";
            updateGutter();
            if (metaEl) {
                const lang = fileName.endsWith(".rs") ? "Rust (rustc 1.80)" :
                    fileName.endsWith(".c") ? "C (gcc 12.2)" :
                        fileName.endsWith(".py") ? "Python (3.11)" : "Assembly (nasm)";
                metaEl.innerHTML = `Language: <strong>${lang}</strong>`;
            }
        }

        function updateGutter() {
            const lines = textarea.value.split("\n").length;
            gutter.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join("<br>");
        }

        textarea.addEventListener("input", updateGutter);
        textarea.addEventListener("scroll", () => {
            gutter.scrollTop = textarea.scrollTop;
        });

        tabsContainer.querySelectorAll(".code-tab").forEach(tab => {
            tab.addEventListener("click", () => {
                tabsContainer.querySelectorAll(".code-tab").forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                loadFile(tab.dataset.file);
                soundFX.click();
            });
        });

        loadFile("net_sentinel.rs");
    }

    window.runCodeStudioScript = function () {
        initAudio();
        const consoleEl = document.getElementById("codeOutputConsole");
        if (!consoleEl) return;
        soundFX.chime();
        consoleEl.textContent = `[COMPILER] Invoking toolchain for ${activeCodeFile}...`;

        setTimeout(() => {
            if (activeCodeFile.endsWith(".rs")) {
                consoleEl.textContent = `   Compiling asterix-engine v2.0.0 (/engine/net_sentinel)
    Finished release [optimized] target(s) in 0.42s
[+] Running target/release/net_sentinel:
[+] NetSentinel v1.0.2 initializing...
[+] Thread pool armed (16 threads). Ready for scan.`;
            } else if (activeCodeFile.endsWith(".c")) {
                consoleEl.textContent = `gcc -O2 -fstack-protector-all -pie dark_engine.c -o /tmp/dark_engine
[+] Executing /tmp/dark_engine:
[DARK-ENGINE] Auditing kernel memory layout...
[+] Page safely mapped READ+WRITE (No execute bit)
[+] Memory defense check PASSED.`;
            } else if (activeCodeFile.endsWith(".py")) {
                consoleEl.textContent = `python3 ai_threat_triage.py
[ALERT] Triggered BLOCK_IP for SYN_FLOOD (load=720)`;
            } else {
                consoleEl.textContent = `nasm -f bin bootloader.asm -o /tmp/bootloader.bin
[+] Output binary size: 512 bytes (Valid MBR 0xAA55 boot signature)`;
            }
        }, 300);
    };

    // -----------------------------------------------------------------
    // 12. AI NEURAL COPILOT (as-ai)
    // -----------------------------------------------------------------
    window.sendAiPrompt = function (text) {
        const input = document.getElementById("aiChatInput");
        if (input) {
            input.value = text;
            sendAiChat();
        }
    };

    window.sendAiChat = function () {
        initAudio();
        const input = document.getElementById("aiChatInput");
        const history = document.getElementById("aiChatHistory");
        if (!input || !history) return;

        const text = input.value.trim();
        if (!text) return;
        input.value = "";

        // User message
        const userMsg = document.createElement("div");
        userMsg.className = "ai-msg user";
        userMsg.innerHTML = `
            <div class="msg-author">OPERATOR</div>
            <div class="msg-body">${escapeHtml(text)}</div>
        `;
        history.appendChild(userMsg);
        history.scrollTop = history.scrollHeight;
        soundFX.click();

        // Bot response simulation
        setTimeout(() => {
            const botMsg = document.createElement("div");
            botMsg.className = "ai-msg bot";
            let reply = "I have cross-checked your inquiry against the ASTERIX Sovereign rules engine. Telemetry indicates all system kernels and persistent stores are operating within nominal thresholds.";

            const lower = text.toLowerCase();
            if (lower.includes("nmap") || lower.includes("recon")) {
                reply = "For stealth reconnaissance without triggering firewall heuristics, run: 'nmap -sS -T2 -D RND:5 -p 22,80,443 <target>'. This uses random IP decoys to mask your origin node.";
            } else if (lower.includes("memory") || lower.includes("vulnerab")) {
                reply = "Kernel memory status: W^X (Write XOR Execute) is strictly enforced. ASLR entropy is active at 28-bit randomization. Stack canaries are verified on all Tier 1 Rust and C utilities.";
            } else if (lower.includes("repair") || lower.includes("leak") || lower.includes("code")) {
                reply = "Auto-Repair Suggestion: Ensure every malloc() or mmap() has a guaranteed corresponding free() or munmap() in the error unwind path, or utilize Rust's RAII ownership system for zero-leak memory safety.";
            } else if (lower.includes("rufus") || lower.includes("persist")) {
                reply = "To flash ASTERIX ISO with live persistence using Rufus on Windows: select your USB drive (>=8GB), drag the 'Persistent partition size' slider to 4GB-16GB, and select MBR with BIOS or UEFI target. Changes will persist permanently!";
            }

            botMsg.innerHTML = `
                <div class="msg-author">[AI] ASTERIX NEURAL ADVISOR</div>
                <div class="msg-body">${reply}</div>
            `;
            history.appendChild(botMsg);
            history.scrollTop = history.scrollHeight;
            soundFX.winOpen();
        }, 450);
    };

    function initVoice() {
        const micBtn = document.getElementById("voiceMicBtn");
        if (!micBtn) return;

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            micBtn.title = "Speech Recognition not supported in this browser";
            micBtn.style.opacity = "0.5";
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = "en-US";

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input = document.getElementById("aiChatInput");
            if (input) {
                input.value = transcript;
                sendAiChat();
            }
        };

        recognition.onerror = () => {
            micBtn.style.background = "";
        };

        recognition.onend = () => {
            micBtn.style.background = "";
        };

        micBtn.addEventListener("click", () => {
            initAudio();
            micBtn.style.background = "var(--accent-red)";
            recognition.start();
        });
    }

    // -----------------------------------------------------------------
    // 13. SOFTWARE CENTER (as-store)
    // -----------------------------------------------------------------
    const SOFTWARE_PACKAGES = [
        { name: "nmap-advanced", ver: "7.94-sec", desc: "Network exploration and security auditing tool", installed: true },
        { name: "metasploit-framework", ver: "6.3.55", desc: "Penetration testing and exploit execution platform", installed: true },
        { name: "wireshark-qt", ver: "4.2.1", desc: "Deep packet analyzer and live network sniffer", installed: true },
        { name: "radare2-suite", ver: "5.8.8", desc: "Advanced reverse engineering and binary analysis suite", installed: true },
        { name: "hashcat-cuda", ver: "6.2.6", desc: "GPU accelerated password recovery tool", installed: true },
        { name: "rustc-nightly", ver: "1.82.0", desc: "Empowering everyone to build reliable and efficient software", installed: true },
        { name: "btop-plus", ver: "1.3.2", desc: "Resource monitor that shows usage and stats for processor, memory", installed: true },
        { name: "proxychains-ng", ver: "4.16", desc: "Redirect connections through SOCKS4/5 and HTTP proxies", installed: false },
        { name: "aircrack-ng", ver: "1.7.0", desc: "Complete suite to assess WiFi network security", installed: false },
        { name: "binwalk", ver: "2.3.3", desc: "Firmware analysis and extraction tool", installed: true }
    ];

    function initSoftwareCenter() {
        const grid = document.getElementById("storePackagesGrid");
        const search = document.getElementById("storeSearchInput");
        if (!grid) return;

        function render(query = "") {
            grid.innerHTML = "";
            const filtered = SOFTWARE_PACKAGES.filter(p => !query || p.name.includes(query) || p.desc.toLowerCase().includes(query.toLowerCase()));
            filtered.forEach(pkg => {
                const card = document.createElement("div");
                card.className = "store-pkg-card";
                card.innerHTML = `
                    <div>
                        <div class="pkg-head">
                            <span class="pkg-icon"><svg class="svg-icon mini" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/></svg></span>
                            <div>
                                <div class="pkg-name">${pkg.name}</div>
                                <div class="pkg-ver">v${pkg.ver}</div>
                            </div>
                        </div>
                        <div class="pkg-desc">${pkg.desc}</div>
                    </div>
                    <button class="pkg-action-btn ${pkg.installed ? "installed" : ""}" onclick="toggleInstallPackage('${pkg.name}')">
                        ${pkg.installed ? "Installed" : "+ Install Package"}
                    </button>
                `;
                grid.appendChild(card);
            });
        }

        window.toggleInstallPackage = function (pkgName) {
            initAudio();
            const pkg = SOFTWARE_PACKAGES.find(p => p.name === pkgName);
            if (!pkg) return;
            pkg.installed = !pkg.installed;
            render(search ? search.value : "");
            soundFX.chime();
        };

        window.syncStoreRepositories = function () {
            initAudio();
            soundFX.chime();
            alert("apt-get update: Updated 2,482 package manifests from deb.asterix-os.org/sec");
        };

        if (search) {
            search.addEventListener("input", (e) => render(e.target.value.trim()));
        }
        render();
    }

    // -----------------------------------------------------------------
    // 14. CONTROL CENTER, WALLPAPERS & THEMES (as-settings)
    // -----------------------------------------------------------------
    const THEME_STORAGE_KEY = "asterix_desktop_theme";
    const WALLPAPER_STORAGE_KEY = "asterix_desktop_wallpaper";

    function initSettings() {
        // Nav tabs
        document.querySelectorAll(".settings-nav .set-nav-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".settings-nav .set-nav-btn").forEach(b => b.classList.remove("active"));
                document.querySelectorAll(".settings-content .set-tab-panel").forEach(p => p.classList.remove("active"));

                btn.classList.add("active");
                const target = document.getElementById(`set-tab-${btn.dataset.setTab}`);
                if (target) target.classList.add("active");
                soundFX.click();
            });
        });

        // Render 26 Wallpapers shelf
        const shelf = document.getElementById("wallpapersShelf");
        const currentWp = localStorage.getItem(WALLPAPER_STORAGE_KEY) || WALLPAPERS[0].file;
        setDesktopWallpaper(currentWp);

        if (shelf) {
            shelf.innerHTML = "";
            WALLPAPERS.forEach(wp => {
                const card = document.createElement("div");
                card.className = `wp-thumb-card ${wp.file === currentWp ? "active" : ""}`;
                card.innerHTML = `
                    <img src="wallpapers/${wp.file}" alt="${wp.title}" class="wp-thumb-img" loading="lazy">
                    <div class="wp-thumb-title">${wp.title}</div>
                `;
                card.addEventListener("click", () => {
                    document.querySelectorAll(".wp-thumb-card").forEach(c => c.classList.remove("active"));
                    card.classList.add("active");
                    setDesktopWallpaper(wp.file);
                    soundFX.click();
                });
                shelf.appendChild(card);
            });
        }

        // Restore theme
        const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) || "theme-cyan";
        selectColorTheme(savedTheme);
    }

    function setDesktopWallpaper(filename) {
        const wpEl = document.getElementById("desktopWallpaper");
        if (wpEl) {
            wpEl.style.backgroundImage = `url("wallpapers/${filename}")`;
            try {
                localStorage.setItem(WALLPAPER_STORAGE_KEY, filename);
            } catch (e) { }
        }
    }

    window.selectColorTheme = function (themeClass) {
        document.body.classList.remove("theme-cyan", "theme-matrix", "theme-magenta", "theme-crimson", "theme-amber");
        document.body.classList.add(themeClass);
        document.querySelectorAll(".theme-card").forEach(card => {
            card.classList.toggle("active", card.dataset.theme === themeClass);
        });
        try {
            localStorage.setItem(THEME_STORAGE_KEY, themeClass);
        } catch (e) { }
        soundFX.click();
    };

    window.toggleScanlines = function (active) {
        document.body.classList.toggle("scanlines-active", active);
        soundFX.click();
    };

    window.toggleAudio = function (active) {
        soundEnabled = active;
        const icon = document.getElementById("audioIcon");
        if (icon) {
            icon.innerHTML = soundEnabled ?
                '<svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>' :
                '<svg class="svg-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>';
        }
    };

    window.toggleBloom = function (active) {
        document.body.classList.toggle("bloom-active", active);
    };

    // -----------------------------------------------------------------
    // 15. DISCORD CLOUD VAULT (as-discord)
    // -----------------------------------------------------------------
    window.sendDiscordTest = function () {
        initAudio();
        const url = document.getElementById("discordWebhookInput").value.trim();
        const msg = document.getElementById("discordMsgInput").value.trim();
        const statusBox = document.getElementById("discordStatusMsg");

        if (!url) {
            statusBox.innerHTML = "<span style='color:var(--accent-red);'>Please enter a valid Discord Webhook URL.</span>";
            soundFX.error();
            return;
        }

        statusBox.innerHTML = "<span style='color:var(--accent-cyan);'>Transmitting payload to Discord Cloud...</span>";
        soundFX.chime();

        fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: "ASTERIX OS // Distro Node",
                avatar_url: "https://raw.githubusercontent.com/NEXO-TECHNOLOGIES/ASTERIX-OS/main/assets/icons/asterix_icon.png",
                content: `**[ASTERIX OS TELEMETRY DISPATCH]**\n${msg}\n*Node: 10.0.8.24 | Kernel: Linux 6.1-sec | Timestamp: ${new Date().toISOString()}*`
            })
        })
            .then(res => {
                if (res.ok) {
                    statusBox.innerHTML = "<span style='color:var(--accent-green);'>Payload transmitted to Discord channel!</span>";
                } else {
                    statusBox.innerHTML = `<span style='color:var(--accent-red);'>Discord API Error: HTTP ${res.status}</span>`;
                }
            })
            .catch(err => {
                statusBox.innerHTML = `<span style='color:var(--accent-red);'>Network error: ${err.message}</span>`;
            });
    };

    window.sendDiscordStatus = function () {
        const msgInput = document.getElementById("discordMsgInput");
        if (msgInput) {
            msgInput.value = "ASTERIX TELEMETRY REPORT: CPU 24% | RAM 3.4GB/16GB | 12 Subsystems Armed | 0 CVE Breaches";
            sendDiscordTest();
        }
    };

    // -----------------------------------------------------------------
    // 16. DESKTOP CONTEXT MENU & SHORTCUTS
    // -----------------------------------------------------------------
    let desktopContextSelection = null;

    function syncDesktopContextSelection(target) {
        const icon = target && target.closest(".desktop-icon-item");
        desktopContextSelection = icon ? icon.dataset.app : null;
        return desktopContextSelection;
    }

    window.openSelectedDesktopItem = function () {
        if (!desktopContextSelection) {
            openWindow("as-terminal");
            return;
        }
        openWindow(desktopContextSelection);
    };

    window.renameSelectedDesktopItem = function () {
        if (!desktopContextSelection) {
            alert("Select a desktop shortcut first.");
            return;
        }
        const icon = document.querySelector(`.desktop-icon-item[data-app="${desktopContextSelection}"]`);
        if (!icon) return;
        const current = icon.querySelector(".desktop-icon-label")?.textContent || desktopContextSelection;
        const next = prompt("Rename shortcut:", current);
        if (!next || !next.trim()) return;
        const label = icon.querySelector(".desktop-icon-label");
        if (label) label.textContent = next.trim();
        soundFX.click();
    };

    window.removeSelectedDesktopItem = function () {
        if (!desktopContextSelection) {
            alert("Select a desktop shortcut first.");
            return;
        }
        const icon = document.querySelector(`.desktop-icon-item[data-app="${desktopContextSelection}"]`);
        if (!icon) return;
        icon.remove();
        saveDesktopIconLayout();
        desktopContextSelection = null;
        soundFX.winClose();
    };

    function initDesktopContextMenu() {
        const menu = document.getElementById("desktopContextMenu");
        const workspace = document.getElementById("desktopWorkspace");
        if (!menu || !workspace) return;

        workspace.addEventListener("contextmenu", (e) => {
            if (e.target.closest(".cyber-window")) return;
            e.preventDefault();
            const icon = e.target.closest(".desktop-icon-item");
            if (icon) {
                syncDesktopContextSelection(icon);
            } else {
                desktopContextSelection = null;
            }
            initAudio();
            menu.style.top = `${e.clientY}px`;
            menu.style.left = `${e.clientX}px`;
            menu.classList.add("open");
            soundFX.click();
        });

        document.addEventListener("click", (e) => {
            if (!menu.contains(e.target)) {
                menu.classList.remove("open");
            }
        });
    }

    function initDesktopIconDrag() {
        const icons = document.querySelectorAll(".desktop-icon-item");
        icons.forEach((item) => {
            let dragging = false;
            let offsetX = 0;
            let offsetY = 0;

            item.addEventListener("pointerdown", (event) => {
                if (event.target.closest("button")) return;
                dragging = true;
                item.dataset.dragMoved = "false";
                const bounds = item.getBoundingClientRect();
                const workspace = document.getElementById("desktopWorkspace");
                const wsBounds = workspace.getBoundingClientRect();
                offsetX = event.clientX - bounds.left;
                offsetY = event.clientY - bounds.top;
                item.setPointerCapture?.(event.pointerId);
                item.style.zIndex = "100";
                item.style.transition = "none";
                item.style.left = `${bounds.left - wsBounds.left}px`;
                item.style.top = `${bounds.top - wsBounds.top}px`;
            });

            item.addEventListener("pointermove", (event) => {
                if (!dragging) return;
                const workspace = document.getElementById("desktopWorkspace");
                const wsBounds = workspace.getBoundingClientRect();
                const nextX = event.clientX - wsBounds.left - offsetX;
                const nextY = event.clientY - wsBounds.top - offsetY;
                item.style.left = `${Math.max(8, Math.min(nextX, wsBounds.width - 90))}px`;
                item.style.top = `${Math.max(30, Math.min(nextY, wsBounds.height - 90))}px`;
                item.dataset.dragMoved = "true";
            });

            item.addEventListener("pointerup", () => {
                dragging = false;
                item.style.zIndex = "2";
                item.style.transition = "all 0.15s";
                saveDesktopIconLayout();
            });

            item.addEventListener("pointerleave", () => {
                if (dragging) {
                    dragging = false;
                    item.style.zIndex = "2";
                    item.style.transition = "all 0.15s";
                    saveDesktopIconLayout();
                }
            });
        });
    }

    window.toggleDesktopFullscreen = function () {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(() => { });
        } else {
            document.exitFullscreen().catch(() => { });
        }
    };

    window.toggleAudioSynth = function () {
        toggleAudio(!soundEnabled);
    };

    window.showSystemInfoModal = function () {
        openWindow("as-settings");
    };

    function initKeyboardShortcuts() {
        document.addEventListener("keydown", (e) => {
            // Alt+Space = Toggle Start Menu
            if (e.altKey && e.code === "Space") {
                e.preventDefault();
                document.getElementById("startBtn").click();
            }
            // Ctrl+Alt+T = Open Terminal
            if (e.ctrlKey && e.altKey && (e.key === "t" || e.key === "T")) {
                e.preventDefault();
                openWindow("as-terminal");
            }
            // Escape = Close menus
            if (e.key === "Escape") {
                const launcher = document.getElementById("appLauncherMenu");
                if (launcher) launcher.classList.remove("open");
                const drawer = document.getElementById("notificationDrawer");
                if (drawer) drawer.classList.remove("open");
                const ctxMenu = document.getElementById("desktopContextMenu");
                if (ctxMenu) ctxMenu.classList.remove("open");
            }
        });
    }

    // -----------------------------------------------------------------
    // 17. BOOT SEQUENCE
    // -----------------------------------------------------------------
    function runBootSequence() {
        const bootScreen = document.getElementById("bootScreen");
        const progressBar = document.getElementById("bootBarProgress");
        const statusLine = document.getElementById("bootStatusLine");
        const skipBtn = document.getElementById("skipBootBtn");
        if (!bootScreen) return;

        const loginState = JSON.parse(localStorage.getItem(DESKTOP_LOGIN_KEY) || "{}") || {};
        const shouldSkip = !!loginState.loggedIn || new URLSearchParams(window.location.search).get("boot") === "skip";

        let pct = 0;
        const steps = [
            { pct: 20, status: "INITIALIZING KERNEL 6.1-SEC..." },
            { pct: 45, status: "VERIFYING SOVEREIGN THREAT TRIAGE ENGINES..." },
            { pct: 75, status: "MOUNTING /asterix_persistent ENCRYPTED VAULT..." },
            { pct: 90, status: "STARTING CYBERGLASS DESKTOP COMPOSITOR..." },
            { pct: 100, status: "DESKTOP ENVIRONMENT READY." }
        ];

        let stepIdx = 0;
        const interval = setInterval(() => {
            pct += 5;
            if (progressBar) progressBar.style.width = `${pct}%`;

            if (stepIdx < steps.length && pct >= steps[stepIdx].pct) {
                if (statusLine) statusLine.textContent = steps[stepIdx].status;
                stepIdx++;
            }

            if (pct >= 100) {
                clearInterval(interval);
                setTimeout(finishBoot, 300);
            }
        }, 60);

        function finishBoot() {
            clearInterval(interval);
            bootScreen.classList.add("boot-done");
            try {
                localStorage.setItem(DESKTOP_BOOT_KEY, JSON.stringify({ bootedAt: Date.now(), user: loginState.username || "operator" }));
            } catch (e) {}
            if (shouldSkip) {
                openWindow("as-terminal");
            }
            soundFX.chime();
        }

        if (skipBtn) {
            skipBtn.addEventListener("click", finishBoot);
        }
    }

    // -----------------------------------------------------------------
    // 17.5. SHOWCASE PORTAL & BREAKTHROUGH MEDIA CONTROLLERS
    // -----------------------------------------------------------------
    const THEATER_PLAYLIST = [
        {
            id: "master",
            badge: "CONSOLIDATED TRAILER (35s)",
            title: "ASTERIX OS Breakthrough Master Showcase",
            file: "media/videos/ASTERIX_OS_BREAKTHROUGH_MASTER_SHOWCASE_1080p.mp4",
            runtime: "0:35",
            desc: "A unified 35-second cinematic showcase trailer revealing all 5 breakthrough engines of ASTERIX OS: AI Attack Path Pathfinder, Decentralized Multiplayer Sync, Ghost Decoy Egress, Edge Mobile RF Sentinel, and Immutable Evidence Vault.",
            social: "Beyond Kali: The next evolution of tactical offensive and defensive operating environments is here. 5 core breakthrough engines running 100% native with zero dependencies! #ASTERIXOS #Infosec #CyberSecurity",
            cmd: "ax breakthrough --showcase"
        },
        {
            id: "pathfinder",
            badge: "ENGINE 01 // GRAPH AI",
            title: "Attack Path Pathfinder Engine",
            file: "media/videos/01_ATTACK_PATH_PATHFINDER_1080p.mp4",
            runtime: "0:07",
            desc: "Autonomous multi-hop lateral movement modeling using Dijkstra choke-point graph analytics. Maps reachable kill chains from external perimeter breach directly to Domain Admin.",
            social: "Why stop at port scanning when your OS can calculate the entire kill chain? [TARGET] Meet the Attack Path Pathfinder in ASTERIX OS. #CyberSecurity #RedTeam #EthicalHacking",
            cmd: "ax pathfinder --target 10.0.8.0/24"
        },
        {
            id: "team",
            badge: "ENGINE 02 // P2P MESH",
            title: "Multiplayer Live Operator Team Sync",
            file: "media/videos/02_MULTIPLAYER_TEAM_SYNC_1080p.mp4",
            runtime: "0:07",
            desc: "Decentralized peer-to-peer operator mesh for live target locking, scope de-confliction radar, and cross-operator beacon sharing without any centralized cloud dependency.",
            social: "Red teaming shouldn't be a solo game.  ASTERIX OS brings live P2P multiplayer engagement telemetry and real-time scope de-confliction. #PenetrationTesting #RedTeamOps",
            cmd: "ax team --status"
        },
        {
            id: "ghost",
            badge: "ENGINE 03 // OPSEC EVASION",
            title: "Ghost Protocol & Adaptive Decoys",
            file: "media/videos/03_GHOST_EGRESS_DECOY_1080p.mp4",
            runtime: "0:07",
            desc: "High-entropy SIEM evasion engine generating synthetic HTTP/DNS egress streams while multiplexing actual C2 beacons across stealth multi-hop routes.",
            social: "Defeat SIEM correlation by blending into legitimate cloud noise.  Ghost Protocol on ASTERIX OS routes stealth beacons under cover of synthetic decoy flows. #OpSec #ThreatHunting",
            cmd: "ax ghost --stealth"
        },
        {
            id: "radio",
            badge: "ENGINE 04 // RF DEFENSE",
            title: "Mobile RF Sensor Mesh & Jamming Sentinel",
            file: "media/videos/04_MOBILE_RF_SENSOR_SENTINEL_1080p.mp4",
            runtime: "0:07",
            desc: "Edge RF telemetry monitor for Android Termux & SDR nodes. Real-time RF spectral noise floor auditing, 802.11 deauth flood alerts, and rogue beacon tri-lateration.",
            social: "Turn edge mobile nodes into distributed RF telemetry sentinels. [SIGNAL] Real-time RF spectral noise floor auditing and 802.11 deauth flood alerts directly from Termux. #SDR #WirelessSecurity",
            cmd: "ax radio --jamming-audit"
        },
        {
            id: "vault",
            badge: "ENGINE 05 // FORENSICS",
            title: "Forensic Evidence Vault & Chain of Custody",
            file: "media/videos/05_TAMPER_PROOF_EVIDENCE_VAULT_1080p.mp4",
            runtime: "0:07",
            desc: "Cryptographic Merkle tree audit logging with SHA-256 block hashing and Ed25519 digital signatures. Generates court-admissible forensic execution proofs.",
            social: "Court-admissible red team reports with zero doubt.  ASTERIX OS logs every keystroke and telemetry packet into an immutable Merkle tree chain-of-custody vault. #DigitalForensics #DFIR",
            cmd: "ax vault --audit"
        }
    ];

    const ARCH_TIERS = {
        "tier1": {
            name: "Tier 1: System Root & Configuration",
            dir: "/ASTERIX OS (Root)",
            tree: "ASTERIX-OS/\n├── README.md               # Master Distro Documentation\n├── BUILD_MANIFEST.json     # Cryptographic Manifest (21 SHA-256 Signatures)\n├── VERSION.toml            # Version 4.9.0-SEC Metadata\n├── SECURITY.md             # Cryptographic & Disclosure Policy\n├── CHANGELOG.md            # Multi-Year Hardened Release Log\n├── ASTERIX_OS_DIAGRAM.png  # Full Visual Architecture Topology\n└── Dockerfile              # Containerized Hermetic Build Sandbox"
        },
        "tier2": {
            name: "Tier 2: Unified Command Dispatcher",
            dir: "/bin",
            tree: "bin/\n├── ax                      # Master 7,400+ line POSIX Bash Omni-Dispatcher\n├── ax.ps1                  # PowerShell Windows Cross-Platform Wrapper\n└── ax.cmd                  # Windows Command Prompt Stub"
        },
        "tier3": {
            name: "Tier 3: Autonomous Defense & Breakthrough Engines",
            dir: "/scripts-hub",
            tree: "scripts-hub/\n├── ax-pathfinder.py        # Autonomous Attack Graph & Dijkstra Lateral Movement\n├── ax-team.py              # Multiplayer Live P2P Operator Synchronization\n├── ax-ghost.py             # Ghost Protocol Synthetic Decoys & SIEM Evasion\n├── ax-radio.py             # Mobile RF Spectrum Sentinel & Jamming Auditor\n├── ax-evidence.py          # Cryptographic Merkle Tree Forensic Evidence Vault\n├── ax-video-engine.py      # Autonomous 1080p 60fps Video Production Studio\n├── ax-release-verify.py    # Ed25519 & SHA-256 Manifest Integrity Auditor\n├── ax-doctor.py            # Comprehensive System Diagnostics Probe\n├── ax-apt-repo.py          # Local Signed APT Repository Host Engine\n└── ax-cartographer.py      # Codebase Topology Graph Engine"
        },
        "tier4": {
            name: "Tier 4: Desktop Environment & Web Portal",
            dir: "/desktop-env & /web-dashboard",
            tree: "desktop-env/\n├── applications/           # .desktop entry specs for XFCE/MATE/Wayland\n└── autostart/              # Live session bootstrapping\nweb-dashboard/\n├── index.html              # Dual-Mode Showcase Portal & Web Desktop OS\n├── style.css               # 2,500+ line Cyberpunk Desktop Theme & Video HUD\n├── app.js                  # In-Browser Virtual POSIX OS & Synthesizer Engine\n├── media/                  # 1080p Breakthrough MP4s & System Diagrams\n└── wallpapers/             # 26 High-Resolution Distro Wallpapers"
        },
        "tier5": {
            name: "Tier 5: Sovereign Native Binaries",
            dir: "/core-utils-* (Rust / C / C++ / Go)",
            tree: "core-utils-rust/             # High-Performance Memory-Safe Daemons\n├── asterix-net-sentinel/   # Thread-pooled live network packet inspector\n├── asterix-crypto-core/    # Parallelized hash cracking & cryptographic suite\n├── asterix-bin-inspector/  # ELF security auditor (NX, ASLR, Canaries, PIE)\n├── asterix-defender-core/  # Real-time threat defense & mitigation daemon\n└── asterix-sys-mon/        # Microsecond system resource telemetry\ncore-utils-c/               # Ultra-hardened C99 system utilities\ncore-utils-go/              # Asynchronous concurrent web reconnaissance\nboot-asm/                   # x86_64 512-byte MBR & UEFI Stage-1 Bootloaders"
        },
        "tier6": {
            name: "Tier 6: AI Brain & Training Curriculum",
            dir: "/asterix-ai & /python-lab",
            tree: "asterix-ai/\n├── ai_brain.py             # Autonomous Decision Engine & LLM Pipeline\n├── tool_generator.py       # Dynamic Just-In-Time Exploit & Defense Generator\n└── rules/                  # Sovereign Security Heuristic Rule Matrices\npython-lab/\n├── curriculum.py           # 12-Tier Red/Blue Operator Training System\n├── test_breakthrough_features.py # Full Pytest Verification Suite\n└── progress.json           # Operator Certification & Skill Ledger"
        },
        "tier7": {
            name: "Tier 7: Edge Telemetry & Android Termux",
            dir: "/termux-mobile",
            tree: "termux-mobile/\n├── asterix-mobile.sh       # Native Rootless Android Cyber Warfare Launcher\n├── target-tracker.sh       # Edge GPS / Wi-Fi / BLE Telemetry Sentinel\n├── asterix-termux-init.sh  # Automated Proot-Debian Mobile Bootstrap\n└── install-termux.sh       # One-Line Termux Deployment Installer"
        },
        "tier8": {
            name: "Tier 8: Hardened Artifacts & Releases",
            dir: "/assets, /packages, /iso",
            tree: "assets/\n├── animations/             # 1080p 60fps MP4 Breakthrough Video Suite\n├── iso-branding/           # GRUB Splash Screens (Cyan, Matrix, Space, Samurai)\n└── wallpapers/             # Distro Wallpapers (1920x1080 & 4K UHD)\npackages/                   # Local .deb distribution bundles\nengine/                     # Debian Live-Build ISO Generation Toolchain"
        }
    };

    function initDualMode() {
        const hash = window.location.hash;
        if (hash === "#desktop") {
            setMode("desktop");
        } else {
            setMode("portal");
        }

        // Launch desktop triggers
        document.querySelectorAll(".btn-launch-desktop, #launchDesktopBtn, .launch-desktop-trigger").forEach(btn => {
            btn.addEventListener("click", (e) => {
                e.preventDefault();
                setMode("desktop");
                window.location.hash = "desktop";
                soundFX.chime();
            });
        });

        // Return to portal trigger
        const returnBtn = document.getElementById("returnPortalBtn");
        if (returnBtn) {
            returnBtn.addEventListener("click", () => {
                setMode("portal");
                window.location.hash = "portal";
                soundFX.click();
            });
        }
    }

    function setMode(mode) {
        if (mode === "desktop") {
            document.body.classList.remove("portal-mode");
            document.body.classList.add("desktop-mode");
            const portal = document.getElementById("portalContainer");
            if (portal) portal.style.display = "none";
            const topBar = document.getElementById("topBar");
            if (topBar) topBar.style.display = "flex";
            const ws = document.getElementById("desktopWorkspace");
            if (ws) ws.style.display = "block";
            const wp = document.getElementById("desktopWallpaper");
            if (wp) wp.style.display = "block";
            const boot = document.getElementById("bootScreen");
            if (boot && !boot.dataset.ran) {
                runBootSequence();
                boot.dataset.ran = "true";
            }
        } else {
            document.body.classList.remove("desktop-mode");
            document.body.classList.add("portal-mode");
            const portal = document.getElementById("portalContainer");
            if (portal) portal.style.display = "block";
            const topBar = document.getElementById("topBar");
            if (topBar) topBar.style.display = "none";
            const ws = document.getElementById("desktopWorkspace");
            if (ws) ws.style.display = "none";
            const wp = document.getElementById("desktopWallpaper");
            if (wp) wp.style.display = "none";
            const boot = document.getElementById("bootScreen");
            if (boot) boot.style.display = "none";
        }
    }

    function initVideoTheater() {
        const playlistContainer = document.getElementById("theaterPlaylist");
        const videoEl = document.getElementById("theaterVideo");
        const badgeEl = document.getElementById("theaterBadge");
        const titleEl = document.getElementById("theaterTitle");
        const descEl = document.getElementById("theaterDesc");
        const socialEl = document.getElementById("theaterSocialText");
        const cmdEl = document.getElementById("theaterCmdText");
        const copyBtn = document.getElementById("copySocialBtn");

        if (!playlistContainer || !videoEl) return;

        playlistContainer.innerHTML = "";
        THEATER_PLAYLIST.forEach((item, idx) => {
            const btn = document.createElement("div");
            btn.className = `theater-play-item ${idx === 0 ? "active" : ""}`;
            btn.innerHTML = `
                <span class="play-item-badge">${item.badge}</span>
                <span class="play-item-title">${item.title}</span>
                <span class="play-item-meta">1080p 60fps &bull; ${item.runtime}</span>
            `;
            btn.addEventListener("click", () => {
                selectTheaterVideo(item, btn);
                soundFX.click();
            });
            playlistContainer.appendChild(btn);
        });

        function selectTheaterVideo(item, btnEl) {
            document.querySelectorAll(".theater-play-item").forEach(el => el.classList.remove("active"));
            if (btnEl) btnEl.classList.add("active");

            videoEl.src = item.file;
            videoEl.play().catch(() => {});

            if (badgeEl) badgeEl.textContent = item.badge;
            if (titleEl) titleEl.textContent = item.title;
            if (descEl) descEl.textContent = item.desc;
            if (socialEl) socialEl.textContent = item.social;
            if (cmdEl) cmdEl.textContent = item.cmd;
        }

        if (copyBtn && socialEl) {
            copyBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(socialEl.textContent).then(() => {
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = "COPIED!";
                    setTimeout(() => { copyBtn.textContent = originalText; }, 2000);
                });
            });
        }

        // Set initial video
        if (playlistContainer.firstChild) {
            selectTheaterVideo(THEATER_PLAYLIST[0], playlistContainer.firstChild);
        }
    }

    function initPortalTerminal() {
        const input = document.getElementById("portalTermInput");
        const chips = document.querySelectorAll(".term-chip-btn");

        if (input) {
            input.addEventListener("keydown", (e) => {
                if (e.key === "Enter") {
                    const cmd = input.value.trim();
                    if (cmd) {
                        printTerminalPromptLine(cmd);
                        executeTerminalCommand(cmd);
                        input.value = "";
                        soundFX.enter();
                    }
                } else if (e.key !== "Shift" && e.key !== "Control" && e.key !== "Alt") {
                    soundFX.type();
                }
            });
        }

        chips.forEach(chip => {
            chip.addEventListener("click", () => {
                const cmd = chip.getAttribute("data-cmd");
                if (cmd) {
                    printTerminalPromptLine(cmd);
                    executeTerminalCommand(cmd);
                    soundFX.enter();
                }
            });
        });

        // Breakthrough card "Run Demo" buttons
        document.querySelectorAll(".btn-run-term").forEach(btn => {
            btn.addEventListener("click", () => {
                const cmd = btn.getAttribute("data-cmd");
                if (cmd) {
                    const termSec = document.getElementById("terminal");
                    if (termSec) termSec.scrollIntoView({ behavior: "smooth" });
                    setTimeout(() => {
                        printTerminalPromptLine(cmd);
                        executeTerminalCommand(cmd);
                        soundFX.enter();
                    }, 400);
                }
            });
        });
    }

    function initArchitectureExplorer() {
        const tabs = document.querySelectorAll(".arch-tier-tab");
        const titleEl = document.getElementById("archTierName");
        const dirEl = document.getElementById("archTierDir");
        const treeEl = document.getElementById("archTierTree");
        const diagramPreview = document.getElementById("diagramPreview");
        const lightbox = document.getElementById("portalLightbox");
        const lightboxImg = document.getElementById("lightboxImg");
        const lightboxClose = document.getElementById("lightboxClose");

        tabs.forEach(tab => {
            tab.addEventListener("click", () => {
                tabs.forEach(t => t.classList.remove("active"));
                tab.classList.add("active");
                const tierId = tab.getAttribute("data-tier");
                const tier = ARCH_TIERS[tierId];
                if (tier) {
                    if (titleEl) titleEl.textContent = tier.name;
                    if (dirEl) dirEl.textContent = tier.dir;
                    if (treeEl) treeEl.textContent = tier.tree;
                }
                soundFX.click();
            });
        });

        if (diagramPreview && lightbox && lightboxImg) {
            diagramPreview.addEventListener("click", () => {
                lightboxImg.src = "media/diagrams/ASTERIX_OS_DIAGRAM.png";
                lightbox.classList.add("open");
                soundFX.winOpen();
            });
        }
        if (lightboxClose && lightbox) {
            lightboxClose.addEventListener("click", () => {
                lightbox.classList.remove("open");
                soundFX.winClose();
            });
        }
        if (lightbox) {
            lightbox.addEventListener("click", (e) => {
                if (e.target === lightbox) {
                    lightbox.classList.remove("open");
                    soundFX.winClose();
                }
            });
        }
    }

    function initPortalGallery() {
        const grid = document.getElementById("portalGalleryGrid");
        const filterBtns = document.querySelectorAll(".gallery-filter-btn");
        if (!grid) return;

        function renderGallery(filter = "all") {
            grid.innerHTML = "";
            let list = WALLPAPERS;
            if (filter === "boot") {
                list = WALLPAPERS.filter(w => w.file.includes("boot_"));
            } else if (filter === "neon") {
                list = WALLPAPERS.filter(w => w.title.toLowerCase().includes("cyber") || w.title.toLowerCase().includes("neon") || w.title.toLowerCase().includes("hacker"));
            } else if (filter === "cosmic") {
                list = WALLPAPERS.filter(w => w.title.toLowerCase().includes("cosmic") || w.title.toLowerCase().includes("space") || w.title.toLowerCase().includes("galaxy") || w.title.toLowerCase().includes("planet"));
            } else if (filter === "samurai") {
                list = WALLPAPERS.filter(w => w.title.toLowerCase().includes("samurai") || w.title.toLowerCase().includes("dragon") || w.title.toLowerCase().includes("phoenix"));
            }

            list.forEach(w => {
                const card = document.createElement("div");
                card.className = "wallpaper-portal-card";
                card.innerHTML = `
                    <img class="wallpaper-portal-thumb" src="wallpapers/${w.file}" alt="${w.title}" loading="lazy" />
                    <div class="wallpaper-portal-footer">
                        <span class="wallpaper-portal-title">${w.title}</span>
                        <a class="wallpaper-download-btn" href="wallpapers/${w.file}" download="${w.file}">Download</a>
                    </div>
                `;
                card.querySelector("img").addEventListener("click", () => {
                    const lightbox = document.getElementById("portalLightbox");
                    const lightboxImg = document.getElementById("lightboxImg");
                    if (lightbox && lightboxImg) {
                        lightboxImg.src = `wallpapers/${w.file}`;
                        lightbox.classList.add("open");
                        soundFX.winOpen();
                    }
                });
                grid.appendChild(card);
            });
        }

        filterBtns.forEach(btn => {
            btn.addEventListener("click", () => {
                filterBtns.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                renderGallery(btn.getAttribute("data-filter"));
                soundFX.click();
            });
        });

        renderGallery("all");
    }

    // -----------------------------------------------------------------
    // 18. MASTER INITIALIZATION
    // -----------------------------------------------------------------
    document.addEventListener("DOMContentLoaded", () => {
        loadVirtualFS();
        const loginState = JSON.parse(localStorage.getItem(DESKTOP_LOGIN_KEY) || "{}") || {};
        if (loginState.loggedIn) {
            const loginBanner = document.getElementById("bootStatusLine");
            if (loginBanner) loginBanner.textContent = `WELCOME BACK ${String(loginState.username || "OPERATOR").toUpperCase()}...`;
        }
        initWindowManager();
        initAppLauncher();
        initNotificationDrawer();
        initClock();
        initTerminal();
        initSecuritySuite();
        initCodeStudio();
        initVoice();
        initSoftwareCenter();
        initSettings();
        initDesktopContextMenu();
        initDesktopIconDrag();
        initFileExplorerContextMenu();
        initKeyboardShortcuts();

        // Initialize portal showcase modules
        initDualMode();
        initVideoTheater();
        initPortalTerminal();
        initArchitectureExplorer();
        initPortalGallery();

        // Audio toggle tray button
        const audioBtn = document.getElementById("audioToggleBtn");
        if (audioBtn) {
            audioBtn.addEventListener("click", () => {
                toggleAudio(!soundEnabled);
                soundFX.click();
            });
        }

        // Power button
        const powerBtn = document.getElementById("powerBtn");
        if (powerBtn) {
            powerBtn.addEventListener("click", () => {
                if (confirm("Reboot ASTERIX OS Web Desktop Node?")) {
                    executeTerminalCommand("reboot");
                }
            });
        }
    });

})();
