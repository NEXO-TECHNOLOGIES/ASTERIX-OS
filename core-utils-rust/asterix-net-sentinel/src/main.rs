//! =====================================================================
//! ASTERIX OS - Pure Rust Network Sentinel & Port Telemetry Engine
//! Concurrency: High-Velocity Thread Pool Architecture
//! Zero External Dependencies - 100% Safe Native Rust
//! =====================================================================

use std::env;
use std::io::{Read, Write};
use std::net::{Ipv4Addr, SocketAddr, TcpStream, ToSocketAddrs};
use std::sync::mpsc::{self, Receiver, Sender};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

#[allow(dead_code)]
const C_RESET: &str = "\x1b[0m";
#[allow(dead_code)]
const C_BOLD: &str = "\x1b[1m";
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
const C_WHITE: &str = "\x1b[38;5;231m";
#[allow(dead_code)]
const C_GRAY: &str = "\x1b[38;5;240m";

const BANNER: &str = r#"
 ╔═══════════════════════════════════════════════════════════════════════════╗
 ║  █████╗ ███████╗  ███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗       ║
 ║ ██╔══██╗██╔════╝  ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║       ║
 ║ ███████║███████╗  ███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║       ║
 ║ ██╔══██║╚════██║  ╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║       ║
 ║ ██║  ██║███████║  ███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║       ║
 ║ ╚═╝  ╚═╝╚══════╝  ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝       ║
 ║           >> NETWORK SENTINEL & SERVICE PROBE ENGINE <<                   ║
 ╚═══════════════════════════════════════════════════════════════════════════╝"#;

const TOP_20_PORTS: &[u16] = &[
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080
];

const TOP_100_PORTS: &[u16] = &[
    7, 9, 13, 21, 22, 23, 25, 26, 37, 53, 79, 80, 81, 88, 106, 110, 111, 113, 119, 135,
    139, 143, 144, 179, 199, 389, 427, 443, 444, 445, 465, 513, 514, 515, 543, 544, 548,
    554, 587, 631, 646, 873, 990, 993, 995, 1025, 1026, 1027, 1028, 1029, 1110, 1433,
    1720, 1723, 1755, 1900, 2000, 2001, 2049, 2121, 2717, 3000, 3128, 3306, 3389, 3986,
    4899, 5000, 5009, 5051, 5060, 5101, 5190, 5357, 5432, 5631, 5666, 5800, 5900, 6000,
    6001, 6646, 7070, 8000, 8008, 8080, 8081, 8443, 8888, 9000, 9090, 9100, 9999, 10000,
    32768, 49152, 49153, 49154, 49155, 49156
];

#[derive(Debug, Clone)]
pub struct PortResult {
    pub port: u16,
    pub is_open: bool,
    pub service: &'static str,
    pub latency_ms: f64,
    pub banner: String,
}

fn resolve_service(port: u16) -> &'static str {
    match port {
        20 | 21 => "FTP",
        22 => "SSH",
        23 => "Telnet",
        25 => "SMTP",
        53 => "DNS",
        80 => "HTTP",
        110 => "POP3",
        111 => "RPCBind",
        123 => "NTP",
        135 => "MSRPC",
        139 | 445 => "SMB/NetBIOS",
        143 => "IMAP",
        389 => "LDAP",
        443 => "HTTPS",
        465 => "SMTPS",
        587 => "Submission",
        636 => "LDAPS",
        993 => "IMAPS",
        995 => "POP3S",
        1433 => "MSSQL",
        1521 => "Oracle DB",
        2049 => "NFS",
        3000 => "Node/React Dev",
        3306 => "MySQL/MariaDB",
        3389 => "RDP",
        5000 => "Flask/Docker Registry",
        5432 => "PostgreSQL",
        5900 => "VNC",
        6379 => "Redis",
        8000 => "HTTP-Alt / Dev",
        8080 => "HTTP-Proxy / Tomcat",
        8443 => "HTTPS-Alt",
        8888 => "HTTP-Admin / Jupyter",
        9000 => "PHP-FPM / Sonar",
        9092 => "Kafka",
        9200 => "Elasticsearch",
        27017 => "MongoDB",
        _ => "Unknown",
    }
}

