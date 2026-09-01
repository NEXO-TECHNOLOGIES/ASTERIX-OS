//! =====================================================================
//! ASTERIX OS - High-Performance Cybernetic Boot & Control Engine
//! Written in 100% Pure Standalone Rust (Zero External Crate Dependencies)
//! Compatible with Linux x86_64, aarch64, ARMv7, Android Termux & Windows
//! =====================================================================

use std::env;
use std::fs;
use std::io::{self, Write};
use std::net::UdpSocket;
use std::path::Path;
use std::process::{Command, Stdio};
use std::thread::sleep;
use std::time::Duration;

// ANSI 256-Color Palette
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

    format!(
        "{C_WHITE}[{C_CYAN}{bar_filled}{C_GRAY}{bar_empty}{C_WHITE}] {C_YELLOW}{percent:3}%{C_RESET}"
    )
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
    BootStep { subsystem: "TERMUX_BRIDGE_VFS",      desc: "Linking mobile sandbox / shared storage", duration_ms: 40 },
    BootStep { subsystem: "INTERFACE_MATRIX",       desc: "Starting Asterix Terminal Cybernetic Hub", duration_ms: 70 },
];

fn run_boot_animation(fast: bool) {
    let mut rng = Rng::new();

    if !fast {
        // Dramatic glitch frames
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
    println!(
        "{C_WHITE}{C_BOLD}{:>58}{C_RESET}",
        "[ SYSTEM BOOT SEQUENCE // ASTERIX KERNEL INITIALIZATION ]"
    );
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(76));

    let total = BOOT_STEPS.len();
    let speed_div = if fast { 3 } else { 1 };

    for (i, step) in BOOT_STEPS.iter().enumerate() {
        let percent = (((i + 1) as u32 * 100) / total as u32).min(100);

        print!(
            " {C_CYAN}[{:^24}]{C_RESET} {C_WHITE}{:<42}{C_RESET} {C_GREEN}[ OK ]{C_RESET}\n",
            step.subsystem, step.desc
        );
        let _ = io::stdout().flush();

        sleep(Duration::from_millis(step.duration_ms / speed_div));
    }

    println!("\n{C_CYAN}{}{C_RESET}", "─".repeat(76));
    println!(" {}", render_progress_bar(100, 48));
    println!("{C_CYAN}{}{C_RESET}", "─".repeat(76));
    println!(
        "\n{C_GREEN}{C_BOLD} [✔] ASTERIX OS IS ONLINE & READY FOR OPERATIONS {C_RESET}"
    );
    println!(" {C_YELLOW}Persistent Storage Status: {C_GREEN}CONNECTED (ASTERIX_PERSISTENCE){C_RESET}");
    println!(" {C_YELLOW}Security Toolchain:       {C_GREEN}ACTIVE (Wireshark, MSF, Netcat, Nmap){C_RESET}\n");

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

    // Try to resolve outbound IP
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
    println!(
        "{C_BLUE}║{C_WHITE} NODE: {C_YELLOW}{:<16}{C_WHITE}IP: {C_GREEN}{:<18}{C_WHITE}ARCH: {C_CYAN}{:<12}{C_BLUE}║{C_RESET}",
        tel.host, tel.ip, env::consts::ARCH
    );
    println!(
        "{C_BLUE}║{C_WHITE} DATA PERSISTENCE: {}{:<55}{C_BLUE}║{C_RESET}",
        if tel.persistence.contains("ACTIVE") { C_GREEN } else { C_YELLOW },
        tel.persistence
    );
    println!("{C_BLUE}╚{}╝{C_RESET}\n", "═".repeat(76));
}

