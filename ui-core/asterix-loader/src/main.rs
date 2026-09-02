//! =====================================================================
//! ASTERIX OS - Master Cybernetic Command & Control Engine
//! Maximum Tier: 12 Specialized Subsystems & Full Security Toolchain
//! 100% Pure Standalone Rust (Zero External Crate Dependencies)
//! =====================================================================

use std::env;
use std::fs;
use std::io::{self, Write};
use std::net::UdpSocket;
use std::path::Path;
use std::process::{Command, Stdio};
use std::thread::sleep;
use std::time::Duration;

// ANSI 256-Color Cyber Palette
const C_RESET: &str = "\x1b[0m";
const C_BOLD: &str = "\x1b[1m";
const C_DIM: &str = "\x1b[2m";
const C_RED: &str = "\x1b[38;5;196m";
const C_ORANGE: &str = "\x1b[38;5;208m";
const C_YELLOW: &str = "\x1b[38;5;220m";
const C_GREEN: &str = "\x1b[38;5;46m";
const C_CYAN: &str = "\x1b[38;5;51m";
const C_BLUE: &str = "\x1b[38;5;45m";
const C_MAGENTA: &str = "\x1b[38;5;201m";
const C_PURPLE: &str = "\x1b[38;5;141m";
const C_WHITE: &str = "\x1b[38;5;231m";
const C_GRAY: &str = "\x1b[38;5;240m";

const BANNER_ART: &str = r#"
    █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ██████╗ ███████╗
   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝    ██╔═══██╗██╔════╝
   ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝     ██║   ██║███████╗
   ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗     ██║   ██║╚════██║
   ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗    ╚██████╔╝███████║
   ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝
                     >> NEXT-GEN CYBERNETIC PLATFORM <<"#;

struct Rng {
    state: u64,
}

impl Rng {
    fn new() -> Self {
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos() as u64)
            .unwrap_or(0xCAFEBABE12345678);
        Self { state: nanos }
    }

    fn next_u32(&mut self) -> u32 {
        self.state = self.state.wrapping_mul(6364136223846793005).wrapping_add(1);
        (self.state >> 32) as u32
    }

    fn next_float(&mut self) -> f32 {
        (self.next_u32() & 0xFFFFFF) as f32 / 16777216.0
    }
}

fn clear_screen() {
    print!("\x1b[2J\x1b[H");
    let _ = io::stdout().flush();
}

fn glitch_banner(banner: &str, rng: &mut Rng, intensity: f32) -> String {
    let glitch_chars = ['#', '@', '%', '&', '!', '$', '?', '0', '1', 'X', 'Z', '<', '>'];
    let mut out = String::with_capacity(banner.len());

    for ch in banner.chars() {
        if ch == '\n' || ch == ' ' {
            out.push(ch);
        } else if rng.next_float() < intensity {
            let idx = (rng.next_u32() as usize) % glitch_chars.len();
            out.push(glitch_chars[idx]);
        } else {
            out.push(ch);
        }
    }
    out
}

fn render_progress_bar(percent: u32, width: usize) -> String {
    let filled = ((width as u32 * percent) / 100) as usize;
    let empty = width.saturating_sub(filled);
    let bar_filled: String = "█".repeat(filled);
    let bar_empty: String = "░".repeat(empty);

    format!("{C_WHITE}[{C_CYAN}{bar_filled}{C_GRAY}{bar_empty}{C_WHITE}] {C_YELLOW}{percent:3}%{C_RESET}")
}

struct BootStep {
    subsystem: &'static str,
    desc: &'static str,
    duration_ms: u64,
}

