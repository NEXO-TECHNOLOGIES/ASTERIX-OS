//! =====================================================================
//! ASTERIX OS - Pure Rust Binary Inspection & Disassembly Forensics Engine
//! Supports: ELF (Linux), PE (Windows), Mach-O (macOS), Raw Binaries
//! Zero External Dependencies - 100% Standalone Memory-Safe Rust
//! =====================================================================

use std::env;
use std::fs::File;
use std::io::{self, Read};
use std::path::Path;

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
 ║  █████╗ ███████╗  ██████╗ ██╗███╗   ██╗      ██████╗ ███████╗             ║
 ║ ██╔══██╗██╔════╝  ██╔══██╗██║████╗  ██║     ██╔═══██╗██╔════╝             ║
 ║ ███████║███████╗  ██████╔╝██║██╔██╗ ██║     ██║   ██║███████╗             ║
 ║ ██╔══██║╚════██║  ██╔══██╗██║██║╚██╗██║     ██║   ██║╚════██║             ║
 ║ ██║  ██║███████║  ██████╔╝██║██║ ╚████║     ╚██████╔╝███████║             ║
 ║ ╚═╝  ╚═╝╚══════╝  ╚═════╝ ╚═╝╚═╝  ╚═══╝      ╚═════╝ ╚══════╝             ║
 ║           >> BINARY INSPECTOR & FORENSIC DISASM ENGINE <<                 ║
 ╚═══════════════════════════════════════════════════════════════════════════╝"#;

#[derive(Debug, Clone)]
pub struct SectionInfo {
    pub name: String,
    pub offset: u64,
    pub size: u64,
    pub vaddr: u64,
    pub entropy: f64,
    pub is_executable: bool,
    pub is_writable: bool,
}

#[derive(Debug, Default)]
pub struct BinaryReport {
    pub file_name: String,
    pub file_size: u64,
    pub format: String,
    pub arch: String,
    pub bitness: String,
    pub endianness: String,
    pub os_abi: String,
    pub file_type: String,
    pub entry_point: u64,
    pub overall_entropy: f64,
    pub sections: Vec<SectionInfo>,
    pub suspicious_flags: Vec<String>,
}

fn calculate_entropy(data: &[u8]) -> f64 {
    if data.is_empty() {
        return 0.0;
    }
    let mut counts = [0usize; 256];
    for &b in data {
        counts[b as usize] += 1;
    }
    let len_f = data.len() as f64;
    let mut entropy = 0.0;
    for &count in &counts {
        if count > 0 {
            let p = count as f64 / len_f;
            entropy -= p * p.log2();
        }
    }
    entropy
}

fn read_u16_le(buf: &[u8]) -> u16 {
    u16::from_le_bytes([buf[0], buf[1]])
}

fn read_u32_le(buf: &[u8]) -> u32 {
    u32::from_le_bytes([buf[0], buf[1], buf[2], buf[3]])
}

fn read_u64_le(buf: &[u8]) -> u64 {
    u64::from_le_bytes([
        buf[0], buf[1], buf[2], buf[3],
        buf[4], buf[5], buf[6], buf[7],
    ])
}

fn read_u16_be(buf: &[u8]) -> u16 {
    u16::from_be_bytes([buf[0], buf[1]])
}

fn read_u32_be(buf: &[u8]) -> u32 {
    u32::from_be_bytes([buf[0], buf[1], buf[2], buf[3]])
}

fn read_u64_be(buf: &[u8]) -> u64 {
    u64::from_be_bytes([
        buf[0], buf[1], buf[2], buf[3],
        buf[4], buf[5], buf[6], buf[7],
    ])
}

