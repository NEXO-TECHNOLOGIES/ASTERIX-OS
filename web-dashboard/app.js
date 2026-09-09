// =====================================================================
// ASTERIX OS - Master Web Portal Logic
// =====================================================================

const WALLPAPERS = [
    { title: "ASTERIX Electric Cyan (GRUB 01)", file: "asterix_boot_01_electric_cyan_1788292127536.jpg", tag: "boot", desc: "Default minimalist geometric cyber boot splash" },
    { title: "Cyberpunk Night Street (GRUB 02)", file: "asterix_boot_02_cyberpunk_city_1788292249067.jpg", tag: "neon", desc: "Rainy neon city with hooded operative" },
    { title: "Matrix Rain Terminal (GRUB 03)", file: "asterix_boot_03_matrix_terminal_1788292325091.jpg", tag: "boot", desc: "Matrix binary data stream terminal splash" },
    { title: "Deep Space Cosmic (GRUB 04)", file: "asterix_boot_04_deep_space_1788292387240.jpg", tag: "cosmic", desc: "Cosmic nebula with glowing A emblem" },
    { title: "Red Samurai Dojo (GRUB 05)", file: "asterix_boot_05_red_samurai_1788292444477.jpg", tag: "neon", desc: "Dramatic samurai aesthetic with burning embers" },
    { title: "Cosmic Neon Monolith", file: "ASTERIX_LINIX_01_Cosmic_Neon.png", tag: "cosmic", desc: "High-resolution cosmic desktop wallpaper" },
    { title: "Green Hacker Command", file: "ASTERIX_LINIX_01_Green_Hacker_1920x1080.png", tag: "neon", desc: "Terminal matrix workstation wallpaper" },
    { title: "Ice Cosmic Nebula", file: "ASTERIX_LINIX_01_Ice_Cosmic_1920x1080.png", tag: "cosmic", desc: "Deep glacial nebula landscape" },
    { title: "Cyberpunk Night Horizon", file: "ASTERIX_LINIX_02_Cyberpunk_Night.png", tag: "neon", desc: "Megacity neon skyline" },
    { title: "Purple Galaxy Portal", file: "ASTERIX_LINIX_02_Purple_Galaxy_1920x1080.png", tag: "cosmic", desc: "Interstellar portal gateway" },
    { title: "Neon City Grid", file: "ASTERIX_LINIX_03_Neon_City_1920x1080.png", tag: "neon", desc: "Cyber grid city streets" },
    { title: "Phoenix Core Cyber", file: "ASTERIX_LINIX_04_Phoenix_Core_1920x1080.png", tag: "neon", desc: "High energy core cyber aesthetic" }
];

const SUBSYSTEMS = [
    { num: "01", icon: "🔍", name: "Reconnaissance & OSINT", tools: "Nmap, Masscan, DnsRecon, Whois, Netdiscover, Sherlock", alias: "as-recon" },
    { num: "02", icon: "🕷️", name: "Web Application Warfare", tools: "SQLMap, Gobuster, Nikto, FFUF, WPScan, Wafw00f", alias: "as-web" },
    { num: "03", icon: "💣", name: "Exploitation & Payloads", tools: "Metasploit Framework, SearchSploit, Socat, Netcat", alias: "as-exploit" },
    { num: "04", icon: "🔑", name: "Password & Hash Auditing", tools: "Hashcat, John The Ripper, Hydra, Crunch, HashID", alias: "as-crack" },
    { num: "05", icon: "🦈", name: "Sniffing & Traffic Control", tools: "Wireshark, TShark, Tcpdump, MacChanger, Hping3", alias: "as-sniff" },
    { num: "06", icon: "📡", name: "Wireless & Radio Attacks", tools: "Aircrack-ng, Wifite, Reaver, Kismet, PixieWPS", alias: "as-wifi" },
    { num: "07", icon: "🔬", name: "Forensics & Steganography", tools: "Binwalk, Foremost, Scalpel, Steghide, Exiftool", alias: "as-forensic" },
    { num: "08", icon: "⚙️", name: "Reverse Engineering (R2)", tools: "Radare2, GDB, Hexedit, XXD, Strings, Valgrind", alias: "as-rev" },
    { num: "09", icon: "🛠️", name: "Full-Stack Dev Studio", tools: "Rust (Cargo), Go, C/C++, Python3, Node.js, LazyGit", alias: "as-dev" },
    { num: "10", icon: "💾", name: "ASTERIX Persistent Vault", tools: "Encrypted USB Storage Overlay, Android SDCard Sync", alias: "vault" },
    { num: "11", icon: "🪟", name: "Quad-Grid Tmux Studio", tools: "4-Way Split Workspace, 100k History, Mouse Scroll", alias: "as-quad" },
    { num: "12", icon: "⚡", name: "Subsystem Telemetry HUD", tools: "Btop, Htop, Sensor Gauges, Network Monitor", alias: "as-hub" }
];

