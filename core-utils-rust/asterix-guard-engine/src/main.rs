//! =====================================================================
//! ASTERIX OS - Pure Rust Automated Security Hardening & Compliance Engine
//! Audits: Kernel security parameters, ASLR, kptr_restrict, dmesg_restrict,
//! filesystem permissions, UID-0 backdoors, and SSH configuration.
//! Zero External Dependencies - 100% Standalone Memory-Safe Rust
//! =====================================================================

use std::env;
use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::Path;

#[allow(dead_code)]
const C_RESET: &str = "\x1b[0m";
#[allow(dead_code)]
const C_BOLD: &str = "\x1b[1m";
#[allow(dead_code)]
const C_RED: &str = "\x1b[38;5;196m";
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
 ║  █████╗ ███████╗   ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗               ║
 ║ ██╔══██╗██╔════╝  ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗              ║
 ║ ███████║███████╗  ██║  ███╗██║   ██║███████║██████╔╝██║  ██║              ║
 ║ ██╔══██║╚════██║  ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║              ║
 ║ ██║  ██║███████║  ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝              ║
 ║ ╚═╝  ╚═╝╚══════╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝               ║
 ║           >> AUTOMATED SECURITY HARDENING & AUDIT ENGINE <<               ║
 ╚═══════════════════════════════════════════════════════════════════════════╝"#;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum AuditStatus {
    Pass,
    Warn,
    Fail,
    Info,
}

#[derive(Debug, Clone)]
pub struct AuditItem {
    pub category: &'static str,
    pub title: &'static str,
    pub current_value: String,
    pub expected_value: &'static str,
    pub status: AuditStatus,
    pub remediation: String,
}

fn read_file_trimmed<P: AsRef<Path>>(path: P) -> Option<String> {
    let mut file = File::open(path).ok()?;
    let mut s = String::new();
    file.read_to_string(&mut s).ok()?;
    Some(s.trim().to_string())
}

fn check_kernel_param(path: &'static str, expected: &'static str, name: &'static str, fix_cmd: &'static str) -> AuditItem {
    match read_file_trimmed(path) {
        Some(val) => {
            let status = if val == expected {
                AuditStatus::Pass
            } else {
                AuditStatus::Fail
            };
            AuditItem {
                category: "Kernel Protection",
                title: name,
                current_value: val,
                expected_value: expected,
                status,
                remediation: fix_cmd.to_string(),
            }
        }
        None => AuditItem {
            category: "Kernel Protection",
            title: name,
            current_value: "Not Supported / Container".to_string(),
            expected_value: expected,
            status: AuditStatus::Info,
            remediation: String::new(),
        },
    }
}

fn audit_kernel_protections() -> Vec<AuditItem> {
    vec![
        check_kernel_param(
            "/proc/sys/kernel/randomize_va_space",
            "2",
            "Address Space Layout Randomization (ASLR)",
            "sysctl -w kernel.randomize_va_space=2",
        ),
        check_kernel_param(
            "/proc/sys/kernel/kptr_restrict",
            "1",
            "Kernel Pointer Restriction (kptr_restrict)",
            "sysctl -w kernel.kptr_restrict=1",
        ),
        check_kernel_param(
            "/proc/sys/kernel/dmesg_restrict",
            "1",
            "Kernel Ring Buffer Log Access (dmesg_restrict)",
            "sysctl -w kernel.dmesg_restrict=1",
        ),
        check_kernel_param(
            "/proc/sys/kernel/yama/ptrace_scope",
            "1",
            "YAMA ptrace Scope (Cross-Process Debugging)",
            "sysctl -w kernel.yama.ptrace_scope=1",
        ),
        check_kernel_param(
            "/proc/sys/fs/protected_symlinks",
            "1",
            "Protected Symlink Following (fs.protected_symlinks)",
            "sysctl -w fs.protected_symlinks=1",
        ),
        check_kernel_param(
            "/proc/sys/fs/protected_hardlinks",
            "1",
            "Protected Hardlink Creation (fs.protected_hardlinks)",
            "sysctl -w fs.protected_hardlinks=1",
        ),
        check_kernel_param(
            "/proc/sys/fs/suid_dumpable",
            "0",
            "SUID Core Dump Disabled (fs.suid_dumpable)",
            "sysctl -w fs.suid_dumpable=0",
        ),
    ]
}