fn parse_elf(data: &[u8], report: &mut BinaryReport) {
    if data.len() < 52 {
        report.format = "Malformed ELF (Too short)".to_string();
        return;
    }

    report.format = "ELF (Executable and Linkable Format)".to_string();
    let is_64 = data[4] == 2;
    report.bitness = if is_64 { "64-bit".to_string() } else { "32-bit".to_string() };

    let is_le = data[5] == 1;
    report.endianness = if is_le { "Little-Endian".to_string() } else { "Big-Endian".to_string() };

    report.os_abi = match data[7] {
        0 => "System V (Default UNIX)",
        1 => "HP-UX",
        2 => "NetBSD",
        3 => "Linux",
        6 => "Solaris",
        9 => "FreeBSD",
        12 => "OpenBSD",
        _ => "Custom/Embedded ABI",
    }.to_string();

    let e_type = if is_le { read_u16_le(&data[16..18]) } else { read_u16_be(&data[16..18]) };
    report.file_type = match e_type {
        1 => "Relocatable Object (.o)",
        2 => "Executable Binary",
        3 => "Shared Object / PIE Executable (.so)",
        4 => "Core Dump",
        _ => "Unknown ELF Type",
    }.to_string();

    let e_machine = if is_le { read_u16_le(&data[18..20]) } else { read_u16_be(&data[18..20]) };
    report.arch = match e_machine {
        0x03 => "x86 (Intel 80386)",
        0x28 => "ARM (32-bit)",
        0x3E => "x86_64 (AMD64)",
        0xB7 => "AArch64 (ARM 64-bit)",
        0xF3 => "RISC-V",
        0x08 => "MIPS",
        0x14 => "PowerPC",
        _ => "Other / Embedded Architecture",
    }.to_string();

    if is_64 {
        if data.len() >= 64 {
            let entry = if is_le { read_u64_le(&data[24..32]) } else { read_u64_be(&data[24..32]) };
            report.entry_point = entry;
            let shoff = if is_le { read_u64_le(&data[40..48]) } else { read_u64_be(&data[40..48]) };
            let shentsize = (if is_le { read_u16_le(&data[58..60]) } else { read_u16_be(&data[58..60]) }) as usize;
            let shnum = (if is_le { read_u16_le(&data[60..62]) } else { read_u16_be(&data[60..62]) }) as usize;
            let shstrndx = (if is_le { read_u16_le(&data[62..64]) } else { read_u16_be(&data[62..64]) }) as usize;

            if shnum > 0 && shentsize >= 64 && shstrndx < shnum {
                let strtab_hdr_offset = (shoff as usize).saturating_add(shstrndx * shentsize);
                if strtab_hdr_offset + 64 <= data.len() {
                    let str_sec = &data[strtab_hdr_offset..];
                    let str_offset = (if is_le { read_u64_le(&str_sec[24..32]) } else { read_u64_be(&str_sec[24..32]) }) as usize;
                    let str_size = (if is_le { read_u64_le(&str_sec[32..40]) } else { read_u64_be(&str_sec[32..40]) }) as usize;

                    if str_offset + str_size <= data.len() {
                        let string_table = &data[str_offset..str_offset + str_size];

                        for i in 0..shnum {
                            let sec_hdr_off = (shoff as usize).saturating_add(i * shentsize);
                            if sec_hdr_off + 64 > data.len() {
                                break;
                            }
                            let s = &data[sec_hdr_off..];
                            let name_idx = (if is_le { read_u32_le(&s[0..4]) } else { read_u32_be(&s[0..4]) }) as usize;
                            let flags = if is_le { read_u64_le(&s[8..16]) } else { read_u64_be(&s[8..16]) };
                            let addr = if is_le { read_u64_le(&s[16..24]) } else { read_u64_be(&s[16..24]) };
                            let offset = if is_le { read_u64_le(&s[24..32]) } else { read_u64_be(&s[24..32]) };
                            let size = if is_le { read_u64_le(&s[32..40]) } else { read_u64_be(&s[32..40]) };

                            let mut sec_name = String::new();
                            if name_idx < string_table.len() {
                                let slice = &string_table[name_idx..];
                                if let Some(end) = slice.iter().position(|&b| b == 0) {
                                    sec_name = String::from_utf8_lossy(&slice[..end]).to_string();
                                }
                            }
                            if sec_name.is_empty() {
                                sec_name = format!("sec_{}", i);
                            }

                            let mut sec_entropy = 0.0;
                            let off_us = offset as usize;
                            let sz_us = size as usize;
                            if off_us < data.len() && sz_us > 0 {
                                let end_us = (off_us + sz_us).min(data.len());
                                sec_entropy = calculate_entropy(&data[off_us..end_us]);
                            }

                            let is_exec = (flags & 0x4) != 0;
                            let is_write = (flags & 0x1) != 0;

                            if is_exec && is_write {
                                report.suspicious_flags.push(format!("W+X Section found: '{}' is both Writable and Executable!", sec_name));
                            }
                            if sec_entropy > 7.3 && sz_us > 1024 {
                                report.suspicious_flags.push(format!("High entropy section '{}' ({:.2}) indicates packing or encryption.", sec_name, sec_entropy));
                            }

                            report.sections.push(SectionInfo {
                                name: sec_name,
                                offset,
                                size,
                                vaddr: addr,
                                entropy: sec_entropy,
                                is_executable: is_exec,
                                is_writable: is_write,
                            });
                        }
                    }
                }
            }
        }
    } else if data.len() >= 52 {
        let entry = (if is_le { read_u32_le(&data[24..28]) } else { read_u32_be(&data[24..28]) }) as u64;
        report.entry_point = entry;
    }
}