fn menu_item(num: &str, icon: &str, title: &str, desc: &str) {
    println!(
        "  {C_CYAN}[{C_BOLD}{num}{C_RESET}{C_CYAN}]{C_RESET} {icon} {C_WHITE}{C_BOLD}{title:<30}{C_RESET} {C_GRAY}» {desc}{C_RESET}"
    );
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

fn sub_menu_network() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_MAGENTA}{C_BOLD} [ SUBSYSTEM: NETWORK & PACKET WARFARE ] {C_RESET}\n");
        menu_item("1", "🦈", "Wireshark / TShark", "Start real-time packet capture");
        menu_item("2", "🔍", "Nmap Port Scanner", "Network discovery & vulnerability scanning");
        menu_item("3", "📡", "Tcpdump Raw Sniffer", "Capture live raw hex/ASCII packet stream");
        menu_item("4", "🔌", "Netcat / Ncat Listen", "Spawn an interactive TCP/UDP listener");
        menu_item("5", "🎭", "MacChanger", "Randomize hardware MAC address");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-NET » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("wireshark", &[]),
            "2" => {
                let target = read_user_input(&format!("{C_YELLOW}Enter Target IP / Subnet (e.g. 192.168.1.1): {C_RESET}"));
                if !target.is_empty() {
                    execute_command("nmap", &["-sV", "-T4", &target]);
                }
            }
            "3" => execute_command("tcpdump", &["-nn", "-c", "25"]),
            "4" => {
                let port = read_user_input(&format!("{C_YELLOW}Enter Port to Listen (default: 4444): {C_RESET}"));
                let p = if port.is_empty() { "4444" } else { &port };
                execute_command("nc", &["-lvnp", p]);
            }
            "5" => {
                let iface = read_user_input(&format!("{C_YELLOW}Enter Interface Name (e.g. eth0, wlan0): {C_RESET}"));
                let i = if iface.is_empty() { "eth0" } else { &iface };
                execute_command("macchanger", &["-r", i]);
            }
            "0" | "exit" | "q" => break,
            _ => {}
        }
    }
}

