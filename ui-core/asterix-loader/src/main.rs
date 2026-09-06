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
#[allow(dead_code)]
const C_RESET: &str = "\x1b[0m";
#[allow(dead_code)]
const C_BOLD: &str = "\x1b[1m";
#[allow(dead_code)]
const C_DIM: &str = "\x1b[2m";
#[allow(dead_code)]
const C_RED: &str = "\x1b[38;5;196m";
#[allow(dead_code)]
const C_ORANGE: &str = "\x1b[38;5;208m";
#[allow(dead_code)]
const C_YELLOW: &str = "\x1b[38;5;220m";
#[allow(dead_code)]
const C_GREEN: &str = "\x1b[38;5;46m";
#[allow(dead_code)]
const C_CYAN: &str = "\x1b[38;5;51m";
#[allow(dead_code)]
const C_BLUE: &str = "\x1b[38;5;45m";
#[allow(dead_code)]
const C_MAGENTA: &str = "\x1b[38;5;201m";
#[allow(dead_code)]
const C_PURPLE: &str = "\x1b[38;5;141m";
#[allow(dead_code)]
const C_WHITE: &str = "\x1b[38;5;231m";
#[allow(dead_code)]
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

    let _total = BOOT_STEPS.len();
    let speed_div = if fast { 3 } else { 1 };

    for (_i, step) in BOOT_STEPS.iter().enumerate() {
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

fn run_system_update() {
    println!("\n{C_CYAN}{C_BOLD}[*] Launching ASTERIX System & Arsenal Update (ax update)...{C_RESET}");
    if Path::new("/usr/local/bin/ax").exists() {
        let _ = Command::new("/usr/local/bin/ax").arg("update").status();
    } else if Path::new("bin/ax").exists() {
        let _ = Command::new("bash").args(["bin/ax", "update"]).status();
    } else {
        println!("{C_YELLOW}[*] Refreshing package repositories...{C_RESET}");
        let _ = Command::new("sudo").args(["apt-get", "update", "-y"]).status();
    }
}

fn run_system_upgrade() {
    println!("\n{C_CYAN}{C_BOLD}[*] Launching ASTERIX Full System & Arsenal Upgrade (ax upgrade)...{C_RESET}");
    if Path::new("/usr/local/bin/ax").exists() {
        let _ = Command::new("/usr/local/bin/ax").arg("upgrade").status();
    } else if Path::new("bin/ax").exists() {
        let _ = Command::new("bash").args(["bin/ax", "upgrade"]).status();
    } else {
        println!("{C_YELLOW}[*] Upgrading package suites...{C_RESET}");
        let _ = Command::new("sudo").args(["apt-get", "upgrade", "-y"]).status();
    }
}

fn run_system_doctor() {
    if Path::new("/usr/local/bin/ax").exists() {
        let _ = Command::new("/usr/local/bin/ax").arg("doctor").status();
    } else if Path::new("bin/ax").exists() {
        let _ = Command::new("bash").args(["bin/ax", "doctor"]).status();
    } else {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_CYAN}{C_BOLD}[ ASTERIX SYSTEM HEALTH & DIAGNOSTICS ]{C_RESET}\n");
        for tool in ["rustc", "cargo", "gcc", "g++", "go", "python3", "nmap", "tmux"] {
            let ok = Command::new(tool).arg("--version").stdout(Stdio::null()).stderr(Stdio::null()).status().map(|s| s.success()).unwrap_or(false);
            if ok {
                println!("  {C_GREEN}✔{C_RESET} {:<16} {C_GREEN}[OK]{C_RESET}", tool);
            } else {
                println!("  {C_RED}✖{C_RESET} {:<16} {C_YELLOW}[MISSING]{C_RESET}", tool);
            }
        }
    }
}

fn dispatch_ax_tool(args: &[String]) {
    if Path::new("/usr/local/bin/ax").exists() {
        let _ = Command::new("/usr/local/bin/ax").args(args).status();
    } else if Path::new("bin/ax").exists() {
        let _ = Command::new("bash").arg("bin/ax").args(args).status();
    } else if Path::new("/etc/asterix/bin/ax").exists() {
        let _ = Command::new("bash").arg("/etc/asterix/bin/ax").args(args).status();
    }
}