fn parse_pe(data: &[u8], report: &mut BinaryReport) {
    if data.len() < 64 {
        report.format = "Malformed PE (Too short)".to_string();
        return;
    }

    report.format = "PE (Portable Executable - Windows)".to_string();
    let pe_offset = read_u32_le(&data[0x3C..0x40]) as usize;

    if pe_offset + 24 > data.len() || &data[pe_offset..pe_offset + 4] != b"PE\0\0" {
        report.format = "MS-DOS Legacy Executable (No PE Header)".to_string();
        return;
    }

    let file_header = &data[pe_offset + 4..];
    let machine = read_u16_le(&file_header[0..2]);
    let num_sections = read_u16_le(&file_header[2..4]) as usize;
    let opt_hdr_size = read_u16_le(&file_header[16..18]) as usize;
    let characteristics = read_u16_le(&file_header[18..20]);

    report.endianness = "Little-Endian".to_string();
    report.arch = match machine {
        0x014C => "x86 (i386)",
        0x8664 => "x86_64 (AMD64)",
        0xAA64 => "ARM64 (AArch64)",
        0x01C0 => "ARM",
        _ => "Unknown Machine",
    }.to_string();

    report.file_type = if (characteristics & 0x2000) != 0 {
        "Dynamic Link Library (DLL)"
    } else {
        "Application Executable (.exe)"
    }.to_string();

    if opt_hdr_size > 0 && pe_offset + 24 + opt_hdr_size <= data.len() {
        let opt_hdr = &data[pe_offset + 24..];
        let magic = read_u16_le(&opt_hdr[0..2]);
        if magic == 0x20B {
            report.bitness = "64-bit (PE32+)".to_string();
            report.entry_point = read_u32_le(&opt_hdr[16..20]) as u64;
        } else if magic == 0x10B {
            report.bitness = "32-bit (PE32)".to_string();
            report.entry_point = read_u32_le(&opt_hdr[16..20]) as u64;
        }
    }

    let sec_table_start = pe_offset + 24 + opt_hdr_size;
    for i in 0..num_sections {
        let sec_offset = sec_table_start + i * 40;
        if sec_offset + 40 > data.len() {
            break;
        }
        let sec_bytes = &data[sec_offset..sec_offset + 40];
        let name_raw = &sec_bytes[0..8];
        let name_end = name_raw.iter().position(|&b| b == 0).unwrap_or(8);
        let sec_name = String::from_utf8_lossy(&name_raw[..name_end]).trim().to_string();

        let virt_size = read_u32_le(&sec_bytes[8..12]) as u64;
        let virt_addr = read_u32_le(&sec_bytes[12..16]) as u64;
        let raw_size = read_u32_le(&sec_bytes[16..20]) as u64;
        let raw_ptr = read_u32_le(&sec_bytes[20..24]) as usize;
        let chars = read_u32_le(&sec_bytes[36..40]);

        let mut sec_entropy = 0.0;
        if raw_ptr < data.len() && raw_size > 0 {
            let end = (raw_ptr + raw_size as usize).min(data.len());
            sec_entropy = calculate_entropy(&data[raw_ptr..end]);
        }

        let is_exec = (chars & 0x20000000) != 0;
        let is_write = (chars & 0x80000000) != 0;

        if is_exec && is_write {
            report.suspicious_flags.push(format!("PE Section '{}' is Writable and Executable (W+X)!", sec_name));
        }
        if sec_entropy > 7.3 && raw_size > 1024 {
            report.suspicious_flags.push(format!("PE Section '{}' has high entropy ({:.2}) — potential packing/cryptor.", sec_name, sec_entropy));
        }

        report.sections.push(SectionInfo {
            name: sec_name,
            offset: raw_ptr as u64,
            size: if raw_size > 0 { raw_size } else { virt_size },
            vaddr: virt_addr,
            entropy: sec_entropy,
            is_executable: is_exec,
            is_writable: is_write,
        });
    }
}

