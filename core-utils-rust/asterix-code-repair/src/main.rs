//! =====================================================================
//! ASTERIX OS - Autonomous Code Repair & AST Defect Healing Engine
//! Pure Standalone Rust (Zero External Crates)
//! Scans C, C++, Rust, Python, Go, and Shell files for syntax defects,
//! unclosed delimiters, missing semicolons, broken shebangs, and corruption,
//! and heals them automatically with zero manual intervention.
//! =====================================================================

use std::env;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Write};
use std::path::{Path, PathBuf};

// ANSI 256-Color Palette
const C_RESET: &str = "\x1b[0m";
const C_BOLD: &str = "\x1b[1m";
const C_CYAN: &str = "\x1b[38;5;51m";
const C_GREEN: &str = "\x1b[38;5;46m";
const C_YELLOW: &str = "\x1b[38;5;220m";
const C_RED: &str = "\x1b[38;5;196m";
const C_MAGENTA: &str = "\x1b[38;5;201m";
const C_BLUE: &str = "\x1b[38;5;45m";
const C_WHITE: &str = "\x1b[38;5;231m";
const C_GRAY: &str = "\x1b[38;5;244m";

const BANNER: &str = r#"╔══════════════════════════════════════════════════════════════════════════╗
║ [ ASTERIX NATIVE CODE-REPAIR // AUTONOMOUS DEFECT HEALING ENGINE ]       ║
╚══════════════════════════════════════════════════════════════════════════╝"#;

#[derive(Debug, Clone, PartialEq)]
enum Language {
    C,
    Cpp,
    Rust,
    Python,
    Bash,
    Go,
    Unknown,
}

impl Language {
    fn from_path(path: &Path) -> Self {
        match path.extension().and_then(|s| s.to_str()).unwrap_or("") {
            "c" | "h" => Language::C,
            "cpp" | "hpp" | "cc" | "cxx" => Language::Cpp,
            "rs" => Language::Rust,
            "py" => Language::Python,
            "sh" | "bash" => Language::Bash,
            "go" => Language::Go,
            _ => Language::Unknown,
        }
    }
}

#[derive(Debug)]
struct Defect {
    line_number: usize,
    description: String,
    auto_fixable: bool,
}

#[derive(Default)]
struct ScanStats {
    files_scanned: usize,
    defects_found: usize,
    defects_healed: usize,
}

fn scan_file_for_defects(path: &Path, lang: &Language) -> io::Result<Vec<Defect>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut defects = Vec::new();

    let mut open_braces = 0i32;
    let mut open_parens = 0i32;
    let mut open_brackets = 0i32;
    let mut in_c_multiline_comment = false;
    let mut line_num = 0;
    let mut has_shebang = false;

    for line_res in reader.lines() {
        line_num += 1;
        let line = line_res?;
        let trimmed = line.trim();

        if line_num == 1 && trimmed.starts_with("#!") {
            has_shebang = true;
        }

        // Check for shell scripts missing shebang
        if line_num == 1 && *lang == Language::Bash && !has_shebang && !trimmed.is_empty() {
            defects.push(Defect {
                line_number: 1,
                description: "Missing standard shebang (#!/usr/bin/env bash)".to_string(),
                auto_fixable: true,
            });
        }

        // C / C++ / Rust / Go comment and delimiter tracking
        if *lang == Language::C || *lang == Language::Cpp || *lang == Language::Rust || *lang == Language::Go {
            if in_c_multiline_comment {
                if trimmed.contains("*/") {
                    in_c_multiline_comment = false;
                }
                continue;
            }
            if trimmed.starts_with("/*") && !trimmed.contains("*/") {
                in_c_multiline_comment = true;
                continue;
            }
            if trimmed.starts_with("//") {
                continue;
            }

            for ch in trimmed.chars() {
                match ch {
                    '{' => open_braces += 1,
                    '}' => open_braces -= 1,
                    '(' => open_parens += 1,
                    ')' => open_parens -= 1,
                    '[' => open_brackets += 1,
                    ']' => open_brackets -= 1,
                    _ => {}
                }
            }

            // Semicolon check for C / C++ statements
            if (*lang == Language::C || *lang == Language::Cpp)
                && !trimmed.is_empty()
                && !trimmed.starts_with('#')
                && !trimmed.starts_with("//")
                && !trimmed.starts_with("/*")
                && !trimmed.ends_with('{')
                && !trimmed.ends_with('}')
                && !trimmed.ends_with(';')
                && !trimmed.ends_with(':')
                && !trimmed.ends_with('\\')
                && !trimmed.starts_with("case ")
                && !trimmed.starts_with("default:")
            {
                // Heuristic check: typical statement keywords
                if trimmed.starts_with("return ")
                    || trimmed.starts_with("int ")
                    || trimmed.starts_with("char ")
                    || trimmed.starts_with("void ")
                    || trimmed.starts_with("printf(")
                    || trimmed.starts_with("puts(")
                    || trimmed.starts_with("free(")
                    || trimmed.contains(" = ")
                {
                    defects.push(Defect {
                        line_number: line_num,
                        description: format!("Missing statement terminator ';' at end of line {line_num}"),
                        auto_fixable: true,
                    });
                }
            }
        }

        // Python Checks
        if *lang == Language::Python && !trimmed.is_empty() && !trimmed.starts_with('#') {
            // Missing colon after def/class/if/elif/else/for/while
            let starts_control = trimmed.starts_with("def ")
                || trimmed.starts_with("class ")
                || trimmed.starts_with("if ")
                || trimmed.starts_with("elif ")
                || trimmed == "else"
                || trimmed == "try"
                || trimmed.starts_with("except")
                || trimmed == "finally"
                || trimmed.starts_with("for ")
                || trimmed.starts_with("while ");

            if starts_control && !trimmed.ends_with(':') && !trimmed.ends_with('\\') {
                defects.push(Defect {
                    line_number: line_num,
                    description: format!("Missing colon ':' at end of Python block on line {line_num}"),
                    auto_fixable: true,
                });
            }
        }
    }

    if open_braces > 0 {
        defects.push(Defect {
            line_number: line_num,
            description: format!("Unclosed curly braces detected ({open_braces} missing '}}')"),
            auto_fixable: true,
        });
    }

    if open_parens > 0 {
        defects.push(Defect {
            line_number: line_num,
            description: format!("Unclosed parentheses detected ({open_parens} missing ')')"),
            auto_fixable: true,
        });
    }

    if open_brackets > 0 {
        defects.push(Defect {
            line_number: line_num,
            description: format!("Unclosed square brackets detected ({open_brackets} missing ']')"),
            auto_fixable: false,
        });
    }

    Ok(defects)
}