const HOME_TABS = {
    overview: [
        { title: "System Mode", value: "Dual-Boot Ready", sub: "ASTERIX + Kali / Linux Boot Targets", liveKey: "systemMode" },
        { title: "AI Runtime", value: "Ollama Local", sub: "qwen2.5:3b-instruct", liveKey: "aiRuntime" },
        { title: "Security Tier", value: "Maximum", sub: "Autonomous threat triage enabled", liveKey: "securityTier" },
        { title: "Boot Disk", value: "Persist + Secure Vault", sub: "Fast live persistence", liveKey: "bootDisk" },
        { title: "Last Action", value: "AI Safe Suggestion", sub: "No dangerous command was executed", liveKey: "lastAction" },
        { title: "OS Status", value: "Stable", sub: "Kernel and telemetry online", liveKey: "osStatus" }
    ],
    dualboot: [
        { title: "Primary Boot", value: "ASTERIX OS", sub: "Main engineering and AI mode" },
        { title: "Secondary Boot", value: "Kali Linux", sub: "Security tools and pentest lab" },
        { title: "Boot Tooling", value: "GRUB / Ventoy", sub: "Persistent multi-boot menu" },
        { title: "Mode Switch", value: "Safe Toggle", sub: "Reboot to desired OS profile" },
        { title: "Boot Policy", value: "Secure by Default", sub: "User confirmation on risky actions" },
        { title: "Recovery", value: "Live USB / Rescue", sub: "Recovery and repair mode" }
    ],
    tools: [
        { title: "Recon", value: "Nmap / Masscan", sub: "Network mapping and host discovery" },
        { title: "Web", value: "SQLMap / Nikto", sub: "Web app exploitation test suite" },
        { title: "Wireless", value: "Aircrack / WiFite", sub: "Wireless field tooling" },
        { title: "Forensics", value: "Binwalk / Foremost", sub: "Artifact analysis and carving" },
        { title: "Reverse", value: "Radare2 / GDB", sub: "Binary analysis and debugging" },
        { title: "Ops", value: "Proxychains / Tmux", sub: "Remote and split-workflow operations" }
    ],
    ai: [
        { title: "Local Model", value: "qwen2.5:3b-instruct", sub: "Offline and private AI core", liveKey: "localModel" },
        { title: "Risk Scan", value: "Security Posture", sub: "CPU, RAM, battery, and network checks", liveKey: "riskScan" },
        { title: "Command Guard", value: "Danger Filter", sub: "Blocks destructive commands", liveKey: "commandGuard" },
        { title: "Code Repair", value: "ASTRIX Healer", sub: "Autonomous fix suggestions", liveKey: "codeRepair" },
        { title: "Memory", value: "Event Log", sub: "Persistent event memory capture", liveKey: "memoryState" },
        { title: "Learning", value: "Self Update", sub: "Nightly rules generation", liveKey: "learningState" }
    ],
    recovery: [
        { title: "Self Heal", value: "Auto Repair", sub: "Recover broken scripts and config" },
        { title: "Boot Rescue", value: "GRUB Recovery", sub: "Live boot fallback" },
        { title: "Disk Safety", value: "Write Guard", sub: "No destructive system override" },
        { title: "Rollback", value: "Backup Restore", sub: "Use last clean copy" },
        { title: "Logs", value: "Telemetry Vault", sub: "Audit trail and memory review" },
        { title: "Mode", value: "Safe / Read Only", sub: "Minimal risk operational mode" }
    ]
};