fn parse_macho(data: &[u8], report: &mut BinaryReport) {
    report.format = "Mach-O (Apple Darwin / macOS / iOS)".to_string();
    if data.len() < 8 {
        return;
    }
    let magic = read_u32_le(&data[0..4]);
    let (is_64, is_le) = match magic {
        0xFEEDFACE => (false, true),
        0xFEEDFACF => (true, true),
        0xCEFAEDFE => (false, false),
        0xCFFAEDFE => (true, false),
        _ => (true, true),
    };
    report.bitness = if is_64 { "64-bit".to_string() } else { "32-bit".to_string() };
    report.endianness = if is_le { "Little-Endian".to_string() } else { "Big-Endian".to_string() };

    let cputype = if is_le { read_u32_le(&data[4..8]) } else { read_u32_be(&data[4..8]) };
    report.arch = match cputype {
        7 => "x86",
        0x01000007 => "x86_64",
        12 => "ARM",
        0x0100000C => "ARM64 (Apple Silicon)",
        _ => "Mach-O Architecture",
    }.to_string();
    report.file_type = "Mach-O Executable / Dynamic Library".to_string();
}

fn inspect_binary(path: &Path) -> io::Result<BinaryReport> {
    let mut file = File::open(path)?;
    let mut buffer = Vec::new();
    file.read_to_end(&mut buffer)?;

    let mut report = BinaryReport::default();
    report.file_name = path.file_name().unwrap_or_default().to_string_lossy().to_string();
    report.file_size = buffer.len() as u64;
    report.overall_entropy = calculate_entropy(&buffer);

    if buffer.starts_with(b"AXCIPH02") {
        report.format = "ASTERIX Encrypted Binary Container (AXCIPH02)".to_string();
        report.file_type = "512-bit ARX Authenticated Cryptographic Volume".to_string();
        report.bitness = "64-bit Assembly/Rust Binary Container".to_string();
        report.arch = "Cross-Platform (x86_64 / ARM64)".to_string();
        if buffer.len() >= 64 {
            let kdf_rounds = read_u32_le(&buffer[36..40]);
            let payload_size = read_u64_le(&buffer[40..48]);
            report.suspicious_flags.push(format!("Encrypted Binary Container detected. KDF: {} rounds, Payload: {} bytes. Decrypt with: 'ax cipher dec <file> <out> <pass>'", kdf_rounds, payload_size));
        }
    } else if buffer.starts_with(b"\x7fELF") {
        parse_elf(&buffer, &mut report);
    } else if buffer.starts_with(b"MZ") {
        parse_pe(&buffer, &mut report);
    } else if buffer.len() >= 4 && (
        &buffer[0..4] == b"\xFE\xED\xFA\xCE" ||
        &buffer[0..4] == b"\xFE\xED\xFA\xCF" ||
        &buffer[0..4] == b"\xCE\xFA\xED\xFE" ||
        &buffer[0..4] == b"\xCF\xFA\xED\xFE"
    ) {
        parse_macho(&buffer, &mut report);
    } else if buffer.starts_with(b"#!") {
        report.format = "Script (Interpreted / Shebang)".to_string();
        let end = buffer.iter().position(|&b| b == b'\n').unwrap_or(buffer.len().min(80));
        report.file_type = String::from_utf8_lossy(&buffer[..end]).trim().to_string();
        report.bitness = "Script / Text".to_string();
        report.arch = "Platform Independent".to_string();
    } else {
        report.format = "Raw Binary / Data Blob".to_string();
        report.bitness = "Unknown".to_string();
        report.arch = "Raw Data".to_string();
    }

    if report.overall_entropy > 7.5 {
        report.suspicious_flags.push(format!("Extremely high overall entropy ({:.2}/8.0). File is likely compressed, encrypted, or packed.", report.overall_entropy));
    }

    Ok(report)
}