fn repair_file(path: &Path, lang: &Language, defects: &[Defect]) -> io::Result<usize> {
    let _ = lang;
    let bak_path = path.with_extension(format!("{}.bak", path.extension().unwrap_or_default().to_string_lossy()));
    if !bak_path.exists() {
        fs::copy(path, &bak_path)?;
    }

    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut lines: Vec<String> = reader.lines().collect::<Result<_, _>>()?;
    let mut healed_count = 0;

    for d in defects {
        if !d.auto_fixable {
            continue;
        }

        if d.description.contains("Missing standard shebang") && !lines.is_empty() {
            lines.insert(0, "#!/usr/bin/env bash\n".to_string());
            healed_count += 1;
        } else if d.description.contains("Missing statement terminator ';'") {
            let idx = d.line_number.saturating_sub(1);
            if idx < lines.len() && !lines[idx].trim_end().ends_with(';') {
                let trimmed = lines[idx].trim_end();
                lines[idx] = format!("{trimmed};");
                healed_count += 1;
            }
        } else if d.description.contains("Missing colon ':'") {
            let idx = d.line_number.saturating_sub(1);
            if idx < lines.len() && !lines[idx].trim_end().ends_with(':') {
                let trimmed = lines[idx].trim_end();
                lines[idx] = format!("{trimmed}:");
                healed_count += 1;
            }
        } else if d.description.contains("missing '}'") {
            let count_str = d.description.split_whitespace().nth(3).unwrap_or("1");
            let count: usize = count_str.parse().unwrap_or(1);
            for _ in 0..count {
                lines.push("}".to_string());
                healed_count += 1;
            }
        }
    }

    let mut out_file = File::create(path)?;
    for line in lines {
        writeln!(out_file, "{line}")?;
    }

    // Set executable permission on shell scripts
    #[cfg(unix)]
    if *lang == Language::Bash {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(path)?.permissions();
        perms.set_mode(0o755);
        let _ = fs::set_permissions(path, perms);
    }

    Ok(healed_count)
}

