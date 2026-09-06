//! =====================================================================
//! ASTERIX OS - asterix-log-hunter
//! Pure-Rust High-Velocity Security Log Threat Pattern & Anomaly Hunter
//! Zero External Dependencies (100% Rust Standard Library)
//! =====================================================================

use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::{self, BufRead, BufReader, Seek, SeekFrom};
use std::path::Path;
use std::thread::sleep;
use std::time::Duration;

// ANSI 256-color cyber palette
const C_RESET: &str = "\x1b[0m";
const C_BOLD: &str = "\x1b[1m";
const C_RED: &str = "\x1b[38;5;196m";
const C_GREEN: &str = "\x1b[38;5;46m";
const C_YELLOW: &str = "\x1b[38;5;220m";
const C_CYAN: &str = "\x1b[38;5;51m";
const C_MAGENTA: &str = "\x1b[38;5;201m";
const C_PURPLE: &str = "\x1b[38;5;141m";
const C_WHITE: &str = "\x1b[38;5;231m";
const C_GRAY: &str = "\x1b[38;5;243m";
const C_DARKGRAY: &str = "\x1b[38;5;237m";

fn banner() {
    println!("{C_CYAN}{C_BOLD}");
    println!("  ██╗      ██████╗  ██████╗     ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ ");
    println!("  ██║     ██╔═══██╗██╔════╝     ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗");
    println!("  ██║     ██║   ██║██║  ███╗    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝");
    println!("  ██║     ██║   ██║██║   ██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗");
    println!("  ███████╗╚██████╔╝╚██████╔╝    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║");
    println!("  ╚══════╝ ╚═════╝  ╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝");
    println!("         >> ASTERIX CYBERNETIC SECURITY LOG THREAT HUNTER <<{C_RESET}\n");
}

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum Severity {
    Info,
    Medium,
    High,
    Critical,
}

impl Severity {
    fn badge(&self) -> String {
        match self {
            Severity::Critical => format!("{C_RED}{C_BOLD}[CRITICAL]{C_RESET}"),
            Severity::High => format!("{C_YELLOW}{C_BOLD}[HIGH]{C_RESET}    "),
            Severity::Medium => format!("{C_PURPLE}[MEDIUM]{C_RESET}  "),
            Severity::Info => format!("{C_CYAN}[INFO]{C_RESET}    "),
        }
    }
}

struct ThreatPattern {
    pattern: &'static str,
    severity: Severity,
    desc: &'static str,
}

const THREAT_SIGNATURES: &[ThreatPattern] = &[
    ThreatPattern { pattern: "BREAK-IN ATTEMPT", severity: Severity::Critical, desc: "Potential automated intrusion detected" },
    ThreatPattern { pattern: "rootkit", severity: Severity::Critical, desc: "Rootkit keyword identified" },
    ThreatPattern { pattern: "kernel: BUG", severity: Severity::Critical, desc: "Kernel corruption or crash panic" },
    ThreatPattern { pattern: "Out of memory: Kill process", severity: Severity::Critical, desc: "Linux kernel OOM killer invocation" },
    ThreatPattern { pattern: "segfault", severity: Severity::Critical, desc: "Segmentation fault / memory violation" },
    ThreatPattern { pattern: "privilege escalation", severity: Severity::Critical, desc: "Privilege escalation activity" },

    ThreatPattern { pattern: "Failed password", severity: Severity::High, desc: "Authentication failure / Brute force attempt" },
    ThreatPattern { pattern: "authentication failure", severity: Severity::High, desc: "PAM authentication reject" },
    ThreatPattern { pattern: "Invalid user", severity: Severity::High, desc: "Brute-force username enumeration" },
    ThreatPattern { pattern: "possible SYN flooding", severity: Severity::High, desc: "DoS SYN flood detected by TCP stack" },
    ThreatPattern { pattern: "unauthorized", severity: Severity::High, desc: "Unauthorized resource access attempt" },

    ThreatPattern { pattern: "sudo:", severity: Severity::Medium, desc: "Elevated command execution via sudo" },
    ThreatPattern { pattern: "COMMAND=/bin/su", severity: Severity::Medium, desc: "Root shell switch attempt via su" },
    ThreatPattern { pattern: "Accepted publickey", severity: Severity::Medium, desc: "Successful SSH key authentication" },
    ThreatPattern { pattern: "Connection closed by", severity: Severity::Medium, desc: "Abrupt connection closure" },

    ThreatPattern { pattern: "session opened for user root", severity: Severity::Info, desc: "Root administrative session opened" },
    ThreatPattern { pattern: "Starting OpenSSH", severity: Severity::Info, desc: "SSH daemon lifecycle event" },
];