fn grab_banner(target: &str, port: u16, timeout: Duration) -> String {
    let addr_str = format!("{}:{}", target, port);
    let socket_addrs: Vec<SocketAddr> = match addr_str.to_socket_addrs() {
        Ok(addrs) => addrs.collect(),
        Err(_) => return String::new(),
    };

    if let Some(&addr) = socket_addrs.first() {
        if let Ok(mut stream) = TcpStream::connect_timeout(&addr, timeout) {
            let _ = stream.set_read_timeout(Some(Duration::from_millis(600)));
            let _ = stream.set_write_timeout(Some(Duration::from_millis(600)));

            // If it's a web port, send a polite HTTP HEAD request
            if port == 80 || port == 8080 || port == 3000 || port == 5000 || port == 8000 {
                let _ = stream.write_all(b"HEAD / HTTP/1.0\r\nUser-Agent: AsterixSentinel/1.0\r\n\r\n");
            }

            let mut buf = [0u8; 512];
            if let Ok(n) = stream.read(&mut buf) {
                if n > 0 {
                    let banner = String::from_utf8_lossy(&buf[..n])
                        .lines()
                        .next()
                        .unwrap_or("")
                        .trim()
                        .to_string();
                    return banner;
                }
            }
        }
    }
    String::new()
}

fn scan_single_port(target: &str, port: u16, timeout: Duration, grab: bool) -> Option<PortResult> {
    let addr_str = format!("{}:{}", target, port);
    let socket_addrs: Vec<SocketAddr> = addr_str.to_socket_addrs().ok()?.collect();

    for &addr in &socket_addrs {
        let start = Instant::now();
        if let Ok(_stream) = TcpStream::connect_timeout(&addr, timeout) {
            let latency_ms = start.elapsed().as_secs_f64() * 1000.0;
            let service = resolve_service(port);
            let mut banner = String::new();
            if grab {
                banner = grab_banner(target, port, timeout);
            }

            return Some(PortResult {
                port,
                is_open: true,
                service,
                latency_ms,
                banner,
            });
        }
    }
    None
}

fn scan_ports_concurrent(
    target: String,
    ports: Vec<u16>,
    threads: usize,
    timeout: Duration,
    grab: bool,
) -> Vec<PortResult> {
    let (tx, rx): (Sender<PortResult>, Receiver<PortResult>) = mpsc::channel();
    let target_arc = Arc::new(target);
    let chunk_size = (ports.len() + threads - 1) / threads;

    let mut handles = Vec::new();

    for chunk in ports.chunks(chunk_size) {
        let chunk_vec = chunk.to_vec();
        let target_clone = Arc::clone(&target_arc);
        let thread_tx = tx.clone();

        let handle = thread::spawn(move || {
            for port in chunk_vec {
                if let Some(res) = scan_single_port(&target_clone, port, timeout, grab) {
                    let _ = thread_tx.send(res);
                }
            }
        });
        handles.push(handle);
    }

    drop(tx); // Close original transmitter so rx terminates when threads complete

    let mut results = Vec::new();
    while let Ok(res) = rx.recv() {
        results.push(res);
    }

    for h in handles {
        let _ = h.join();
    }

    results.sort_by_key(|r| r.port);
    results
}