fn extract_strings(data: &[u8], min_len: usize) -> Vec<(usize, String)> {
    let mut results = Vec::new();
    let mut current = Vec::new();
    let mut start_offset = 0;

    for (i, &b) in data.iter().enumerate() {
        if b.is_ascii_graphic() || b == b' ' || b == b'\t' {
            if current.is_empty() {
                start_offset = i;
            }
            current.push(b);
        } else {
            if current.len() >= min_len {
                if let Ok(s) = String::from_utf8(current.clone()) {
                    results.push((start_offset, s));
                }
            }
            current.clear();
        }
    }
    if current.len() >= min_len {
        if let Ok(s) = String::from_utf8(current) {
            results.push((start_offset, s));
        }
    }
    results
}

fn render_hex_view(data: &[u8], start_offset: usize, length: usize) {
    let end = (start_offset + length).min(data.len());
    let slice = &data[start_offset..end];

    println!("{C_BLUE}Offset (h)   00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  Decoded Text{C_RESET}");
    println!("{C_GRAY}{}{C_RESET}", "─".repeat(76));

    for (row_idx, chunk) in slice.chunks(16).enumerate() {
        let cur_offset = start_offset + row_idx * 16;
        print!("{C_CYAN}{:08X}   {C_RESET}", cur_offset);

        // Hex representation
        for i in 0..16 {
            if i == 8 {
                print!(" ");
            }
            if i < chunk.len() {
                let b = chunk[i];
                if b == 0 {
                    print!("{C_GRAY}00 {C_RESET}");
                } else if b.is_ascii_graphic() {
                    print!("{C_GREEN}{:02X} {C_RESET}", b);
                } else if b > 127 {
                    print!("{C_ORANGE}{:02X} {C_RESET}", b);
                } else {
                    print!("{C_WHITE}{:02X} {C_RESET}", b);
                }
            } else {
                print!("   ");
            }
        }

        print!(" {C_GRAY}|{C_RESET}");
        // ASCII representation
        for &b in chunk {
            if b.is_ascii_graphic() || b == b' ' {
                print!("{C_WHITE}{}{C_RESET}", b as char);
            } else {
                print!("{C_GRAY}.{C_RESET}");
            }
        }
        println!("{C_GRAY}|{C_RESET}");
    }
}