document.addEventListener("DOMContentLoaded", () => {
    renderHomeTabs();
    renderWallpapers("all");
    renderSubsystems();
    setupFilters();
    setupSearch();
    setupTabButtons();
    setupDualBootLoader();
    refreshLiveProfile();
    updateMoodDashboard();
    setInterval(refreshLiveProfile, 5000);
    setInterval(updateMoodDashboard, 3000);
});

function moodThemeForState(mood) {
    const normalized = String(mood || "balanced").toLowerCase();
    const themes = {
        balanced: { accent: "#00f0ff", glow: "rgba(0, 240, 255, 0.5)", bodyClass: "mood-balanced" },
        frustrated: { accent: "#ff4d6d", glow: "rgba(255, 77, 109, 0.55)", bodyClass: "mood-frustrated" },
        stressed: { accent: "#ffb703", glow: "rgba(255, 183, 3, 0.55)", bodyClass: "mood-stressed" },
        urgent: { accent: "#facc15", glow: "rgba(250, 204, 21, 0.55)", bodyClass: "mood-urgent" },
        curious: { accent: "#8b5cf6", glow: "rgba(139, 92, 246, 0.55)", bodyClass: "mood-curious" },
        excited: { accent: "#00ff88", glow: "rgba(0, 255, 136, 0.55)", bodyClass: "mood-excited" },
        "empathetic-direct": { accent: "#ff4d6d", glow: "rgba(255, 77, 109, 0.55)", bodyClass: "mood-frustrated" },
        "urgent-priority": { accent: "#facc15", glow: "rgba(250, 204, 21, 0.55)", bodyClass: "mood-urgent" },
        "teach-and-explain": { accent: "#8b5cf6", glow: "rgba(139, 92, 246, 0.55)", bodyClass: "mood-curious" },
        motivating: { accent: "#00ff88", glow: "rgba(0, 255, 136, 0.55)", bodyClass: "mood-excited" },
    };
    return themes[normalized] || themes.balanced;
}

function getSelectedBootTarget() {
    const selected = document.querySelector(".os-entry.selected .os-name");
    return selected ? selected.textContent.trim() : "ASTERIX OS";
}

function applyMoodTheme(snapshot) {
    const mood = (snapshot && (snapshot.mood || snapshot.response_style)) || "balanced";
    const theme = moodThemeForState(mood);
    const moodIntensity = {
        balanced: 16,
        frustrated: 28,
        stressed: 30,
        urgent: 32,
        curious: 22,
        excited: 26,
        "empathetic-direct": 30,
        "urgent-priority": 34,
        "teach-and-explain": 24,
        motivating: 28,
    };
    const moodBoost = moodIntensity[mood] || moodIntensity.balanced;
    const bootTarget = getSelectedBootTarget();
    const bootBoost = {
        "ASTERIX OS": 0,
        "Kali Linux": 4,
        "Windows 11": 2,
        "Live Rescue": 6,
    }[bootTarget] || 0;

    document.body.classList.remove(
        "mood-balanced", "mood-frustrated", "mood-stressed", "mood-urgent", "mood-curious", "mood-excited"
    );
    document.body.classList.add(theme.bodyClass);
    document.documentElement.style.setProperty("--theme-accent", theme.accent);
    document.documentElement.style.setProperty("--theme-glow", theme.glow);
    document.documentElement.style.setProperty("--pulse-size", `${moodBoost + bootBoost + 14}px`);
    document.documentElement.style.setProperty("--pulse-speed", `${Math.max(1.2, 3.4 - (moodBoost / 18))}s`);
}

function updateEmotionMeter(snapshot) {
    const moodSummary = snapshot.mood_summary || {};
    const stress = Number(moodSummary.stress || 0);
    const frustration = Number(moodSummary.frustration || 0);
    const urgency = Number(moodSummary.urgency || 0);
    const curiosity = Number(moodSummary.curiosity || 0);
    const calm = Number(moodSummary.calm || 1);
    const intensity = Math.min(100, Math.round(((stress * 20) + (frustration * 18) + (urgency * 24) + (curiosity * 16) + (Math.max(0, 5 - calm) * 10))));
    const meter = document.getElementById("emotionMeterFill");
    const text = document.getElementById("emotionMeterText");
    if (meter) meter.style.width = `${intensity}%`;
    if (text) text.textContent = snapshot.mood || snapshot.response_style || "balanced";
    const accent = moodThemeForState(snapshot.mood || snapshot.response_style || "balanced").accent;
    if (meter) meter.style.background = `linear-gradient(90deg, ${accent}, rgba(255,255,255,0.8))`;
}