fn measure_latency_jitter(target: &str, port: u16, count: usize) {
    println!("{C_CYAN}{C_BOLD} 📶 MEASURING SOCKET RTT & JITTER TO {}:{}{C_RESET}", target, port);
    println!("{C_GRAY}{}{C_RESET}", "─".repeat(60));

    let addr_str = format!("{}:{}", target, port);
    let socket_addrs: Vec<SocketAddr> = match addr_str.to_socket_addrs() {
        Ok(a) => a.collect(),
        Err(e) => {
            println!("{C_RED}[!] Failed to resolve target: {}{C_RESET}", e);
            return;
        }
    };

    let target_addr = match socket_addrs.first() {
        Some(a) => *a,
        None => return,
    };

    let mut latencies: Vec<f64> = Vec::with_capacity(count);

    for i in 1..=count {
        let start = Instant::now();
        match TcpStream::connect_timeout(&target_addr, Duration::from_millis(1500)) {
            Ok(_) => {
                let ms = start.elapsed().as_secs_f64() * 1000.0;
                println!("  Probe #{:02}: {C_GREEN}CONNECTED{C_RESET} in {C_YELLOW}{:.2} ms{C_RESET}", i, ms);
                latencies.push(ms);
            }
            Err(e) => {
                println!("  Probe #{:02}: {C_RED}FAILED{C_RESET} ({})", i, e);
            }
        }
        thread::sleep(Duration::from_millis(150));
    }

    if !latencies.is_empty() {
        let min = latencies.iter().cloned().fold(f64::INFINITY, f64::min);
        let max = latencies.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        let sum: f64 = latencies.iter().sum();
        let avg = sum / latencies.len() as f64;

        let mut diffs: Vec<f64> = Vec::new();
        for w in latencies.windows(2) {
            diffs.push((w[1] - w[0]).abs());
        }
        let jitter = if !diffs.is_empty() {
            diffs.iter().sum::<f64>() / diffs.len() as f64
        } else {
            0.0
        };

        println!("{C_GRAY}{}{C_RESET}", "─".repeat(60));
        println!("  {C_WHITE}Probes Sent:{C_RESET} {}  |  {C_GREEN}Success:{C_RESET} {}", count, latencies.len());
        println!("  {C_CYAN}Min RTT:{C_RESET} {:.2} ms  |  {C_CYAN}Avg RTT:{C_RESET} {:.2} ms  |  {C_CYAN}Max RTT:{C_RESET} {:.2} ms", min, avg, max);
        println!("  {C_YELLOW}Jitter:{C_RESET}  {:.2} ms", jitter);
    }
    println!();
}

fn calculate_subnet(ip_str: &str, mask_bits: u8) {
    println!("{C_CYAN}{C_BOLD} 🌐 ASTERIX CIDR SUBNET CALCULATOR{C_RESET}");
    println!("{C_GRAY}{}{C_RESET}", "─".repeat(60));

    let ip: Ipv4Addr = match ip_str.parse() {
        Ok(ip) => ip,
        Err(_) => {
            println!("{C_RED}[!] Invalid IPv4 address: {}{C_RESET}", ip_str);
            return;
        }
    };

    if mask_bits > 32 {
        println!("{C_RED}[!] Mask bits must be 0-32{C_RESET}");
        return;
    }

    let ip_u32 = u32::from(ip);
    let mask_u32 = if mask_bits == 0 { 0 } else { !0u32 << (32 - mask_bits) };
    let net_u32 = ip_u32 & mask_u32;
    let bcast_u32 = net_u32 | !mask_u32;

    let net_ip = Ipv4Addr::from(net_u32);
    let mask_ip = Ipv4Addr::from(mask_u32);
    let bcast_ip = Ipv4Addr::from(bcast_u32);
    let total_hosts = if mask_bits >= 31 {
        (1 << (32 - mask_bits)) as u64
    } else {
        ((1u64 << (32 - mask_bits)) - 2).max(1)
    };

    println!("  {C_WHITE}Input IP:{C_RESET}         {C_YELLOW}{ip}{C_RESET} /{mask_bits}");
    println!("  {C_WHITE}Subnet Mask:{C_RESET}      {C_CYAN}{mask_ip}{C_RESET}");
    println!("  {C_WHITE}Network Address:{C_RESET}  {C_GREEN}{net_ip}{C_RESET}");
    println!("  {C_WHITE}Broadcast IP:{C_RESET}     {C_MAGENTA}{bcast_ip}{C_RESET}");
    println!("  {C_WHITE}Usable Range:{C_RESET}     {C_CYAN}{} - {}{C_RESET}",
        Ipv4Addr::from(net_u32 + 1),
        Ipv4Addr::from(bcast_u32 - 1)
    );
    println!("  {C_WHITE}Usable Hosts:{C_RESET}     {C_GREEN}{total_hosts}{C_RESET}");
    println!("{C_GRAY}{}{C_RESET}\n", "─".repeat(60));
}

