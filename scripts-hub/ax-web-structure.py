#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Web Code Structure & Deep Source Extraction Engine
  Command: ax web-structure / ax curl-tree / ax webdump / ax websnoop
  Zero External Dependencies: 100% Python Standard Library
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import json
import time
import ssl
import socket
import argparse
import urllib.request
import urllib.parse
import urllib.error
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any

# Ensure UTF-8 output across Windows, Linux, and Android Termux
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ANSI 256-Color Cyber Palette
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_CYAN    = "\033[38;5;51m"
C_GREEN   = "\033[38;5;46m"
C_YELLOW  = "\033[38;5;220m"
C_RED     = "\033[38;5;196m"
C_MAGENTA = "\033[38;5;201m"
C_WHITE   = "\033[38;5;231m"
C_GRAY    = "\033[38;5;244m"
C_BLUE    = "\033[38;5;45m"
C_ORANGE  = "\033[38;5;208m"

BANNER = f"""{C_CYAN}{C_BOLD}╔══════════════════════════════════════════════════════════════════════════╗
║{C_WHITE}{C_BOLD}   🌌 ASTERIX OS — WEB CODE STRUCTURE & DEEP SOURCE ENGINE v3.0          {C_RESET}{C_CYAN}║
║{C_MAGENTA}   [ Full DOM Hierarchy • JS/CSS Asset Tree • API Routes • Offline Dump ]  {C_RESET}{C_CYAN}║
╚══════════════════════════════════════════════════════════════════════════╝{C_RESET}"""

SEP = f"{C_BLUE}{'─'*74}{C_RESET}"
HSEP = f"{C_CYAN}{'═'*74}{C_RESET}"

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 AsterixWebEngine/3.0"