function applyLiveProfileToHomeCards(snapshot) {
    const mood = snapshot.mood || "balanced";
    const style = snapshot.response_style || "balanced";
    const trainingCompleted = snapshot.training_completed || 0;
    const learningQuota = snapshot.learning_quota || 100;
    const trainingPercent = Math.min(100, Math.round((trainingCompleted / learningQuota) * 100));

    applyMoodTheme(snapshot);

    const overviewCards = document.querySelectorAll("#overviewGrid .home-card");
    const aiCards = document.querySelectorAll("#aiGrid .home-card");

    if (overviewCards.length >= 6) {
        overviewCards[1].querySelector(".home-card-value").textContent = mood.toUpperCase();
        overviewCards[1].querySelector(".home-card-sub").textContent = `${style} response mode`; 
        overviewCards[4].querySelector(".home-card-value").textContent = style.toUpperCase();
        overviewCards[4].querySelector(".home-card-sub").textContent = `${trainingCompleted}/${learningQuota} training cycles`;
        overviewCards[5].querySelector(".home-card-value").textContent = trainStateLabel(mood, style);
        overviewCards[5].querySelector(".home-card-sub").textContent = `${trainingPercent}% learning complete`;
    }

    if (aiCards.length >= 6) {
        aiCards[0].querySelector(".home-card-value").textContent = "qwen2.5:3b-instruct";
        aiCards[0].querySelector(".home-card-sub").textContent = `Mood: ${mood}`;
        aiCards[1].querySelector(".home-card-value").textContent = `${trainingPercent}%`;
        aiCards[1].querySelector(".home-card-sub").textContent = `${trainingCompleted} / ${learningQuota} cycles`;
        aiCards[2].querySelector(".home-card-value").textContent = style.toUpperCase();
        aiCards[2].querySelector(".home-card-sub").textContent = `Blocks risky actions`;
        aiCards[3].querySelector(".home-card-value").textContent = "ACTIVE";
        aiCards[3].querySelector(".home-card-sub").textContent = `Fix loop tuned for ${mood}`;
        aiCards[4].querySelector(".home-card-value").textContent = "LIVE";
        aiCards[4].querySelector(".home-card-sub").textContent = `Last mood: ${mood}`;
        aiCards[5].querySelector(".home-card-value").textContent = "RUNNING";
        aiCards[5].querySelector(".home-card-sub").textContent = `${trainingPercent}% complete`;
    }

    const bootTrainingNote = document.getElementById("bootTrainingNote");
    if (bootTrainingNote) {
        const bootLabel = document.querySelector(".os-entry.selected .os-name")?.textContent || "ASTERIX OS";
        bootTrainingNote.textContent = `AI training: ${mood} mood • ${style} mode • preferred boot: ${bootLabel}`;
    }
}

function trainStateLabel(mood, style) {
    if (mood === "stressed" || mood === "frustrated") return "Urgent";
    if (style === "teach-and-explain") return "Explaining";
    if (style === "motivating") return "Boosted";
    return "Stable";
}