const BOOT_STEPS: &[BootStep] = &[
    BootStep { subsystem: "INITIALIZING_CORE_KERNEL", desc: "Loading Asterix Microkernel v4.9.0-sec", duration_ms: 60 },
    BootStep { subsystem: "HARDWARE_ABSTRACTION",   desc: "Probing I/O bus & DMA memory channels",   duration_ms: 50 },
    BootStep { subsystem: "MEMORY_RING_BUFFERS",    desc: "Allocating locked ring buffers cache",    duration_ms: 40 },
    BootStep { subsystem: "CHACHA20_CRYPTO_VAULT",   desc: "Initializing AES-256-GCM & ChaCha20",      duration_ms: 50 },
    BootStep { subsystem: "PACKET_DRIVER_HOOKS",    desc: "Injecting eBPF bytecode & raw sockets",   duration_ms: 60 },
    BootStep { subsystem: "STORAGE_CONTROLLER",     desc: "Mounting rootfs (Read-Only OverlayFS)",   duration_ms: 45 },
    BootStep { subsystem: "ASTERIX_PERSISTENCE",    desc: "Verifying 'ASTERIX-PERSISTENCE' volume",  duration_ms: 90 },
    BootStep { subsystem: "SECURITY_SUITE_ENGINE",  desc: "Pre-allocating Metasploit, Wireshark, Nmap", duration_ms: 60 },
    BootStep { subsystem: "DEVELOPER_WORKSPACE",    desc: "Hooking Rust, Go, GCC, Python, Node.js", duration_ms: 50 },
    BootStep { subsystem: "INTERFACE_MATRIX",       desc: "Starting Asterix Master Command Hub",     duration_ms: 70 },
];

fn run_boot_animation(fast: bool) {
    let mut rng = Rng::new();

    if !fast {
        let colors = [C_CYAN, C_MAGENTA, C_GREEN, C_RED];
        for (i, color) in colors.iter().enumerate() {
            clear_screen();
            let glitched = glitch_banner(BANNER_ART, &mut rng, 0.25 - (i as f32 * 0.05));
            println!("{color}{C_BOLD}{glitched}{C_RESET}");
            let _ = io::stdout().flush();
            sleep(Duration::from_millis(60));
        }
    }

    clear_screen();
    println!("{C_CYAN}{C_BOLD}{BANNER_ART}{C_RESET}");
    println!("\n{C_BLUE}{}{C_RESET}", "═".repeat(76));
    println!("{C_WHITE}{C_BOLD}{:>58}{C_RESET}", "[ SYSTEM BOOT SEQUENCE // ASTERIX KERNEL INITIALIZATION ]");
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(76));

    let total = BOOT_STEPS.len();
    let speed_div = if fast { 3 } else { 1 };

    for (i, step) in BOOT_STEPS.iter().enumerate() {
        print!(" {C_CYAN}[{:^24}]{C_RESET} {C_WHITE}{:<42}{C_RESET} {C_GREEN}[ OK ]{C_RESET}\n", step.subsystem, step.desc);
        let _ = io::stdout().flush();
        sleep(Duration::from_millis(step.duration_ms / speed_div));
    }

    println!("\n{C_CYAN}{}{C_RESET}", "─".repeat(76));
    println!(" {}", render_progress_bar(100, 48));
    println!("{C_CYAN}{}{C_RESET}", "─".repeat(76));
    println!("\n{C_GREEN}{C_BOLD} [✔] ASTERIX OS IS ONLINE & READY FOR OPERATIONS {C_RESET}");
    println!(" {C_YELLOW}Persistent Storage Status: {C_GREEN}CONNECTED (ASTERIX_PERSISTENCE){C_RESET}");
    println!(" {C_YELLOW}Master Arsenal:            {C_GREEN}MAXIMUM TIER (Recon, Web, Exploit, Crypto, Dev){C_RESET}\n");

    if !fast {
        sleep(Duration::from_millis(700));
    }
}

struct SystemTelemetry {
    host: String,
    ip: String,
    persistence: String,
}

fn get_system_telemetry() -> SystemTelemetry {
    let host = env::var("HOSTNAME")
        .or_else(|_| env::var("COMPUTERNAME"))
        .unwrap_or_else(|_| "asterix-node".to_string());

    let ip = match UdpSocket::bind("0.0.0.0:0") {
        Ok(socket) => match socket.connect("8.8.8.8:80") {
            Ok(_) => match socket.local_addr() {
                Ok(addr) => addr.ip().to_string(),
                Err(_) => "127.0.0.1 (Offline)".to_string(),
            },
            Err(_) => "127.0.0.1 (Offline)".to_string(),
        },
        Err(_) => "127.0.0.1 (Offline)".to_string(),
    };

    let home = env::var("HOME").or_else(|_| env::var("USERPROFILE")).unwrap_or_default();
    let persistent_dir = format!("{}/asterix_persistent", home);
    let has_persistence = Path::new("/asterix_persistent").exists() || Path::new(&persistent_dir).exists();

    let persistence = if has_persistence {
        "ACTIVE [Persistent Volume Attached]".to_string()
    } else {
        "SIMULATED [Local Storage Mode]".to_string()
    };

    SystemTelemetry { host, ip, persistence }
}

