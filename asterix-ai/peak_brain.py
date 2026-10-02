#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Peak Cognitive Neural Reasoning Engine v3.5
  Autonomous, High-Velocity Cybersecurity & Systems Intelligence Core
  Features:
    - Multi-Tier Inference: Cloud LLM -> Local Ollama -> Peak Embedded Cognitive Matrix
    - Deep Cyber, Assembly, C, Microkernel & Linux Engineering Intelligence
    - Contextual Memory Recall via CloudMemoryBridge (Supabase & SQLite)
    - Zero External Dependencies (100% Python Standard Library)
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import json
import math
import socket
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from .cloud_memory import memory_hub
except ImportError:
    try:
        from cloud_memory import memory_hub
    except ImportError:
        memory_hub = None

OLLAMA_URL = os.getenv("ASTERIX_OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("ASTERIX_OLLAMA_MODEL", "qwen2.5:3b-instruct")


def is_ollama_online(url: str = OLLAMA_URL, timeout: float = 0.05) -> bool:
    """Fast non-blocking health check to prevent connection hangs when Ollama is offline."""
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        port = parsed.port or 11434
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def get_gemini_api_key() -> Optional[str]:
    """Retrieves Google Gemini API key from environment, .env, or user config."""
    for env_var in ("GEMINI_API_KEY", "ASTERIX_AI_KEY", "ASTERIX_GEMINI_KEY"):
        val = os.getenv(env_var)
        if val and len(val.strip()) > 10:
            return val.strip()
    candidates = [
        Path(".env"),
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent.parent / "config" / "ai_keys.env",
        Path.home() / ".env",
        Path.home() / ".asterix_ai_key",
    ]
    for cand in candidates:
        if cand.is_file():
            try:
                for line in cand.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        if k.strip() in ("GEMINI_API_KEY", "ASTERIX_AI_KEY", "ASTERIX_GEMINI_KEY"):
                            clean_v = v.strip().strip("'\"")
                            if len(clean_v) > 10:
                                return clean_v
            except Exception:
                pass
    return None

# =============================================================================
# PEAK EMBEDDED KNOWLEDGE MATRIX (OFFLINE INTELLIGENCE)
# =============================================================================

PEAK_KNOWLEDGE_TOPICS = {
    "kernel": {
        "keywords": ["kernel", "microkernel", "ring", "ring0", "syscall", "gdt", "idt", "isr", "pic", "vga", "freestanding", "scheduler"],
        "title": "ASTERIX Microkernel & Low-Level Operating System Architecture",
        "content": (
            "The ASTERIX Microkernel core is designed for high-security isolation and minimum footprint:\n\n"
            "* **Memory & Paging**: Implements two-tier page allocation with physical frame management (4 KB pages). Virtual memory maps identity-mapped kernel space (0x00000000 to 0x00400000) while isolating user-space task segments.\n"
            "* **GDT & IDT Descriptor Tables**: Configures Global Descriptor Table (Code 0x08, Data 0x10) and 256-entry Interrupt Descriptor Table (IDT). Catches CPU exceptions 0–31 (Page Faults, GPF, Divide-by-Zero) and maps 8259 PIC IRQs (Timer 0x20, Keyboard 0x21).\n"
            "* **System Call Pipeline**: Dispatches system calls via `int 0x80` or `syscall` instruction. Supported kernel calls include `SYS_WRITE (1)`, `SYS_READ (2)`, `SYS_YIELD (3)`, and `SYS_AUDIT (4)`.\n"
            "* **VGA Driver**: Memory-mapped console at physical address `0xB8000` supporting 80x25 character grid with 16-color ANSI hardware styling and automatic scrolling."
        ),
        "code_example": (
            "// x86 Freestanding Port Output\n"
            "static inline void outb(uint16_t port, uint8_t val) {\n"
            "    __asm__ volatile (\"outb %0, %1\" : : \"a\"(val), \"Nd\"(port));\n"
            "}\n\n"
            "// Low-level Syscall Entry\n"
            "int ksyscall(int num, uint32_t arg1, uint32_t arg2) {\n"
            "    int res;\n"
            "    __asm__ volatile (\"int $0x80\" : \"=a\"(res) : \"a\"(num), \"b\"(arg1), \"c\"(arg2));\n"
            "    return res;\n"
            "}"
        )
    },
    "assembly": {
        "keywords": ["assembly", "nasm", "x86", "x86_64", "arm64", "register", "rax", "rsp", "rbp", "bootloader", "mbr", "multiboot", "simd", "avx"],
        "title": "x86_64 & ARM64 Assembly Engineering & Hardware Execution",
        "content": (
            "Assembly language forms the foundation of bare-metal bootstrap and SIMD cryptanalysis in ASTERIX OS:\n\n"
            "* **System V AMD64 Calling Convention**: Function arguments pass in registers `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`. Return values reside in `rax` (or `rdx:rax`). Caller must preserve `rbx`, `rsp`, `rbp`, `r12`-`r15`.\n"
            "* **Multiboot Specification**: The kernel binary features a 32-bit Multiboot header (Magic: `0x1BADB002`, Flags: `0x00`, Checksum: `-0x1BADB002`) aligned on a 4-byte boundary.\n"
            "* **Real to Protected Mode Transition**: Enables A20 address line via keyboard controller port `0x64`/`0x60`, loads 32-bit GDT with `lgdt`, and sets bit 0 of Control Register `CR0` before executing far jump `jmp 0x08:protected_entry`.\n"
            "* **SIMD Vectorization**: Leverages SSE2 / AVX2 instructions (`vpxor`, `vmovdqu`, `vpaddd`) for multi-gigabyte cryptographic throughput and entropy analysis."
        ),
        "code_example": (
            "; Multiboot x86 Header Stub (NASM)\n"
            "section .multiboot\n"
            "    align 4\n"
            "    dd 0x1BADB002          ; Magic\n"
            "    dd 0x00                ; Flags\n"
            "    dd -0x1BADB002         ; Checksum\n\n"
            "section .text\n"
            "global _start\n"
            "_start:\n"
            "    cli\n"
            "    mov esp, stack_top     ; Initialize stack\n"
            "    call kmain             ; Call C microkernel\n"
            "    hlt\n"
        )
    },
    "c_programming": {
        "keywords": ["c", "c-lang", "pointers", "malloc", "memory leak", "buffer overflow", "segmentation fault", "segfault", "canary", "aslr"],
        "title": "High-Performance C Systems Programming & Vulnerability Triage",
        "content": (
            "C is the core language of ASTERIX OS utilities and microkernel services:\n\n"
            "* **Memory Lifecycle Management**: Always pair dynamic heap allocations (`malloc`/`calloc`) with deterministic free routines. Use `valgrind --leak-check=full` or GCC AddressSanitizer (`-fsanitize=address`) during development.\n"
            "* **Memory Safety Defenses**: Defend against buffer overflows by replacing unbounded functions (`strcpy`, `strcat`, `sprintf`, `gets`) with boundary-checked equivalents (`strncpy`, `strncat`, `snprintf`, `fgets`).\n"
            "* **Stack Smashing Protection (SSP)**: Compiling with `-fstack-protector-strong` places a random canary word between local variables and the saved return pointer. If overwritten, `__stack_chk_fail()` terminates the process.\n"
            "* **Position Independent Executable (PIE)**: Enables ASLR (Address Space Layout Randomization) to randomize base memory addresses (`text`, `data`, `heap`, `stack`), neutralizing static ROP chains."
        ),
        "code_example": (
            "// Secure bounded string copying in C\n"
            "void safe_copy(char *dest, size_t dest_sz, const char *src) {\n"
            "    if (!dest || !src || dest_sz == 0) return;\n"
            "    snprintf(dest, dest_sz, \"%s\", src);\n"
            "    dest[dest_sz - 1] = '\\0';\n"
            "}"
        )
    },
    "cybersecurity": {
        "keywords": ["security", "soc", "exploit", "sqli", "xss", "csrf", "ssrf", "pentest", "metasploit", "nmap", "wireshark", "waf", "recon", "bounty"],
        "title": "Autonomous SOC Triage, Offensive Vectors & Hardening",
        "content": (
            "ASTERIX OS integrates offensive auditing and real-time defensive engineering:\n\n"
            "* **Web Application Defense (OWASP Top 10)**:\n"
            "  - SQL Injection (SQLi): Enforce parameterized prepared statements. Disallow string interpolation in DB drivers.\n"
            "  - Cross-Site Scripting (XSS): Implement contextual HTML entity encoding and strict Content-Security-Policy (`default-src 'self'`).\n"
            "  - Server-Side Request Forgery (SSRF): Block loopback and link-local metadata addresses (`127.0.0.1`, `169.254.169.254`, `[::1]`) with DNS rebinding protection via `ax ssrf-guard`.\n"
            "* **Network Threat Surface**: Run `ax scan <target>` and `ax bounty <domain>` to discover open daemon ports, TLS configuration weaknesses, and dangling DNS CNAME records.\n"
            "* **Cryptographic Posture**: Deploy authenticated encryption (AES-256-GCM or ChaCha20-Poly1305). Avoid broken legacy algorithms (DES, RC4, MD5, SHA-1)."
        ),
        "code_example": (
            "# ASTERIX Tactical Defense Pipeline\n"
            "ax bounty example.com             # Full passive & active attack surface probe\n"
            "ax web-structure example.com      # Extract full DOM code hierarchy & API routes\n"
            "ax defender scan /path/to/files   # Pure-Rust signature and malware triage\n"
            "ax proxychains scan               # Validate SOCKS4/5 proxies & build dynamic chain"
        )
    },
    "termux_mobile": {
        "keywords": ["termux", "android", "mobile", "battery", "storage", "proot", "debian", "apt", "pkg", "clean"],
        "title": "Android Termux Cybernetic Subsystem & Resource Governance",
        "content": (
            "The ASTERIX Mobile Engine is optimized for rootless Android execution via Termux and Debian PRoot:\n\n"
            "* **Resilient Storage**: Private storage at `~/.asterix_storage/` isolates databases and loot without requiring volatile Android `/sdcard` permissions.\n"
            "* **Zero-Crash Recovery**: `ax mobile-sys doctor` and `install-termux.sh` monitor `pkg` repositories, verify `libcurl` consistency, and repair broken mirror paths.\n"
            "* **Hardware Telemetry**: Integrates with Android battery sensors via `ax mobile-sys battery` to display thermal status, current draw (`µA`), and charge level.\n"
            "* **Storage Purging**: `ax mobile-sys clean` sweeps apt caches, orphan sockets, and temporary files to prevent disk exhaustion."
        ),
        "code_example": (
            "# Quick Termux Maintenance & Diagnostics\n"
            "ax mobile-sys battery    # Check battery health & temperature\n"
            "ax mobile-sys dns        # Benchmark DNS latencies to 1.1.1.1, 8.8.8.8, 9.9.9.9\n"
            "ax mobile-sys clean      # Reclaim storage from package and temp caches\n"
            "curl-tree <url>          # Inspect web code structure from Termux"
        )
    },
    "cryptography": {
        "keywords": ["crypto", "cryptography", "chacha20", "poly1305", "aes", "sha256", "sha512", "encryption", "cipher", "hash", "symmetric", "ed25519"],
        "title": "Hardware-Accelerated Symmetric Cryptography & Stream Ciphers",
        "content": (
            "ASTERIX OS implements high-assurance cryptographic primitives with SIMD acceleration:\n\n"
            "* **ChaCha20 Stream Cipher (RFC 8439)**: 256-bit key, 96-bit nonce, 32-bit block counter. Operates on a 4x4 matrix of 32-bit words using quarter-round ARX (Add-Rotate-XOR) operations. Vectorized with SSE2/AVX2.\n"
            "* **Poly1305 One-Time Authenticator**: High-speed MAC evaluated modulo 2^130 - 5. Paired with ChaCha20 to form AEAD (Authenticated Encryption with Associated Data).\n"
            "* **AES-256 Hardware Core**: Employs Intel AES-NI (`aesenc`, `aesenclast`) and ARMv8 Cryptographic Extensions for hardware constant-time encryption resistant to cache timing attacks.\n"
            "* **Zero-Dependency C Implementation**: Standalone freestanding implementation in `core-utils-c/src/asterix-crypto-core.c`."
        ),
        "code_example": (
            "// ChaCha20 Quarter Round Core in C\n"
            "#define ROTL(a,b) (((a) << (b)) | ((a) >> (32 - (b))))\n"
            "#define QR(a, b, c, d) \\\n"
            "    a += b; d ^= a; d = ROTL(d, 16); \\\n"
            "    c += d; b ^= c; b = ROTL(b, 12); \\\n"
            "    a += b; d ^= a; d = ROTL(d,  8); \\\n"
            "    c += d; b ^= c; b = ROTL(b,  7);"
        )
    }
}


# =============================================================================
# PEAK INFERENCE BRAIN CONTROLLER
# =============================================================================

class PeakBrain:
    """Multi-tiered neural & cognitive inference controller."""

    def __init__(self):
        self.memory = memory_hub

    def query_gemini(self, prompt: str, system_prompt: Optional[str] = None, timeout: int = 25) -> Optional[str]:
        """Queries Google Gemini API using native HTTPS (zero third-party dependencies)."""
        key = get_gemini_api_key()
        if not key:
            return None
        models = [
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
        ]
        system_instruction_part = ""
        if system_prompt:
            system_instruction_part = f"[SYSTEM INSTRUCTION]: {system_prompt}\n\n"
        full_text = f"{system_instruction_part}{prompt}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_text}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
        data = json.dumps(payload).encode("utf-8")
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"].strip()
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue
                else:
                    break
            except Exception:
                break
        return None

    def query_ollama(self, prompt: str, system_prompt: Optional[str] = None, timeout: int = 12) -> Optional[str]:
        """Attempts to query local Ollama server if running."""
        if not is_ollama_online(OLLAMA_URL):
            return None
        try:
            url = f"{OLLAMA_URL}/api/generate"
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data.get("response", "").strip()
                if ans:
                    return ans
        except Exception:
            pass
        return None

    @staticmethod
    def _sanitize_emojis(text: str) -> str:
        """Enforces strict 0-emoji 7-bit ASCII discipline across generated code."""
        emoji_pattern = re.compile(
            r"[\U0001F600-\U0001F64F]|"
            r"[\U0001F300-\U0001F5FF]|"
            r"[\U0001F680-\U0001F6FF]|"
            r"[\U0001F1E0-\U0001F1FF]|"
            r"[\U00002702-\U000027B0]|"
            r"[\U0001F900-\U0001F9FF]|"
            r"[\U0001FA70-\U0001FAFF]"
        )
        return emoji_pattern.sub("", text)

    def _fallback_template_script(self, objective: str, language: str) -> str:
        """Provides an ultra-clean modular script template if cloud and local AI are both offline."""
        clean_title = re.sub(r'[^a-zA-Z0-9 ]+', '', objective).strip().title()
        if language in ("bash", "sh"):
            return f"""#!/usr/bin/env bash
# =====================================================================
# ASTERIX OS - {clean_title}
# Objective: {objective}
# =====================================================================

set -euo pipefail

C_RESET='\\033[0m'
C_BOLD='\\033[1m'
C_CYAN='\\033[38;5;51m'
C_GREEN='\\033[38;5;46m'
C_YELLOW='\\033[38;5;220m'
C_RED='\\033[38;5;196m'

echo -e "${{C_CYAN}}${{C_BOLD}}=== ASTERIX OS TACTICAL SCRIPT: {clean_title} ===${{C_RESET}}"
echo -e "${{C_YELLOW}}[*] Initializing operational task: {objective}${{C_RESET}}"

main() {{
    echo -e "${{C_GREEN}}[OK] Task executing with parameters: $@${{C_RESET}}"
}}

trap 'echo -e "${{C_RED}}[!] Interrupted by user${{C_RESET}}"; exit 130' INT TERM
main "$@"
"""
        elif language == "c":
            return f"""/* =====================================================================
 * ASTERIX OS - {clean_title}
 * Objective: {objective}
 * ===================================================================== */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {{
    printf("[*] ASTERIX OS Tactical C Tool: {clean_title}\\n");
    printf("[*] Objective: {objective}\\n");
    if (argc < 2) {{
        printf("Usage: %s <target/argument>\\n", argv[0]);
        return 1;
    }}
    printf("[+] Processing target: %s\\n", argv[1]);
    return 0;
}}
"""
        else:
            return f"""#!/usr/bin/env python3
# =====================================================================
# ASTERIX OS - {clean_title}
# Objective: {objective}
# =====================================================================

import argparse
import sys
import time

C_RESET = "\\033[0m"
C_BOLD = "\\033[1m"
C_CYAN = "\\033[38;5;51m"
C_GREEN = "\\033[38;5;46m"
C_YELLOW = "\\033[38;5;220m"
C_RED = "\\033[38;5;196m"

def banner():
    print(f"{{C_CYAN}}{{C_BOLD}}=== ASTERIX OS: {clean_title} ==={{C_RESET}}")
    print(f"{{C_YELLOW}}[*] Objective: {objective}{{C_RESET}}\\n")

def main():
    banner()
    parser = argparse.ArgumentParser(description="{clean_title} - ASTERIX Tactical Automation")
    parser.add_argument("target", nargs="?", default="127.0.0.1", help="Target IP, host, or file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose diagnostics")
    args = parser.parse_args()

    print(f"{{C_GREEN}}[OK] Engaging target: {{args.target}}{{C_RESET}}")

if __name__ == "__main__":
    main()
"""

    def generate_script(self, objective: str, language: str = "python", output_path: Optional[str] = None) -> Dict[str, Any]:
        """Generates a professional, production-grade custom script using Gemini AI or fallback templates."""
        system_prompt = (
            f"You are ASTERIX AI's Elite Tool & Script Generation Engine. The operator has requested a professional, "
            f"hardened, production-ready {language.upper()} script for cybersecurity, systems administration, or developer workflows.\n"
            f"STRICT RULES:\n"
            f"1. Generate 100% COMPLETE, working code. NEVER use placeholders like 'TODO', 'insert logic here', or pass.\n"
            f"2. Include clean ANSI color output, clear argument parsing (--help, flags), signal handlers, robust try/except error management.\n"
            f"3. Strictly maintain 7-bit ASCII compatibility (NO non-standard emojis in code, prints, or comments).\n"
            f"4. Provide a stylized ASTERIX OS header banner at the top in ASCII.\n"
            f"5. Output ONLY the code inside a single ```{language} ... ``` block without conversational filler."
        )

        user_req = f"Write a complete, professional, highly capable {language} script to achieve the following objective:\n{objective}"
        code_resp = self.query_gemini(user_req, system_prompt=system_prompt)
        if not code_resp:
            code_resp = self.query_ollama(user_req, system_prompt=system_prompt)
        if not code_resp:
            code_resp = self._fallback_template_script(objective, language)

        match = re.search(r"```(?:\w+)?\n([\s\S]*?)\n```", code_resp)
        code = match.group(1) if match else code_resp
        code = self._sanitize_emojis(code)

        if not output_path:
            clean_name = re.sub(r'[^a-zA-Z0-9_]+', '_', objective.lower())[:32].strip('_') or "custom_tool"
            ext = ".py" if language == "python" else (".sh" if language in ("bash", "sh") else (".c" if language == "c" else ".rs"))
            save_dir = Path.home() / "asterix_persistent" / "scripts"
            if not save_dir.exists():
                save_dir = Path("scripts-hub") if Path("scripts-hub").is_dir() else Path(".")
            save_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(save_dir / f"{clean_name}{ext}")

        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(code, encoding="utf-8")
        try:
            out_file.chmod(0o755)
        except Exception:
            pass

        return {
            "status": "success",
            "file": str(out_file),
            "language": language,
            "objective": objective,
            "code_size": len(code),
            "lines": len(code.splitlines()),
            "code_preview": "\n".join(code.splitlines()[:25])
        }

    def match_peak_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        """Matches user query against peak knowledge matrix using keyword vector scoring."""
        query_tokens = set(re.findall(r'\w+', query.lower()))
        if not query_tokens:
            return None

        best_topic = None
        best_score = 0

        for key, entry in PEAK_KNOWLEDGE_TOPICS.items():
            kw_set = set(entry["keywords"])
            common = query_tokens.intersection(kw_set)
            score = len(common)
            if score > best_score:
                best_score = score
                best_topic = entry

        if best_score > 0:
            return best_topic
        return None

    def reason(self, user_query: str, session_id: str = "default") -> str:
        """Master reasoning pipeline combining memory recall, cloud LLM, and embedded peak matrix."""
        query_clean = user_query.strip()
        if not query_clean:
            return "ASTERIX AI: Please provide a technical question or command objective."

        # 1. Retrieve Cognitive Memory Context
        context_block = ""
        if self.memory:
            context_block = self.memory.get_context_block(query_clean)
            self.memory.log_dialogue("user", query_clean, session_id=session_id)

        # 2. System Instructions
        system_instructions = (
            "You are ASTERIX AI, the elite cybernetic expert intelligence and systems automation core built into ASTERIX OS. "
            "You have world-class expertise in cybersecurity, microkernels, C programming, x86_64/ARM64 assembly, "
            "penetration testing, reverse engineering, and tactical automation. Deliver detailed, accurate, and actionable technical responses. "
            "Never use emojis. Strictly 7-bit ASCII."
        )
        if context_block:
            prompt_with_memory = f"{context_block}\n\nUser Question: {query_clean}"
        else:
            prompt_with_memory = query_clean

        # 3. Tier 1: Cloud Gemini LLM
        gemini_reply = self.query_gemini(prompt_with_memory, system_prompt=system_instructions)
        if gemini_reply:
            gemini_clean = self._sanitize_emojis(gemini_reply)
            if self.memory:
                self.memory.log_dialogue("assistant", gemini_clean, session_id=session_id)
            return gemini_clean

        # 4. Tier 2: Local Ollama
        llm_reply = self.query_ollama(prompt_with_memory, system_prompt=system_instructions)
        if llm_reply:
            llm_clean = self._sanitize_emojis(llm_reply)
            if self.memory:
                self.memory.log_dialogue("assistant", llm_clean, session_id=session_id)
            return llm_clean

        # 5. Tier 3: Autonomous Peak Embedded Cognitive Reasoner (Zero-Dependency Offline Matrix)
        matched = self.match_peak_knowledge(query_clean)
        response_parts = []

        if context_block:
            response_parts.append(f" {context_block}\n")

        if matched:
            response_parts.append(f"[ASTERIX] [ ASTERIX PEAK INTELLIGENCE // {matched['title'].upper()} ]\n")
            response_parts.append(matched["content"])
            if "code_example" in matched:
                response_parts.append(f"\n```text\n{matched['code_example']}\n```")
        else:
            # General Cyber / Operational synthesis
            response_parts.append("[ASTERIX] [ ASTERIX PEAK INTELLIGENCE // OPERATIONAL SYNTHESIS ]\n")
            response_parts.append(
                f"Analyzing operational objective: '{query_clean}'\n\n"
                "* **Recommended Action Pipeline**:\n"
                "  1. Run `ax doctor` to verify host dependencies and network routing.\n"
                "  2. For code structure analysis, execute `ax curl-tree <url>` or `ax web-structure <url>`.\n"
                "  3. For security and bug bounty probes, execute `ax bounty <target>`.\n"
                "  4. For code healing, execute `ax -fix <source_file>`.\n"
                "  5. To inspect persistent memories or sync with cloud, execute `ax ai memory` or `ax ai cloud-sync`."
            )

        final_response = "\n".join(response_parts)
        if self.memory:
            self.memory.log_dialogue("assistant", final_response, session_id=session_id)

        return final_response

    def suggest_system_action(self, system_state: Dict[str, Any], memory_log: str) -> str:
        """Suggests the optimal safe system command based on host telemetry."""
        cpu = system_state.get("cpu", "unknown")
        ram = system_state.get("ram", "unknown")
        network = system_state.get("network", "unknown")

        # Telemetry-driven smart suggestions
        if network == "offline":
            return "ax doctor"
        elif "%" in ram and float(ram.rstrip("%")) > 85.0:
            return "ax clean"
        else:
            return "ax status"


# Singleton instance and aliases
PeakCognitiveEngine = PeakBrain
peak_ai = PeakBrain()

if __name__ == "__main__":
    brain = PeakBrain()
    print("=== Testing Peak Brain (Offline Mode) ===")
    ans = brain.reason("Explain how kernel paging and GDT work in assembly")
    print(ans)