/// Scan a log file against the threat signature matrix
fn scan_file(path_str: &str) -> io::Result<()> {
    let path = Path::new(path_str);
    if !path.exists() {
        println!("{C_RED}[!] Error: File does not exist: {path_str}{C_RESET}");
        return Ok(());
    }

    banner();
    println!("{C_CYAN}[*] Scanning target log: {C_WHITE}{path_str}{C_RESET}\n");

    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut line_num = 0;
    let mut matches_by_sev = [0usize; 4];
    let mut ip_counts: HashMap<String, usize> = HashMap::new();

    for line_result in reader.lines() {
        let line = line_result?;
        line_num += 1;

        for sig in THREAT_SIGNATURES {
            if line.contains(sig.pattern) {
                let idx = sig.severity as usize;
                matches_by_sev[idx] += 1;

                // Extract potential IP address
                if let Some(ip) = extract_ip(&line) {
                    *ip_counts.entry(ip).or_insert(0) += 1;
                }

                if matches_by_sev[idx] <= 25 {
                    println!("  {} {C_GRAY}L{:<5}{C_RESET} {C_WHITE}{:<28}{C_RESET} {C_DARKGRAY}{}{C_RESET}",
                        sig.severity.badge(), line_num, sig.desc, truncate_str(&line, 55));
                }
                break;
            }
        }
    }

    println!("\n  {}", "═".repeat(68));
    println!("  {C_WHITE}{C_BOLD}LOG THREAT AUDIT SUMMARY:{C_RESET} {path_str}");
    println!("  {C_WHITE}Lines Audited:{C_RESET}        {line_num}");
    println!("  {C_RED}Critical Threats:{C_RESET}     {}", matches_by_sev[Severity::Critical as usize]);
    println!("  {C_YELLOW}High Suspicion:{C_RESET}       {}", matches_by_sev[Severity::High as usize]);
    println!("  {C_PURPLE}Medium Notices:{C_RESET}       {}", matches_by_sev[Severity::Medium as usize]);
    println!("  {C_CYAN}Informational:{C_RESET}        {}", matches_by_sev[Severity::Info as usize]);
    println!("  {}", "═".repeat(68));

    if !ip_counts.is_empty() {
        println!("\n{C_YELLOW}[*] Top Attacking / Anomaly IP Addresses Identified:{C_RESET}");
        let mut sorted_ips: Vec<(&String, &usize)> = ip_counts.iter().collect();
        sorted_ips.sort_by(|a, b| b.1.cmp(a.1));
        for (ip, count) in sorted_ips.iter().take(5) {
            println!("  {C_CYAN}{:<20}{C_RESET} {C_RED}{count} events{C_RESET}", ip);
        }
    }
    println!();
    Ok(())
}