fn print_report(report: &BinaryReport) {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!("{C_BLUE}{}{C_RESET}", "═".repeat(78));
    println!(" {C_WHITE}{C_BOLD}TARGET BINARY:{C_RESET} {C_YELLOW}{}{C_RESET} ({C_WHITE}{:.2} KB{C_RESET} / {C_WHITE}{} bytes{C_RESET})",
        report.file_name,
        report.file_size as f64 / 1024.0,
        report.file_size
    );
    println!("{C_BLUE}{}{C_RESET}", "═".repeat(78));

    println!(" {C_CYAN}► Format:{C_RESET}       {C_WHITE}{}{C_RESET}", report.format);
    println!(" {C_CYAN}► Architecture:{C_RESET} {C_GREEN}{}{C_RESET} [{C_YELLOW}{}{C_RESET}]", report.arch, report.bitness);
    println!(" {C_CYAN}► Endianness:{C_RESET}   {C_WHITE}{}{C_RESET}", report.endianness);
    if !report.os_abi.is_empty() {
        println!(" {C_CYAN}► OS / ABI:{C_RESET}     {C_WHITE}{}{C_RESET}", report.os_abi);
    }
    println!(" {C_CYAN}► File Type:{C_RESET}    {C_WHITE}{}{C_RESET}", report.file_type);
    println!(" {C_CYAN}► Entry Point:{C_RESET}  {C_MAGENTA}0x{:016X}{C_RESET}", report.entry_point);

    let entropy_color = if report.overall_entropy > 7.2 {
        C_RED
    } else if report.overall_entropy > 6.0 {
        C_YELLOW
    } else {
        C_GREEN
    };
    println!(" {C_CYAN}► Shannon Entropy:{C_RESET} {entropy_color}{:.4} / 8.0000{C_RESET}", report.overall_entropy);

    if !report.suspicious_flags.is_empty() {
        println!("\n{C_RED}{C_BOLD} ⚠ SECURITY & PACKING ALERTS:{C_RESET}");
        for flag in &report.suspicious_flags {
            println!("  {C_RED}✖{C_RESET} {C_YELLOW}{flag}{C_RESET}");
        }
    }

    if !report.sections.is_empty() {
        println!("\n{C_CYAN}{C_BOLD} 📁 SECTION BREAKDOWN & ENTROPY MAP:{C_RESET}");
        println!("  {C_GRAY}{:<18} {:<14} {:<12} {:<10} {:<8} {}{C_RESET}",
            "NAME", "V-ADDR", "SIZE", "ENTROPY", "FLAGS", "STATUS");
        println!("  {C_GRAY}{}{C_RESET}", "─".repeat(74));

        for sec in &report.sections {
            let ent_col = if sec.entropy > 7.2 {
                C_RED
            } else if sec.entropy > 6.0 {
                C_YELLOW
            } else {
                C_GREEN
            };

            let mut flags = String::new();
            if sec.is_executable { flags.push('X'); }
            if sec.is_writable { flags.push('W'); }
            if flags.is_empty() { flags = "R".to_string(); }

            let status = if sec.entropy > 7.2 {
                format!("{C_RED}[PACKED/CRYPT]{C_RESET}")
            } else if sec.is_executable && sec.is_writable {
                format!("{C_RED}[W+X RISK]{C_RESET}")
            } else {
                format!("{C_GREEN}[NORMAL]{C_RESET}")
            };

            println!("  {C_WHITE}{:<18}{C_RESET} {C_MAGENTA}0x{:010X}{C_RESET} {C_WHITE}{:<12}{C_RESET} {ent_col}{:<10.3}{C_RESET} {C_YELLOW}{:<8}{C_RESET} {}",
                sec.name, sec.vaddr, sec.size, sec.entropy, flags, status);
        }
    }
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));
}

fn print_json_report(report: &BinaryReport) {
    print!("{{\"file_name\":\"{}\",\"file_size\":{},\"format\":\"{}\",\"arch\":\"{}\",\"bitness\":\"{}\",\"entry_point\":{},\"entropy\":{:.4},\"sections\":[",
        report.file_name, report.file_size, report.format, report.arch, report.bitness, report.entry_point, report.overall_entropy);
    for (i, sec) in report.sections.iter().enumerate() {
        if i > 0 { print!(","); }
        print!("{{\"name\":\"{}\",\"vaddr\":{},\"size\":{},\"entropy\":{:.4},\"executable\":{},\"writable\":{}}}",
            sec.name, sec.vaddr, sec.size, sec.entropy, sec.is_executable, sec.is_writable);
    }
    println!("]}}");
}

