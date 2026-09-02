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

document.addEventListener("DOMContentLoaded", () => {
    renderWallpapers("all");
    renderSubsystems();
    setupFilters();
    setupSearch();
});

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