fn audit_user_accounts() -> Vec<AuditItem> {
    let mut items = Vec::new();
    let passwd_path = Path::new("/etc/passwd");

    if let Some(content) = read_file_trimmed(passwd_path) {
        let mut uid0_users = Vec::new();
        for line in content.lines() {
            let fields: Vec<&str> = line.split(':').collect();
            if fields.len() >= 3 {
                let username = fields[0];
                let uid = fields[2];
                if uid == "0" && username != "root" {
                    uid0_users.push(username.to_string());
                }
            }
        }

        if uid0_users.is_empty() {
            items.push(AuditItem {
                category: "User Authentication",
                title: "Root Privileged Accounts (UID 0)",
                current_value: "Only 'root' has UID 0".to_string(),
                expected_value: "Only 'root' has UID 0",
                status: AuditStatus::Pass,
                remediation: String::new(),
            });
        } else {
            items.push(AuditItem {
                category: "User Authentication",
                title: "Root Privileged Accounts (UID 0)",
                current_value: format!("Unauthorized UID-0 accounts: {:?}", uid0_users),
                expected_value: "Only 'root' has UID 0",
                status: AuditStatus::Fail,
                remediation: "Inspect and remove backdoored UID-0 accounts from /etc/passwd".to_string(),
            });
        }
    } else {
        items.push(AuditItem {
            category: "User Authentication",
            title: "/etc/passwd Audit",
            current_value: "Non-UNIX Environment".to_string(),
            expected_value: "File present",
            status: AuditStatus::Info,
            remediation: String::new(),
        });
    }

    items
}

fn audit_ssh_config() -> Vec<AuditItem> {
    let mut items = Vec::new();
    let sshd_paths = ["/etc/ssh/sshd_config", "/etc/ssh/sshd_config.d/00-asterix.conf"];
    let mut config_found = false;

    for path_str in &sshd_paths {
        if let Some(content) = read_file_trimmed(path_str) {
            config_found = true;
            let mut root_login = "yes (default)".to_string();
            let mut pass_auth = "yes (default)".to_string();
            let mut x11 = "no".to_string();

            for line in content.lines() {
                let trimmed = line.trim();
                if trimmed.starts_with('#') || trimmed.is_empty() {
                    continue;
                }
                let lower = trimmed.to_lowercase();
                if lower.starts_with("permitrootlogin ") {
                    root_login = trimmed.split_whitespace().nth(1).unwrap_or("").to_string();
                } else if lower.starts_with("passwordauthentication ") {
                    pass_auth = trimmed.split_whitespace().nth(1).unwrap_or("").to_string();
                } else if lower.starts_with("x11forwarding ") {
                    x11 = trimmed.split_whitespace().nth(1).unwrap_or("").to_string();
                }
            }

            let root_status = if root_login == "no" || root_login == "prohibit-password" {
                AuditStatus::Pass
            } else {
                AuditStatus::Warn
            };

            items.push(AuditItem {
                category: "SSH Daemon Hardening",
                title: "SSH Root Login Policy (PermitRootLogin)",
                current_value: root_login,
                expected_value: "no / prohibit-password",
                status: root_status,
                remediation: "Set 'PermitRootLogin no' in /etc/ssh/sshd_config".to_string(),
            });

            let pass_status = if pass_auth == "no" {
                AuditStatus::Pass
            } else {
                AuditStatus::Warn
            };

            items.push(AuditItem {
                category: "SSH Daemon Hardening",
                title: "SSH Password Authentication (PasswordAuthentication)",
                current_value: pass_auth,
                expected_value: "no (prefer SSH keys)",
                status: pass_status,
                remediation: "Set 'PasswordAuthentication no' and use Ed25519 SSH keys".to_string(),
            });

            let x11_status = if x11 == "no" {
                AuditStatus::Pass
            } else {
                AuditStatus::Warn
            };

            items.push(AuditItem {
                category: "SSH Daemon Hardening",
                title: "SSH X11 GUI Forwarding (X11Forwarding)",
                current_value: x11,
                expected_value: "no",
                status: x11_status,
                remediation: "Set 'X11Forwarding no' in /etc/ssh/sshd_config".to_string(),
            });
            break;
        }
    }

    if !config_found {
        items.push(AuditItem {
            category: "SSH Daemon Hardening",
            title: "OpenSSH Daemon Service",
            current_value: "No SSH server installed / inactive".to_string(),
            expected_value: "Not listening publicly",
            status: AuditStatus::Pass,
            remediation: String::new(),
        });
    }

    items
}