fn print_header(tel: &SystemTelemetry) {
    clear_screen();
    println!("{C_CYAN}{C_BOLD}{BANNER_ART}{C_RESET}");
    println!("           {C_MAGENTA}{C_BOLD}>> ASTERIX CYBERNETIC COMMAND & CONTROL HUB <<{C_RESET}");
    println!("{C_BLUE}╔{}╗{C_RESET}", "═".repeat(76));
    println!("{C_BLUE}║{C_WHITE} NODE: {C_YELLOW}{:<16}{C_WHITE}IP: {C_GREEN}{:<18}{C_WHITE}ARCH: {C_CYAN}{:<12}{C_BLUE}║{C_RESET}", tel.host, tel.ip, env::consts::ARCH);
    println!("{C_BLUE}║{C_WHITE} DATA PERSISTENCE: {}{:<55}{C_BLUE}║{C_RESET}", if tel.persistence.contains("ACTIVE") { C_GREEN } else { C_YELLOW }, tel.persistence);
    println!("{C_BLUE}╚{}╝{C_RESET}\n", "═".repeat(76));
}

fn menu_item(num: &str, icon: &str, title: &str, desc: &str) {
    println!("  {C_CYAN}[{C_BOLD}{num}{C_RESET}{C_CYAN}]{C_RESET} {icon} {C_WHITE}{C_BOLD}{title:<32}{C_RESET} {C_GRAY}» {desc}{C_RESET}");
}

fn read_user_input(prompt: &str) -> String {
    print!("{prompt}");
    let _ = io::stdout().flush();
    let mut buffer = String::new();
    let _ = io::stdin().read_line(&mut buffer);
    buffer.trim().to_string()
}

fn pause_for_user() {
    let _ = read_user_input(&format!("\n{C_GRAY}Press Enter to return...{C_RESET}"));
}

fn execute_command(cmd: &str, args: &[&str]) {
    println!("{C_CYAN}[*] Launching {cmd}...{C_RESET}");
    match Command::new(cmd).args(args).status() {
        Ok(status) => {
            if !status.success() {
                println!("{C_YELLOW}[!] Notice: Process exited with status {status}{C_RESET}");
            }
        }
        Err(e) => {
            println!("{C_RED}[!] Error executing {cmd}: {e}{C_RESET}");
            println!("{C_YELLOW}[*] Ensure the tool is installed (e.g. sudo apt install {cmd}){C_RESET}");
        }
    }
    pause_for_user();
}

// ---------------------------------------------------------------------
// 12 SPECIALIZED SUBSYSTEM MENUS
// ---------------------------------------------------------------------

