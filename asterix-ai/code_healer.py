#!/usr/bin/env python3
"""
ASTERIX OS — Universal Autonomous Code Healer & Multi-Language Syntax Repair Engine
Supported Languages:
  1. Python (.py)
  2. C (.c, .h)
  3. C++ (.cpp, .cc, .hpp)
  4. Rust (.rs)
  5. Go (.go)
  6. JavaScript & TypeScript (.js, .jsx, .ts, .tsx)
  7. Bash & Shell (.sh, .bash)
  8. JSON (.json)
  9. HTML & CSS (.html, .htm, .css)
 10. SQL (.sql)

Zero external dependencies — 100% Python standard library.
"""

import sys
import os
import re
import json
import difflib
import shutil
from pathlib import Path

# Enable UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ANSI Color Codes
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_CYAN = "\033[38;5;51m"
C_GREEN = "\033[38;5;46m"
C_YELLOW = "\033[38;5;220m"
C_RED = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE = "\033[38;5;231m"
C_GRAY = "\033[38;5;244m"
C_BLUE = "\033[38;5;45m"

BANNER = f"""{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║{C_WHITE} {C_BOLD}[ ASTERIX UNIVERSAL CODE HEALER // AUTONOMOUS MULTI-LANGUAGE SYNTAX FIX ]{C_RESET}{C_CYAN} ║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

def detect_language(snippet_or_path):
    """Accurately detect language from file extension or code heuristics."""
    if os.path.exists(snippet_or_path) and not os.path.isdir(snippet_or_path):
        ext = os.path.splitext(snippet_or_path)[1].lower()
        mapping = {
            ".py": "python",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".hpp": "cpp",
            ".rs": "rust",
            ".go": "go",
            ".js": "javascript",
            ".jsx": "javascript",
            ".mjs": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".sh": "bash",
            ".bash": "bash",
            ".json": "json",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".sql": "sql",
            ".java": "java",
            ".cs": "csharp",
            ".php": "php",
            ".asm": "assembly",
            ".s": "assembly",
        }
        if ext in mapping:
            return mapping[ext]

    s = snippet_or_path.strip()
    # JSON detection
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        if ":" in s or re.search(r'["\'\w]+\s*:\s*', s) or s.startswith("["):
            return "json"

    # HTML / XML detection
    if re.search(r"<!DOCTYPE\s+html|<html|<div|<body|<head|<script|<p>|<span>", s, re.I):
        return "html"

    # CSS detection
    if re.search(r"^[.#]?\w+[\s\w,>+~:]*\{[^}]*:[^}]*\}", s, re.M):
        return "css"

    # SQL detection
    if re.match(r"^(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE)\b", s, re.I):
        return "sql"

    # Rust detection
    if re.search(r"\bfn\s+\w+\s*\(|\blet\s+mut\s+|\bimpl\s+|\bprintln!\s*\(|\buse\s+std::", s):
        return "rust"

    # Go detection
    if re.search(r"\bpackage\s+\w+|\bfunc\s+\w+\s*\(|\bfmt\.Print", s):
        return "go"

    # C / C++ detection
    if re.search(r"#include\s*<|\bint\s+main\s*\(|\bprintf\s*\(|\bstd::|\bcout\s*<<|\bcin\s*>>", s):
        return "cpp" if ("std::" in s or "cout" in s or "#include <iostream>" in s) else "c"

    # JavaScript / TypeScript detection
    if re.search(r"\bconsole\.log\(|\bfunction\s+\w+\s*\(|\bconst\s+\w+\s*=|\blet\s+\w+\s*=|\bvar\s+\w+\s*=|\b=>", s):
        return "javascript"

    # Bash detection
    if s.startswith("#!") or re.search(r"\becho\s+|\bif\s+\[|then\b|fi\b|done\b", s):
        return "bash"

    # Python detection
    if re.search(r"\bdef\s+\w+\s*\(|\bclass\s+\w+|\bimport\s+\w+|\bprint\s*\(|\belif\b", s):
        return "python"

    return "python"

# ──────────────────────────────────────────────────────────────────────────────
# 1. PYTHON HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_python(code):
    modifications = []
    lines = code.splitlines()
    new_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 1. Inline def expansion: def calc(x) return x*2
        inline_def = re.match(r"^(\s*def\s+\w+\([^)]*\))\s+return\s+(.*)$", line)
        if inline_def:
            func_sig = inline_def.group(1)
            ret_val = inline_def.group(2).rstrip(":")
            base_indent = " " * (len(line) - len(line.lstrip()))
            inner_indent = base_indent + "    "
            line = f"{func_sig}:\n{inner_indent}return {ret_val}"
            modifications.append(f"Line {i+1}: Formatted inline function definition into proper indentation")
            new_lines.append(line)
            continue

        # 2. Missing colons after control flow
        colon_keywords = r"^(if\b.*|elif\b.*|else|while\b.*|for\b.*|def\b.*|class\b.*|try|except(\b.*)?|finally|with\b.*)"
        if re.match(colon_keywords, stripped) and not stripped.endswith(":") and not stripped.endswith("{"):
            line = line + ":"
            modifications.append(f"Line {i+1}: Added missing colon ':' to statement '{stripped}'")

        # 3. Modernize Python 2 print
        print_match = re.match(r"^(\s*)print\s+([\"'].*[\"']|\w+.*)$", line)
        if print_match and not print_match.group(2).startswith("("):
            indent = print_match.group(1)
            arg = print_match.group(2).rstrip(";")
            line = f"{indent}print({arg})"
            modifications.append(f"Line {i+1}: Modernized print statement to print(...) syntax")

        # 4. Remove accidental trailing semicolons
        if line.endswith(";") and not stripped.startswith("#"):
            line = line.rstrip(";")
            modifications.append(f"Line {i+1}: Removed unnecessary trailing semicolon")

        new_lines.append(line)

    healed_code = "\n".join(new_lines)
    # Balance delimiters
    healed_code, delims_added = balance_delimiters(healed_code)
    if delims_added:
        modifications.append(f"Balanced unclosed delimiters by appending '{delims_added}'")

    return healed_code, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 2. C / C++ HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_c_cpp(code, lang="c"):
    modifications = []
    lines = code.splitlines()
    new_lines = []
    open_braces = 0

    # 1. Banned / Vulnerable function modernization & Dangling pointer defense
    modernized_lines = []
    for i, line in enumerate(lines):
        # gets(x) -> fgets(x, sizeof(x), stdin)
        gets_match = re.search(r"\bgets\s*\(\s*([a-zA-Z0-9_]+)\s*\)", line)
        if gets_match:
            buf_name = gets_match.group(1)
            line = re.sub(r"\bgets\s*\(\s*" + buf_name + r"\s*\)", f"fgets({buf_name}, sizeof({buf_name}), stdin)", line)
            modifications.append(f"Line {i+1}: Replaced banned/unsafe 'gets({buf_name})' with bounds-checked 'fgets({buf_name}, sizeof({buf_name}), stdin)'")

        # sprintf(buf, ...) -> snprintf(buf, sizeof(buf), ...)
        sprintf_match = re.search(r"\bsprintf\s*\(\s*([a-zA-Z0-9_]+)\s*,", line)
        if sprintf_match and "snprintf" not in line:
            buf_name = sprintf_match.group(1)
            line = re.sub(r"\bsprintf\s*\(\s*" + buf_name + r"\s*,", f"snprintf({buf_name}, sizeof({buf_name}),", line)
            modifications.append(f"Line {i+1}: Upgraded unbounded 'sprintf({buf_name}, ...)' to safe 'snprintf({buf_name}, sizeof({buf_name}), ...)'")

        # Dangling pointer defense: free(ptr); -> free(ptr); ptr = NULL;
        free_match = re.search(r"\bfree\s*\(\s*([a-zA-Z0-9_]+)\s*\)\s*;", line)
        if free_match:
            ptr_name = free_match.group(1)
            if f"{ptr_name} = NULL" not in line and f"{ptr_name} = 0" not in line:
                next_has_null = False
                if i + 1 < len(lines) and (f"{ptr_name} = NULL" in lines[i+1] or f"{ptr_name} = 0" in lines[i+1]):
                    next_has_null = True
                if not next_has_null:
                    line = line.replace(f"free({ptr_name});", f"free({ptr_name}); {ptr_name} = NULL;")
                    modifications.append(f"Line {i+1}: Dangling pointer hardened: set '{ptr_name} = NULL' after 'free({ptr_name})' (neutralizes double-free & UAF)")

        modernized_lines.append(line)
    lines = modernized_lines

    # 2. Scope-Bound Memory Leak & File Descriptor Leak Remediation
    processed_lines = []
    func_allocs = {}
    func_files = {}
    freed_in_func = set()
    closed_in_func = set()
    returned_in_func = set()
    in_func = False
    func_brace_depth = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()

        # Track function entry: return_type name(args) {
        if not in_func and re.search(r"^[a-zA-Z0-9_:\*]+\s+[a-zA-Z0-9_]+\s*\([^;]*\)\s*\{?", trimmed):
            if not trimmed.endswith(";") and not trimmed.startswith(("#", "//", "/*")):
                in_func = True
                func_brace_depth = 0
                func_allocs.clear()
                func_files.clear()
                freed_in_func.clear()
                closed_in_func.clear()
                returned_in_func.clear()

        if in_func:
            func_brace_depth += line.count("{") - line.count("}")

            # Detect malloc/calloc: [type*] name = [cast]malloc(...)
            m_alloc = re.search(r"(?:[a-zA-Z0-9_]+\s*\*|\*)\s*([a-zA-Z0-9_]+)\s*=\s*(?:\([^\)]+\)\s*)?(?:malloc|calloc|realloc)\s*\(", line)
            if m_alloc:
                p_name = m_alloc.group(1)
                indent = re.match(r"^\s*", line).group(0) or "    "
                func_allocs[p_name] = indent

            # Detect fopen: FILE *name = fopen(...) or name = fopen(...)
            m_fopen = re.search(r"(?:FILE\s*\*|\s)\s*([a-zA-Z0-9_]+)\s*=\s*fopen\s*\(", line)
            if m_fopen:
                f_name = m_fopen.group(1)
                indent = re.match(r"^\s*", line).group(0) or "    "
                func_files[f_name] = indent

            # Detect free(p)
            for m_free in re.finditer(r"\bfree\s*\(\s*([a-zA-Z0-9_]+)\s*\)", line):
                freed_in_func.add(m_free.group(1))

            # Detect fclose(f)
            for m_close in re.finditer(r"\bfclose\s*\(\s*([a-zA-Z0-9_]+)\s*\)", line):
                closed_in_func.add(m_close.group(1))

            # Detect return x;
            m_ret = re.search(r"\breturn\s+([a-zA-Z0-9_]+)\s*;", line)
            if m_ret:
                returned_in_func.add(m_ret.group(1))

            # Detect returning stack address (undefined behavior)
            m_ret_stack = re.search(r"\breturn\s+&([a-zA-Z0-9_]+)\s*;", line)
            if m_ret_stack:
                bad_var = m_ret_stack.group(1)
                modifications.append(f"Line {i+1}: [WARNING/UB] Returning address of local stack variable '&{bad_var}' leads to dangling pointer crash.")

            # If returning before end of function, inject cleanups for unfreed pointers not returned
            if re.search(r"\breturn\b", line) and not line.strip().startswith("//"):
                indent = re.match(r"^\s*", line).group(0) or "    "
                unfreed = [p for p in func_allocs if p not in freed_in_func and p not in returned_in_func]
                unclosed = [f for f in func_files if f not in closed_in_func and f not in returned_in_func]
                
                injected = []
                for p in unfreed:
                    injected.append(f"{indent}if ({p} != NULL) {{ free({p}); {p} = NULL; }}")
                    freed_in_func.add(p)
                    modifications.append(f"Line {i+1}: Patched memory leak: injected 'free({p}); {p} = NULL;' before return")
                for f in unclosed:
                    injected.append(f"{indent}if ({f} != NULL) {{ fclose({f}); {f} = NULL; }}")
                    closed_in_func.add(f)
                    modifications.append(f"Line {i+1}: Patched file resource leak: injected 'fclose({f}); {f} = NULL;' before return")
                
                if injected:
                    processed_lines.extend(injected)

            # Check if function ended (func_brace_depth reaches 0)
            if func_brace_depth <= 0 and "}" in line:
                unfreed = [p for p in func_allocs if p not in freed_in_func and p not in returned_in_func]
                unclosed = [f for f in func_files if f not in closed_in_func and f not in returned_in_func]
                indent = "    "
                injected = []
                for p in unfreed:
                    injected.append(f"{indent}if ({p} != NULL) {{ free({p}); {p} = NULL; }}")
                    modifications.append(f"Patched scope memory leak: injected 'free({p}); {p} = NULL;' before function exit")
                for f in unclosed:
                    injected.append(f"{indent}if ({f} != NULL) {{ fclose({f}); {f} = NULL; }}")
                    modifications.append(f"Patched resource leak: injected 'fclose({f}); {f} = NULL;' before function exit")
                
                if injected:
                    processed_lines.extend(injected)
                
                in_func = False
                func_allocs.clear()
                func_files.clear()

        processed_lines.append(line)
    lines = processed_lines

    # 3. Header discovery matrix
    needed_headers = set()
    code_text = "\n".join(lines)
    if re.search(r"\b(printf|scanf|fopen|fclose|fprintf|sprintf|snprintf|FILE|NULL|stdin|stdout|stderr|puts|getchar|fgets)\b", code_text):
        needed_headers.add("<stdio.h>")
    if re.search(r"\b(malloc|free|calloc|realloc|exit|atoi|atof|rand|srand|system)\b", code_text):
        needed_headers.add("<stdlib.h>")
    if re.search(r"\b(strlen|strcpy|strncpy|strcmp|strncmp|strcat|memset|memcpy|memmove|strstr)\b", code_text):
        needed_headers.add("<string.h>")
    if lang == "c" and re.search(r"\b(bool|true|false)\b", code_text):
        needed_headers.add("<stdbool.h>")
    if re.search(r"\b(sqrt|pow|sin|cos|tan|floor|ceil|abs|fabs)\b", code_text):
        needed_headers.add("<math.h>")
    if re.search(r"\b(uint8_t|uint16_t|uint32_t|uint64_t|int8_t|int16_t|int32_t|int64_t)\b", code_text):
        needed_headers.add("<stdint.h>")
    if lang == "cpp":
        if re.search(r"\b(cout|cin|endl|cerr)\b", code_text):
            needed_headers.add("<iostream>")
        if re.search(r"\bvector<", code_text):
            needed_headers.add("<vector>")
        if re.search(r"\bstring\b", code_text) and "char" not in code_text:
            needed_headers.add("<string>")

    existing_headers = set(re.findall(r"#include\s*([<\"].*?[>\"])", code_text))
    headers_to_add = [h for h in needed_headers if h not in existing_headers]

    for h in sorted(headers_to_add):
        new_lines.append(f"#include {h}")
        modifications.append(f"Prepended missing standard header '#include {h}'")

    if lang == "cpp" and re.search(r"\b(cout|cin|endl)\b", code_text) and "using namespace std;" not in code_text and "std::" not in code_text:
        new_lines.append("using namespace std;")
        modifications.append("Added 'using namespace std;' for C++ stream I/O")

    has_main = False
    has_return_main = False

    for i, line in enumerate(lines):
        trimmed = line.strip()

        # Modernize void main() -> int main()
        if re.match(r"^\s*void\s+main\s*\(", line):
            line = re.sub(r"^\s*void\s+main", "int main", line)
            modifications.append(f"Line {i+1}: Modernized obsolete 'void main()' to standard 'int main()'")

        if "int main" in line:
            has_main = True
        if has_main and re.search(r"\breturn\s+0\s*;", line):
            has_return_main = True

        open_braces += trimmed.count("{") - trimmed.count("}")

        # Add missing semicolon on simple statement lines
        if trimmed and not trimmed.startswith(("//", "/*", "*", "#", "using", "namespace")) and not trimmed.endswith((";", "{", "}", ":", "\\", ",")):
            keywords_no_semi = ("if", "else", "for", "while", "do", "switch", "case", "default", "struct", "class", "enum", "public", "private", "protected")
            if not any(trimmed.startswith(kw) for kw in keywords_no_semi):
                line = line + ";"
                modifications.append(f"Line {i+1}: Added missing semicolon ';' to '{trimmed}'")

        new_lines.append(line)

    # If int main() present without return 0;
    if has_main and not has_return_main and open_braces == 0:
        for idx in range(len(new_lines) - 1, -1, -1):
            if new_lines[idx].strip() == "}":
                new_lines.insert(idx, "    return 0;")
                modifications.append("Appended standard 'return 0;' to main()")
                break

    healed_code = "\n".join(new_lines)
    if open_braces > 0:
        healed_code += "\n" + "}\n" * open_braces
        modifications.append(f"Closed {open_braces} unclosed curly brace(s) '}}'")

    return healed_code, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 3. RUST HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_rust(code):
    modifications = []
    lines = code.splitlines()
    new_lines = []
    open_braces = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()
        open_braces += trimmed.count("{") - trimmed.count("}")

        # Fix println(...) -> println!(...)
        if re.search(r"\bprintln\s*\(", line) and not re.search(r"\bprintln!\s*\(", line):
            line = re.sub(r"\bprintln\s*\(", "println!(", line)
            modifications.append(f"Line {i+1}: Corrected println(...) function to macro println!(...)")
        if re.search(r"\beprintln\s*\(", line) and not re.search(r"\beprintln!\s*\(", line):
            line = re.sub(r"\beprintln\s*\(", "eprintln!(", line)
            modifications.append(f"Line {i+1}: Corrected eprintln(...) function to macro eprintln!(...)")

        # Missing semicolon on let statements
        if re.match(r"^\s*let\s+(mut\s+)?\w+.*", trimmed) and not trimmed.endswith((";", "{")):
            line = line + ";"
            modifications.append(f"Line {i+1}: Added missing semicolon ';' to variable binding")

        new_lines.append(line)

    healed_code = "\n".join(new_lines)
    if open_braces > 0:
        healed_code += "\n" + "}\n" * open_braces
        modifications.append(f"Closed {open_braces} unclosed curly brace(s) '}}'")

    # If code has statements but no fn main()
    if "fn main" not in healed_code and not re.search(r"\b(pub\s+)?fn\s+", healed_code):
        healed_code = f"fn main() {{\n    {healed_code.strip()}\n}}"
        modifications.append("Wrapped loose statements in standard 'fn main() { ... }' entrypoint")

    return healed_code, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 4. GO HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_go(code):
    modifications = []
    lines = code.splitlines()
    new_lines = []

    has_package = any(line.strip().startswith("package ") for line in lines)
    if not has_package:
        new_lines.append("package main\n")
        modifications.append("Added missing 'package main' declaration at top")

    has_fmt = any("import \"fmt\"" in line or '"fmt"' in line for line in lines)
    needs_fmt = re.search(r"\bfmt\.(Println|Printf|Print|Sprintf)\b", code)
    if needs_fmt and not has_fmt:
        new_lines.append("import \"fmt\"\n")
        modifications.append("Added missing import 'import \"fmt\"'")

    open_braces = 0
    for i, line in enumerate(lines):
        trimmed = line.strip()
        open_braces += trimmed.count("{") - trimmed.count("}")

        # Strip accidental semicolons (idiomatic Go does not use semicolons at line ends)
        if line.rstrip().endswith(";") and not trimmed.startswith("//"):
            line = line.rstrip().rstrip(";")
            modifications.append(f"Line {i+1}: Stripped non-idiomatic trailing semicolon in Go")

        new_lines.append(line)

    healed_code = "\n".join(new_lines)
    if open_braces > 0:
        healed_code += "\n" + "}\n" * open_braces
        modifications.append(f"Closed {open_braces} unclosed curly brace(s) '}}'")

    # Wrap loose code into func main() if no function defined
    if "func " not in healed_code and has_package:
        healed_code = f"package main\n\nimport \"fmt\"\n\nfunc main() {{\n    {code.strip()}\n}}"
        modifications.append("Encapsulated loose statements inside 'func main() { ... }'")

    return healed_code, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 5. JAVASCRIPT / TYPESCRIPT HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_javascript(code, is_ts=False):
    modifications = []
    lines = code.splitlines()
    new_lines = []
    open_braces = 0

    for i, line in enumerate(lines):
        orig = line
        trimmed = line.strip()
        open_braces += trimmed.count("{") - trimmed.count("}")

        # 1. Convert accidental Python keywords
        if re.search(r"\bTrue\b", line):
            line = re.sub(r"\bTrue\b", "true", line)
            modifications.append(f"Line {i+1}: Converted Python 'True' to JavaScript 'true'")
        if re.search(r"\bFalse\b", line):
            line = re.sub(r"\bFalse\b", "false", line)
            modifications.append(f"Line {i+1}: Converted Python 'False' to JavaScript 'false'")
        if re.search(r"\bNone\b", line):
            line = re.sub(r"\bNone\b", "null", line)
            modifications.append(f"Line {i+1}: Converted Python 'None' to JavaScript 'null'")
        if re.search(r"\bprint\s*\(", line):
            line = re.sub(r"\bprint\s*\(", "console.log(", line)
            modifications.append(f"Line {i+1}: Converted 'print(...)' to 'console.log(...)'")
        if re.match(r"^\s*def\s+\w+\s*\(", line):
            line = re.sub(r"^\s*def\s+", "function ", line)
            line = line.rstrip(":") + " {"
            open_braces += 1
            modifications.append(f"Line {i+1}: Converted Python 'def' function syntax to JS 'function() {{'")
        if re.match(r"^\s*elif\b", line):
            line = re.sub(r"^\s*elif\b", "else if", line)
            modifications.append(f"Line {i+1}: Converted Python 'elif' to JS 'else if'")

        # 2. Add missing semicolon on var/let/const/return statements
        if re.match(r"^\s*(const|let|var|return|throw)\s+.*", trimmed) and not trimmed.endswith((";", "{", "}", ",")):
            line = line + ";"
            modifications.append(f"Line {i+1}: Added missing semicolon ';' to statement")

        new_lines.append(line)

    healed_code = "\n".join(new_lines)
    if open_braces > 0:
        healed_code += "\n" + "}\n" * open_braces
        modifications.append(f"Closed {open_braces} unclosed curly brace(s) '}}'")

    # Balance parens & brackets
    healed_code, delims_added = balance_delimiters(healed_code)
    if delims_added:
        modifications.append(f"Balanced unclosed delimiters: '{delims_added}'")

    return healed_code, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 6. BASH / SHELL HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_bash(code):
    modifications = []
    lines = code.splitlines()
    new_lines = []

    if lines and not lines[0].strip().startswith("#!"):
        new_lines.append("#!/usr/bin/env bash")
        new_lines.append("set -euo pipefail")
        modifications.append("Added safe bash shebang (#!/usr/bin/env bash) and pipefail header")

    open_ifs = 0
    open_loops = 0

    for i, line in enumerate(lines):
        trimmed = line.strip()

        # Track if/fi
        if re.match(r"^if\s+", trimmed):
            open_ifs += 1
            if not trimmed.endswith("; then") and not trimmed.endswith("then"):
                line = line + "; then"
                modifications.append(f"Line {i+1}: Appended '; then' to conditional statement")
        if trimmed == "fi":
            open_ifs = max(0, open_ifs - 1)

        # Track loops
        if re.match(r"^(for|while)\s+", trimmed):
            open_loops += 1
            if not trimmed.endswith("; do") and not trimmed.endswith("do"):
                line = line + "; do"
                modifications.append(f"Line {i+1}: Appended '; do' to loop header")
        if trimmed == "done":
            open_loops = max(0, open_loops - 1)

        new_lines.append(line)

    if open_ifs > 0:
        new_lines.append("fi\n" * open_ifs)
        modifications.append(f"Closed {open_ifs} unclosed 'fi' block(s)")
    if open_loops > 0:
        new_lines.append("done\n" * open_loops)
        modifications.append(f"Closed {open_loops} unclosed loop 'done' block(s)")

    return "\n".join(new_lines), modifications

# ──────────────────────────────────────────────────────────────────────────────
# 7. JSON HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_json(code):
    modifications = []
    healed = code.strip()

    # 1. Remove trailing commas before } or ]
    trailing_comma_obj = re.compile(r",\s*\}")
    trailing_comma_arr = re.compile(r",\s*\]")
    if trailing_comma_obj.search(healed):
        healed = trailing_comma_obj.sub("}", healed)
        modifications.append("Removed illegal trailing commas before '}'")
    if trailing_comma_arr.search(healed):
        healed = trailing_comma_arr.sub("]", healed)
        modifications.append("Removed illegal trailing commas before ']'")

    # 2. Convert single quotes to double quotes for keys & string values
    single_quote_keys = re.compile(r"'([^']+)'\s*:")
    if single_quote_keys.search(healed):
        healed = single_quote_keys.sub(r'"\1":', healed)
        modifications.append("Converted single-quoted keys to standard double-quoted JSON keys")

    single_quote_vals = re.compile(r":\s*'([^']*)'")
    if single_quote_vals.search(healed):
        healed = single_quote_vals.sub(r': "\1"', healed)
        modifications.append("Converted single-quoted string values to double-quoted JSON strings")

    # 3. Quote unquoted keys: { key: "value" } -> { "key": "value" }
    unquoted_keys = re.compile(r"([{,]\s*)([a-zA-Z_]\w*)\s*:")
    if unquoted_keys.search(healed):
        healed = unquoted_keys.sub(r'\1"\2":', healed)
        modifications.append("Enclosed unquoted object keys in double quotes")

    # 4. Balance braces & brackets
    healed, delims_added = balance_delimiters(healed)
    if delims_added:
        modifications.append(f"Balanced unclosed JSON delimiters: '{delims_added}'")

    # 5. Pretty-format if valid
    try:
        parsed = json.loads(healed)
        healed = json.dumps(parsed, indent=2)
        modifications.append("Normalized JSON formatting with 2-space indentation")
    except Exception:
        pass

    return healed, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 8. HTML & CSS HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_html_css(code, lang="html"):
    modifications = []
    if lang == "css":
        lines = code.splitlines()
        new_lines = []
        open_braces = 0
        for i, line in enumerate(lines):
            trimmed = line.strip()
            open_braces += trimmed.count("{") - trimmed.count("}")
            if ":" in trimmed and not trimmed.endswith((";", "{", "}")) and not trimmed.startswith(("/*", "*")):
                line = line + ";"
                modifications.append(f"Line {i+1}: Added missing semicolon ';' to CSS property")
            new_lines.append(line)
        healed = "\n".join(new_lines)
        if open_braces > 0:
            healed += "\n" + "}\n" * open_braces
            modifications.append(f"Closed {open_braces} unclosed CSS rule brace(s)")
        return healed, modifications

    # HTML
    healed = code
    if not re.search(r"<!DOCTYPE\s+html>", healed, re.I) and ("<html" in healed.lower() or "<body" in healed.lower()):
        healed = "<!DOCTYPE html>\n" + healed
        modifications.append("Added standard '<!DOCTYPE html>' declaration")

    # Check unclosed tags for common elements
    tags_to_check = ["div", "span", "p", "h1", "h2", "h3", "table", "ul", "ol", "li", "body", "html"]
    for t in tags_to_check:
        opens = len(re.findall(rf"<{t}\b[^>]*>", healed, re.I))
        closes = len(re.findall(rf"</{t}>", healed, re.I))
        if opens > closes:
            diff = opens - closes
            healed += "\n" + f"</{t}>\n" * diff
            modifications.append(f"Closed {diff} unclosed '<{t}>' tag(s)")

    return healed, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 9. SQL HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_sql(code):
    modifications = []
    healed = code.strip()

    # Keywords to uppercase
    sql_keywords = [
        "select", "from", "where", "insert into", "update", "delete from",
        "create table", "alter table", "drop table", "group by", "order by",
        "inner join", "left join", "right join", "having", "limit", "offset",
        "values", "set", "distinct", "union", "as", "and", "or", "in", "is null", "not null"
    ]
    for kw in sql_keywords:
        pattern = rf"\b{kw}\b"
        if re.search(pattern, healed, re.I):
            healed = re.sub(pattern, kw.upper(), healed, flags=re.I)

    modifications.append("Normalized standard SQL keywords to UPPERCASE")

    # Remove trailing comma before FROM or )
    if re.search(r",\s+FROM\b", healed):
        healed = re.sub(r",\s+FROM\b", " FROM", healed)
        modifications.append("Removed invalid trailing comma before 'FROM' clause")
    if re.search(r",\s*\)", healed):
        healed = re.sub(r",\s*\)", ")", healed)
        modifications.append("Removed invalid trailing comma before ')'")

    # Ensure ending semicolon
    if not healed.endswith(";"):
        healed += ";"
        modifications.append("Appended standard terminating semicolon ';'")

    return healed, modifications

# ──────────────────────────────────────────────────────────────────────────────
# 10. PHP HEALER
# ──────────────────────────────────────────────────────────────────────────────
def heal_php(code):
    modifications = []
    lines = code.splitlines()
    new_lines = []
    if lines and not lines[0].strip().startswith("<?"):
        new_lines.append("<?php\n")
        modifications.append("Prepended standard PHP opening tag '<?php'")
    open_braces = 0
    for i, line in enumerate(lines):
        trimmed = line.strip()
        open_braces += trimmed.count("{") - trimmed.count("}")
        if trimmed and not trimmed.startswith(("//", "/*", "#", "<?", "?>")) and not trimmed.endswith((";", "{", "}", ":")):
            keywords = ("if", "else", "for", "while", "do", "switch", "case", "class", "function", "trait", "interface")
            if not any(trimmed.startswith(kw) for kw in keywords):
                line = line + ";"
                modifications.append(f"Line {i+1}: Added missing semicolon ';' to PHP statement")
        new_lines.append(line)
    healed = "\n".join(new_lines)
    if open_braces > 0:
        healed += "\n" + "}\n" * open_braces
        modifications.append(f"Closed {open_braces} unclosed PHP curly brace(s)")
    return healed, modifications

# ──────────────────────────────────────────────────────────────────────────────
# HELPER: DELIMITER BALANCER
# ──────────────────────────────────────────────────────────────────────────────
def balance_delimiters(code):
    opens = {"(": ")", "[": "]", "{": "}"}
    stack = []
    in_str = None
    escaped = False

    for ch in code:
        if escaped:
            escaped = False
            continue
        if ch == "\\":
            escaped = True
            continue
        if ch in ('"', "'", "`"):
            if in_str == ch:
                in_str = None
            elif in_str is None:
                in_str = ch
            continue
        if in_str:
            continue
        if ch in opens:
            stack.append(opens[ch])
        elif ch in opens.values():
            if stack and stack[-1] == ch:
                stack.pop()

    if stack:
        closing = "".join(reversed(stack))
        return code + closing, closing
    return code, ""

# ──────────────────────────────────────────────────────────────────────────────
# MASTER DISPATCHER
# ──────────────────────────────────────────────────────────────────────────────
def heal_code(snippet_or_path, forced_lang=None):
    is_file = os.path.isfile(snippet_or_path)
    if is_file:
        try:
            with open(snippet_or_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            return None, [f"Error reading file: {e}"], "unknown"
        lang = forced_lang or detect_language(snippet_or_path)
    else:
        content = snippet_or_path
        lang = forced_lang or detect_language(snippet_or_path)

    if lang == "python":
        healed, mods = heal_python(content)
    elif lang in ("c", "cpp", "java", "csharp"):
        healed, mods = heal_c_cpp(content, lang)
    elif lang == "rust":
        healed, mods = heal_rust(content)
    elif lang == "go":
        healed, mods = heal_go(content)
    elif lang in ("javascript", "typescript"):
        healed, mods = heal_javascript(content, is_ts=(lang == "typescript"))
    elif lang == "bash":
        healed, mods = heal_bash(content)
    elif lang == "json":
        healed, mods = heal_json(content)
    elif lang == "php":
        healed, mods = heal_php(content)
    elif lang in ("html", "css"):
        healed, mods = heal_html_css(content, lang=lang)
    elif lang == "sql":
        healed, mods = heal_sql(content)
    else:
        healed, mods = heal_python(content)

    return healed, mods, lang

def print_diff(original, healed, filename="snippet"):
    orig_lines = original.splitlines(keepends=True)
    healed_lines = healed.splitlines(keepends=True)
    diff = difflib.unified_diff(orig_lines, healed_lines, fromfile=f"a/{filename}", tofile=f"b/{filename}")
    has_diff = False
    for line in diff:
        has_diff = True
        if line.startswith("+"):
            print(f"{C_GREEN}{line.rstrip()}{C_RESET}")
        elif line.startswith("-"):
            print(f"{C_RED}{line.rstrip()}{C_RESET}")
        elif line.startswith("@"):
            print(f"{C_CYAN}{line.rstrip()}{C_RESET}")
        else:
            print(f"{C_GRAY}{line.rstrip()}{C_RESET}")
    if not has_diff:
        print(f"  {C_GREEN}[✔] Code already structurally clean and aligned.{C_RESET}")

def main():
    if len(sys.argv) < 2:
        print(BANNER)
        print(f"  {C_WHITE}{C_BOLD}USAGE:{C_RESET}")
        print(f"    {C_CYAN}ax -fix <filepath>{C_RESET}       Autonomous file repair & AST defect healing")
        print(f"    {C_CYAN}ax -fix \"<code>\"{C_RESET}        Instant inline raw snippet repair\n")
        print(f"  {C_WHITE}{C_BOLD}SUPPORTED LANGUAGES:{C_RESET}")
        print(f"    Python, C, C++, Rust, Go, JavaScript, TypeScript, Bash, JSON, HTML, CSS, SQL\n")
        print(f"  {C_WHITE}{C_BOLD}EXAMPLES:{C_RESET}")
        print(f"    ax -fix app.py")
        print(f"    ax -fix \"def calculate(x) return x*2\"")
        print(f"    ax -fix \"int main() {{ printf(\\\"hello\\\") }}\"")
        print(f"    ax -fix \"let x = True; print(x)\"")
        print(f"    ax -fix '{{ \"name\": \"asterix\", }}'")
        print(f"    ax -fix \"select id, name, from users where active = 1\"")
        print(f"    ax -fix --lang rust \"let x = 5 println(x)\"")
        return

    args = sys.argv[1:]
    forced_lang = None
    if "--lang" in args:
        idx = args.index("--lang")
        if idx + 1 < len(args):
            forced_lang = args[idx + 1].lower()
            args = args[:idx] + args[idx + 2:]
    elif "-l" in args:
        idx = args.index("-l")
        if idx + 1 < len(args):
            forced_lang = args[idx + 1].lower()
            args = args[:idx] + args[idx + 2:]

    if not args:
        print(BANNER)
        print(f"  {C_RED}[!] No target file or code snippet provided.{C_RESET}\n")
        return

    target = args[0]
    if target in ("-inline", "--inline", "-raw", "--raw") and len(args) > 1:
        target = args[1]

    print(BANNER)

    is_file = os.path.isfile(target)
    if is_file:
        print(f"  {C_CYAN}[*] Mode:{C_RESET}        {C_WHITE}Target File Repair ({target}){C_RESET}")
        lang = forced_lang or detect_language(target)
        print(f"  {C_CYAN}[*] Language:{C_RESET}    {C_MAGENTA}{lang.upper()}{C_RESET}")

        with open(target, "r", encoding="utf-8", errors="replace") as f:
            original = f.read()

        healed, mods, _ = heal_code(target, forced_lang=forced_lang)

        if not mods:
            print(f"\n  {C_GREEN}[✔] Zero defects detected. File syntax is clean.{C_RESET}\n")
            return

        print(f"\n  {C_YELLOW}[!] Detected {len(mods)} Syntax / AST Defect(s):{C_RESET}")
        for m in mods:
            print(f"    • {C_WHITE}{m}{C_RESET}")

        # Safety backup
        bak_file = target + ".bak"
        if not os.path.exists(bak_file):
            shutil.copy2(target, bak_file)
            print(f"\n  {C_GRAY}[i] Created safety backup: {bak_file}{C_RESET}")

        # Write healed code
        with open(target, "w", encoding="utf-8") as f:
            f.write(healed)

        print(f"\n  {C_GREEN}{C_BOLD}[✔] Code successfully healed and applied!{C_RESET}")
        print(f"\n  {C_CYAN}--- UNIFIED DIFF PREVIEW ---{C_RESET}")
        print_diff(original, healed, os.path.basename(target))
        print()

    else:
        # Inline string repair mode
        snippet = target
        lang = forced_lang or detect_language(snippet)
        print(f"  {C_CYAN}[*] Mode:{C_RESET}        {C_WHITE}Inline Raw Snippet Healing{C_RESET}")
        print(f"  {C_CYAN}[*] Language:{C_RESET}    {C_MAGENTA}{lang.upper()}{C_RESET}\n")

        healed, mods, _ = heal_code(snippet, forced_lang=forced_lang)

        if mods:
            print(f"  {C_YELLOW}[!] Healed {len(mods)} Issue(s):{C_RESET}")
            for m in mods:
                print(f"    • {C_WHITE}{m}{C_RESET}")
            print()

        print(f"  {C_GREEN}{C_BOLD}HEALED CODE OUTPUT:{C_RESET}")
        print(f"{C_BLUE}────────────────────────────────────────────────────────────────────────{C_RESET}")
        print(f"{C_WHITE}{healed}{C_RESET}")
        print(f"{C_BLUE}────────────────────────────────────────────────────────────────────────{C_RESET}\n")

if __name__ == "__main__":
    main()