# Common Tech Signatures
FRAMEWORK_SIGNATURES = [
    ("React", [r"_reactRoot", r"react\.production", r"react-dom", r"data-reactroot", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"]),
    ("Next.js", [r"/_next/", r"__NEXT_DATA__", r"next/dist"]),
    ("Vue.js", [r"data-v-[a-f0-9]+", r"vue\.runtime", r"vue\.global", r"__VUE__"]),
    ("Nuxt.js", [r"/_nuxt/", r"__NUXT__"]),
    ("Angular", [r"ng-version", r"ng-app", r"vendor/angular", r"_nghost", r"_ngcontent"]),
    ("Svelte", [r"svelte-[a-z0-9]+", r"__svelte"]),
    ("Tailwind CSS", [r"tailwind", r"border-t-transparent", r"grid-cols-", r"sm:px-", r"md:flex"]),
    ("Bootstrap", [r"bootstrap(?:\.min)?\.css", r"bootstrap(?:\.min)?\.js", r"class=[\"'][^\"']*\b(?:btn-primary|navbar-nav|container-fluid)\b"]),
    ("jQuery", [r"jquery(?:\.min)?\.js", r"\$\.fn\.jquery", r"jQuery v[0-9]"]),
    ("WordPress", [r"/wp-content/", r"/wp-includes/", r"wp-json", r"name=[\"']generator[\"'][^>]*WordPress"]),
    ("Shopify", [r"cdn\.shopify\.com", r"Shopify\.theme", r"ShopifyAnalytics"]),
    ("Django", [r"csrfmiddlewaretoken", r"__admin__"]),
    ("Laravel", [r"laravel_session", r"XSRF-TOKEN"]),
]

SERVER_SIGNATURES = [
    ("Cloudflare", ["cloudflare", "cf-ray", "__cfduid"]),
    ("Nginx", ["nginx"]),
    ("Apache", ["apache"]),
    ("Vercel", ["vercel", "x-vercel-id"]),
    ("Netlify", ["netlify"]),
    ("AWS CloudFront", ["cloudfront", "x-amz-cf-id"]),
    ("Fastly", ["fastly"]),
    ("Akamai", ["akamai"]),
]


# =============================================================================
# 1. DOM TREE BUILDER & HTML STRUCTURAL PARSER
# =============================================================================

class DOMNode:
    """Represents a node in the parsed document tree."""
    def __init__(self, tag: str, attrs: Dict[str, str], parent: Optional['DOMNode'] = None):
        self.tag = tag.lower()
        self.attrs = attrs
        self.parent = parent
        self.children: List['DOMNode'] = []
        self.text_content: str = ""
        self.id = attrs.get("id", "")
        self.classes = [c for c in attrs.get("class", "").split() if c]

    def add_child(self, child: 'DOMNode'):
        self.children.append(child)


class StructuralHTMLParser(HTMLParser):
    """Parses HTML into a lightweight structural DOM tree while cataloging assets and routes."""
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.root = DOMNode("__root__", {})
        self.current = self.root

        # Asset & Resource Catalogs
        self.title: str = ""
        self.scripts: List[Dict[str, Any]] = []
        self.stylesheets: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        self.forms: List[Dict[str, Any]] = []
        self.meta_tags: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        self.media_assets: List[Dict[str, str]] = []

        # Internal state
        self._in_title = False
        self._in_script = False
        self._in_style = False
        self._current_script_body = ""
        self._current_script_attrs: Dict[str, str] = {}
        self._current_style_body = ""
        self._current_style_attrs: Dict[str, str] = {}
        self._current_form: Optional[Dict[str, Any]] = None

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        # Track title
        if tag_lower == "title":
            self._in_title = True

        # Track meta tags
        if tag_lower == "meta":
            self.meta_tags.append(attr_dict)

        # Track script tags
        if tag_lower == "script":
            self._in_script = True
            self._current_script_body = ""
            self._current_script_attrs = attr_dict
            src = attr_dict.get("src")
            if src:
                full_url = urllib.parse.urljoin(self.base_url, src)
                self.scripts.append({
                    "src": full_url,
                    "raw_src": src,
                    "type": attr_dict.get("type", "text/javascript"),
                    "async": "async" in attr_dict,
                    "defer": "defer" in attr_dict,
                    "module": attr_dict.get("type") == "module",
                    "inline": False,
                })

        # Track stylesheets
        if tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href")
            if href:
                full_url = urllib.parse.urljoin(self.base_url, href)
                if "stylesheet" in rel:
                    self.stylesheets.append({
                        "href": full_url,
                        "raw_href": href,
                        "rel": rel,
                        "media": attr_dict.get("media", "all"),
                    })
                elif any(x in rel for x in ["icon", "preload", "prefetch", "preconnect", "canonical", "manifest"]):
                    self.links.append({
                        "href": full_url,
                        "raw_href": href,
                        "rel": rel,
                        "as": attr_dict.get("as", ""),
                    })

        # Track inline style
        if tag_lower == "style":
            self._in_style = True
            self._current_style_body = ""
            self._current_style_attrs = attr_dict

        # Track images and media
        if tag_lower == "img":
            src = attr_dict.get("src") or attr_dict.get("data-src")
            if src:
                self.images.append({
                    "src": urllib.parse.urljoin(self.base_url, src),
                    "alt": attr_dict.get("alt", ""),
                })
        elif tag_lower in {"video", "audio", "source"}:
            src = attr_dict.get("src")
            if src:
                self.media_assets.append({
                    "src": urllib.parse.urljoin(self.base_url, src),
                    "type": tag_lower,
                })

        # Track forms & action endpoints
        if tag_lower == "form":
            action = attr_dict.get("action", "")
            full_action = urllib.parse.urljoin(self.base_url, action) if action else self.base_url
            self._current_form = {
                "action": full_action,
                "raw_action": action,
                "method": attr_dict.get("method", "GET").upper(),
                "id": attr_dict.get("id", ""),
                "name": attr_dict.get("name", ""),
                "inputs": [],
            }
            self.forms.append(self._current_form)

        if tag_lower in {"input", "select", "textarea", "button"} and self._current_form is not None:
            self._current_form["inputs"].append({
                "tag": tag_lower,
                "name": attr_dict.get("name", ""),
                "type": attr_dict.get("type", "text"),
                "value": attr_dict.get("value", ""),
                "id": attr_dict.get("id", ""),
            })

        # Build DOM tree
        node = DOMNode(tag_lower, attr_dict, parent=self.current)
        self.current.add_child(node)
        if tag_lower not in self.VOID_TAGS:
            self.current = node

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if tag_lower == "title":
            self._in_title = False
        elif tag_lower == "script":
            self._in_script = False
            if not self._current_script_attrs.get("src") and self._current_script_body.strip():
                self.scripts.append({
                    "src": None,
                    "raw_src": "[inline]",
                    "type": self._current_script_attrs.get("type", "text/javascript"),
                    "inline": True,
                    "content": self._current_script_body.strip(),
                })
        elif tag_lower == "style":
            self._in_style = False
            if self._current_style_body.strip():
                self.stylesheets.append({
                    "href": None,
                    "raw_href": "[inline]",
                    "rel": "stylesheet",
                    "inline": True,
                    "content": self._current_style_body.strip(),
                })
        elif tag_lower == "form":
            self._current_form = None

        if tag_lower not in self.VOID_TAGS and self.current.parent is not None:
            # Walk up to matching tag or parent
            temp = self.current
            while temp.parent is not None and temp.tag != tag_lower:
                temp = temp.parent
            if temp.tag == tag_lower and temp.parent is not None:
                self.current = temp.parent

    def handle_data(self, data: str):
        if self._in_title:
            self.title += data.strip()
        if self._in_script:
            self._current_script_body += data
        if self._in_style:
            self._current_style_body += data
        if self.current and data.strip():
            self.current.text_content += (" " + data.strip())


# =============================================================================
# 2. CODE DE-MINIFIER & PRETTIFIER
# =============================================================================

def prettify_html(html: str) -> str:
    """Lightweight pure Python HTML indenting and prettifier."""
    tokens = re.split(r'(<[^>]+>)', html)
    out: List[str] = []
    indent = 0
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    for token in tokens:
        stripped = token.strip()
        if not stripped:
            continue
        if stripped.startswith("<!--"):
            out.append("  " * indent + stripped)
        elif stripped.startswith("</"):
            indent = max(0, indent - 1)
            out.append("  " * indent + stripped)
        elif stripped.startswith("<"):
            # Check void or self-closing
            is_self = stripped.endswith("/>") or any(stripped.lower().startswith(f"<{vt}") for vt in void_tags)
            is_doctype = stripped.lower().startswith("<!doctype")
            out.append("  " * indent + stripped)
            if not is_self and not is_doctype and not stripped.startswith("<?"):
                indent += 1
        else:
            # Text chunk
            out.append("  " * indent + stripped)
    return "\n".join(out)


def prettify_js_css(code: str) -> str:
    """Prettifies minified JavaScript or CSS into structured readable lines."""
    # Expand braces and semicolons if minified (few or no newlines)
    if "\n" not in code or (len(code) > 80 and code.count("\n") < len(code) / 80):
        code = re.sub(r'([;{}])', r'\1\n', code)
    lines = code.split("\n")
    out: List[str] = []
    indent = 0
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("}") or line_s.startswith("]"):
            indent = max(0, indent - 1)
        out.append("  " * indent + line_s)
        if line_s.endswith("{") or line_s.endswith("["):
            indent += 1
    return "\n".join(out)


def colorize_code(code: str, lang: str = "html", max_lines: int = 400) -> str:
    """Colorizes code using ANSI escape codes for Termux terminal display."""
    lines = code.split("\n")[:max_lines]
    colored_lines = []
    for i, line in enumerate(lines, 1):
        line_num = f"{C_GRAY}{i:4d} │{C_RESET} "
        if lang == "html":
            # Colorize tags and strings
            c_line = re.sub(r'(</?[a-zA-Z0-9_-]+)', rf'{C_CYAN}\1{C_RESET}', line)
            c_line = re.sub(r'([a-zA-Z0-9_-]+)=', rf'{C_YELLOW}\1{C_RESET}=', c_line)
            c_line = re.sub(r'("[^"]*"|\'[^\']*\')', rf'{C_GREEN}\1{C_RESET}', c_line)
        elif lang in {"js", "javascript"}:
            c_line = re.sub(r'\b(function|const|let|var|return|if|else|import|export|from|async|await|class|new|try|catch)\b', rf'{C_MAGENTA}\1{C_RESET}', line)
            c_line = re.sub(r'("[^"]*"|\'[^\']*\'|`[^`]*`)', rf'{C_GREEN}\1{C_RESET}', line)
            c_line = re.sub(r'(//.*$)', rf'{C_GRAY}\1{C_RESET}', c_line)
        elif lang == "css":
            c_line = re.sub(r'([a-zA-Z0-9_-]+)\s*:', rf'{C_YELLOW}\1{C_RESET}:', line)
            c_line = re.sub(r'({|})', rf'{C_CYAN}\1{C_RESET}', c_line)
            c_line = re.sub(r'(#[a-fA-F0-9]{3,6}|rgba?\([^)]+\))', rf'{C_GREEN}\1{C_RESET}', c_line)
        else:
            c_line = line
        colored_lines.append(line_num + c_line)
    return "\n".join(colored_lines)


# =============================================================================
# 3. ENDPOINT & API ROUTE MINER (SCRIPTS & HTML)
# =============================================================================

def extract_endpoints_from_code(code: str, base_url: str) -> List[Dict[str, str]]:
    """Extracts REST API routes, fetch calls, ajax endpoints, and tokens from code."""
    discovered: List[Dict[str, str]] = []
    seen: Set[str] = set()

    # 1. Regex patterns for API routes
    patterns = [
        (r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', "fetch"),
        (r'axios\.(?:get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', "axios"),
        (r'\$\.(?:ajax|get|post|getJSON)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', "jquery.ajax"),
        (r'new\s+WebSocket\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', "websocket"),
        (r'[\'"`](/api/v[0-9]/[^\'"`\s?#]+)[\'"`]', "api_vN_route"),
        (r'[\'"`](/api/[^\'"`\s?#]+)[\'"`]', "api_route"),
        (r'[\'"`](/v[0-9]/[^\'"`\s?#]+)[\'"`]', "versioned_route"),
        (r'[\'"`](https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/(?:api|rest|graphql|v1|v2)[^\'"`\s]*)[\'"`]', "external_api"),
        (r'[\'"`](/graphql[^\'"`\s]*)[\'"`]', "graphql_route"),
    ]

    for pat, kind in patterns:
        for match in re.finditer(pat, code):
            ep = match.group(1).strip()
            if not ep or ep in seen or len(ep) > 180:
                continue
            seen.add(ep)
            full = urllib.parse.urljoin(base_url, ep) if ep.startswith("/") else ep
            discovered.append({
                "endpoint": ep,
                "full_url": full,
                "type": kind,
            })

    return discovered


# =============================================================================
# 4. MASTER WEB STRUCTURE EXTRACTOR ENGINE
# =============================================================================

class WebStructureExtractor:
    """Master controller for fetching, parsing, profiling, and dumping site code architecture."""

    def __init__(self, target_url: str, timeout: int = 15, user_agent: Optional[str] = None, max_assets: int = 10):
        self.raw_url = target_url
        self.timeout = timeout
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.max_assets = max_assets
        self.normalized_url = self._normalize_url(target_url)

        # Extracted data
        self.status_code: int = 0
        self.headers: Dict[str, str] = {}
        self.html_body: str = ""
        self.final_url: str = self.normalized_url
        self.dom_parser: Optional[StructuralHTMLParser] = None
        self.tech_stack: List[str] = []
        self.security_headers: Dict[str, Any] = {}
        self.all_endpoints: List[Dict[str, str]] = []
        self.downloaded_assets: Dict[str, Dict[str, str]] = {}

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url

    def fetch_page(self) -> bool:
        """Fetches target webpage with custom SSL and redirect handling."""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = urllib.request.Request(
            self.normalized_url,
            headers={"User-Agent": self.user_agent, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                self.status_code = resp.getcode()
                self.final_url = resp.geturl()
                self.headers = {k.lower(): v for k, v in resp.headers.items()}
                raw_data = resp.read()
                # Decode body
                charset = resp.headers.get_content_charset() or "utf-8"
                try:
                    self.html_body = raw_data.decode(charset, errors="replace")
                except Exception:
                    self.html_body = raw_data.decode("utf-8", errors="replace")
            return True
        except urllib.error.HTTPError as e:
            self.status_code = e.code
            self.headers = {k.lower(): v for k, v in e.headers.items()}
            try:
                self.html_body = e.read().decode("utf-8", errors="replace")
            except Exception:
                self.html_body = ""
            return bool(self.html_body)
        except Exception as e:
            # Fallback to HTTP if HTTPS failed on initial bare attempt
            if self.normalized_url.startswith("https://") and not self.raw_url.startswith("https://"):
                try:
                    self.normalized_url = "http://" + self.raw_url
                    req = urllib.request.Request(self.normalized_url, headers={"User-Agent": self.user_agent})
                    with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as resp:
                        self.status_code = resp.getcode()
                        self.final_url = resp.geturl()
                        self.headers = {k.lower(): v for k, v in resp.headers.items()}
                        self.html_body = resp.read().decode("utf-8", errors="replace")
                    return True
                except Exception:
                    pass
            raise RuntimeError(f"Connection failed for {self.normalized_url}: {e}")

    def parse_structure(self):
        """Parses HTML into DOM tree, discovers scripts, styles, forms, and detects tech stack."""
        self.dom_parser = StructuralHTMLParser(self.final_url)
        try:
            self.dom_parser.feed(self.html_body)
        except Exception:
            pass

        # Detect Tech Stack
        self._detect_technologies()

        # Audit Security Headers
        self._audit_security_headers()

        # Extract Endpoints from HTML body and inline scripts
        discovered = extract_endpoints_from_code(self.html_body, self.final_url)
        self.all_endpoints.extend(discovered)

        # Also add form actions to endpoints
        for form in self.dom_parser.forms:
            self.all_endpoints.append({
                "endpoint": form["raw_action"] or "[current_page]",
                "full_url": form["action"],
                "type": f"form ({form['method']}) inputs:{len(form['inputs'])}",
            })

    def _detect_technologies(self):
        detected: Set[str] = set()

        # Check headers
        server_header = self.headers.get("server", "").lower()
        powered_by = self.headers.get("x-powered-by", "").lower()

        for sname, sigs in SERVER_SIGNATURES:
            if any(sig in server_header or sig in powered_by or sig in self.headers for sig in sigs):
                detected.add(sname)

        if powered_by:
            detected.add(f"Powered-By: {powered_by}")

        # Check HTML & Scripts
        for fname, patterns in FRAMEWORK_SIGNATURES:
            for pat in patterns:
                if re.search(pat, self.html_body, re.IGNORECASE):
                    detected.add(fname)
                    break

        self.tech_stack = sorted(list(detected))

    def _audit_security_headers(self):
        checks = {
            "Content-Security-Policy (CSP)": "content-security-policy" in self.headers,
            "Strict-Transport-Security (HSTS)": "strict-transport-security" in self.headers,
            "X-Frame-Options (Clickjack)": "x-frame-options" in self.headers,
            "X-Content-Type-Options": "x-content-type-options" in self.headers,
            "Referrer-Policy": "referrer-policy" in self.headers,
            "Permissions-Policy": "permissions-policy" in self.headers,
            "Access-Control-Allow-Origin (CORS)": "access-control-allow-origin" in self.headers,
        }
        self.security_headers = checks

    def fetch_key_scripts(self):
        """Fetches top external scripts to mine deeper endpoints and functions."""
        if not self.dom_parser:
            return

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        scripts_to_fetch = [s for s in self.dom_parser.scripts if s.get("src")][:self.max_assets]
        for s in scripts_to_fetch:
            src = s["src"]
            try:
                req = urllib.request.Request(src, headers={"User-Agent": self.user_agent})
                with urllib.request.urlopen(req, timeout=6, context=ctx) as r:
                    code = r.read().decode("utf-8", errors="replace")
                    filename = Path(urllib.parse.urlparse(src).path).name or "script.js"
                    self.downloaded_assets[src] = {
                        "filename": filename,
                        "type": "javascript",
                        "content": code,
                        "size": len(code),
                    }
                    # Extract endpoints inside downloaded JS
                    js_endpoints = extract_endpoints_from_code(code, self.final_url)
                    for ep in js_endpoints:
                        if not any(e["endpoint"] == ep["endpoint"] for e in self.all_endpoints):
                            ep["found_in"] = filename
                            self.all_endpoints.append(ep)
            except Exception:
                continue

    # ─────────────────────────────────────────────────────────────────────────
    # Visual Tree Rendering
    # ─────────────────────────────────────────────────────────────────────────

    def generate_ascii_tree(self, max_depth: int = 4) -> str:
        """Renders an ASCII/ANSI structural tree of the website DOM and assets."""
        if not self.dom_parser or not self.dom_parser.root.children:
            return "No DOM structure available."

        lines: List[str] = []
        parsed = urllib.parse.urlparse(self.final_url)
        lines.append(f"{C_CYAN}{C_BOLD}{parsed.scheme}://{parsed.netloc}{parsed.path}{C_RESET} {C_GREEN}[HTTP {self.status_code}]{C_RESET}")

        # Meta summary branch
        lines.append(f"├── {C_YELLOW}{C_BOLD}METADATA & HEADERS{C_RESET}")
        title_str = self.dom_parser.title or "[No Title]"
        lines.append(f"│   ├── {C_WHITE}Title:{C_RESET} {C_GREEN}{title_str}{C_RESET}")
        if self.tech_stack:
            lines.append(f"│   ├── {C_WHITE}Tech Stack:{C_RESET} {C_MAGENTA}{', '.join(self.tech_stack)}{C_RESET}")
        lines.append(f"│   └── {C_WHITE}Server:{C_RESET} {C_CYAN}{self.headers.get('server', 'Hidden / Unknown')}{C_RESET}")

        # Scripts branch
        s_count = len(self.dom_parser.scripts)
        lines.append(f"├── {C_YELLOW}{C_BOLD}JAVASCRIPT ARCHITECTURE ({s_count} scripts detected){C_RESET}")
        for idx, s in enumerate(self.dom_parser.scripts[:8]):
            prefix = "│   └── " if (idx == min(s_count, 8) - 1 and s_count <= 8) else "│   ├── "
            if s.get("inline"):
                preview = s.get("content", "")[:35].replace("\n", " ") + "..."
                lines.append(f"{prefix}{C_YELLOW}[inline script]{C_RESET} {C_GRAY}{preview}{C_RESET}")
            else:
                s_name = Path(urllib.parse.urlparse(s['src']).path).name or s['src']
                mod_flag = f" {C_CYAN}[module]{C_RESET}" if s.get("module") else ""
                lines.append(f"{prefix}{C_CYAN}{s_name}{C_RESET}{mod_flag} {C_GRAY}({s['src'][:45]}...){C_RESET}")
        if s_count > 8:
            lines.append(f"│   └── {C_GRAY}... and {s_count - 8} more script files{C_RESET}")

        # Stylesheets branch
        c_count = len(self.dom_parser.stylesheets)
        lines.append(f"├── {C_YELLOW}{C_BOLD}STYLESHEETS & DESIGN ({c_count} sheets detected){C_RESET}")
        for idx, c in enumerate(self.dom_parser.stylesheets[:6]):
            prefix = "│   └── " if (idx == min(c_count, 6) - 1 and c_count <= 6) else "│   ├── "
            if c.get("inline"):
                lines.append(f"{prefix}{C_YELLOW}[inline style block]{C_RESET}")
            else:
                c_name = Path(urllib.parse.urlparse(c['href']).path).name or c['href']
                lines.append(f"{prefix}{C_GREEN}{c_name}{C_RESET} {C_GRAY}({c['href'][:45]}...){C_RESET}")
        if c_count > 6:
            lines.append(f"│   └── {C_GRAY}... and {c_count - 6} more stylesheets{C_RESET}")

        # Endpoints & Forms branch
        e_count = len(self.all_endpoints)
        lines.append(f"├── {C_YELLOW}{C_BOLD}DISCOVERED API ROUTES & FORMS ({e_count} detected){C_RESET}")
        for idx, ep in enumerate(self.all_endpoints[:8]):
            prefix = "│   └── " if (idx == min(e_count, 8) - 1 and e_count <= 8) else "│   ├── "
            lines.append(f"{prefix}{C_WHITE}{ep['endpoint']}{C_RESET} {C_MAGENTA}[{ep['type']}]{C_RESET}")
        if e_count > 8:
            lines.append(f"│   └── {C_GRAY}... and {e_count - 8} more routes/endpoints{C_RESET}")

        # DOM Layout branch
        lines.append(f"└── {C_YELLOW}{C_BOLD}DOM COMPONENT HIERARCHY{C_RESET}")
        self._render_node_tree(self.dom_parser.root, lines, prefix="    ", depth=0, max_depth=max_depth)

        return "\n".join(lines)

    def _render_node_tree(self, node: DOMNode, lines: List[str], prefix: str, depth: int, max_depth: int):
        if depth > max_depth:
            return

        # Filter out empty or noise tags
        display_children = [c for c in node.children if c.tag not in {"head", "meta", "link", "script", "style", "title"}]

        for idx, child in enumerate(display_children):
            is_last = (idx == len(display_children) - 1)
            branch = "└── " if is_last else "├── "

            # Tag attributes string
            id_str = f"{C_CYAN}#{child.id}{C_RESET}" if child.id else ""
            cls_str = f"{C_YELLOW}.{'.'.join(child.classes[:2])}{C_RESET}" if child.classes else ""
            tag_display = f"{C_GREEN}<{child.tag}>{C_RESET} {id_str} {cls_str}".strip()

            lines.append(f"{prefix}{branch}{tag_display}")

            next_prefix = prefix + ("    " if is_last else "│   ")
            self._render_node_tree(child, lines, next_prefix, depth + 1, max_depth)

    # ─────────────────────────────────────────────────────────────────────────
    # Offline Code Structure Dumper
    # ─────────────────────────────────────────────────────────────────────────

    def dump_code_structure(self, output_dir: str) -> Dict[str, Any]:
        """Downloads, formats, and exports the entire site's code assets into an organized folder."""
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        js_dir = out_path / "js"
        css_dir = out_path / "css"
        assets_dir = out_path / "assets"
        js_dir.mkdir(exist_ok=True)
        css_dir.mkdir(exist_ok=True)
        assets_dir.mkdir(exist_ok=True)

        # 1. Prettified index.html
        beautified_html = prettify_html(self.html_body)
        (out_path / "index.html").write_text(beautified_html, encoding="utf-8", errors="replace")

        # 2. Structure Tree file
        ascii_tree = self.generate_ascii_tree(max_depth=6)
        # Strip ANSI colors for text file
        clean_tree = re.sub(r'\033\[[0-9;]*m', '', ascii_tree)
        (out_path / "structure_tree.txt").write_text(clean_tree, encoding="utf-8")

        # 3. Discovered Endpoints JSON
        (out_path / "endpoints.json").write_text(json.dumps(self.all_endpoints, indent=2), encoding="utf-8")

        # 4. Tech Stack & Security Report
        report = {
            "target_url": self.raw_url,
            "final_url": self.final_url,
            "http_status": self.status_code,
            "title": self.dom_parser.title if self.dom_parser else "",
            "tech_stack": self.tech_stack,
            "security_headers": self.security_headers,
            "headers": self.headers,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }
        (out_path / "tech_stack.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

        # 5. Fetch & Dump JavaScript Files
        saved_scripts: List[str] = []
        if self.dom_parser:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            for idx, s in enumerate(self.dom_parser.scripts):
                src = s.get("src")
                if src:
                    parsed_src = urllib.parse.urlparse(src)
                    fname = Path(parsed_src.path).name or f"script_{idx}.js"
                    if not fname.endswith(".js"):
                        fname += ".js"
                    dest_file = js_dir / fname
                    # Use cached if already fetched
                    if src in self.downloaded_assets:
                        raw_code = self.downloaded_assets[src]["content"]
                    else:
                        try:
                            req = urllib.request.Request(src, headers={"User-Agent": self.user_agent})
                            with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
                                raw_code = r.read().decode("utf-8", errors="replace")
                        except Exception:
                            continue
                    prettified = prettify_js_css(raw_code)
                    dest_file.write_text(prettified, encoding="utf-8", errors="replace")
                    saved_scripts.append(str(dest_file.name))
                elif s.get("inline") and s.get("content"):
                    dest_file = js_dir / f"inline_script_{idx}.js"
                    prettified = prettify_js_css(s["content"])
                    dest_file.write_text(prettified, encoding="utf-8", errors="replace")
                    saved_scripts.append(str(dest_file.name))

        # 6. Fetch & Dump CSS Files
        saved_styles: List[str] = []
        if self.dom_parser:
            for idx, c in enumerate(self.dom_parser.stylesheets):
                href = c.get("href")
                if href:
                    parsed_href = urllib.parse.urlparse(href)
                    fname = Path(parsed_href.path).name or f"style_{idx}.css"
                    if not fname.endswith(".css"):
                        fname += ".css"
                    dest_file = css_dir / fname
                    try:
                        req = urllib.request.Request(href, headers={"User-Agent": self.user_agent})
                        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
                            raw_css = r.read().decode("utf-8", errors="replace")
                            prettified_css = prettify_js_css(raw_css)
                            dest_file.write_text(prettified_css, encoding="utf-8", errors="replace")
                            saved_styles.append(str(dest_file.name))
                    except Exception:
                        continue
                elif c.get("inline") and c.get("content"):
                    dest_file = css_dir / f"inline_style_{idx}.css"
                    prettified_css = prettify_js_css(c["content"])
                    dest_file.write_text(prettified_css, encoding="utf-8", errors="replace")
                    saved_styles.append(str(dest_file.name))

        # 7. Summary Manifest
        manifest = {
            "source_url": self.final_url,
            "dump_time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "files": {
                "html": "index.html",
                "tree": "structure_tree.txt",
                "endpoints": "endpoints.json",
                "tech_stack": "tech_stack.json",
                "scripts": saved_scripts,
                "stylesheets": saved_styles,
            }
        }
        (out_path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return {
            "status": "success",
            "output_directory": str(out_path),
            "manifest": manifest,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Full JSON Representation
    # ─────────────────────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.raw_url,
            "final_url": self.final_url,
            "status_code": self.status_code,
            "title": self.dom_parser.title if self.dom_parser else "",
            "tech_stack": self.tech_stack,
            "security_headers": self.security_headers,
            "scripts": self.dom_parser.scripts if self.dom_parser else [],
            "stylesheets": self.dom_parser.stylesheets if self.dom_parser else [],
            "forms": self.dom_parser.forms if self.dom_parser else [],
            "endpoints": self.all_endpoints,
            "meta_tags": self.dom_parser.meta_tags if self.dom_parser else [],
        }


# =============================================================================
# 5. CLI INTERFACE
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Web Code Structure & Deep Source Extraction Engine"
    )
    parser.add_argument("url", help="Target URL or domain (e.g. example.com or https://target.com)")
    parser.add_argument("--tree", action="store_true", help="Display full visual DOM hierarchy and code asset tree")
    parser.add_argument("--source", action="store_true", help="Display beautified, syntax-highlighted source code with line numbers")
    parser.add_argument("--endpoints", action="store_true", help="Display discovered internal API routes, AJAX/Fetch endpoints, and forms")
    parser.add_argument("--scripts", action="store_true", help="Display all script bundles and extracted JS endpoints")
    parser.add_argument("--tech", action="store_true", help="Display tech stack, CMS, frameworks, and security headers audit")
    parser.add_argument("--dump", metavar="DIR", help="Download and reconstruct the complete site code structure into an organized offline directory")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON structure")
    parser.add_argument("--depth", type=int, default=4, help="Maximum DOM tree depth (default: 4)")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP connection timeout in seconds (default: 15)")
    parser.add_argument("--lines", type=int, default=300, help="Max lines to display in source mode (default: 300)")

    args = parser.parse_args()

    # If no specific mode requested, default to tree view
    if not (args.tree or args.source or args.endpoints or args.scripts or args.tech or args.dump or args.json):
        args.tree = True

    if not args.json:
        print(BANNER)

    try:
        extractor = WebStructureExtractor(args.url, timeout=args.timeout)
        if not args.json:
            print(f"{C_YELLOW}[*] Probing target:{C_RESET} {C_WHITE}{extractor.normalized_url}{C_RESET}")
        extractor.fetch_page()
        extractor.parse_structure()
        extractor.fetch_key_scripts()
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}))
        else:
            print(f"\n{C_RED}[!] Error extracting web code structure: {e}{C_RESET}")
        sys.exit(1)

    # 1. JSON Mode
    if args.json:
        print(json.dumps(extractor.to_dict(), indent=2))
        return

    # 2. Tech Stack Mode
    if args.tech:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}TECHNOLOGY STACK & SECURITY POSTURE AUDIT{C_RESET}")
        print(f"{HSEP}")
        print(f"  {C_WHITE}Target:{C_RESET}    {C_GREEN}{extractor.final_url}{C_RESET}")
        print(f"  {C_WHITE}Status:{C_RESET}    {C_CYAN}HTTP {extractor.status_code}{C_RESET}")
        print(f"  {C_WHITE}Title:{C_RESET}     {C_WHITE}{extractor.dom_parser.title if extractor.dom_parser else 'N/A'}{C_RESET}")
        print(f"  {C_WHITE}Tech:{C_RESET}      {C_MAGENTA}{', '.join(extractor.tech_stack) or 'Generic / Minimal'}{C_RESET}")
        print(f"\n  {C_YELLOW}{C_BOLD}Security Headers Analysis:{C_RESET}")
        for header_name, present in extractor.security_headers.items():
            badge = f"{C_GREEN}[ PROTECTED ]{C_RESET}" if present else f"{C_RED}[ MISSING ]{C_RESET}"
            print(f"    {badge:24s} {header_name}")
        print(f"{SEP}\n")

    # 3. Endpoints Mode
    if args.endpoints:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}DISCOVERED API ROUTES, FORMS & ENDPOINTS ({len(extractor.all_endpoints)}){C_RESET}")
        print(f"{HSEP}")
        if not extractor.all_endpoints:
            print(f"  {C_GRAY}No explicit API routes or forms found in initial payload.{C_RESET}")
        else:
            for ep in extractor.all_endpoints:
                t_badge = f"{C_MAGENTA}[{ep['type']}]{C_RESET}"
                print(f"  {t_badge:30s} {C_WHITE}{ep['endpoint']}{C_RESET}")
                if ep.get("endpoint") != ep.get("full_url"):
                    print(f"  {' '*20} ↳ {C_GRAY}{ep['full_url']}{C_RESET}")
        print(f"{SEP}\n")

    # 4. Scripts Mode
    if args.scripts:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}JAVASCRIPT ARCHITECTURE & SCRIPT BUNDLES ({len(extractor.dom_parser.scripts)}){C_RESET}")
        print(f"{HSEP}")
        for s in extractor.dom_parser.scripts:
            if s.get("inline"):
                print(f"  {C_YELLOW}[inline block]{C_RESET} {C_GRAY}{len(s.get('content', ''))} bytes{C_RESET}")
            else:
                mod = f" {C_CYAN}[module]{C_RESET}" if s.get("module") else ""
                print(f"  {C_WHITE}{s['src']}{C_RESET}{mod}")
        print(f"{SEP}\n")

    # 5. Tree Mode
    if args.tree:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}FULL SITE ARCHITECTURE & CODE STRUCTURE TREE{C_RESET}")
        print(f"{HSEP}\n")
        print(extractor.generate_ascii_tree(max_depth=args.depth))
        print(f"\n{SEP}")
        print(f" {C_GRAY}Run with {C_WHITE}--dump <folder>{C_GRAY} to download the entire structured codebase.{C_RESET}\n")

    # 6. Source Mode
    if args.source:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}BEAUTIFIED SOURCE CODE (Top {args.lines} Lines){C_RESET}")
        print(f"{HSEP}\n")
        prettified = prettify_html(extractor.html_body)
        print(colorize_code(prettified, lang="html", max_lines=args.lines))
        print(f"\n{SEP}\n")

    # 7. Dump Mode
    if args.dump:
        print(f"\n{HSEP}")
        print(f" {C_CYAN}{C_BOLD}DUMPING & RECONSTRUCTING CODE STRUCTURE{C_RESET}")
        print(f"{HSEP}")
        print(f"  {C_YELLOW}[*] Output Directory:{C_RESET} {C_WHITE}{args.dump}{C_RESET}")
        res = extractor.dump_code_structure(args.dump)
        print(f"  {C_GREEN}[✔] Source code and assets successfully dumped!{C_RESET}")
        print(f"  ├── index.html            (Beautified HTML source)")
        print(f"  ├── structure_tree.txt    (Architectural ASCII tree)")
        print(f"  ├── endpoints.json        (All discovered API routes)")
        print(f"  ├── tech_stack.json       (Tech stack & security audit)")
        print(f"  ├── manifest.json         (Project manifest)")
        print(f"  ├── js/                   ({len(res['manifest']['files']['scripts'])} JS bundles saved)")
        print(f"  └── css/                  ({len(res['manifest']['files']['stylesheets'])} CSS stylesheets saved)")
        print(f"{SEP}\n")


if __name__ == "__main__":
    main()