fn sub_menu_recon() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_CYAN}{C_BOLD} [ 01: RECONNAISSANCE & OSINT ARSENAL ] {C_RESET}\n");
        menu_item("1", "🔍", "Nmap Stealth SYN Scan", "Port scanning, service detection & OS discovery");
        menu_item("2", "⚡", "Masscan High-Speed Sweep", "Scan entire IP ranges at gigabit speed");
        menu_item("3", "🌐", "DnsRecon & DNSEnum", "DNS enumeration and zone transfer checks");
        menu_item("4", "🕵️", "Whois Domain Intelligence", "Query registrar and ASN allocation data");
        menu_item("5", "📡", "Netdiscover ARP Sweep", "Local network active host discovery");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-RECON » {C_RESET}"));
        match choice.as_str() {
            "1" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Target IP/Domain: {C_RESET}"));
                if !target.is_empty() { execute_command("nmap", &["-sV", "-sC", "-T4", &target]); }
            }
            "2" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Subnet (e.g. 192.168.1.0/24): {C_RESET}"));
                if !target.is_empty() { execute_command("masscan", &["-p1-65535", &target, "--rate=1000"]); }
            }
            "3" => {
                let domain = read_user_input(&format!("{C_YELLOW}Enter Domain Name: {C_RESET}"));
                if !domain.is_empty() { execute_command("dnsrecon", &["-d", &domain]); }
            }
            "4" => {
                let domain = read_user_input(&format!("{C_YELLOW}Enter Domain or IP: {C_RESET}"));
                if !domain.is_empty() { execute_command("whois", &[&domain]); }
            }
            "5" => execute_command("netdiscover", &["-r", "192.168.1.0/24"]),
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_web() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_MAGENTA}{C_BOLD} [ 02: WEB APPLICATION WARFARE ] {C_RESET}\n");
        menu_item("1", "💉", "SQLMap Automated Injector", "Database takeover and SQL injection tests");
        menu_item("2", "📁", "Gobuster Directory Fuzzer", "High-speed URL directory brute-force");
        menu_item("3", "🔎", "Nikto Web Vulnerability Scan", "Scan for misconfigurations and outdated web files");
        menu_item("4", "⚡", "FFUF Fast Web Fuzzer", "High performance web fuzzing in Go");
        menu_item("5", "🛡️", "Wafw00f Firewall Detector", "Identify web application firewalls (WAF)");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_MAGENTA}ASTERIX-WEB » {C_RESET}"));
        match choice.as_str() {
            "1" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter Vulnerable Target URL: {C_RESET}"));
                if !url.is_empty() { execute_command("sqlmap", &["-u", &url, "--batch", "--banner"]); }
            }
            "2" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter Target Web URL: {C_RESET}"));
                if !url.is_empty() { execute_command("gobuster", &["dir", "-u", &url, "-w", "/usr/share/wordlists/dirb/common.txt"]); }
            }
            "3" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter Host URL: {C_RESET}"));
                if !url.is_empty() { execute_command("nikto", &["-h", &url]); }
            }
            "4" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter URL with FUZZ keyword: {C_RESET}"));
                if !url.is_empty() { execute_command("ffuf", &["-u", &url, "-w", "/usr/share/wordlists/dirb/common.txt"]); }
            }
            "5" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter Target Domain: {C_RESET}"));
                if !url.is_empty() { execute_command("wafw00f", &[&url]); }
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_exploit() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_RED}{C_BOLD} [ 03: EXPLOITATION & PAYLOADS ] {C_RESET}\n");
        menu_item("1", "💣", "Metasploit MSFConsole", "Omnipresent exploit & payload framework");
        menu_item("2", "🔎", "SearchSploit ExploitDB", "Query offline verified exploit database");
        menu_item("3", "🔌", "Netcat / Ncat Interactive", "Spawn TCP/UDP listeners and relays");
        menu_item("4", "⚡", "Socat Encrypted Tunnels", "Create bidirectional SSL/TLS relays");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_RED}ASTERIX-EXPLOIT » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("msfconsole", &[]),
            "2" => {
                let q = read_user_input(&format!("{C_YELLOW}Enter Search Term (e.g. openssh, apache): {C_RESET}"));
                if !q.is_empty() { execute_command("searchsploit", &[&q]); }
            }
            "3" => {
                let port = read_user_input(&format!("{C_YELLOW}Enter Port to Listen on (default: 4444): {C_RESET}"));
                let p = if port.is_empty() { "4444" } else { &port };
                execute_command("nc", &["-lvnp", p]);
            }
            "4" => {
                let args_str = read_user_input(&format!("{C_YELLOW}Enter Socat Arguments: {C_RESET}"));
                let args: Vec<&str> = args_str.split_whitespace().collect();
                if !args.is_empty() { execute_command("socat", &args); }
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_passwords() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_YELLOW}{C_BOLD} [ 04: PASSWORD & HASH AUDITING ] {C_RESET}\n");
        menu_item("1", "⚡", "Hashcat GPU/CPU Cracker", "World's fastest rule-based password cracker");
        menu_item("2", "🥩", "John the Ripper", "Multi-algorithm hash and shadow file cracker");
        menu_item("3", "🐉", "Hydra Online Brute-Force", "Fast network authentication cracker (SSH, FTP)");
        menu_item("4", "📜", "Crunch Wordlist Generator", "Generate custom wordlists and character masks");
        menu_item("5", "❓", "HashID Identifier", "Identify unknown cryptographic hash formats");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_YELLOW}ASTERIX-PASS » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("hashcat", &["-b"]),
            "2" => {
                let hash_file = read_user_input(&format!("{C_YELLOW}Enter Path to Hash File: {C_RESET}"));
                if !hash_file.is_empty() { execute_command("john", &[&hash_file]); }
            }
            "3" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Target IP: {C_RESET}"));
                let service = read_user_input(&format!("{C_YELLOW}Enter Service (e.g. ssh, ftp): {C_RESET}"));
                if !target.is_empty() && !service.is_empty() {
                    execute_command("hydra", &["-l", "root", "-P", "/usr/share/wordlists/rockyou.txt", &target, &service]);
                }
            }
            "4" => {
                let min = read_user_input(&format!("{C_YELLOW}Min Length (e.g. 6): {C_RESET}"));
                let max = read_user_input(&format!("{C_YELLOW}Max Length (e.g. 8): {C_RESET}"));
                let chars = read_user_input(&format!("{C_YELLOW}Character Set (e.g. abc123): {C_RESET}"));
                if !min.is_empty() && !max.is_empty() && !chars.is_empty() {
                    execute_command("crunch", &[&min, &max, &chars]);
                }
            }
            "5" => {
                let hash_str = read_user_input(&format!("{C_YELLOW}Enter Hash to Identify: {C_RESET}"));
                if !hash_str.is_empty() { execute_command("hashid", &[&hash_str]); }
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_sniffing() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_BLUE}{C_BOLD} [ 05: SNIFFING & TRAFFIC INTERCEPTION ] {C_RESET}\n");
        menu_item("1", "🦈", "Wireshark Packet Sniffer", "Graphical deep packet inspection and filter suite");
        menu_item("2", "📡", "TShark CLI Sniffer", "Live terminal packet capture with eBPF filter");
        menu_item("3", "📦", "Tcpdump Hex Sniffer", "Raw packet capture stream directly to pcap");
        menu_item("4", "🎭", "MacChanger Randomizer", "Randomize hardware MAC address on interface");
        menu_item("5", "⚡", "Hping3 Packet Crafter", "Custom TCP/IP packet assembler and tester");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_BLUE}ASTERIX-SNIFF » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("wireshark", &[]),
            "2" => execute_command("tshark", &["-i", "any", "-c", "50"]),
            "3" => execute_command("tcpdump", &["-nn", "-c", "25"]),
            "4" => {
                let iface = read_user_input(&format!("{C_YELLOW}Enter Interface Name (e.g. eth0, wlan0): {C_RESET}"));
                let i = if iface.is_empty() { "eth0" } else { &iface };
                execute_command("macchanger", &["-r", i]);
            }
            "5" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Target IP: {C_RESET}"));
                if !target.is_empty() { execute_command("hping3", &["-S", "-p", "80", "-c", "5", &target]); }
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_wireless() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_CYAN}{C_BOLD} [ 06: WIRELESS & RADIO WARFARE ] {C_RESET}\n");
        menu_item("1", "📡", "Aircrack-ng Suite", "802.11 wireless WEP/WPA/WPA2 capture and cracker");
        menu_item("2", "🤖", "Wifite Automated Auditor", "Automated attack on WPA handshakes and WPS PINs");
        menu_item("3", "🔓", "Reaver WPS Tool", "Brute-force WPS PINs to recover WPA passwords");
        menu_item("4", "🛰️", "Kismet Wireless Detector", "Wireless network detector, sniffer, and IDS");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-WIFI » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("aircrack-ng", &["--help"]),
            "2" => execute_command("wifite", &[]),
            "3" => execute_command("reaver", &["--help"]),
            "4" => execute_command("kismet", &[]),
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_forensics() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_PURPLE}{C_BOLD} [ 07: FORENSICS & STEGANOGRAPHY ] {C_RESET}\n");
        menu_item("1", "🔬", "Binwalk Firmware Extractor", "Analyze and extract embedded files in firmware");
        menu_item("2", "⛏️", "Foremost File Carver", "Recover lost files based on headers and footers");
        menu_item("3", "🖼️", "Steghide Data Hider", "Embed or extract hidden files in JPEG/BMP/WAV");
        menu_item("4", "🏷️", "Exiftool Metadata Inspector", "Read and edit metadata in photos, PDFs, docs");
        menu_item("5", "🛡️", "Chkrootkit System Audit", "Scan local Linux system for rootkits and backdoors");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_PURPLE}ASTERIX-FORENSIC » {C_RESET}"));
        match choice.as_str() {
            "1" => {
                let file = read_user_input(&format!("{C_YELLOW}Enter Firmware Path: {C_RESET}"));
                if !file.is_empty() { execute_command("binwalk", &["-e", &file]); }
            }
            "2" => {
                let image = read_user_input(&format!("{C_YELLOW}Enter Disk Image Path: {C_RESET}"));
                if !image.is_empty() { execute_command("foremost", &["-i", &image]); }
            }
            "3" => {
                let img = read_user_input(&format!("{C_YELLOW}Enter Stego File Path: {C_RESET}"));
                if !img.is_empty() { execute_command("steghide", &["extract", "-sf", &img]); }
            }
            "4" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter File to Inspect: {C_RESET}"));
                if !target.is_empty() { execute_command("exiftool", &[&target]); }
            }
            "5" => execute_command("chkrootkit", &[]),
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_reverse() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_GREEN}{C_BOLD} [ 08: REVERSE ENGINEERING & BINARY STUDIO ] {C_RESET}\n");
        menu_item("1", "🔬", "Radare2 (R2) Disassembler", "Advanced command-line reverse engineering engine");
        menu_item("2", "🐞", "GDB GNU Debugger", "Inspect registers, breakpoints, and memory dumps");
        menu_item("3", "📝", "Hexedit Terminal Editor", "Direct byte-level editing of binary files");
        menu_item("4", "📄", "XXD Hex Dumper", "Generate hexadecimal dumps and patches");
        menu_item("5", "🔍", "Strings String Extractor", "Extract printable ASCII/Unicode strings from binary");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_GREEN}ASTERIX-REVERSE » {C_RESET}"));
        match choice.as_str() {
            "1" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Binary Path (e.g. /bin/ls): {C_RESET}"));
                if !target.is_empty() { execute_command("r2", &["-AA", &target]); }
            }
            "2" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Binary to Debug: {C_RESET}"));
                if !target.is_empty() { execute_command("gdb", &[&target]); }
            }
            "3" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter File to Hexedit: {C_RESET}"));
                if !target.is_empty() { execute_command("hexedit", &[&target]); }
            }
            "4" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Binary Path: {C_RESET}"));
                if !target.is_empty() { execute_command("xxd", &[&target]); }
            }
            "5" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Binary Path: {C_RESET}"));
                if !target.is_empty() { execute_command("strings", &[&target]); }
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_developer() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_CYAN}{C_BOLD} [ 09: FULL-STACK DEVELOPER STUDIO ] {C_RESET}\n");
        menu_item("1", "🦀", "Rust & Cargo Studio", "rustc, cargo build, cargo run, clippy");
        menu_item("2", "🐹", "Go (Golang) Workspace", "go build, go run, go test, go install");
        menu_item("3", "🐍", "Python & Pip Workspace", "python3, pip, ipython, venv manager");
        menu_item("4", "⚡", "C / C++ & Build Systems", "gcc, g++, clang, make, cmake, gdb");
        menu_item("5", "🌐", "Node.js & Web Studio", "node, npm, npx, yarn package engine");
        menu_item("6", "🐙", "LazyGit & VCS Hub", "Launch interactive terminal Git interface");
        menu_item("7", "📡", "HTTPie API Workbench", "REST API, JSON debug & HTTP client");
        menu_item("8", "🗄️", "Database Console (SQLite)", "SQLite3 interactive relational engine");
        menu_item("9", "🚀", "CLI Power Utilities", "ripgrep (rg), fzf, bat, eza, zoxide");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-DEV » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("rustc", &["--version"]),
            "2" => execute_command("go", &["version"]),
            "3" => execute_command("ipython3", &[]),
            "4" => execute_command("gcc", &["--version"]),
            "5" => execute_command("node", &["--version"]),
            "6" => execute_command("lazygit", &[]),
            "7" => {
                let url = read_user_input(&format!("{C_YELLOW}Enter API URL: {C_RESET}"));
                if !url.is_empty() { execute_command("http", &[&url]); }
            }
            "8" => {
                let db = read_user_input(&format!("{C_YELLOW}Enter SQLite file (default: dev.db): {C_RESET}"));
                let p = if db.is_empty() { "dev.db" } else { &db };
                execute_command("sqlite3", &[p]);
            }
            "9" => {
                println!("\n{C_CYAN}{C_BOLD}[*] Power CLI Utilities Available:{C_RESET}");
                println!("  • ripgrep:  rg <query>      (ultra-fast recursive search)");
                println!("  • fzf:      fzf             (fuzzy file/history search)");
                println!("  • bat:      batcat <file>   (syntax-highlighted cat)");
                println!("  • eza:      eza -la --icons (modern file metadata)");
                println!("  • zoxide:   z <dir>         (smart directory jumping)");
                pause_for_user();
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_persistence() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_GREEN}{C_BOLD} [ 10: ASTERIX PERSISTENCE MANAGER ] {C_RESET}\n");

        let home = env::var("HOME").or_else(|_| env::var("USERPROFILE")).unwrap_or_default();
        let target_dir = format!("{}/asterix_persistent", home);
        let _ = fs::create_dir_all(&target_dir);

        println!(" {C_WHITE}Persistent Storage Path:{C_RESET} {C_CYAN}{target_dir}{C_RESET}\n");
        menu_item("1", "📁", "Browse Persistent Vault", "List all persistent stored assets");
        menu_item("2", "💾", "Save Operational Note", "Write persistent note to storage");
        menu_item("3", "📱", "Sync with Android /sdcard/", "Bridge to Termux external storage");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_GREEN}ASTERIX-VAULT » {C_RESET}"));
        match choice.as_str() {
            "1" => {
                println!("\n{C_CYAN}Contents of {target_dir}:{C_RESET}");
                if let Ok(entries) = fs::read_dir(&target_dir) {
                    let mut found = false;
                    for entry in entries.flatten() {
                        found = true;
                        let name = entry.file_name().to_string_lossy().to_string();
                        let size = entry.metadata().map(|m| m.len()).unwrap_or(0);
                        println!("  {C_GREEN}📄 {name:<30} {C_YELLOW}({size} bytes){C_RESET}");
                    }
                    if !found { println!("  {C_GRAY}(Vault is currently empty){C_RESET}"); }
                }
                pause_for_user();
            }
            "2" => {
                let fname = read_user_input(&format!("{C_YELLOW}Enter filename (default: note.txt): {C_RESET}"));
                let filename = if fname.is_empty() { "note.txt" } else { &fname };
                let content = read_user_input(&format!("{C_YELLOW}Enter note content: {C_RESET}"));
                let filepath = format!("{target_dir}/{filename}");
                if let Ok(mut file) = fs::OpenOptions::new().create(true).append(true).open(&filepath) {
                    let _ = writeln!(file, "{content}");
                    println!("{C_GREEN}[✔] Saved to persistent vault: {filepath}{C_RESET}");
                }
                sleep(Duration::from_millis(900));
            }
            "3" => {
                if Path::new("/sdcard").exists() {
                    let _ = fs::create_dir_all("/sdcard/ASTERIX_DATA");
                    let _ = Command::new("ln").args(["-s", "/sdcard/ASTERIX_DATA", &format!("{target_dir}/android_shared")]).status();
                    println!("{C_GREEN}[✔] Linked Android /sdcard/ASTERIX_DATA to persistence vault!{C_RESET}");
                } else {
                    println!("{C_YELLOW}[!] Android /sdcard/ not detected in current environment.{C_RESET}");
                }
                sleep(Duration::from_millis(1200));
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn launch_quad_grid() {
    println!("\n{C_CYAN}{C_BOLD}[*] Launching ASTERIX 4-Way Quad-Grid Tmux Workspace...{C_RESET}");
    println!("{C_YELLOW}Layout Map:{C_RESET}");
    println!("  ┌───────────────┬───────────────┐");
    println!("  │ [1] SNIFFER   │ [2] SCANNER   │");
    println!("  ├───────────────┼───────────────┤");
    println!("  │ [3] SHELL     │ [4] MONITOR   │");
    println!("  └───────────────┴───────────────┘");
    println!("{C_CYAN}Controls:{C_RESET} Mouse Scroll enabled | Ctrl+A q (re-tile) | Ctrl+A y (sync typing)\n");
    sleep(Duration::from_millis(1500));

    let conf = if Path::new("/etc/asterix/asterix.tmux.conf").exists() {
        "/etc/asterix/asterix.tmux.conf"
    } else {
        "ui-core/asterix.tmux.conf"
    };

    let _ = Command::new("tmux").args(["-f", conf, "new-session", "\\;", "split-window", "-h", "\\;", "split-window", "-v", "\\;", "select-pane", "-t", "0", "\\;", "split-window", "-v", "\\;", "select-layout", "tiled"]).status();
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let fast = args.iter().any(|a| a == "--fast");
    let skip = args.iter().any(|a| a == "--skip");
    let menu_only = args.iter().any(|a| a == "--menu");
    let boot_only = args.iter().any(|a| a == "--boot-only");

    // Subsystem Direct CLI Flags
    if args.iter().any(|a| a == "--recon") { sub_menu_recon(); return; }
    if args.iter().any(|a| a == "--web-audit") { sub_menu_web(); return; }
    if args.iter().any(|a| a == "--exploit") { sub_menu_exploit(); return; }
    if args.iter().any(|a| a == "--passwords") { sub_menu_passwords(); return; }
    if args.iter().any(|a| a == "--sniffing") { sub_menu_sniffing(); return; }
    if args.iter().any(|a| a == "--wireless") { sub_menu_wireless(); return; }
    if args.iter().any(|a| a == "--forensics") { sub_menu_forensics(); return; }
    if args.iter().any(|a| a == "--reverse") { sub_menu_reverse(); return; }
    if args.iter().any(|a| a == "--dev") { sub_menu_developer(); return; }
    if args.iter().any(|a| a == "--quad") { launch_quad_grid(); return; }

    if !skip && !menu_only {
        run_boot_animation(fast);
    }

    if boot_only {
        return;
    }

    loop {
        let tel = get_system_telemetry();
        print_header(&tel);

        println!("{C_WHITE}{C_BOLD} [ MASTER SECURITY & ENGINEERING MATRIX ] {C_RESET}\n");
        menu_item("1",  "🔍", "01. Reconnaissance & OSINT", "Nmap, Masscan, Amass, Dnsrecon, Whois");
        menu_item("2",  "🕷️", "02. Web Application Security", "SQLMap, Gobuster, Nikto, FFUF, Wafw00f");
        menu_item("3",  "💣", "03. Exploitation & Payloads", "Metasploit MSF, SearchSploit, Socat");
        menu_item("4",  "🔑", "04. Password & Hash Auditing", "Hashcat, John The Ripper, Hydra, Crunch");
        menu_item("5",  "🦈", "05. Sniffing & Traffic Control", "Wireshark, TShark, Tcpdump, MacChanger");
        menu_item("6",  "📡", "06. Wireless & Radio Attacks", "Aircrack-ng, Wifite, Reaver, Kismet");
        menu_item("7",  "🔬", "07. Forensics & Steganography", "Binwalk, Foremost, Steghide, Exiftool");
        menu_item("8",  "⚙️", "08. Reverse Engineering (R2)", "Radare2, GDB, Hexedit, XXD, Strings");
        menu_item("9",  "🛠️", "09. Full-Stack Dev Studio", "Rust, Go, C/C++, Python, Node, LazyGit");
        menu_item("10", "💾", "10. ASTERIX Persistent Vault", "Manage encrypted data & loot storage");
        menu_item("11", "🪟", "11. Quad-Grid Tmux Studio", "4-way synchronized terminal workspace");
        menu_item("12", "⚡", "12. Hardware & Resource HUD", "Btop, Htop, CPU & Memory Telemetry");
        menu_item("13", "💻", "13. Superuser Shell Prompt", "Drop into enhanced cyber Zsh/Bash");
        menu_item("0",  "⛔", "Power Off / Exit System", "Terminate session or shutdown");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-CONTROL » {C_RESET}"));

        match choice.as_str() {
            "1" => sub_menu_recon(),
            "2" => sub_menu_web(),
            "3" => sub_menu_exploit(),
            "4" => sub_menu_passwords(),
            "5" => sub_menu_sniffing(),
            "6" => sub_menu_wireless(),
            "7" => sub_menu_forensics(),
            "8" => sub_menu_reverse(),
            "9" => sub_menu_developer(),
            "10" => sub_menu_persistence(),
            "11" => launch_quad_grid(),
            "12" => {
                let monitor = if Command::new("btop").stdout(Stdio::null()).spawn().is_ok() {
                    "btop"
                } else if Command::new("htop").stdout(Stdio::null()).spawn().is_ok() {
                    "htop"
                } else {
                    "top"
                };
                execute_command(monitor, &[]);
            }
            "13" => {
                let shell = env::var("SHELL").unwrap_or_else(|_| "/bin/bash".to_string());
                println!("\n{C_GREEN}[*] Spawning ASTERIX Interactive Superuser Shell (type 'exit' to return)...{C_RESET}");
                let _ = Command::new(shell).status();
            }
            "0" | "exit" | "quit" | "q" => {
                println!("\n{C_RED}[*] Terminating ASTERIX Control Center... Goodbye.{C_RESET}\n");
                break;
            }
            _ => {}
        }
    }
}