function updateMoodDashboard() {
    const responseText = {
        balanced: "I will keep this steady and efficient while we work through it.",
        frustrated: "I hear the pressure. I will fix this fast and keep the steps simple.",
        stressed: "I hear the pressure. I will fix this fast and keep the steps simple.",
        urgent: "I will prioritize this now and keep the fix focused on the fastest path.",
        curious: "Let me explain what is happening and show the exact next step in plain language.",
        excited: "Awesome. Let’s move fast and keep this momentum high.",
        "empathetic-direct": "I hear the pressure. I will fix this fast and keep the steps simple.",
        "urgent-priority": "I will prioritize this now and keep the fix focused on the fastest path.",
        "teach-and-explain": "Let me explain what is happening and show the exact next step in plain language.",
        motivating: "Awesome. Let’s move fast and keep this momentum high.",
    };

    const moodFallback = {
        mood: "balanced",
        response_style: "balanced",
        training_completed: 0,
        learning_quota: 100,
        confidence: 0.75,
        mood_summary: {
            frustration: 0,
            stress: 0,
            urgency: 0,
            curiosity: 0,
            excitement: 0,
            calm: 1,
        }
    };

    const snapshot = window.__ASTERIX_LIVE_PROFILE__ || moodFallback;
    const moodName = snapshot.mood || "balanced";
    const currentMood = snapshot.response_style || moodName || "balanced";
    const moodStatus = document.getElementById("aiMoodStatus");
    const moodScore = document.getElementById("aiMoodScore");
    const responseMessage = document.getElementById("aiResponseMessage");
    const moodSummary = snapshot.mood_summary || {};
    applyLiveProfileToHomeCards(snapshot);
    updateEmotionMeter(snapshot);

    const frustration = Number(moodSummary.frustration || 0);
    const stress = Number(moodSummary.stress || 0);
    const urgency = Number(moodSummary.urgency || 0);
    const curiosity = Number(moodSummary.curiosity || 0);

    if (moodStatus) moodStatus.textContent = currentMood;
    if (moodScore) moodScore.textContent = `confidence ${(snapshot.confidence || 0.75).toFixed(2)}`;
    if (responseMessage) responseMessage.textContent = responseText[currentMood] || responseText[moodName] || responseText.balanced;

    const moodValues = {
        frustration: document.getElementById("moodFrustration"),
        stress: document.getElementById("moodStress"),
        urgency: document.getElementById("moodUrgency"),
        curiosity: document.getElementById("moodCuriosity"),
    };

    const bars = {
        frustration: document.getElementById("barFrustration"),
        stress: document.getElementById("barStress"),
        urgency: document.getElementById("barUrgency"),
        curiosity: document.getElementById("barCuriosity"),
    };

    Object.entries({ frustration, stress, urgency, curiosity }).forEach(([key, value]) => {
        if (moodValues[key]) moodValues[key].textContent = String(value);
        if (bars[key]) bars[key].style.width = `${Math.min(100, value * 20)}%`;
    });
}

async function refreshLiveProfile() {
    try {
        const response = await fetch("../asterix-ai/profile_status.json");
        if (!response.ok) return;
        const data = await response.json();
        window.__ASTERIX_LIVE_PROFILE__ = data;
        updateMoodDashboard();
    } catch (error) {
        window.__ASTERIX_LIVE_PROFILE__ = window.__ASTERIX_LIVE_PROFILE__ || {
            mood: "balanced",
            response_style: "balanced",
            confidence: 0.75,
            mood_summary: { frustration: 0, stress: 0, urgency: 0, curiosity: 0 },
        };
        updateMoodDashboard();
    }
}