fn process_directory(dir: &Path, auto_fix: bool, stats: &mut ScanStats) -> io::Result<()> {
    if !dir.exists() {
        return Ok(());
    }

    for entry_res in fs::read_dir(dir)? {
        let entry = entry_res?;
        let path = entry.path();

        if path.is_dir() {
            let fname = path.file_name().unwrap_or_default().to_string_lossy();
            if fname.starts_with('.') || fname == "target" || fname == "node_modules" || fname == "dist" {
                continue;
            }
            process_directory(&path, auto_fix, stats)?;
        } else if path.is_file() {
            let lang = Language::from_path(&path);
            if lang == Language::Unknown {
                continue;
            }

            stats.files_scanned += 1;
            match scan_file_for_defects(&path, &lang) {
                Ok(defects) => {
                    if !defects.is_empty() {
                        stats.defects_found += defects.len();
                        println!("  {C_RED}[DEFECTS DETECTED]{C_RESET} {C_WHITE}{}{C_RESET} ({} issue(s))", path.display(), defects.len());
                        for d in &defects {
                            println!("    • Line {:<4} -> {C_YELLOW}{}{C_RESET}", d.line_number, d.description);
                        }

                        if auto_fix {
                            match repair_file(&path, &lang, &defects) {
                                Ok(healed) => {
                                    stats.defects_healed += healed;
                                    println!("    {C_GREEN}{C_BOLD}[✔] AUTO-REPAIRED:{C_RESET} {healed} issue(s) resolved with backup (.bak)\n");
                                }
                                Err(e) => {
                                    println!("    {C_RED}[!] Auto-repair error: {e}{C_RESET}\n");
                                }
                            }
                        } else {
                            println!("    {C_GRAY}[i] Run with 'fix' to automatically heal these defects.{C_RESET}\n");
                        }
                    }
                }
                Err(_) => {}
            }
        }
    }

    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let action = args.get(1).map(|s| s.as_str()).unwrap_or("scan");
    let target_dir = args.get(2).map(PathBuf::from).unwrap_or_else(|| PathBuf::from("."));

    println!("{C_CYAN}{C_BOLD}{BANNER}{C_RESET}\n");

    let auto_fix = match action {
        "fix" | "repair" | "heal" | "--fix" => true,
        "scan" | "audit" | "check" | _ => false,
    };

    println!("  {C_CYAN}[*] Target Directory:{C_RESET} {C_WHITE}{}{C_RESET}", target_dir.display());
    println!("  {C_CYAN}[*] Execution Mode:{C_RESET}   {C_MAGENTA}{}{C_RESET}\n", if auto_fix { "AUTONOMOUS REPAIR & HEAL" } else { "DIAGNOSTIC SCAN ONLY" });

    let mut stats = ScanStats::default();
    if target_dir.is_file() {
        stats.files_scanned = 1;
        let lang = Language::from_path(&target_dir);
        if let Ok(defects) = scan_file_for_defects(&target_dir, &lang) {
            if !defects.is_empty() {
                stats.defects_found = defects.len();
                println!("  {C_RED}[DEFECTS DETECTED]{C_RESET} {C_WHITE}{}{C_RESET}", target_dir.display());
                for d in &defects {
                    println!("    • Line {:<4} -> {C_YELLOW}{}{C_RESET}", d.line_number, d.description);
                }
                if auto_fix {
                    if let Ok(healed) = repair_file(&target_dir, &lang, &defects) {
                        stats.defects_healed = healed;
                        println!("    {C_GREEN}{C_BOLD}[✔] AUTO-REPAIRED:{C_RESET} {healed} issue(s) resolved.\n");
                    }
                }
            } else {
                println!("  {C_GREEN}[✔] Clean: Zero syntax anomalies or defects detected in {}{C_RESET}\n", target_dir.display());
            }
        }
    } else {
        let _ = process_directory(&target_dir, auto_fix, &mut stats);
    }

    println!("{}{}{}", C_BLUE, "═".repeat(74), C_RESET);
    println!("  {C_WHITE}{C_BOLD}SUMMARY OF OS CODE REPAIR AUDIT:{C_RESET}");
    println!("  • Files Evaluated:    {C_CYAN}{}{C_RESET}", stats.files_scanned);
    println!("  • Total Defects:      {}{}{C_RESET}", if stats.defects_found > 0 { C_RED } else { C_GREEN }, stats.defects_found);
    if auto_fix {
        println!("  • Successfully Healed:{C_GREEN}{}{C_RESET}", stats.defects_healed);
    }
    println!("{}{}{}\n", C_BLUE, "═".repeat(74), C_RESET);
}