fn print_cli_help() {
    println!("{C_CYAN}{C_BOLD}{BANNER_ART}{C_RESET}");
    println!("           {C_MAGENTA}{C_BOLD}>> UNIFIED OS & ARSENAL CONTROL ENGINE [ax / asterix] <<{C_RESET}\n");
    println!("{C_WHITE}{C_BOLD}USAGE:{C_RESET}");
    println!("  {C_CYAN}ax{C_RESET} <command> [arguments...]");
    println!("  {C_CYAN}asterix{C_RESET} <command> [arguments...]\n");
    println!("{C_WHITE}{C_BOLD}CORE SYSTEM & PACKAGE OPERATIONS:{C_RESET}");
    println!("  {C_GREEN}ax update{C_RESET}               Refresh package indexes, git core & security databases");
    println!("  {C_GREEN}ax upgrade{C_RESET}              Full upgrade: OS packages, C/C++/Go/Asm/Rust toolchains");
    println!("  {C_GREEN}ax install <pkgs>{C_RESET}       Install packages automatically via system package manager");
    println!("  {C_GREEN}ax remove <pkgs>{C_RESET}        Uninstall specified packages");
    println!("  {C_GREEN}ax search <query>{C_RESET}       Search package repositories");
    println!("  {C_GREEN}ax clean{C_RESET}                Purge unused packages, build artifacts & system cache");
    println!("  {C_GREEN}ax build{C_RESET}                Compile all native multi-language tool suites");
    println!("  {C_GREEN}ax doctor{C_RESET}               Run deep diagnostics on compilers, tools & storage");
    println!("  {C_GREEN}ax status{C_RESET}               Display live system telemetry HUD (Node, IP, Storage)");
    println!("  {C_GREEN}ax version{C_RESET}              Show ASTERIX OS release information\n");

    println!("{C_WHITE}{C_BOLD}NETWORK & DIAGNOSTIC SUITE:{C_RESET}");
    println!("  {C_YELLOW}ax ip{C_RESET}                   Display LAN IP, WAN public IP, interfaces & gateway");
    println!("  {C_YELLOW}ax ports{C_RESET}                Audit open listening TCP/UDP sockets and processes");
    println!("  {C_YELLOW}ax ping <target>{C_RESET}        Cybernetic ICMP latency probe");
    println!("  {C_YELLOW}ax scan <target>{C_RESET}        Rapid port and service scanner");
    println!("  {C_YELLOW}ax netrecon [subnet]${C_RESET}    Automated network discovery & diagnostic reporter");
    println!("  {C_YELLOW}ax mac [iface]${C_RESET}          Inspect or randomize/spoof interface MAC address");
    println!("  {C_YELLOW}ax webrecon <url>${C_RESET}       High-performance Go web reconnaissance engine\n");

    println!("{C_WHITE}{C_BOLD}SECURITY, CRYPTO & FORENSICS:{C_RESET}");
    println!("  {C_MAGENTA}ax hash <file|str>${C_RESET}      Multi-hash calculator (MD5, SHA-1, SHA-256, CRC32)");
    println!("  {C_MAGENTA}ax shred <file>${C_RESET}         Cryptographic multi-pass secure file obliteration");
    println!("  {C_MAGENTA}ax rootkit${C_RESET}              Scan for anomalous kernel modules and hidden procs");
    println!("  {C_MAGENTA}ax trace [pid]${C_RESET}          Live syscall monitor and process tracer");
    println!("  {C_MAGENTA}ax vuln [target]${C_RESET}        Cyber vulnerability assessment scanner");
    println!("  {C_MAGENTA}ax packet${C_RESET}               Interactive raw packet crafting and injection");
    println!("  {C_MAGENTA}ax darktrace [mod]${C_RESET}        Stealth memory triage, entropy audit & telemetry");
    println!("  {C_MAGENTA}ax shadowcam <audit|scan>${C_RESET}Camera & RTSP/ONVIF surveillance security auditor");
    println!("  {C_MAGENTA}ax dark-engine [sub]${C_RESET}      Pure-Rust Shannon entropy & W^X memory page scanner");
    println!("  {C_MAGENTA}ax log-hunter <scan|stream>${C_RESET}Pure-Rust threat-pattern security log analyzer");
    println!("  {C_MAGENTA}ax defender [status|scan]${C_RESET}   Pure-Rust Antivirus & Windows Security Center shield");
    println!("  {C_MAGENTA}ax firewall [status|rules]${C_RESET}  Host packet filter & stealth drop firewall rules");
    println!("  {C_MAGENTA}ax isolate [lockdown|unlock]${C_RESET}Emergency endpoint network isolation killswitch");
    println!("  {C_MAGENTA}ax anti-net${C_RESET}                Master Anti-Network Attack interactive defense hub");
    println!("  {C_MAGENTA}ax anti-email <audit|breach>${C_RESET}Defensive email & account security (SPF/DMARC/breach)");
    println!("  {C_MAGENTA}ax anti-arp <status|lock>${C_RESET}   ARP poisoning defense & permanent gateway locking");
    println!("  {C_MAGENTA}ax anti-syn <enable|status>${C_RESET} TCP SYN flood shield & embryonic rate limiter");
    println!("  {C_MAGENTA}ax anti-dns <check|lock>${C_RESET}   DNS poisoning detector & immutable resolver lock");
    println!("  {C_MAGENTA}ax anti-scan <status|enable>${C_RESET}Port scan detector & dynamic 30-min auto-quarantine");
    println!("  {C_MAGENTA}ax anti-rev <audit|watch>${C_RESET}  Process anti-debugging, dumpable lock & anti-tampering");
    println!("  {C_MAGENTA}ax thunder [args]${C_RESET}          THUNDER Enterprise Network & Device Defender");
    println!("  {C_MAGENTA}ax ip-rotator [args]${C_RESET}       THUNDER 105-endpoint IP rotator & MAC randomizer");
    println!("  {C_MAGENTA}ax pkg <sync|status>${C_RESET}       Synchronize & manage external security packages");
    println!("  {C_MAGENTA}ax wscan [url]${C_RESET}             WSCAN web weakness & vulnerability scanner");
    println!("  {C_MAGENTA}ax lightning{C_RESET}               LIGHTNING WAF reverse-proxy, Web SOC & IDS engine");
    println!("  {C_MAGENTA}ax game [boost|status]${C_RESET}     eSports kernel game mode, CPU/RAM/TCP latency optimizer");
    println!("  {C_MAGENTA}ax overdrive${C_RESET}               APEX OVERDRIVE 60 FPS glassmorphic gaming HUD (port 4888)");
    println!("  {C_MAGENTA}ax snapshot <create|list|restore>${C_RESET} System Restore & VSS cryptographic point-in-time rollback");
    println!("  {C_MAGENTA}ax event-log <audit|stream>${C_RESET}  Windows Event Viewer & System Reliability Index monitor");
    println!("  {C_MAGENTA}ax sfc <scan|repair>${C_RESET}        System File Checker & DISM binary integrity verification");
    println!("  {C_MAGENTA}ax taskmgr <priority|eco|audit>${C_RESET}Task Manager & EcoQoS Efficiency Mode process priority");
    println!("  {C_MAGENTA}ax secpol <audit|enforce>${C_RESET}   Local Security Policy & NSA/CIS Zero-Vulnerability baseline");
    println!("  {C_MAGENTA}ax sandbox [launch|run]${C_RESET}     Disposable ephemeral sandbox (Windows Sandbox equivalent)");
    println!("  {C_MAGENTA}ax applocker [audit|lockdown]${C_RESET}Application identity & binary whitelisting (AppLocker)");
    println!("  {C_MAGENTA}ax bitlocker [status|audit]${C_RESET}  LUKS2 AES-256-XTS volume & swap encryption (BitLocker)");
    println!("  {C_MAGENTA}ax cred-guard [audit|lockdown]${C_RESET}Process memory anti-dumping & credential vault shield");
    println!("  {C_MAGENTA}ax exploit-guard [audit|asr]${C_RESET} Hardware DEP/NX & Attack Surface Reduction (ASR) rules");
    println!("  {C_MAGENTA}ax undercover [on|off]${C_RESET}     Kali Undercover instant Windows PowerShell disguise");
    println!("  {C_MAGENTA}ax nuke [wipe|test]${C_RESET}          Emergency anti-forensic duress wipe & history shredder");
    println!("  {C_MAGENTA}ax tweaks [mac|ipv6|dns]${C_RESET}   Kali Tweaks MAC randomizer, DNS & IPv6 leak armor");
    println!("  {C_MAGENTA}ax forensic-mode <enable>${C_RESET}  Kali Live forensic write-blocker (noswap noautomount)");
    println!("  {C_MAGENTA}ax rf-audit${C_RESET}                Multi-radio wireless, monitor mode & Bluetooth audit");
    println!("  {C_MAGENTA}ax power [status|boost|save]${C_RESET} Mobile/Linux CPU governor, thermal & battery controller");
    println!("  {C_MAGENTA}ax clean-pro${C_RESET}               Zero-crash cache purge, temporary file cleanup & SSD TRIM");
    println!("  {C_MAGENTA}ax flow${C_RESET}                    Real-time socket states, DNS latency benchmark & flow monitor");
    println!("  {C_MAGENTA}ax ssl-audit <domain>${C_RESET}      Deep SSL/TLS cipher auditor, expiry tracker & SAN inspector");
    println!("  {C_MAGENTA}ax hashdeep <baseline|audit>${C_RESET} Recursive cryptographic binary integrity & tampering auditor");
    println!("  {C_MAGENTA}ax yara-scan [dir]${C_RESET}          YARA rule-based webshell, C2 beacon & shellcode scanner");
    println!("  {C_MAGENTA}ax mac-guard${C_RESET}                AppArmor & SELinux Mandatory Access Control confinement");
    println!("  {C_MAGENTA}ax timeline [dir] [mins]${C_RESET}    Digital forensics MACB activity reconstructor & timestomp audit");
    println!("  {C_MAGENTA}ax trash [list|restore|empty]${C_RESET} Secure recycle bin & quarantined media storage");
    println!("  {C_MAGENTA}ax carve <target> [out]${C_RESET}     Foremost & Scalpel digital forensics deleted media recovery");
    println!("  {C_MAGENTA}ax logwatch${C_RESET}             Real-time security log and auth anomaly watcher\n");

    println!("{C_WHITE}{C_BOLD}VAULT, WORKSPACE & DESKTOP HUD:{C_RESET}");
    println!("  {C_BLUE}ax backup${C_RESET}               Sync and compress vault to Discord and Cloud Panel");
    println!("  {C_BLUE}ax loot${C_RESET}                 Browse captured hashes, scan reports & intelligence");
    println!("  {C_BLUE}ax scaffold <lang> <name>${C_RESET} Scaffolds Rust, C, C++, Go, Python, or Node project");
    println!("  {C_BLUE}ax mem${C_RESET}                  Physical memory and ring buffer inspector");
    println!("  {C_BLUE}ax env${C_RESET}                  Dump environment variables & security configurations");
    println!("  {C_BLUE}ax wallpaper [random]${C_RESET}   Instantly cycle desktop cyberpunk wallpaper");
    println!("  {C_BLUE}ax hud [on|off|restart]${C_RESET} Toggle Conky desktop telemetry overlay");
    println!("  {C_BLUE}ax top${C_RESET}                  Launch Btop / Htop cyber resource monitor\n");

    println!("{C_WHITE}{C_BOLD}DIRECT CYBER SUBSYSTEM JUMPERS:{C_RESET}");
    println!("  {C_CYAN}ax recon${C_RESET}                01. Reconnaissance & OSINT");
    println!("  {C_CYAN}ax web${C_RESET}                  02. Web Application Warfare");
    println!("  {C_CYAN}ax exploit${C_RESET}              03. Exploitation & Payloads");
    println!("  {C_CYAN}ax crack${C_RESET}                04. Password & Hash Auditing");
    println!("  {C_CYAN}ax sniff${C_RESET}                05. Sniffing & Traffic Control");
    println!("  {C_CYAN}ax wifi${C_RESET}                 06. Wireless Attacks");
    println!("  {C_CYAN}ax forensics${C_RESET}            07. Digital Forensics & Stego");
    println!("  {C_CYAN}ax rev${C_RESET}                  08. Reverse Engineering (Radare2, GDB)");
    println!("  {C_CYAN}ax dev${C_RESET}                  09. Full-Stack Developer Studio");
    println!("  {C_CYAN}ax quad${C_RESET}                 11. Instant 4-Way Tmux Quad-Grid Cyber Studio");
    println!("  {C_CYAN}ax portal${C_RESET}               12. Web Operations Media Portal (port 7777)");
    println!("  {C_CYAN}ax discord${C_RESET}              Discord Remote Vault Bridge & Notifications\n");
    println!("{C_WHITE}{C_BOLD}INTERACTIVE COMMAND HUB:{C_RESET}");
    println!("  Run {C_YELLOW}ax${C_RESET} or {C_YELLOW}asterix${C_RESET} with no parameters to launch the full Cybernetic Command Center.\n");
}