function setupDualBootLoader() {
    const entries = document.querySelectorAll(".os-entry");
    const progressBar = document.getElementById("bootProgressBar");
    const bootModeText = document.getElementById("bootModeText");
    const bootStatusText = document.getElementById("bootStatusText");
    const logLines = document.getElementById("bootLogLines");
    const countdownValue = document.getElementById("countdownValue");

    if (!entries.length || !progressBar || !bootModeText || !bootStatusText) return;

    const bootMessages = {
        "ASTERIX OS": [
            "Initializing ASTERIX kernel",
            "Loading secure AI runtime",
            "Mounting persistent vault",
            "Launching command matrix"
        ],
        "Kali Linux": [
            "Loading Kali kernel",
            "Activating toolchain modules",
            "Mounting penetration workspace",
            "Starting security environment"
        ],
        "Windows 11": [
            "Booting Windows boot manager",
            "Loading Win32 subsystem",
            "Starting user session",
            "Preparing desktop"
        ],
        "Live Rescue": [
            "Booting rescue shell",
            "Scanning recovery partitions",
            "Preparing minimal repair environment",
            "Launching diagnostics"
        ]
    };

    const runBootSequence = (label) => {
        let progress = 0;
        const messages = bootMessages[label] || bootMessages["ASTERIX OS"];
        if (logLines) {
            logLines.innerHTML = messages.map(msg => `<div>[boot] ${msg}</div>`).join("");
        }
        bootStatusText.textContent = "LOADING BOOT SEQUENCE";
        bootModeText.textContent = `Loading ${label}...`;
        progressBar.style.width = "0%";

        const timer = setInterval(() => {
            progress += 10;
            progressBar.style.width = `${progress}%`;
            if (countdownValue) countdownValue.textContent = `${Math.max(0, 7 - Math.floor(progress / 14))}s`;

            if (logLines && messages[progress / 10 - 1]) {
                const item = document.createElement("div");
                item.textContent = `[boot] ${messages[Math.max(0, Math.floor((progress - 10) / 25))]}`;
                logLines.appendChild(item);
            }

            if (progress >= 100) {
                clearInterval(timer);
                bootStatusText.textContent = "BOOT COMPLETE";
                bootModeText.textContent = `${label} ready`;
                if (countdownValue) countdownValue.textContent = "0s";
            }
        }, 150);
    };

    const bootThemeByLabel = {
        "ASTERIX OS": { color: "#00f0ff", glow: "rgba(0, 240, 255, 0.7)" },
        "Kali Linux": { color: "#00ff88", glow: "rgba(0, 255, 136, 0.85)" },
        "Windows 11": { color: "#6ea8fe", glow: "rgba(110, 168, 254, 0.75)" },
        "Live Rescue": { color: "#ffb703", glow: "rgba(255, 183, 3, 0.8)" },
    };

    const applyBootGlow = (label) => {
        const theme = bootThemeByLabel[label] || bootThemeByLabel["ASTERIX OS"];
        document.documentElement.style.setProperty("--boot-accent", theme.color);
        document.documentElement.style.setProperty("--boot-glow", theme.glow);
    };

    entries.forEach(entry => {
        entry.addEventListener("click", () => {
            entries.forEach(item => item.classList.toggle("selected", item === entry));
            const label = entry.querySelector(".os-name")?.textContent || "ASTERIX OS";
            applyBootGlow(label);
            runBootSequence(label);
            const trainingNote = document.getElementById("bootTrainingNote");
            if (trainingNote) {
                trainingNote.textContent = `AI training: learned boot preference for ${label}`;
            }
        });
    });
}

function renderHomeTabs() {
    Object.entries(HOME_TABS).forEach(([tabName, cards]) => {
        const host = document.getElementById(`${tabName}Grid`);
        if (!host) return;
        host.innerHTML = cards.map(card => `
            <div class="home-card">
                <div class="home-card-title">${card.title}</div>
                <div class="home-card-value">${card.value}</div>
                <div class="home-card-sub">${card.sub}</div>
            </div>
        `).join("");
    });
}

function setupTabButtons() {
    const buttons = document.querySelectorAll(".tab-button");
    const panels = document.querySelectorAll(".tab-panel");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.toggle("active", b === btn));
            panels.forEach(panel => {
                const isActive = panel.id === `tab-${btn.dataset.tab}`;
                panel.classList.toggle("active", isActive);
            });
        });
    });
}

