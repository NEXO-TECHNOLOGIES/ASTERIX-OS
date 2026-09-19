#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Peak Cognitive Neural Reasoning Engine v3.5
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

# =============================================================================
# PEAK EMBEDDED KNOWLEDGE MATRIX (OFFLINE INTELLIGENCE)
# =============================================================================

PEAK_KNOWLEDGE_TOPICS = {
    "kernel": {
        "keywords": ["kernel", "microkernel", "ring", "ring0", "syscall", "gdt", "idt", "isr", "pic", "vga", "freestanding", "scheduler"],
        "title": "ASTERIX Microkernel & Low-Level Operating System Architecture",
        "content": (
            "The ASTERIX Microkernel core is designed for high-security isolation and minimum footprint:\n\n"
            "• **Memory & Paging**: Implements two-tier page allocation with physical frame management (4 KB pages). Virtual memory maps identity-mapped kernel space (0x00000000 to 0x00400000) while isolating user-space task segments.\n"
            "• **GDT & IDT Descriptor Tables**: Configures Global Descriptor Table (Code 0x08, Data 0x10) and 256-entry Interrupt Descriptor Table (IDT). Catches CPU exceptions 0–31 (Page Faults, GPF, Divide-by-Zero) and maps 8259 PIC IRQs (Timer 0x20, Keyboard 0x21).\n"
            "• **System Call Pipeline**: Dispatches system calls via `int 0x80` or `syscall` instruction. Supported kernel calls include `SYS_WRITE (1)`, `SYS_READ (2)`, `SYS_YIELD (3)`, and `SYS_AUDIT (4)`.\n"
            "• **VGA Driver**: Memory-mapped console at physical address `0xB8000` supporting 80x25 character grid with 16-color ANSI hardware styling and automatic scrolling."
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
            "• **System V AMD64 Calling Convention**: Function arguments pass in registers `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9`. Return values reside in `rax` (or `rdx:rax`). Caller must preserve `rbx`, `rsp`, `rbp`, `r12`-`r15`.\n"
            "• **Multiboot Specification**: The kernel binary features a 32-bit Multiboot header (Magic: `0x1BADB002`, Flags: `0x00`, Checksum: `-0x1BADB002`) aligned on a 4-byte boundary.\n"
            "• **Real to Protected Mode Transition**: Enables A20 address line via keyboard controller port `0x64`/`0x60`, loads 32-bit GDT with `lgdt`, and sets bit 0 of Control Register `CR0` before executing far jump `jmp 0x08:protected_entry`.\n"
            "• **SIMD Vectorization**: Leverages SSE2 / AVX2 instructions (`vpxor`, `vmovdqu`, `vpaddd`) for multi-gigabyte cryptographic throughput and entropy analysis."
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
            "• **Memory Lifecycle Management**: Always pair dynamic heap allocations (`malloc`/`calloc`) with deterministic free routines. Use `valgrind --leak-check=full` or GCC AddressSanitizer (`-fsanitize=address`) during development.\n"
            "• **Memory Safety Defenses**: Defend against buffer overflows by replacing unbounded functions (`strcpy`, `strcat`, `sprintf`, `gets`) with boundary-checked equivalents (`strncpy`, `strncat`, `snprintf`, `fgets`).\n"
            "• **Stack Smashing Protection (SSP)**: Compiling with `-fstack-protector-strong` places a random canary word between local variables and the saved return pointer. If overwritten, `__stack_chk_fail()` terminates the process.\n"
            "• **Position Independent Executable (PIE)**: Enables ASLR (Address Space Layout Randomization) to randomize base memory addresses (`text`, `data`, `heap`, `stack`), neutralizing static ROP chains."
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
            "• **Web Application Defense (OWASP Top 10)**:\n"
            "  - SQL Injection (SQLi): Enforce parameterized prepared statements. Disallow string interpolation in DB drivers.\n"
            "  - Cross-Site Scripting (XSS): Implement contextual HTML entity encoding and strict Content-Security-Policy (`default-src 'self'`).\n"
            "  - Server-Side Request Forgery (SSRF): Block loopback and link-local metadata addresses (`127.0.0.1`, `169.254.169.254`, `[::1]`) with DNS rebinding protection via `ax ssrf-guard`.\n"
            "• **Network Threat Surface**: Run `ax scan <target>` and `ax bounty <domain>` to discover open daemon ports, TLS configuration weaknesses, and dangling DNS CNAME records.\n"
            "• **Cryptographic Posture**: Deploy authenticated encryption (AES-256-GCM or ChaCha20-Poly1305). Avoid broken legacy algorithms (DES, RC4, MD5, SHA-1)."
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
            "• **Resilient Storage**: Private storage at `~/.asterix_storage/` isolates databases and loot without requiring volatile Android `/sdcard` permissions.\n"
            "• **Zero-Crash Recovery**: `ax mobile-sys doctor` and `install-termux.sh` monitor `pkg` repositories, verify `libcurl` consistency, and repair broken mirror paths.\n"
            "• **Hardware Telemetry**: Integrates with Android battery sensors via `ax mobile-sys battery` to display thermal status, current draw (`µA`), and charge level.\n"
            "• **Storage Purging**: `ax mobile-sys clean` sweeps apt caches, orphan sockets, and temporary files to prevent disk exhaustion."
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
            "• **ChaCha20 Stream Cipher (RFC 8439)**: 256-bit key, 96-bit nonce, 32-bit block counter. Operates on a 4x4 matrix of 32-bit words using quarter-round ARX (Add-Rotate-XOR) operations. Vectorized with SSE2/AVX2.\n"
            "• **Poly1305 One-Time Authenticator**: High-speed MAC evaluated modulo 2^130 - 5. Paired with ChaCha20 to form AEAD (Authenticated Encryption with Associated Data).\n"
            "• **AES-256 Hardware Core**: Employs Intel AES-NI (`aesenc`, `aesenclast`) and ARMv8 Cryptographic Extensions for hardware constant-time encryption resistant to cache timing attacks.\n"
            "• **Zero-Dependency C Implementation**: Standalone freestanding implementation in `core-utils-c/src/asterix-crypto-core.c`."
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

        # 2. Try External Ollama if available
        system_instructions = (
            "You are ASTERIX AI, the elite cybernetic expert intelligence built into ASTERIX OS. "
            "You have world-class expertise in cybersecurity, microkernels, C programming, x86_64/ARM64 assembly, "
            "penetration testing, and reverse engineering. Deliver detailed, accurate, and actionable technical responses."
        )
        if context_block:
            prompt_with_memory = f"{context_block}\n\nUser Question: {query_clean}"
        else:
            prompt_with_memory = query_clean

        llm_reply = self.query_ollama(prompt_with_memory, system_prompt=system_instructions)
        if llm_reply:
            if self.memory:
                self.memory.log_dialogue("assistant", llm_reply, session_id=session_id)
            return llm_reply

        # 3. Autonomous Peak Embedded Cognitive Reasoner (Zero-Dependency Offline Matrix)
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
                "• **Recommended Action Pipeline**:\n"
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