fn sub_menu_maintenance() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_GREEN}{C_BOLD} [ 16: SYSTEM MAINTENANCE & ARSENAL UPDATE CENTER ] {C_RESET}\n");
        menu_item("1", "🔄", "Synchronize & Update (ax update)", "Fetch repo indexes, git updates & security signatures");
        menu_item("2", "⚡", "Comprehensive Upgrade (ax upgrade)", "Upgrade OS packages & rebuild all native tool suites");
        menu_item("3", "🩺", "System Diagnostics (ax doctor)", "Audit compiler toolchains, reverse engineering & storage");
        menu_item("4", "🧹", "Purge Cache & Artifacts (ax clean)", "Clean apt/pkg caches & temporary build files");
        menu_item("5", "🔨", "Master Multi-Language Rebuild (ax build)", "Compile C, C++, Go, NASM & Rust from source");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_GREEN}ASTERIX-MAINTENANCE » {C_RESET}"));
        match choice.as_str() {
            "1" => { run_system_update(); pause_for_user(); }
            "2" => { run_system_upgrade(); pause_for_user(); }
            "3" => { run_system_doctor(); pause_for_user(); }
            "4" => {
                println!("{C_CYAN}[*] Running system cache cleanup...{C_RESET}");
                if Path::new("/usr/local/bin/ax").exists() {
                    let _ = Command::new("/usr/local/bin/ax").arg("clean").status();
                } else if Path::new("bin/ax").exists() {
                    let _ = Command::new("bash").args(["bin/ax", "clean"]).status();
                }
                pause_for_user();
            }
            "5" => {
                println!("{C_CYAN}[*] Running master multi-language build...{C_RESET}");
                if Path::new("build-all.sh").exists() {
                    let _ = Command::new("bash").arg("build-all.sh").status();
                } else if Path::new("/etc/asterix/build-all.sh").exists() {
                    let _ = Command::new("bash").arg("/etc/asterix/build-all.sh").status();
                }
                pause_for_user();
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let first_arg = args.get(1).map(|s| s.as_str()).unwrap_or("");

    // Fast-path subcommand router for `ax` and `asterix`
    match first_arg {
        "update" => { run_system_update(); return; }
        "upgrade" => { run_system_upgrade(); return; }
        "doctor" | "check" => { run_system_doctor(); return; }
        "status" | "info" | "telemetry" => {
            let tel = get_system_telemetry();
            print_header(&tel);
            return;
        }
        "version" | "-v" | "--version" => {
            println!("{C_CYAN}{C_BOLD}ASTERIX OS [ax / asterix]{C_RESET} {C_GREEN}v1.2.0-cyber{C_RESET}");
            println!("{C_GRAY}Architecture: {} | Target: {}{C_RESET}", env::consts::ARCH, env::consts::OS);
            return;
        }
        "help" | "-h" | "--help" => {
            print_cli_help();
            return;
        }
        "install" | "add" => {
            if args.len() < 3 {
                println!("{C_RED}[!] Error: Specify package(s) to install.{C_RESET}\nUsage: ax install <pkg...>");
                return;
            }
            if Path::new("/usr/local/bin/ax").exists() {
                let _ = Command::new("/usr/local/bin/ax").args(&args[1..]).status();
            } else if Path::new("bin/ax").exists() {
                let _ = Command::new("bash").arg("bin/ax").args(&args[1..]).status();
            } else {
                let _ = Command::new("sudo").args(["apt-get", "install", "-y"]).args(&args[2..]).status();
            }
            return;
        }
        "remove" | "uninstall" | "rm" => {
            if args.len() < 3 {
                println!("{C_RED}[!] Error: Specify package(s) to remove.{C_RESET}\nUsage: ax remove <pkg...>");
                return;
            }
            if Path::new("/usr/local/bin/ax").exists() {
                let _ = Command::new("/usr/local/bin/ax").args(&args[1..]).status();
            } else if Path::new("bin/ax").exists() {
                let _ = Command::new("bash").arg("bin/ax").args(&args[1..]).status();
            } else {
                let _ = Command::new("sudo").args(["apt-get", "remove", "-y"]).args(&args[2..]).status();
            }
            return;
        }
        "search" => {
            if args.len() < 3 {
                println!("{C_RED}[!] Error: Specify search term.{C_RESET}\nUsage: ax search <keyword>");
                return;
            }
            if Path::new("/usr/local/bin/ax").exists() {
                let _ = Command::new("/usr/local/bin/ax").args(&args[1..]).status();
            } else {
                let _ = Command::new("apt-cache").arg("search").args(&args[2..]).status();
            }
            return;
        }
        "clean" | "autoclean" => {
            if Path::new("/usr/local/bin/ax").exists() {
                let _ = Command::new("/usr/local/bin/ax").arg("clean").status();
            } else {
                let _ = Command::new("sudo").args(["apt-get", "autoremove", "-y"]).status();
            }
            return;
        }
        "build" | "compile" => {
            if Path::new("build-all.sh").exists() {
                let _ = Command::new("bash").arg("build-all.sh").status();
            } else if Path::new("/etc/asterix/build-all.sh").exists() {
                let _ = Command::new("bash").arg("/etc/asterix/build-all.sh").status();
            }
            return;
        }
        "recon" | "--recon" => { sub_menu_recon(); return; }
        "web" | "web-audit" | "--web-audit" => { sub_menu_web(); return; }
        "exploit" | "--exploit" => { sub_menu_exploit(); return; }
        "passwords" | "crack" | "--passwords" => { sub_menu_passwords(); return; }
        "sniffing" | "sniff" | "--sniffing" => { sub_menu_sniffing(); return; }
        "wireless" | "wifi" | "--wireless" => { sub_menu_wireless(); return; }
        "forensics" | "--forensics" => { sub_menu_forensics(); return; }
        "reverse" | "rev" | "--reverse" => { sub_menu_reverse(); return; }
        "dev" | "--dev" => { sub_menu_developer(); return; }
        "quad" | "--quad" => { launch_quad_grid(); return; }
        "portal" | "--portal" => {
            let portal_script = if Path::new("/etc/asterix/ui-core/asterix-web-portal.sh").exists() {
                "/etc/asterix/ui-core/asterix-web-portal.sh"
            } else {
                "ui-core/asterix-web-portal.sh"
            };
            let _ = Command::new(portal_script).status();
            return;
        }
        "discord" | "--discord" => {
            let discord_script = if Path::new("/etc/asterix/ui-core/asterix-discord.sh").exists() {
                "/etc/asterix/ui-core/asterix-discord.sh"
            } else {
                "ui-core/asterix-discord.sh"
            };
            let _ = Command::new(discord_script).args(["setup"]).status();
            return;
        }
        "maintenance" => { sub_menu_maintenance(); return; }

        // Network & Diagnostic Commands
        "ip" | "myip" => { dispatch_ax_tool(&args[1..]); return; }
        "ports" | "listen" => { dispatch_ax_tool(&args[1..]); return; }
        "ping" => { dispatch_ax_tool(&args[1..]); return; }
        "scan" => { dispatch_ax_tool(&args[1..]); return; }
        "netrecon" => { dispatch_ax_tool(&args[1..]); return; }
        "mac" => { dispatch_ax_tool(&args[1..]); return; }
        "webrecon" => { dispatch_ax_tool(&args[1..]); return; }
        "dns" | "dig" => { dispatch_ax_tool(&args[1..]); return; }
        "whois" => { dispatch_ax_tool(&args[1..]); return; }
        "traceroute" | "tracepath" => { dispatch_ax_tool(&args[1..]); return; }
        "arp" => { dispatch_ax_tool(&args[1..]); return; }
        "connections" | "conns" => { dispatch_ax_tool(&args[1..]); return; }

        // Security, Crypto & Forensics
        "hash" => { dispatch_ax_tool(&args[1..]); return; }
        "shred" => { dispatch_ax_tool(&args[1..]); return; }
        "rootkit" => { dispatch_ax_tool(&args[1..]); return; }
        "trace" | "proctrace" => { dispatch_ax_tool(&args[1..]); return; }
        "vuln" | "vulnscan" => { dispatch_ax_tool(&args[1..]); return; }
        "packet" | "packetcraft" => { dispatch_ax_tool(&args[1..]); return; }
        "logwatch" => { dispatch_ax_tool(&args[1..]); return; }
        "firewall" | "ufw" | "iptables" => { dispatch_ax_tool(&args[1..]); return; }
        "audit" | "hardening" => { dispatch_ax_tool(&args[1..]); return; }
        "suid" => { dispatch_ax_tool(&args[1..]); return; }
        "certs" | "ssl" => { dispatch_ax_tool(&args[1..]); return; }
        "b64enc" | "b64dec" | "hexenc" | "hexdec" => { dispatch_ax_tool(&args[1..]); return; }
        "genpass" | "password" => { dispatch_ax_tool(&args[1..]); return; }
        "entropy" => { dispatch_ax_tool(&args[1..]); return; }

        // System, Hardware & Monitoring
        "cpu" | "cpuinfo" => { dispatch_ax_tool(&args[1..]); return; }
        "disk" | "df" => { dispatch_ax_tool(&args[1..]); return; }
        "service" | "systemctl" => { dispatch_ax_tool(&args[1..]); return; }
        "ps" | "procs" => { dispatch_ax_tool(&args[1..]); return; }
        "benchmark" | "bench" => { dispatch_ax_tool(&args[1..]); return; }

        // Vault, Workspace & Desktop HUD
        "backup" => { dispatch_ax_tool(&args[1..]); return; }
        "loot" => { dispatch_ax_tool(&args[1..]); return; }
        "scaffold" | "new" => { dispatch_ax_tool(&args[1..]); return; }
        "mem" | "ram" => { dispatch_ax_tool(&args[1..]); return; }
        "env" => { dispatch_ax_tool(&args[1..]); return; }
        "wallpaper" | "wp" => { dispatch_ax_tool(&args[1..]); return; }
        "hud" => { dispatch_ax_tool(&args[1..]); return; }
        "top" | "htop" | "btop" => { dispatch_ax_tool(&args[1..]); return; }
        "compress" | "tar" => { dispatch_ax_tool(&args[1..]); return; }
        "extract" | "untar" => { dispatch_ax_tool(&args[1..]); return; }
        "find-large" | "bigfiles" => { dispatch_ax_tool(&args[1..]); return; }
        "list" | "commands" => { dispatch_ax_tool(&args[1..]); return; }

        // Tactical Cyber Operations, Deception & Anti-Forensics
        "anti-net" | "antinet" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-email" | "antiemail" | "anti-gmail" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-arp" | "antiarp" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-syn" | "antisyn" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-dns" | "antidns" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-scan" | "antiscan" => { dispatch_ax_tool(&args[1..]); return; }
        "anti-rev" | "antirev" | "anti-reverse" => { dispatch_ax_tool(&args[1..]); return; }
        "thunder" => { dispatch_ax_tool(&args[1..]); return; }
        "defender" | "antivirus" | "av" | "shield" => { dispatch_ax_tool(&args[1..]); return; }
        "fw" | "virus-scan" => { dispatch_ax_tool(&args[1..]); return; }
        "isolate" | "unisolate" | "quarantine" => { dispatch_ax_tool(&args[1..]); return; }
        "ip-rotator" | "iprotator" => { dispatch_ax_tool(&args[1..]); return; }
        "pkg" | "packages" | "pkg-sync" => { dispatch_ax_tool(&args[1..]); return; }
        "wscan" | "web-scan" | "frality" => { dispatch_ax_tool(&args[1..]); return; }
        "lightning" | "waf" | "soc" => { dispatch_ax_tool(&args[1..]); return; }
        "game" | "gaming" | "boost" => { dispatch_ax_tool(&args[1..]); return; }
        "overdrive" | "apex" | "apex-overdrive" => { dispatch_ax_tool(&args[1..]); return; }
        "snapshot" | "restore" | "vss" => { dispatch_ax_tool(&args[1..]); return; }
        "event-log" | "eventvwr" | "events" | "reliability" => { dispatch_ax_tool(&args[1..]); return; }
        "sfc" | "integrity" | "scannow" => { dispatch_ax_tool(&args[1..]); return; }
        "taskmgr" | "task" | "tasks" | "eco" => { dispatch_ax_tool(&args[1..]); return; }
        "secpol" | "security-policy" | "gpo" => { dispatch_ax_tool(&args[1..]); return; }
        "sandbox" | "isolate-run" => { dispatch_ax_tool(&args[1..]); return; }
        "applocker" | "whitelist" | "app-id" => { dispatch_ax_tool(&args[1..]); return; }
        "bitlocker" | "luks" | "vault-crypt" => { dispatch_ax_tool(&args[1..]); return; }
        "cred-guard" | "credguard" | "key-vault" => { dispatch_ax_tool(&args[1..]); return; }
        "exploit-guard" | "exploitguard" | "asr" => { dispatch_ax_tool(&args[1..]); return; }
        "undercover" | "stealth-desktop" | "disguise" => { dispatch_ax_tool(&args[1..]); return; }
        "nuke" | "duress" | "emergency-wipe" => { dispatch_ax_tool(&args[1..]); return; }
        "tweaks" | "kali-tweaks" | "sys-tune" => { dispatch_ax_tool(&args[1..]); return; }
        "forensic-mode" | "forensics-mode" | "write-block" => { dispatch_ax_tool(&args[1..]); return; }
        "rf-audit" | "air-audit" | "kismet-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "power" | "governor" | "cpu-power" | "battery-health" => { dispatch_ax_tool(&args[1..]); return; }
        "clean-pro" | "disk-clean" | "purge-cache" | "trim" => { dispatch_ax_tool(&args[1..]); return; }
        "flow" | "net-flow" | "netstat-pro" | "socket-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "ssl-audit" | "cert-audit" | "tls-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "hashdeep" | "integrity-scan" | "baseline" | "hash-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "yara-scan" | "threat-audit" | "malware-audit" | "signature-scan" => { dispatch_ax_tool(&args[1..]); return; }
        "mac-guard" | "apparmor" | "confinement" | "mac-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "timeline" | "forensic-timeline" | "incident-triage" | "macb" => { dispatch_ax_tool(&args[1..]); return; }
        "trash" | "recycle-bin" | "rm-safe" | "safe-rm" => { dispatch_ax_tool(&args[1..]); return; }
        "carve" | "foremost" | "recover-media" | "scalpel" => { dispatch_ax_tool(&args[1..]); return; }
        "ai" | "asterix-ai" | "ask-ai" | "expert-system" => { dispatch_ax_tool(&args[1..]); return; }
        "auto-compile" | "autocompile" | "compile-fix" | "autofix-build" => { dispatch_ax_tool(&args[1..]); return; }
        "os-computing" | "os-collaborate" | "host-sync" | "os-bridge" | "os-imitate" => { dispatch_ax_tool(&args[1..]); return; }
        "code-repair" | "code-fix" | "fix-code" | "os-fix" | "repair-code" | "heal-code" => { dispatch_ax_tool(&args[1..]); return; }
        "proxychains" | "proxy-chains" | "proxychains-creator" | "proxy-creator" | "proxy" => { dispatch_ax_tool(&args[1..]); return; }
        "darktrace" => { dispatch_ax_tool(&args[1..]); return; }
        "shadowcam" | "cctv" | "cam-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "dark-engine" => { dispatch_ax_tool(&args[1..]); return; }
        "log-hunter" | "loghunter" => { dispatch_ax_tool(&args[1..]); return; }
        "matrix" => { dispatch_ax_tool(&args[1..]); return; }
        "stealth" | "ghost" => { dispatch_ax_tool(&args[1..]); return; }
        "killswitch" | "lockdown" => { dispatch_ax_tool(&args[1..]); return; }
        "decoy" | "honeypot" => { dispatch_ax_tool(&args[1..]); return; }
        "payload" | "revshell" => { dispatch_ax_tool(&args[1..]); return; }
        "malware-scan" | "webshell" => { dispatch_ax_tool(&args[1..]); return; }
        "tor-status" | "tor" | "onion" => { dispatch_ax_tool(&args[1..]); return; }
        "quote" | "ethos" => { dispatch_ax_tool(&args[1..]); return; }

        // Additional Network & Recon
        "subdomains" | "subenum" => { dispatch_ax_tool(&args[1..]); return; }
        "banner-grab" | "grab" => { dispatch_ax_tool(&args[1..]); return; }
        "wifi-scan" | "airmon" => { dispatch_ax_tool(&args[1..]); return; }
        "sniff-live" | "pcap" => { dispatch_ax_tool(&args[1..]); return; }
        "speedtest" | "bandwidth" => { dispatch_ax_tool(&args[1..]); return; }

        // Additional Security, Crypto & Forensics
        "encrypt" | "enc" => { dispatch_ax_tool(&args[1..]); return; }
        "decrypt" | "dec" => { dispatch_ax_tool(&args[1..]); return; }
        "exif" | "metadata" => { dispatch_ax_tool(&args[1..]); return; }
        "docker-audit" | "container" => { dispatch_ax_tool(&args[1..]); return; }
        "qr" | "qrcode" => { dispatch_ax_tool(&args[1..]); return; }
        "sysfetch" | "neofetch" | "fetch" => { dispatch_ax_tool(&args[1..]); return; }
        "traffic" | "netstat-live" => { dispatch_ax_tool(&args[1..]); return; }
        "kernel-hardening" | "sysctl-check" => { dispatch_ax_tool(&args[1..]); return; }
        "fim-init" => { dispatch_ax_tool(&args[1..]); return; }
        "fim-check" => { dispatch_ax_tool(&args[1..]); return; }
        "auth-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "git-secrets" | "secrets" => { dispatch_ax_tool(&args[1..]); return; }
        "cis-audit" | "compliance" => { dispatch_ax_tool(&args[1..]); return; }
        "cert-check" => { dispatch_ax_tool(&args[1..]); return; }
        "pstree" | "process-tree" => { dispatch_ax_tool(&args[1..]); return; }
        "env-audit" => { dispatch_ax_tool(&args[1..]); return; }

        // Network Intelligence & Telemetry
        "ip-geo" | "geoip" => { dispatch_ax_tool(&args[1..]); return; }
        "net-route" | "routing" => { dispatch_ax_tool(&args[1..]); return; }
        "listening" | "ports-deep" => { dispatch_ax_tool(&args[1..]); return; }
        "cron-audit" | "timers" => { dispatch_ax_tool(&args[1..]); return; }

        // Crypto, Certs & Encoding
        "cert-create" | "self-cert" => { dispatch_ax_tool(&args[1..]); return; }
        "json-format" | "json" => { dispatch_ax_tool(&args[1..]); return; }

        // System Power & I/O Telemetry
        "disk-io" | "iostats" => { dispatch_ax_tool(&args[1..]); return; }
        "uptime-stats" | "loadavg" => { dispatch_ax_tool(&args[1..]); return; }
        "battery" => { dispatch_ax_tool(&args[1..]); return; }
        "pkg-verify" | "debsums" => { dispatch_ax_tool(&args[1..]); return; }

        // Advanced Offensive & Forensics (v2.8.0)
        "ssh-audit" | "sshd-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "arp-detect" | "arp-spoof" => { dispatch_ax_tool(&args[1..]); return; }
        "hexdump" | "xxd" => { dispatch_ax_tool(&args[1..]); return; }
        "strings-scan" | "strings" => { dispatch_ax_tool(&args[1..]); return; }
        "shadow-audit" | "passwd-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "usb-audit" | "usb" => { dispatch_ax_tool(&args[1..]); return; }
        "dmesg-watch" | "klog" => { dispatch_ax_tool(&args[1..]); return; }
        "net-neighbors" | "neigh" | "arp-table" => { dispatch_ax_tool(&args[1..]); return; }
        "nft-rules" | "firewall-rules" => { dispatch_ax_tool(&args[1..]); return; }
        "syscall-trace" | "strace" => { dispatch_ax_tool(&args[1..]); return; }
        "open-files" | "lsof" => { dispatch_ax_tool(&args[1..]); return; }
        "container-escape" | "escape-check" => { dispatch_ax_tool(&args[1..]); return; }
        "port-knock" | "knock" => { dispatch_ax_tool(&args[1..]); return; }
        "mem-regions" | "memmap" => { dispatch_ax_tool(&args[1..]); return; }

        // Deep Core Root & Kernel Hardening (v2.9.0)
        "kmod-audit" | "lkm-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "deleted-procs" | "ghost-procs" => { dispatch_ax_tool(&args[1..]); return; }
        "cap-audit" | "capabilities" => { dispatch_ax_tool(&args[1..]); return; }
        "ebpf-audit" | "bpf-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "root-persistence" | "persistence" => { dispatch_ax_tool(&args[1..]); return; }
        "seccomp-audit" | "seccomp" => { dispatch_ax_tool(&args[1..]); return; }
        "tty-snoop" | "tiocsti-check" => { dispatch_ax_tool(&args[1..]); return; }
        "kexec-lockdown" | "lockdown-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "mem-protect" | "cpu-mitigations" => { dispatch_ax_tool(&args[1..]); return; }
        "mount-hardening" | "mount-audit" => { dispatch_ax_tool(&args[1..]); return; }
        "ipc-audit" | "ipcs-check" => { dispatch_ax_tool(&args[1..]); return; }
        "dmesg-exploit" | "kernel-corruption" => { dispatch_ax_tool(&args[1..]); return; }
        "root-jail" | "unshare-jail" => { dispatch_ax_tool(&args[1..]); return; }
        "core-dump-audit" | "coredump" => { dispatch_ax_tool(&args[1..]); return; }

        // Omni-Dispatcher Fallback: dynamically executes any OS tool via ax
        _ => {
            if !first_arg.is_empty() && !first_arg.starts_with("--") {
                dispatch_ax_tool(&args[1..]);
                return;
            }
        }
    }

    let fast = args.iter().any(|a| a == "--fast");
    let skip = args.iter().any(|a| a == "--skip");
    let menu_only = args.iter().any(|a| a == "--menu");
    let boot_only = args.iter().any(|a| a == "--boot-only");

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
        menu_item("11", "🤖", "11. Discord Cloud Vault Bridge", "Sync backups, loot & task alerts");
        menu_item("12", "🌐", "12. Web Operations Portal", "Launch localhost:7777 media & HUD portal");
        menu_item("13", "🪟", "13. Quad-Grid Tmux Studio", "4-way synchronized terminal workspace");
        menu_item("14", "⚡", "14. Hardware & Resource HUD", "Btop, Htop, CPU & Memory Telemetry");
        menu_item("15", "💻", "15. Superuser Shell Prompt", "Drop into enhanced cyber Zsh/Bash");
        menu_item("16", "🔄", "16. System Maintenance & Update", "ax update, ax upgrade, ax doctor, ax clean");
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
            "11" => {
                let discord_script = if Path::new("/etc/asterix/ui-core/asterix-discord.sh").exists() {
                    "/etc/asterix/ui-core/asterix-discord.sh"
                } else {
                    "ui-core/asterix-discord.sh"
                };
                let _ = Command::new(discord_script).status();
                pause_for_user();
            }
            "12" => {
                let portal_script = if Path::new("/etc/asterix/ui-core/asterix-web-portal.sh").exists() {
                    "/etc/asterix/ui-core/asterix-web-portal.sh"
                } else {
                    "ui-core/asterix-web-portal.sh"
                };
                let _ = Command::new(portal_script).status();
            }
            "13" => launch_quad_grid(),
            "14" => {
                let monitor = if Command::new("btop").stdout(Stdio::null()).spawn().is_ok() {
                    "btop"
                } else if Command::new("htop").stdout(Stdio::null()).spawn().is_ok() {
                    "htop"
                } else {
                    "top"
                };
                execute_command(monitor, &[]);
            }
            "15" => {
                let shell = env::var("SHELL").unwrap_or_else(|_| "/bin/bash".to_string());
                println!("\n{C_GREEN}[*] Spawning ASTERIX Interactive Superuser Shell (type 'exit' to return)...{C_RESET}");
                let _ = Command::new(shell).status();
            }
            "16" => sub_menu_maintenance(),
            "0" | "exit" | "quit" | "q" => {
                println!("\n{C_RED}[*] Terminating ASTERIX Control Center... Goodbye.{C_RESET}\n");
                break;
            }
            _ => {}
        }
    }
}