fn print_help() {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!(r#"
USAGE:
    asterix-bin-inspector <FILE> [OPTIONS]

ARGUMENTS:
    <FILE>                  Path to target ELF, PE, Mach-O or raw binary

OPTIONS:
    -a, --all               Run comprehensive binary inspection & analysis (Default)
    -H, --header            Inspect and decode binary headers only
    -S, --sections          Display section table and calculate Shannon entropy
    -s, --strings           Extract and filter forensic cyber strings (URLs, IPs, keys)
        --min-len <N>       Minimum string length for extraction (Default: 4)
    -x, --hex               Display colorized hexadecimal dump
        --offset <HEX/DEC>  Hex dump starting byte offset (Default: 0)
        --len <N>           Hex dump byte count (Default: 256)
    -j, --json              Output machine-readable JSON format
    -h, --help              Print this help manual
    -v, --version           Print version information

EXAMPLES:
    asterix-bin-inspector /bin/ls
    asterix-bin-inspector sample.exe --sections
    asterix-bin-inspector payload.bin --hex --offset 0x100 --len 128
    asterix-bin-inspector target.so --strings --min-len 6
"#);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 || args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
        print_help();
        return;
    }

    if args.contains(&"--version".to_string()) || args.contains(&"-v".to_string()) {
        println!("{C_CYAN}asterix-bin-inspector v1.0.0 (ASTERIX OS Cyber Suite){C_RESET}");
        return;
    }

    let mut target_file: Option<String> = None;
    let mut show_header = false;
    let mut show_sections = false;
    let mut show_strings = false;
    let mut show_hex = false;
    let mut json_mode = false;
    let mut min_str_len = 4usize;
    let mut hex_offset = 0usize;
    let mut hex_len = 256usize;

    let mut i = 1;
    while i < args.len() {
        match args[i].as_str() {
            "-a" | "--all" => {
                show_header = true;
                show_sections = true;
            }
            "-H" | "--header" => show_header = true,
            "-S" | "--sections" => show_sections = true,
            "-s" | "--strings" => show_strings = true,
            "-x" | "--hex" => show_hex = true,
            "-j" | "--json" => json_mode = true,
            "--min-len" => {
                i += 1;
                if i < args.len() {
                    min_str_len = args[i].parse().unwrap_or(4);
                }
            }
            "--offset" => {
                i += 1;
                if i < args.len() {
                    let s = &args[i];
                    if s.starts_with("0x") || s.starts_with("0X") {
                        hex_offset = usize::from_str_radix(&s[2..], 16).unwrap_or(0);
                    } else {
                        hex_offset = s.parse().unwrap_or(0);
                    }
                }
            }
            "--len" => {
                i += 1;
                if i < args.len() {
                    hex_len = args[i].parse().unwrap_or(256);
                }
            }
            arg if !arg.starts_with('-') && target_file.is_none() => {
                target_file = Some(arg.to_string());
            }
            _ => {}
        }
        i += 1;
    }

    let file_path = match target_file {
        Some(f) => f,
        None => {
            eprintln!("{C_RED}[!] Error: Target file not specified.{C_RESET}");
            print_help();
            return;
        }
    };

    let path = Path::new(&file_path);
    if !path.exists() {
        eprintln!("{C_RED}[!] Error: File '{}' not found.{C_RESET}", file_path);
        return;
    }

    let report = match inspect_binary(path) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("{C_RED}[!] Error reading file: {}{C_RESET}", e);
            return;
        }
    };

    if json_mode {
        print_json_report(&report);
        return;
    }

    if !show_header && !show_sections && !show_strings && !show_hex {
        print_report(&report);
        return;
    }

    if show_header || show_sections {
        print_report(&report);
    }

    if show_strings {
        println!("{C_CYAN}{C_BOLD} 🔤 FORENSIC STRINGS EXTRACTION (Min Length: {}):{C_RESET}", min_str_len);
        if let Ok(mut file) = File::open(path) {
            let mut buf = Vec::new();
            if file.read_to_end(&mut buf).is_ok() {
                let strings = extract_strings(&buf, min_str_len);
                println!("  Found {} extractable strings:\n", strings.len());
                let mut shown = 0;
                for (offset, s) in &strings {
                    let is_url = s.starts_with("http://") || s.starts_with("https://");
                    let is_path = s.starts_with('/') || (s.len() > 3 && s.chars().nth(1) == Some(':'));
                    let is_sensitive = s.to_lowercase().contains("password") ||
                                       s.to_lowercase().contains("token") ||
                                       s.to_lowercase().contains("secret") ||
                                       s.to_lowercase().contains("key");

                    let color = if is_url {
                        C_MAGENTA
                    } else if is_sensitive {
                        C_RED
                    } else if is_path {
                        C_YELLOW
                    } else {
                        C_WHITE
                    };

                    println!("  {C_CYAN}0x{:08X}:{C_RESET} {color}{}{C_RESET}", offset, s);
                    shown += 1;
                    if shown >= 100 && strings.len() > 100 {
                        println!("  {C_GRAY}... [Truncated: showing first 100 of {} strings] ...{C_RESET}", strings.len());
                        break;
                    }
                }
            }
        }
        println!();
    }

    if show_hex {
        println!("{C_CYAN}{C_BOLD} 🔍 COLORIZED HEXADECIMAL DUMP (Offset: 0x{:X}, Length: {} bytes):{C_RESET}", hex_offset, hex_len);
        if let Ok(mut file) = File::open(path) {
            let mut buf = Vec::new();
            if file.read_to_end(&mut buf).is_ok() {
                render_hex_view(&buf, hex_offset, hex_len);
            }
        }
        println!();
    }
}