// Render Wallpapers
function renderWallpapers(filter) {
    const grid = document.getElementById("wallpaperGrid");
    grid.innerHTML = "";

    const filtered = filter === "all" ? WALLPAPERS : WALLPAPERS.filter(w => w.tag === filter);

    filtered.forEach(wp => {
        const card = document.createElement("div");
        card.className = "gallery-card";
        card.onclick = () => openModal(`wallpapers/${wp.file}`, wp.title);

        card.innerHTML = `
            <div class="gallery-img-wrapper">
                <img src="wallpapers/${wp.file}" alt="${wp.title}" loading="lazy">
            </div>
            <div class="gallery-info">
                <div>
                    <div class="gallery-name">${wp.title}</div>
                    <div style="font-size:0.75rem; color:#8492a6; margin-top:2px;">${wp.desc}</div>
                </div>
                <span class="gallery-tag">${wp.tag.toUpperCase()}</span>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Filter Buttons
function setupFilters() {
    const buttons = document.querySelectorAll(".filter-btn");
    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            renderWallpapers(btn.dataset.filter);
        });
    });
}

// Render Subsystems
function renderSubsystems(query = "") {
    const grid = document.getElementById("subsystemsGrid");
    grid.innerHTML = "";

    const q = query.toLowerCase();
    const filtered = SUBSYSTEMS.filter(s => 
        s.name.toLowerCase().includes(q) || 
        s.tools.toLowerCase().includes(q) ||
        s.alias.toLowerCase().includes(q)
    );

    filtered.forEach(sub => {
        const card = document.createElement("div");
        card.className = "subsystem-card";
        card.innerHTML = `
            <div class="subsystem-header">
                <span class="subsystem-icon">${sub.icon}</span>
                <div class="subsystem-title">${sub.num}. ${sub.name}</div>
            </div>
            <div class="subsystem-tools">${sub.tools}</div>
            <span class="key-badge">${sub.alias}</span>
        `;
        grid.appendChild(card);
    });
}

// Tool Search
function setupSearch() {
    const input = document.getElementById("toolSearch");
    input.addEventListener("input", (e) => {
        renderSubsystems(e.target.value);
    });
}

// Fullscreen Modal
function openModal(imgSrc, title) {
    const modal = document.getElementById("imageModal");
    const modalImg = document.getElementById("modalImg");
    const caption = document.getElementById("modalCaption");

    modal.style.display = "flex";
    modalImg.src = imgSrc;
    caption.textContent = title;
}

function closeModal() {
    document.getElementById("imageModal").style.display = "none";
}

// Discord Webhook Integration
async function sendDiscordTest() {
    const webhookUrl = document.getElementById("discordWebhookInput").value.trim();
    const message = document.getElementById("discordMsgInput").value.trim() || "ASTERIX OS Web Portal Alert Transmitted!";
    const statusBox = document.getElementById("discordStatusMsg");

    if (!webhookUrl.startsWith("https://discord.com/api/webhooks/")) {
        statusBox.className = "status-box error";
        statusBox.textContent = "[!] Please enter a valid Discord Webhook URL starting with https://discord.com/api/webhooks/";
        return;
    }

    try {
        const payload = {
            username: "ASTERIX OS NODE",
            avatar_url: "https://raw.githubusercontent.com/alexhack235-code/ASTERIX-BOOTING-SEQUENCE/main/assets/iso-branding/asterix_boot_01_electric_cyan_1788292127536.jpg",
            embeds: [{
                title: "⚡ ASTERIX OS Web Dispatcher",
                description: message,
                color: 65535,
                fields: [
                    { name: "Node Status", value: "ONLINE", inline: true },
                    { name: "Persistence", value: "ACTIVE", inline: true }
                ],
                footer: { text: "ASTERIX Cybernetic Platform" }
            }]
        };

        const response = await fetch(webhookUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            statusBox.className = "status-box success";
            statusBox.textContent = "[✔] Payload successfully transmitted to Discord server!";
        } else {
            statusBox.className = "status-box error";
            statusBox.textContent = `[!] Discord API responded with error code: ${response.status}`;
        }
    } catch (err) {
        statusBox.className = "status-box error";
        statusBox.textContent = `[!] Network error: ${err.message}`;
    }
}

async function sendDiscordStatus() {
    const webhookUrl = document.getElementById("discordWebhookInput").value.trim();
    const statusBox = document.getElementById("discordStatusMsg");

    if (!webhookUrl.startsWith("https://discord.com/api/webhooks/")) {
        statusBox.className = "status-box error";
        statusBox.textContent = "[!] Please enter a valid Discord Webhook URL.";
        return;
    }

    try {
        const payload = {
            username: "ASTERIX OS TELEMETRY",
            embeds: [{
                title: "📊 ASTERIX Node Telemetry Report",
                color: 16711807,
                fields: [
                    { name: "Host", value: "asterix-sec-node", inline: true },
                    { name: "Kernel", value: "6.1.0-sec-amd64", inline: true },
                    { name: "Workspace", value: "Quad-Grid Tmux", inline: true },
                    { name: "Storage Vault", value: "/asterix_persistent", inline: true },
                    { name: "Security Tier", value: "MAXIMUM", inline: true }
                ],
                footer: { text: "ASTERIX Telemetry Core" }
            }]
        };

        const response = await fetch(webhookUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            statusBox.className = "status-box success";
            statusBox.textContent = "[✔] Telemetry report posted to Discord!";
        } else {
            statusBox.className = "status-box error";
            statusBox.textContent = `[!] Error code: ${response.status}`;
        }
    } catch (err) {
        statusBox.className = "status-box error";
        statusBox.textContent = `[!] Network error: ${err.message}`;
    }
}