fn audit_filesystem_permissions() -> Vec<AuditItem> {
    let mut items = Vec::new();

    let shadow = Path::new("/etc/shadow");
    if shadow.exists() {
        if let Ok(_meta) = fs::metadata(shadow) {
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                let mode = _meta.permissions().mode() & 0o777;
                let status = if mode == 0o000 || mode == 0o640 || mode == 0o600 {
                    AuditStatus::Pass
                } else {
                    AuditStatus::Fail
                };
                items.push(AuditItem {
                    category: "Filesystem Permissions",
                    title: "/etc/shadow Permission Mask",
                    current_value: format!("{:04o}", mode),
                    expected_value: "0640 or 0000",
                    status,
                    remediation: "chmod 640 /etc/shadow && chown root:shadow /etc/shadow".to_string(),
                });
            }
            #[cfg(not(unix))]
            {
                items.push(AuditItem {
                    category: "Filesystem Permissions",
                    title: "/etc/shadow Permission Mask",
                    current_value: "File present (Non-UNIX filesystem)".to_string(),
                    expected_value: "Restricted",
                    status: AuditStatus::Pass,
                    remediation: String::new(),
                });
            }
        }
    }

    let sudoers = Path::new("/etc/sudoers");
    if sudoers.exists() {
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            if let Ok(meta) = fs::metadata(sudoers) {
                let mode = meta.permissions().mode() & 0o777;
                let status = if mode == 0o440 {
                    AuditStatus::Pass
                } else {
                    AuditStatus::Fail
                };
                items.push(AuditItem {
                    category: "Filesystem Permissions",
                    title: "/etc/sudoers Permission Mask",
                    current_value: format!("{:04o}", mode),
                    expected_value: "0440",
                    status,
                    remediation: "chmod 440 /etc/sudoers".to_string(),
                });
            }
        }
    }

    items
}

fn calculate_compliance_score(items: &[AuditItem]) -> (u32, u32, u32, u32) {
    let mut pass = 0u32;
    let mut warn = 0u32;
    let mut fail = 0u32;

    for it in items {
        match it.status {
            AuditStatus::Pass => pass += 1,
            AuditStatus::Warn => warn += 1,
            AuditStatus::Fail => fail += 1,
            AuditStatus::Info => {}
        }
    }

    let total = pass + warn + fail;
    let score = if total > 0 {
        ((pass * 100 + warn * 50) / total).min(100)
    } else {
        100
    };

    (score, pass, warn, fail)
}

fn print_report(items: &[AuditItem]) {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!("{C_BLUE}{}{C_RESET}", "═".repeat(78));
    println!(" {C_WHITE}{C_BOLD}ASTERIX OS CYBERNETIC SECURITY HARDENING & COMPLIANCE SCORECARD{C_RESET}");
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));

    let (score, pass, warn, fail) = calculate_compliance_score(items);

    let score_color = if score >= 85 {
        C_GREEN
    } else if score >= 60 {
        C_YELLOW
    } else {
        C_RED
    };

    println!("  {C_WHITE}Security Compliance Score:{C_RESET} {score_color}{C_BOLD}{} / 100{C_RESET}", score);
    println!("  {C_GREEN}✔ PASSED:{C_RESET} {:2}  |  {C_YELLOW}⚠ WARNINGS:{C_RESET} {:2}  |  {C_RED}✖ FAILED:{C_RESET} {:2}\n",
        pass, warn, fail);

    let mut current_cat = "";
    for it in items {
        if it.category != current_cat {
            current_cat = it.category;
            println!("{C_CYAN}{C_BOLD}─── {} ───{C_RESET}", current_cat);
        }

        let badge = match it.status {
            AuditStatus::Pass => format!("{C_GREEN}[ PASS ]{C_RESET}"),
            AuditStatus::Warn => format!("{C_YELLOW}[ WARN ]{C_RESET}"),
            AuditStatus::Fail => format!("{C_RED}[ FAIL ]{C_RESET}"),
            AuditStatus::Info => format!("{C_GRAY}[ INFO ]{C_RESET}"),
        };

        println!("  {} {C_WHITE}{:<48}{C_RESET} Value: {C_YELLOW}{}{C_RESET}",
            badge, it.title, it.current_value);

        if it.status == AuditStatus::Fail || it.status == AuditStatus::Warn {
            if !it.remediation.is_empty() {
                println!("     {C_GRAY}↳ Fix:{C_RESET} {C_CYAN}{}{C_RESET}", it.remediation);
            }
        }
    }

    println!("\n{C_BLUE}{}{C_RESET}", "═".repeat(78));
    if fail > 0 || warn > 0 {
        println!(" {C_YELLOW}Tip:{C_RESET} Run with {C_CYAN}--generate-fix{C_RESET} to create an automated hardening script.");
    } else {
        println!(" {C_GREEN}Asterix System Hardening Verified. No immediate vulnerabilities detected.{C_RESET}");
    }
    println!("{C_BLUE}{}{C_RESET}\n", "═".repeat(78));
}