fn print_help() {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!(r#"
USAGE:
    asterix-net-sentinel [TARGET] [OPTIONS]

ARGUMENTS:
    <TARGET>                Host IP, domain name (e.g. 127.0.0.1, localhost)

PORT OPTIONS:
    -p, --ports <PORTS>     Ports to probe:
                            • top20     - Top 20 critical services (Default)
                            • top100   - Top 100 common ports
                            • 1-1024    - Port range
                            • 80,443,22 - Comma-separated list
    -t, --threads <NUM>     Concurrent scanning threads (Default: 50)
    -w, --timeout <MS>      Connection timeout in milliseconds (Default: 400)
    -b, --banner            Enable banner grabbing on open ports

DIAGNOSTIC MODES:
    --ping <TARGET>         Measure TCP socket RTT latency & jitter
    --subnet <IP/MASK>      Calculate IPv4 CIDR subnet metrics (e.g. 192.168.1.50/24)
    -j, --json              Output results in structured JSON format
    -h, --help              Print this help manual

EXAMPLES:
    asterix-net-sentinel 127.0.0.1 --ports top20
    asterix-net-sentinel 192.168.1.1 -p 1-1000 -t 100 --banner
    asterix-net-sentinel --ping 1.1.1.1
    asterix-net-sentinel --subnet 10.0.0.1/22
"#);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 || args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
        print_help();
        return;
    }

    if args.contains(&"--version".to_string()) || args.contains(&"-v".to_string()) {
        println!("{C_CYAN}asterix-net-sentinel v1.0.0 (ASTERIX OS Cyber Suite){C_RESET}");
        return;
    }

    let mut target: Option<String> = None;
    let mut port_spec = "top20".to_string();
    let mut threads = 50usize;
    let mut timeout_ms = 400u64;
    let mut grab_banners = false;
    let mut json_mode = false;
    let mut ping_target: Option<String> = None;
    let mut subnet_input: Option<String> = None;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-p" | "--ports" => {
                i += 1;
                if i < args.len() { port_spec = args[i].clone(); }
            }
            "-t" | "--threads" => {
                i += 1;
                if i < args.len() { threads = args[i].parse().unwrap_or(50); }
            }
            "-w" | "--timeout" => {
                i += 1;
                if i < args.len() { timeout_ms = args[i].parse().unwrap_or(400); }
            }
            "-b" | "--banner" => grab_banners = true,
            "-j" | "--json" => json_mode = true,
            "--ping" => {
                i += 1;
                if i < args.len() { ping_target = Some(args[i].clone()); }
            }
            "--subnet" => {
                i += 1;
                if i < args.len() { subnet_input = Some(args[i].clone()); }
            }
            arg if !arg.starts_with('-') && target.is_none() => {
                target = Some(arg.to_string());
            }
            _ => {}
        }
        i += 1;
    }

    if let Some(sub) = subnet_input {
        let parts: Vec<&str> = sub.split('/').collect();
        if parts.len() == 2 {
            let mask = parts[1].parse::<u8>().unwrap_or(24);
            calculate_subnet(parts[0], mask);
        } else {
            calculate_subnet(&sub, 24);
        }
        return;
    }

    if let Some(pt) = ping_target {
        measure_latency_jitter(&pt, 80, 5);
        return;
    }

    let host = match target {
        Some(h) => h,
        None => {
            eprintln!("{C_RED}[!] Error: Target host not specified.{C_RESET}");
            print_help();
            return;
        }
    };

    let ports_to_scan: Vec<u16> = if port_spec == "top20" {
        TOP_20_PORTS.to_vec()
    } else if port_spec == "top100" {
        TOP_100_PORTS.to_vec()
    } else if port_spec.contains('-') {
        let parts: Vec<&str> = port_spec.split('-').collect();
        let start: u16 = parts.get(0).and_then(|p| p.parse().ok()).unwrap_or(1);
        let end: u16 = parts.get(1).and_then(|p| p.parse().ok()).unwrap_or(1024);
        (start..=end).collect()
    } else {
        port_spec.split(',')
            .filter_map(|p| p.trim().parse::<u16>().ok())
            .collect()
    };

    if ports_to_scan.is_empty() {
        eprintln!("{C_RED}[!] Error: No valid ports specified to scan.{C_RESET}");
        return;
    }

    if !json_mode {
        println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
        println!("{C_BLUE}{}{C_RESET}", "═".repeat(78));
        println!(" {C_WHITE}{C_BOLD}TARGET HOST:{C_RESET}     {C_YELLOW}{host}{C_RESET}");
        println!(" {C_WHITE}Ports To Probe:{C_RESET}  {C_CYAN}{} ports{C_RESET} ({})", ports_to_scan.len(), port_spec);
        println!(" {C_WHITE}Concurrency:{C_RESET}     {C_GREEN}{} threads{C_RESET} | {C_WHITE}Timeout:{C_RESET} {C_YELLOW}{} ms{C_RESET}", threads, timeout_ms);
        println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));
        println!("  {C_CYAN}[*] Initiating high-velocity sentinel sweep...{C_RESET}\n");
    }

    let start_time = Instant::now();
    let timeout = Duration::from_millis(timeout_ms);
    let open_ports = scan_ports_concurrent(host.clone(), ports_to_scan.clone(), threads, timeout, grab_banners);
    let duration = start_time.elapsed();

    if json_mode {
        print!("{{\"target\":\"{}\",\"ports_scanned\":{},\"duration_ms\":{:.2},\"open_ports\":[",
            host, ports_to_scan.len(), duration.as_secs_f64() * 1000.0);
        for (idx, p) in open_ports.iter().enumerate() {
            if idx > 0 { print!(","); }
            print!("{{\"port\":{},\"service\":\"{}\",\"latency_ms\":{:.2},\"banner\":\"{}\"}}",
                p.port, p.service, p.latency_ms, p.banner.replace('"', "\\\""));
        }
        println!("]}}");
        return;
    }

    if open_ports.is_empty() {
        println!("  {C_YELLOW}[!] No open ports detected among {} probed targets.{C_RESET}", ports_to_scan.len());
    } else {
        println!("  {C_GRAY}{:<8} {:<10} {:<18} {:<12} {}{C_RESET}",
            "PORT", "STATE", "SERVICE", "LATENCY", "BANNER / IDENT");
        println!("  {C_GRAY}{}{C_RESET}", "─".repeat(74));

        for p in &open_ports {
            let banner_display = if p.banner.is_empty() {
                format!("{C_GRAY}[No Banner]{C_RESET}")
            } else {
                format!("{C_WHITE}{}{C_RESET}", p.banner)
            };

            println!("  {C_GREEN}{:<8}{C_RESET} {C_CYAN}{:<10}{C_RESET} {C_YELLOW}{:<18}{C_RESET} {C_WHITE}{:<12.2} ms{C_RESET} {}",
                p.port, "OPEN", p.service, p.latency_ms, banner_display);
        }
    }

    println!("\n{C_BLUE}{}{C_RESET}", "═".repeat(78));
    println!(" {C_GREEN}✔ Scan Completed:{C_RESET} {C_WHITE}{} open ports found{C_RESET} in {C_CYAN}{:.2}s{C_RESET}",
        open_ports.len(), duration.as_secs_f64());
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));
}