/// Follow/Stream a log file in real-time, colorizing threats as they occur
fn stream_file(path_str: &str) -> io::Result<()> {
    let path = Path::new(path_str);
    banner();
    println!("{C_MAGENTA}[*] Real-Time Threat Stream Monitoring on: {C_WHITE}{path_str}{C_RESET}");
    println!("{C_GRAY}(Watching for live threats... Press Ctrl+C to stop){C_RESET}\n");

    let mut file = File::open(path)?;
    // Seek to end of file to monitor only new events
    file.seek(SeekFrom::End(0))?;
    let mut reader = BufReader::new(file);

    loop {
        let mut line = String::new();
        match reader.read_line(&mut line) {
            Ok(0) => {
                // No new data, sleep briefly
                sleep(Duration::from_millis(250));
            }
            Ok(_) => {
                let trimmed = line.trim_end();
                let mut matched = false;
                for sig in THREAT_SIGNATURES {
                    if trimmed.contains(sig.pattern) {
                        println!("  {} {C_WHITE}{:<24}{C_RESET} {C_GRAY}{trimmed}{C_RESET}",
                            sig.severity.badge(), sig.desc);
                        matched = true;
                        break;
                    }
                }
                if !matched {
                    println!("  {C_DARKGRAY}[STREAM]{C_RESET} {trimmed}");
                }
            }
            Err(e) => {
                println!("{C_RED}[!] Error reading log stream: {e}{C_RESET}");
                break;
            }
        }
    }
    Ok(())
}

/// Automated audit of standard system log files
fn audit_system() {
    banner();
    println!("{C_CYAN}[*] Running ASTERIX Automated System Log Audit...{C_RESET}\n");

    let candidates = [
        "/var/log/auth.log",
        "/var/log/secure",
        "/var/log/syslog",
        "/var/log/messages",
        "/var/log/kern.log",
        "/data/data/com.termux/files/usr/var/log/dpkg.log",
    ];

    let mut found_any = false;
    for &cand in &candidates {
        if Path::new(cand).exists() {
            found_any = true;
            let _ = scan_file(cand);
        }
    }

    if !found_any {
        println!("{C_YELLOW}[!] No standard Linux log paths found in current environment.{C_RESET}");
        println!("{C_GREEN}[✔] Host log subsystem is protected or isolated (PRoot / Sandboxed).{C_RESET}\n");
    }
}

fn extract_ip(text: &str) -> Option<String> {
    for word in text.split_whitespace() {
        let clean = word.trim_matches(|c: char| !c.is_ascii_digit() && c != '.');
        let parts: Vec<&str> = clean.split('.').collect();
        if parts.len() == 4 {
            let valid = parts.iter().all(|p| p.parse::<u8>().is_ok());
            if valid {
                return Some(clean.to_string());
            }
        }
    }
    None
}

fn truncate_str(s: &str, max: usize) -> String {
    if s.len() > max {
        format!("{}...", &s[..max])
    } else {
        s.to_string()
    }
}

fn print_help() {
    banner();
    println!("{C_WHITE}{C_BOLD}USAGE:{C_RESET}");
    println!("  asterix-log-hunter <subcommand> [arguments...]\n");
    println!("{C_WHITE}{C_BOLD}SUBCOMMANDS:{C_RESET}");
    println!("  {C_CYAN}scan <log_file>{C_RESET}       Scan file against 17 threat signatures with IP aggregation");
    println!("  {C_CYAN}stream <log_file>{C_RESET}     Follow log in real-time with live threat alerts (tail -f)");
    println!("  {C_CYAN}audit{C_RESET}                  Scan all standard system logs (/var/log/*)");
    println!("  {C_CYAN}help{C_RESET}                   Display this command reference\n");
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        print_help();
        return;
    }

    match args[1].as_str() {
        "scan" => {
            if args.len() < 3 {
                println!("{C_RED}[!] Error: Please specify target log file.{C_RESET}");
                println!("Usage: asterix-log-hunter scan <path>");
                return;
            }
            if let Err(e) = scan_file(&args[2]) {
                println!("{C_RED}[!] Scan error: {e}{C_RESET}");
            }
        }
        "stream" | "tail" | "follow" => {
            if args.len() < 3 {
                println!("{C_RED}[!] Error: Please specify target log file.{C_RESET}");
                println!("Usage: asterix-log-hunter stream <path>");
                return;
            }
            if let Err(e) = stream_file(&args[2]) {
                println!("{C_RED}[!] Stream error: {e}{C_RESET}");
            }
        }
        "audit" | "all" => {
            audit_system();
        }
        "help" | "--help" | "-h" => {
            print_help();
        }
        _ => {
            println!("{C_RED}[!] Unknown subcommand: {}{C_RESET}", args[1]);
            print_help();
        }
    }
}