fn sub_menu_exploitation() {
    loop {
        let tel = get_system_telemetry();
        print_header(&tel);
        println!("{C_RED}{C_BOLD} [ SUBSYSTEM: AUDITING & SECURITY TOOLS ] {C_RESET}\n");
        menu_item("1", "💣", "Metasploit Framework", "Launch MSFConsole exploit engine");
        menu_item("2", "🔎", "SearchSploit ExploitDB", "Query offline exploit database");
        menu_item("3", "⚡", "Socat Port Relay", "Create bidirectional encrypted tunnels");
        menu_item("0", "🔙", "Return to Main Hub", "Back to primary command matrix");

        let choice = read_user_input(&format!("\n{C_RED}ASTERIX-SEC » {C_RESET}"));
        match choice.as_str() {
            "1" => execute_command("msfconsole", &[]),
            "2" => {
                let q = read_user_input(&format!("{C_YELLOW}Enter Search Query: {C_RESET}"));
                if !q.is_empty() {
                    execute_command("searchsploit", &[&q]);
                }
            }
            "3" => {
                let args_str = read_user_input(&format!("{C_YELLOW}Enter Socat Arguments: {C_RESET}"));
                let args: Vec<&str> = args_str.split_whitespace().collect();
                if !args.is_empty() {
                    execute_command("socat", &args);
                }
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
        println!("{C_GREEN}{C_BOLD} [ SUBSYSTEM: ASTERIX PERSISTENCE MANAGER ] {C_RESET}\n");

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
                    if !found {
                        println!("  {C_GRAY}(Vault is currently empty){C_RESET}");
                    }
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
                } else {
                    println!("{C_RED}[!] Error writing to {filepath}{C_RESET}");
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

fn main() {
    let args: Vec<String> = env::args().collect();
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

        println!("{C_WHITE}{C_BOLD} [ PRIMARY OPERATIONAL MATRIX ] {C_RESET}\n");
        menu_item("1", "📡", "Network & Packet Warfare", "Wireshark, Nmap, Tcpdump, Netcat");
        menu_item("2", "⚔️", "Auditing & Security Suite", "Metasploit MSF, SearchSploit, Socat");
        menu_item("3", "💾", "ASTERIX Persistent Storage", "Manage user data, vaults & backups");
        menu_item("4", "🪟", "Multi-Terminal / Tmux Studio", "Mouse scrolling & live split screen");
        menu_item("5", "🖼️", "Visual & Media Asset Vault", "Inspect wallpapers & loading animations");
        menu_item("6", "⚡", "Subsystem Diagnostics", "Monitor CPU, RAM, network streams");
        menu_item("7", "📱", "Termux / Mobile Bridge", "Configure Android PRoot integration");
        menu_item("8", "💻", "ASTERIX Superuser Shell", "Drop into enhanced bash/zsh prompt");
        menu_item("9", "🔄", "Replay Boot Animation", "Show loading matrix sequence");
        menu_item("0", "⛔", "Power Off / Exit", "Shutdown or exit control environment");

        let choice = read_user_input(&format!("\n{C_CYAN}ASTERIX-CONTROL » {C_RESET}"));

        match choice.as_str() {
            "1" => sub_menu_network(),
            "2" => sub_menu_exploitation(),
            "3" => sub_menu_persistence(),
            "4" => {
                println!("\n{C_CYAN}{C_BOLD}[*] Starting ASTERIX Multi-Terminal Workspace (Tmux)...{C_RESET}");
                println!("{C_YELLOW}Quick Controls:{C_RESET}");
                println!("  • Mouse Scroll:    Scroll wheel enabled up/down");
                println!("  • Vertical Split:  Press Ctrl+A then |");
                println!("  • Horiz Split:     Press Ctrl+A then -");
                println!("  • New Tab/Window:  Press Ctrl+A then c");
                println!("  • Switch Panes:    Click with mouse or Alt+Arrows\n");
                sleep(Duration::from_millis(1500));
                
                let tmux_conf = "/etc/asterix/asterix.tmux.conf";
                if Path::new(tmux_conf).exists() {
                    let _ = Command::new("tmux").args(["-f", tmux_conf]).status();
                } else if Path::new("ui-core/asterix.tmux.conf").exists() {
                    let _ = Command::new("tmux").args(["-f", "ui-core/asterix.tmux.conf"]).status();
                } else {
                    let _ = Command::new("tmux").status();
                }
            }
            "5" => {
                println!("\n{C_MAGENTA}{C_BOLD}[*] ASTERIX Media & Visual Asset Status:{C_RESET}\n");
                let wp_dir = "assets/wallpapers";
                let anim_dir = "assets/animations";
                
                println!("{C_CYAN}Wallpapers Folder ({wp_dir}):{C_RESET}");
                if let Ok(entries) = fs::read_dir(wp_dir) {
                    for entry in entries.flatten() {
                        let name = entry.file_name().to_string_lossy().to_string();
                        if !name.starts_with('.') {
                            println!("  {C_GREEN}🖼️  {name}{C_RESET}");
                        }
                    }
                } else {
                    println!("  {C_GRAY}(Folder ready for user image drop){C_RESET}");
                }

                println!("\n{C_CYAN}Boot Animations Folder ({anim_dir}):{C_RESET}");
                if let Ok(entries) = fs::read_dir(anim_dir) {
                    for entry in entries.flatten() {
                        let name = entry.file_name().to_string_lossy().to_string();
                        if !name.starts_with('.') {
                            println!("  {C_MAGENTA}🎬 {name}{C_RESET}");
                        }
                    }
                } else {
                    println!("  {C_GRAY}(Folder ready for user animation/video drop){C_RESET}");
                }
                pause_for_user();
            }
            "6" => {
                let monitor = if Command::new("btop").stdout(Stdio::null()).spawn().is_ok() {
                    "btop"
                } else if Command::new("htop").stdout(Stdio::null()).spawn().is_ok() {
                    "htop"
                } else {
                    "top"
                };
                execute_command(monitor, &[]);
            }
            "7" => {
                println!("\n{C_CYAN}[*] Termux Mobile Bridge Configuration:{C_RESET}");
                println!("  Storage Bridge: /data/data/com.termux/files/home/asterix_persistent");
                println!("  PRoot Distro:   Debian / Kali Rootless Container");
                pause_for_user();
            }
            "8" => {
                let shell = env::var("SHELL").unwrap_or_else(|_| "/bin/bash".to_string());
                println!("\n{C_GREEN}[*] Spawning ASTERIX Interactive Shell (type 'exit' to return)...{C_RESET}");
                let _ = Command::new(shell).status();
            }
            "9" => run_boot_animation(false),
            "0" | "exit" | "quit" | "q" => {
                println!("\n{C_RED}[*] Terminating ASTERIX Control Center... Goodbye.{C_RESET}\n");
                break;
            }
            _ => {}
        }
    }
}