fn generate_hardening_script(items: &[AuditItem], output_path: &Path) -> io::Result<()> {
    let mut file = File::create(output_path)?;
    writeln!(file, "#!/usr/bin/env bash")?;
    writeln!(file, "# =====================================================================")?;
    writeln!(file, "# ASTERIX OS - Automated Security Hardening & Remediation Script")?;
    writeln!(file, "# Generated: {:?}", std::time::SystemTime::now())?;
    writeln!(file, "# =====================================================================\n")?;
    writeln!(file, "set -e\n")?;
    writeln!(file, "echo '[*] Applying Asterix OS Hardening Rules...'")?;

    for it in items {
        if (it.status == AuditStatus::Fail || it.status == AuditStatus::Warn) && !it.remediation.is_empty() {
            writeln!(file, "\n# {}", it.title)?;
            writeln!(file, "{}", it.remediation)?;
        }
    }

    writeln!(file, "\necho '[✔] Asterix Security Hardening Applied Successfully!'")?;
    println!("{C_GREEN}{C_BOLD}[✔] Hardening script generated at: {}{C_RESET}", output_path.display());
    Ok(())
}

fn print_json(items: &[AuditItem]) {
    let (score, pass, warn, fail) = calculate_compliance_score(items);
    print!("{{\"compliance_score\":{},\"pass\":{},\"warn\":{},\"fail\":{},\"items\":[",
        score, pass, warn, fail);
    for (i, it) in items.iter().enumerate() {
        if i > 0 { print!(","); }
        let st_str = match it.status {
            AuditStatus::Pass => "PASS",
            AuditStatus::Warn => "WARN",
            AuditStatus::Fail => "FAIL",
            AuditStatus::Info => "INFO",
        };
        print!("{{\"category\":\"{}\",\"title\":\"{}\",\"status\":\"{}\",\"current_value\":\"{}\",\"expected_value\":\"{}\",\"remediation\":\"{}\"}}",
            it.category, it.title, st_str, it.current_value, it.expected_value, it.remediation.replace('"', "\\\""));
    }
    println!("]}}");
}

fn print_help() {
    println!("{C_CYAN}{C_BOLD}{}{C_RESET}", BANNER);
    println!(r#"
USAGE:
    asterix-guard-engine [OPTIONS]

OPTIONS:
    -a, --audit             Run comprehensive system security audit (Default)
    -g, --generate-fix      Generate automated bash hardening remediation script
    -o, --out <FILE>        Output file for remediation script (Default: asterix-harden.sh)
    -j, --json              Output results in structured JSON format
    -h, --help              Print this help manual

EXAMPLES:
    asterix-guard-engine
    asterix-guard-engine --generate-fix -o apply-hardening.sh
    asterix-guard-engine --json
"#);
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.contains(&"--help".to_string()) || args.contains(&"-h".to_string()) {
        print_help();
        return;
    }

    let mut items = Vec::new();
    items.extend(audit_kernel_protections());
    items.extend(audit_user_accounts());
    items.extend(audit_filesystem_permissions());
    items.extend(audit_ssh_config());

    if args.contains(&"--json".to_string()) || args.contains(&"-j".to_string()) {
        print_json(&items);
        return;
    }

    if args.contains(&"--generate-fix".to_string()) || args.contains(&"-g".to_string()) {
        let mut out = Path::new("asterix-harden.sh");
        if let Some(pos) = args.iter().position(|a| a == "-o" || a == "--out") {
            if pos + 1 < args.len() {
                out = Path::new(&args[pos + 1]);
            }
        }
        let _ = generate_hardening_script(&items, out);
        return;
    }

    print_report(&items);
}
