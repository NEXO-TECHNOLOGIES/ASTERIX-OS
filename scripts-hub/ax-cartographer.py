#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS - Autonomous Codebase Cartographer & Architecture Synthesizer
  Tool: ax map / ax scaffold
  Version: 2.0.0
  Zero Dependencies: 100% Python Standard Library
===============================================================================
"""

import os
import sys
import ast
import re
import json
import html
import time
import argparse
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Set, Any, Optional, Tuple

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Terminal ANSI Colors
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_DIM     = "\033[2m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_WHITE   = "\033[97m"

BANNER = f"""{C_CYAN}{C_BOLD}
   █████╗ ███████╗████████╗███████╗██████╗ ██╗██╗  ██╗     ███╗   ███╗ █████╗ ██████╗ 
  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║╚██╗██╔╝     ████╗ ████║██╔══██╗██╔══██╗
  ███████║███████╗   ██║   █████╗  ██████╔╝██║ ╚███╔╝█████╗██╔████╔██║███████║██████╔╝
  ██╔══██║╚════██║   ██║   ██╔══╝  ██╔══██╗██║ ██╔██╗╚════╝██║╚██╔╝██║██╔══██║██╔═══╝ 
  ██║  ██║███████║   ██║   ███████╗██║  ██║██║██╔╝ ██╗     ██║ ╚═╝ ██║██║  ██║██║     
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     
{C_RESET}{C_MAGENTA}       ASTERIX Codebase Cartographer & Architecture Synthesizer v2.0{C_RESET}
"""

IGNORE_DIRS = {
    ".git", ".github", "node_modules", "venv", ".venv", "env", ".env",
    "__pycache__", "target", "dist", "build", "out", ".asterix_vault",
    ".idea", ".vscode", "vendor", "bin", "iso-images", "assets"
}

LANG_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".hpp": "cpp",
    ".cc": "cpp",
    ".java": "java",
    ".cs": "csharp",
    ".php": "php",
    ".sh": "bash",
    ".bash": "bash",
    ".json": "json",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
}

class Symbol:
    def __init__(self, name: str, kind: str, line: int, signature: str = "", doc: str = ""):
        self.name = name
        self.kind = kind  # class, function, method, route, model, struct, interface
        self.line = line
        self.signature = signature
        self.doc = doc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "line": self.line,
            "signature": self.signature,
            "doc": self.doc
        }

class FileNode:
    def __init__(self, path: Path, rel_path: str, lang: str):
        self.path = path
        self.rel_path = rel_path.replace("\\", "/")
        self.lang = lang
        self.lines = 0
        self.size_bytes = 0
        self.symbols: List[Symbol] = []
        self.imports: List[str] = []
        self.routes: List[str] = []
        self.models: List[str] = []
        self.internal_deps: Set[str] = set()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.rel_path,
            "language": self.lang,
            "lines": self.lines,
            "size_bytes": self.size_bytes,
            "symbols": [s.to_dict() for s in self.symbols],
            "imports": self.imports,
            "routes": self.routes,
            "models": self.models,
            "internal_deps": sorted(list(self.internal_deps))
        }

class CodebaseCartographer:
    def __init__(self, root_dir: str):
        self.root = Path(root_dir).resolve()
        self.nodes: Dict[str, FileNode] = {}
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.cycles: List[List[str]] = []
        self.orphans: List[str] = []
        self.bottlenecks: List[Tuple[str, int]] = []
        self.total_lines = 0
        self.lang_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"files": 0, "lines": 0})

    def scan(self):
        """Walks the codebase and parses all source files."""
        for root, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in LANG_EXTENSIONS:
                    file_path = Path(root) / file
                    try:
                        rel_path = str(file_path.relative_to(self.root))
                    except ValueError:
                        rel_path = str(file_path)
                    
                    lang = LANG_EXTENSIONS[ext]
                    node = FileNode(file_path, rel_path, lang)
                    self._parse_file(node)
                    self.nodes[node.rel_path] = node
                    
                    # Track stats
                    self.total_lines += node.lines
                    self.lang_stats[lang]["files"] += 1
                    self.lang_stats[lang]["lines"] += node.lines

        self._resolve_dependencies()
        self._detect_cycles()
        self._find_orphans_and_bottlenecks()

    def _parse_file(self, node: FileNode):
        try:
            content = node.path.read_text(encoding="utf-8", errors="replace")
            node.size_bytes = len(content.encode("utf-8"))
            lines = content.splitlines()
            node.lines = len(lines)
            
            if node.lang == "python":
                self._parse_python(node, content)
            elif node.lang in ("javascript", "typescript"):
                self._parse_javascript(node, lines)
            elif node.lang == "rust":
                self._parse_rust(node, lines)
            elif node.lang == "go":
                self._parse_go(node, lines)
            elif node.lang in ("c", "cpp"):
                self._parse_c_cpp(node, lines)
            else:
                self._parse_generic(node, lines)
        except Exception:
            pass

    def _parse_python(self, node: FileNode, content: str):
        try:
            tree = ast.parse(content)
        except Exception:
            self._parse_python_regex(node, content.splitlines())
            return

        for stmt in tree.body:
            if isinstance(stmt, ast.Import):
                for alias in stmt.names:
                    node.imports.append(alias.name)
            elif isinstance(stmt, ast.ImportFrom):
                mod = stmt.module or ""
                for alias in stmt.names:
                    node.imports.append(f"{mod}.{alias.name}" if mod else alias.name)
            elif isinstance(stmt, ast.ClassDef):
                doc = ast.get_docstring(stmt) or ""
                bases = [b.id for b in stmt.bases if isinstance(b, ast.Name)]
                kind = "model" if any(b in ("Model", "Base", "Document") for b in bases) else "class"
                if kind == "model":
                    node.models.append(stmt.name)
                sig = f"class {stmt.name}({', '.join(bases)})"
                node.symbols.append(Symbol(stmt.name, kind, stmt.lineno, sig, doc.splitlines()[0] if doc else ""))
                
                # Check methods
                for item in stmt.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_doc = ast.get_docstring(item) or ""
                        args = [a.arg for a in item.args.args]
                        m_sig = f"{item.name}({', '.join(args)})"
                        node.symbols.append(Symbol(f"{stmt.name}.{item.name}", "method", item.lineno, m_sig, method_doc.splitlines()[0] if method_doc else ""))
            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                doc = ast.get_docstring(stmt) or ""
                args = [a.arg for a in stmt.args.args]
                sig = f"{stmt.name}({', '.join(args)})"
                
                is_route = False
                for dec in stmt.decorator_list:
                    dec_str = ast.dump(dec)
                    if any(r in dec_str for r in ("get", "post", "put", "delete", "route", "patch")):
                        is_route = True
                        node.routes.append(stmt.name)
                        node.symbols.append(Symbol(stmt.name, "route", stmt.lineno, sig, doc.splitlines()[0] if doc else ""))
                        break
                if not is_route:
                    node.symbols.append(Symbol(stmt.name, "function", stmt.lineno, sig, doc.splitlines()[0] if doc else ""))

    def _parse_python_regex(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("import ") or s.startswith("from "):
                node.imports.append(s)
            elif s.startswith("class "):
                m = re.match(r"class\s+([a-zA-Z0-9_]+)", s)
                if m:
                    node.symbols.append(Symbol(m.group(1), "class", idx, s.split(":")[0]))
            elif s.startswith("def ") or s.startswith("async def "):
                m = re.match(r"(?:async\s+)?def\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", s)
                if m:
                    node.symbols.append(Symbol(m.group(1), "function", idx, f"{m.group(1)}({m.group(2)})"))

    def _parse_javascript(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("import ") or "require(" in s:
                node.imports.append(s)
            r_match = re.search(r"\b(app|router)\.(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]", s)
            if r_match:
                verb, endpoint = r_match.group(2).upper(), r_match.group(3)
                node.routes.append(f"{verb} {endpoint}")
                node.symbols.append(Symbol(f"{verb} {endpoint}", "route", idx, s))
            c_match = re.match(r"^(?:export\s+)?class\s+([a-zA-Z0-9_]+)", s)
            if c_match:
                node.symbols.append(Symbol(c_match.group(1), "class", idx, s))
            f_match = re.match(r"^(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z0-9_]+)\s*\((.*?)\)", s)
            if f_match:
                node.symbols.append(Symbol(f_match.group(1), "function", idx, f"{f_match.group(1)}({f_match.group(2)})"))
            af_match = re.match(r"^(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s*)?\((.*?)\)\s*=>", s)
            if af_match:
                node.symbols.append(Symbol(af_match.group(1), "function", idx, f"{af_match.group(1)}({af_match.group(2)})"))

    def _parse_rust(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("use "):
                node.imports.append(s)
            m = re.match(r"^(?:pub(?:\([^\)]+\))?\s+)?(struct|enum|trait)\s+([a-zA-Z0-9_]+)", s)
            if m:
                node.symbols.append(Symbol(m.group(2), m.group(1), idx, s))
            fn_m = re.match(r"^(?:pub(?:\([^\)]+\))?\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*(?:<[^>]+>)?\s*\((.*?)\)", s)
            if fn_m:
                node.symbols.append(Symbol(fn_m.group(1), "function", idx, f"{fn_m.group(1)}({fn_m.group(2)})"))
            if any(s.startswith(p) for p in ("#[get(", "#[post(", "#[put(", "#[delete(")):
                node.routes.append(s)

    def _parse_go(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("import "):
                node.imports.append(s)
            m = re.match(r"^type\s+([a-zA-Z0-9_]+)\s+(struct|interface)", s)
            if m:
                node.symbols.append(Symbol(m.group(1), m.group(2), idx, s))
            fn_m = re.match(r"^func\s+(?:\([^\)]+\)\s+)?([a-zA-Z0-9_]+)\s*\((.*?)\)", s)
            if fn_m:
                node.symbols.append(Symbol(fn_m.group(1), "function", idx, f"{fn_m.group(1)}({fn_m.group(2)})"))
            r_m = re.search(r"\b(GET|POST|PUT|DELETE|PATCH)\s*\(\s*\"([^\"]+)\"", s)
            if r_m:
                node.routes.append(f"{r_m.group(1)} {r_m.group(2)}")

    def _parse_c_cpp(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("#include"):
                node.imports.append(s)
            m = re.match(r"^(?:class|struct)\s+([a-zA-Z0-9_]+)", s)
            if m and not s.endswith(";"):
                node.symbols.append(Symbol(m.group(1), "class", idx, s))
            fn_m = re.match(r"^[a-zA-Z0-9_:\*&]+\s+([a-zA-Z0-9_]+)\s*\((.*?)\)\s*\{?", s)
            if fn_m and not s.startswith("return") and not s.startswith("if") and not s.startswith("while"):
                node.symbols.append(Symbol(fn_m.group(1), "function", idx, f"{fn_m.group(1)}({fn_m.group(2)})"))

    def _parse_generic(self, node: FileNode, lines: List[str]):
        for idx, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("import ") or s.startswith("require ") or s.startswith("using "):
                node.imports.append(s)

    def _resolve_dependencies(self):
        """Builds directed dependency edges between internal files."""
        name_to_relpath = {}
        for rel_path in self.nodes:
            stem = Path(rel_path).stem
            name_to_relpath[stem] = rel_path
            name_to_relpath[rel_path] = rel_path

        for src_rel, node in self.nodes.items():
            for imp in node.imports:
                clean = imp.replace("import", "").replace("from", "").replace("require", "").replace("use", "").replace("#include", "").strip(" ()'\"<>;")
                for token in re.findall(r"[a-zA-Z0-9_\-\./]+", clean):
                    token_stem = Path(token).stem
                    if token_stem in name_to_relpath and name_to_relpath[token_stem] != src_rel:
                        target_rel = name_to_relpath[token_stem]
                        node.internal_deps.add(target_rel)
                        self.graph[src_rel].add(target_rel)
                        self.reverse_graph[target_rel].add(src_rel)

    def _detect_cycles(self):
        """Tarjan's or DFS cycle detection to find circular dependencies."""
        visited = set()
        rec_stack = []
        in_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.append(node)
            in_stack.add(node)

            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in in_stack:
                    idx = rec_stack.index(neighbor)
                    cycle = rec_stack[idx:] + [neighbor]
                    if cycle not in self.cycles and len(cycle) > 1:
                        self.cycles.append(cycle)

            rec_stack.pop()
            in_stack.remove(node)

        for n in list(self.nodes.keys()):
            if n not in visited:
                dfs(n)

    def _find_orphans_and_bottlenecks(self):
        """Identifies orphan files and central bottleneck nodes."""
        entrypoints = {"main.py", "app.py", "index.js", "index.ts", "main.go", "main.rs", "server.js", "setup.py"}
        
        in_degrees = []
        for rel_path, node in self.nodes.items():
            deg = len(self.reverse_graph[rel_path])
            in_degrees.append((rel_path, deg))
            
            if deg == 0 and Path(rel_path).name not in entrypoints:
                self.orphans.append(rel_path)

        in_degrees.sort(key=lambda x: x[1], reverse=True)
        self.bottlenecks = [item for item in in_degrees if item[1] > 1][:10]

    def print_summary(self):
        print(BANNER)
        print(f"  {C_BOLD}Root Directory:{C_RESET} {self.root}")
        print(f"  {C_BOLD}Total Files Parsed:{C_RESET} {len(self.nodes)}")
        print(f"  {C_BOLD}Total Lines of Code:{C_RESET} {self.total_lines:,}")
        print()

        print(f"  {C_CYAN}{C_BOLD}LANGUAGE BREAKDOWN{C_RESET}")
        print(f"  {'Language':<15} {'Files':<10} {'Lines of Code':<15} {'Percentage':<10}")
        print(f"  {'-'*55}")
        for lang, stats in sorted(self.lang_stats.items(), key=lambda x: x[1]["lines"], reverse=True):
            pct = (stats["lines"] / self.total_lines * 100) if self.total_lines else 0
            print(f"  {lang.capitalize():<15} {stats['files']:<10} {stats['lines']:<15,} {pct:>6.1f}%")
        print()

        total_symbols = sum(len(n.symbols) for n in self.nodes.values())
        total_routes = sum(len(n.routes) for n in self.nodes.values())
        total_models = sum(len(n.models) for n in self.nodes.values())
        print(f"  {C_GREEN}{C_BOLD}TOPOLOGY METRICS{C_RESET}")
        print(f"  • Total Symbols Extracted: {C_BOLD}{total_symbols}{C_RESET}")
        print(f"  • API Endpoints Discovered: {C_BOLD}{total_routes}{C_RESET}")
        print(f"  • Data Models / Schemas:   {C_BOLD}{total_models}{C_RESET}")
        print(f"  • Dependency Edges:        {C_BOLD}{sum(len(v) for v in self.graph.values())}{C_RESET}")
        print()

        print(f"  {C_YELLOW}{C_BOLD}ARCHITECTURAL HEALTH{C_RESET}")
        if self.cycles:
            print(f"  • {C_RED}[ALERT] Circular Dependencies Detected:{C_RESET} {len(self.cycles)} loops")
        else:
            print(f"  • {C_GREEN}[CLEAN] Circular Dependencies:{C_RESET} 0 (Healthy DAG)")

        if self.orphans:
            print(f"  • {C_YELLOW}[NOTICE] Potential Orphan / Unused Files:{C_RESET} {len(self.orphans)}")
        else:
            print(f"  • {C_GREEN}[CLEAN] Orphan Files:{C_RESET} 0")

        if self.bottlenecks:
            print(f"  • {C_CYAN}[CORE ANCHORS] High-Coupling Central Modules:{C_RESET}")
            for path, deg in self.bottlenecks[:5]:
                print(f"      ↳ {C_BOLD}{path}{C_RESET} (referenced by {deg} files)")
        print()

    def print_audit(self):
        print(BANNER)
        print(f"  {C_BOLD}{C_CYAN}=== ASTERIX ARCHITECTURE & QUALITY AUDIT ==={C_RESET}\n")
        
        print(f"  {C_BOLD}1. Circular Dependency Analysis:{C_RESET}")
        if not self.cycles:
            print(f"     {C_GREEN}✓ No circular dependencies detected. Clean unidirectional flow.{C_RESET}")
        else:
            print(f"     {C_RED}⚠ Found {len(self.cycles)} circular dependency loops!{C_RESET}")
            for idx, cycle in enumerate(self.cycles[:10], 1):
                chain = " -> ".join(cycle)
                print(f"     [{idx}] {chain}")
        print()

        print(f"  {C_BOLD}2. Orphan Modules (No Inbound Imports):{C_RESET}")
        if not self.orphans:
            print(f"     {C_GREEN}✓ All files are referenced within the codebase.{C_RESET}")
        else:
            print(f"     {C_YELLOW}Found {len(self.orphans)} potentially unused / isolated files:{C_RESET}")
            for orphan in self.orphans[:15]:
                print(f"     • {orphan}")
            if len(self.orphans) > 15:
                print(f"     ... and {len(self.orphans) - 15} more.")
        print()

        print(f"  {C_BOLD}3. Central Core Modules (High Fan-In):{C_RESET}")
        for path, deg in self.bottlenecks:
            print(f"     • {C_CYAN}{path}{C_RESET} -> imported by {deg} modules")
        print()

    def print_tree(self):
        print(BANNER)
        print(f"  {C_BOLD}Project Topology Tree: {self.root}{C_RESET}\n")
        
        tree = {}
        for rel_path, node in sorted(self.nodes.items()):
            parts = rel_path.split("/")
            curr = tree
            for part in parts[:-1]:
                curr = curr.setdefault(part, {})
            curr[parts[-1]] = node

        def render_tree(d, prefix=""):
            items = list(d.items())
            for idx, (name, val) in enumerate(items):
                is_last = (idx == len(items) - 1)
                connector = "└── " if is_last else "├── "
                sub_prefix = "    " if is_last else "│   "
                
                if isinstance(val, FileNode):
                    sym_badge = f"{C_CYAN}[{len(val.symbols)} syms]{C_RESET}" if val.symbols else ""
                    route_badge = f" {C_GREEN}[{len(val.routes)} routes]{C_RESET}" if val.routes else ""
                    model_badge = f" {C_MAGENTA}[{len(val.models)} models]{C_RESET}" if val.models else ""
                    print(f"{prefix}{connector}{C_WHITE}{name}{C_RESET} ({val.lines} lines) {sym_badge}{route_badge}{model_badge}")
                else:
                    print(f"{prefix}{connector}{C_YELLOW}{C_BOLD}{name}/{C_RESET}")
                    render_tree(val, prefix + sub_prefix)

        render_tree(tree, "  ")
        print()

    def export_context_blueprint(self) -> str:
        """Emits an ultra-dense, token-efficient architectural blueprint for LLMs/AI."""
        output = [
            "# ARCHITECTURAL BLUEPRINT & CONTEXT DOSSIER",
            f"Repository Root: {self.root.name}",
            f"Total Files: {len(self.nodes)} | Total LOC: {self.total_lines:,}",
            "Language Breakdown: " + ", ".join(f"{l}: {s['lines']} lines" for l, s in self.lang_stats.items()),
            "",
            "## CORE HIGH-COUPLING ANCHORS",
        ]
        for path, deg in self.bottlenecks[:5]:
            output.append(f"- `{path}` (in-degree: {deg})")

        output.append("\n## SYMBOL & API TOPOLOGY")
        for rel_path, node in sorted(self.nodes.items()):
            if not node.symbols and not node.routes and not node.models:
                continue
            output.append(f"\n### File: `{node.rel_path}` ({node.lang}, {node.lines} lines)")
            if node.internal_deps:
                output.append(f"  Dependencies: {', '.join(sorted(node.internal_deps))}")
            if node.routes:
                output.append("  Endpoints:")
                for r in node.routes:
                    output.append(f"    - {r}")
            if node.models:
                output.append(f"  Models: {', '.join(node.models)}")
            if node.symbols:
                output.append("  Symbols:")
                for s in node.symbols[:20]:
                    doc_str = f" // {s.doc}" if s.doc else ""
                    output.append(f"    - [{s.kind}] `{s.signature or s.name}` (line {s.line}){doc_str}")
        
        return "\n".join(output)

    def export_mermaid(self) -> str:
        """Generates GitHub/GitLab markdown Mermaid diagram."""
        lines = ["```mermaid", "graph TD"]
        for rel_path in self.nodes:
            clean_id = re.sub(r"[^a-zA-Z0-9_]", "_", rel_path)
            lines.append(f"  {clean_id}[\"{rel_path}\"]")

        for src, dests in self.graph.items():
            src_id = re.sub(r"[^a-zA-Z0-9_]", "_", src)
            for dest in dests:
                dest_id = re.sub(r"[^a-zA-Z0-9_]", "_", dest)
                lines.append(f"  {src_id} --> {dest_id}")
        lines.append("```")
        return "\n".join(lines)

    def export_html_dashboard(self, output_path: str):
        """Generates a self-contained, zero-dependency dark-mode interactive HTML dashboard."""
        nodes_data = []
        links_data = []

        for rel_path, node in self.nodes.items():
            nodes_data.append({
                "id": rel_path,
                "label": Path(rel_path).name,
                "path": rel_path,
                "lang": node.lang,
                "lines": node.lines,
                "symbols": len(node.symbols),
                "routes": len(node.routes),
                "inDegree": len(self.reverse_graph[rel_path]),
                "outDegree": len(self.graph[rel_path]),
                "isOrphan": rel_path in self.orphans
            })

        for src, dests in self.graph.items():
            for dest in dests:
                links_data.append({"source": src, "target": dest})

        stats_json = json.dumps({
            "totalFiles": len(self.nodes),
            "totalLines": self.total_lines,
            "totalSymbols": sum(len(n.symbols) for n in self.nodes.values()),
            "totalRoutes": sum(len(n.routes) for n in self.nodes.values()),
            "cycleCount": len(self.cycles),
            "orphanCount": len(self.orphans),
            "languages": self.lang_stats
        })

        nodes_json = json.dumps(nodes_data)
        links_json = json.dumps(links_data)

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>ASTERIX OS - Codebase Cartographer</title>
<style>
  :root {{
    --bg: #0d1117;
    --panel: #161b22;
    --border: #30363d;
    --accent: #58a6ff;
    --accent-alt: #bc8cff;
    --text: #c9d1d9;
    --text-bright: #ffffff;
    --green: #3fb950;
    --red: #f85149;
    --yellow: #d29922;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    display: flex;
    height: 100vh;
    overflow: hidden;
  }}
  #sidebar {{
    width: 380px;
    background: var(--panel);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    z-index: 10;
  }}
  .brand {{
    padding: 16px;
    border-bottom: 1px solid var(--border);
    background: #090d13;
  }}
  .brand h1 {{
    font-size: 1.15rem;
    color: var(--text-bright);
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .brand p {{
    font-size: 0.78rem;
    color: #8b949e;
    margin-top: 4px;
  }}
  .search-box {{
    padding: 12px;
    border-bottom: 1px solid var(--border);
  }}
  .search-box input {{
    width: 100%;
    padding: 8px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text-bright);
    font-size: 0.85rem;
    outline: none;
  }}
  .search-box input:focus {{
    border-color: var(--accent);
  }}
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    padding: 12px;
    border-bottom: 1px solid var(--border);
  }}
  .stat-card {{
    background: var(--bg);
    padding: 10px;
    border-radius: 6px;
    border: 1px solid var(--border);
  }}
  .stat-label {{ font-size: 0.7rem; color: #8b949e; text-transform: uppercase; }}
  .stat-val {{ font-size: 1.2rem; font-weight: bold; color: var(--accent); margin-top: 2px; }}
  .filter-bar {{
    padding: 8px 12px;
    display: flex;
    gap: 6px;
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
  }}
  .filter-btn {{
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    cursor: pointer;
  }}
  .filter-btn.active {{
    background: var(--accent);
    color: #000;
    font-weight: bold;
    border-color: var(--accent);
  }}
  #node-list {{
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }}
  .node-item {{
    padding: 8px 12px;
    border-radius: 6px;
    margin-bottom: 4px;
    background: var(--bg);
    border: 1px solid var(--border);
    cursor: pointer;
    font-size: 0.82rem;
    transition: all 0.15s ease;
  }}
  .node-item:hover, .node-item.selected {{
    border-color: var(--accent);
    background: #1f242c;
  }}
  .node-title {{ font-weight: 600; color: var(--text-bright); display: flex; justify-content: space-between; }}
  .node-meta {{ font-size: 0.72rem; color: #8b949e; margin-top: 3px; display: flex; gap: 8px; }}
  #main-viewport {{
    flex: 1;
    display: flex;
    flex-direction: column;
    position: relative;
  }}
  #canvas-container {{
    flex: 1;
    overflow: hidden;
    position: relative;
    background: radial-gradient(circle, #161b22 10%, #0d1117 90%);
  }}
  svg {{ width: 100%; height: 100%; cursor: grab; }}
  svg:active {{ cursor: grabbing; }}
  .node-circle {{ fill: var(--panel); stroke: var(--accent); stroke-width: 2; transition: all 0.2s; }}
  .node-circle:hover {{ stroke: #fff; stroke-width: 3.5; }}
  .node-text {{ fill: var(--text-bright); font-size: 11px; font-weight: 500; pointer-events: none; }}
  .link {{ stroke: #30363d; stroke-width: 1.5; stroke-opacity: 0.6; }}
  .link.highlight {{ stroke: var(--yellow); stroke-width: 2.5; stroke-opacity: 1; }}
  #details-panel {{
    position: absolute;
    top: 20px;
    right: 20px;
    width: 320px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    display: none;
  }}
  #details-panel h3 {{ color: var(--text-bright); font-size: 1rem; margin-bottom: 8px; word-break: break-all; }}
  #details-panel p {{ font-size: 0.8rem; margin-bottom: 6px; color: #8b949e; }}
  #details-panel .badge {{ display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; background: #21262d; margin-right: 4px; }}
</style>
</head>
<body>

<div id="sidebar">
  <div class="brand">
    <h1>⚡ ASTERIX CARTOGRAPHER</h1>
    <p>Autonomous Architecture Topology Engine</p>
  </div>
  <div class="search-box">
    <input type="text" id="searchInput" placeholder="Search modules, routes, symbols..." oninput="filterNodes()">
  </div>
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Total Files</div>
      <div class="stat-val" id="statFiles">0</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Total Lines</div>
      <div class="stat-val" id="statLines">0</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Endpoints</div>
      <div class="stat-val" id="statRoutes" style="color:var(--green)">0</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Cycles / Loops</div>
      <div class="stat-val" id="statCycles" style="color:var(--yellow)">0</div>
    </div>
  </div>
  <div class="filter-bar">
    <button class="filter-btn active" onclick="setFilter('all')">All</button>
    <button class="filter-btn" onclick="setFilter('routes')">Endpoints</button>
    <button class="filter-btn" onclick="setFilter('anchors')">Core Anchors</button>
    <button class="filter-btn" onclick="setFilter('orphans')">Orphans</button>
  </div>
  <div id="node-list"></div>
</div>

<div id="main-viewport">
  <div id="canvas-container">
    <svg id="viewportSvg">
      <g id="zoomGroup">
        <g id="linksGroup"></g>
        <g id="nodesGroup"></g>
      </g>
    </svg>
  </div>

  <div id="details-panel">
    <h3 id="detailTitle">Module</h3>
    <p><strong>Path:</strong> <span id="detailPath"></span></p>
    <p><strong>Language:</strong> <span id="detailLang"></span></p>
    <p><strong>Lines:</strong> <span id="detailLines"></span></p>
    <p><strong>Symbols:</strong> <span id="detailSymbols"></span></p>
    <p><strong>In-Degree:</strong> <span id="detailInDegree"></span> (references)</p>
    <p><strong>Out-Degree:</strong> <span id="detailOutDegree"></span> (dependencies)</p>
  </div>
</div>

<script>
  const stats = {stats_json};
  const nodes = {nodes_json};
  const links = {links_json};

  document.getElementById('statFiles').innerText = stats.totalFiles;
  document.getElementById('statLines').innerText = stats.totalLines.toLocaleString();
  document.getElementById('statRoutes').innerText = stats.totalRoutes;
  document.getElementById('statCycles').innerText = stats.cycleCount;

  let currentFilter = 'all';

  function renderList(filtered) {{
    const container = document.getElementById('node-list');
    container.innerHTML = '';
    filtered.forEach(n => {{
      const div = document.createElement('div');
      div.className = 'node-item';
      div.onclick = () => selectNode(n);
      div.innerHTML = `
        <div class="node-title">
          <span>${{n.label}}</span>
          <span style="color:var(--accent-alt)">${{n.lang}}</span>
        </div>
        <div class="node-meta">
          <span>${{n.lines}} LOC</span>
          <span>${{n.symbols}} syms</span>
          ${{n.routes ? `<span style="color:var(--green)">${{n.routes}} routes</span>` : ''}}
          ${{n.isOrphan ? `<span style="color:var(--yellow)">orphan</span>` : ''}}
        </div>
      `;
      container.appendChild(div);
    }});
  }}

  function setFilter(f) {{
    currentFilter = f;
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    event.target.classList.add('active');
    filterNodes();
  }}

  function filterNodes() {{
    const q = document.getElementById('searchInput').value.toLowerCase();
    const filtered = nodes.filter(n => {{
      const matchesSearch = n.path.toLowerCase().includes(q) || n.label.toLowerCase().includes(q);
      if (!matchesSearch) return false;
      if (currentFilter === 'routes') return n.routes > 0;
      if (currentFilter === 'anchors') return n.inDegree > 1;
      if (currentFilter === 'orphans') return n.isOrphan;
      return true;
    }});
    renderList(filtered);
  }}

  function selectNode(n) {{
    document.getElementById('details-panel').style.display = 'block';
    document.getElementById('detailTitle').innerText = n.label;
    document.getElementById('detailPath').innerText = n.path;
    document.getElementById('detailLang').innerText = n.lang;
    document.getElementById('detailLines').innerText = n.lines;
    document.getElementById('detailSymbols').innerText = n.symbols;
    document.getElementById('detailInDegree').innerText = n.inDegree;
    document.getElementById('detailOutDegree').innerText = n.outDegree;
  }}

  function layoutGraph() {{
    const nodesGroup = document.getElementById('nodesGroup');
    const linksGroup = document.getElementById('linksGroup');
    nodesGroup.innerHTML = '';
    linksGroup.innerHTML = '';

    const width = 1200;
    const height = 800;
    const nodeMap = {{}};

    const count = nodes.length;
    const radius = Math.min(width, height) * 0.4;
    const centerX = width / 2;
    const centerY = height / 2;

    nodes.forEach((n, idx) => {{
      const angle = (idx / count) * 2 * Math.PI;
      const r = radius * (0.4 + 0.6 * ((idx % 3) / 2));
      n.x = centerX + r * Math.cos(angle);
      n.y = centerY + r * Math.sin(angle);
      nodeMap[n.id] = n;
    }});

    links.forEach(l => {{
      const s = nodeMap[l.source];
      const t = nodeMap[l.target];
      if (s && t) {{
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', s.x);
        line.setAttribute('y1', s.y);
        line.setAttribute('x2', t.x);
        line.setAttribute('y2', t.y);
        line.setAttribute('class', 'link');
        linksGroup.appendChild(line);
      }}
    }});

    nodes.forEach(n => {{
      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${{n.x}}, ${{n.y}})`);
      g.style.cursor = 'pointer';
      g.onclick = () => selectNode(n);

      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', Math.min(18, Math.max(7, n.inDegree * 3 + 6)));
      circle.setAttribute('class', 'node-circle');
      if (n.routes > 0) circle.style.stroke = 'var(--green)';
      if (n.isOrphan) circle.style.stroke = 'var(--yellow)';

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', 14);
      text.setAttribute('y', 4);
      text.setAttribute('class', 'node-text');
      text.textContent = n.label;

      g.appendChild(circle);
      g.appendChild(text);
      nodesGroup.appendChild(g);
    }});
  }}

  renderList(nodes);
  layoutGraph();
</script>
</body>
</html>
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_template)


class ArchitectureScaffolder:
    """Auto-generates clean, pattern-matching boilerplate (routes, services, models) adhering to project style."""

    @staticmethod
    def scaffold(scaffold_type: str, name: str, target_dir: Optional[str] = None):
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", name).lower()
        class_name = "".join(part.capitalize() for part in clean_name.split("_"))
        target_dir_path = Path(target_dir or ".").resolve()

        print(BANNER)
        print(f"  {C_CYAN}{C_BOLD}[SCAFFOLDER] Synthesizing architectural component: {clean_name}{C_RESET}\n")

        if scaffold_type in ("route", "api", "endpoint"):
            file_path = target_dir_path / f"{clean_name}_routes.py"
            code = f'''"""
===============================================================================
  {class_name} API Router
  Generated autonomously by ASTERIX OS Cartographer
===============================================================================
"""

from typing import Dict, Any, List, Optional

# Standard Route Dispatcher & Controller
class {class_name}Controller:
    """Handles business operations for {clean_name}."""
    
    @classmethod
    def list_items(cls, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve paginated collection of {clean_name}."""
        return [{{"id": 1, "name": "{clean_name}_demo", "status": "active"}}]

    @classmethod
    def get_by_id(cls, item_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single {clean_name} entity."""
        return {{"id": item_id, "name": "{clean_name}_entity"}}

    @classmethod
    def create(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and create new {clean_name} entity."""
        return {{"status": "created", "data": payload}}

# Framework Handler Stubs (FastAPI / Flask compatible)
def register_routes(app_router):
    """Registers standard REST endpoints."""
    app_router.add_route("GET", "/api/{clean_name}", {class_name}Controller.list_items)
    app_router.add_route("GET", "/api/{clean_name}/<id>", {class_name}Controller.get_by_id)
    app_router.add_route("POST", "/api/{clean_name}", {class_name}Controller.create)
'''
        elif scaffold_type in ("service", "controller"):
            file_path = target_dir_path / f"{clean_name}_service.py"
            code = f'''"""
===============================================================================
  {class_name} Service Layer
  Generated autonomously by ASTERIX OS Cartographer
===============================================================================
"""

from typing import Dict, Any, Optional

class {class_name}Service:
    """Core domain logic and transactions for {clean_name}."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}

    def execute_workflow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes transactional logic with validation."""
        if not params:
            raise ValueError("Parameters cannot be empty.")
        
        result = {{
            "operation": "{clean_name}",
            "status": "success",
            "payload": params
        }}
        return result
'''
        elif scaffold_type in ("model", "schema"):
            file_path = target_dir_path / f"{clean_name}_model.py"
            code = f'''"""
===============================================================================
  {class_name} Data Model & Schema
  Generated autonomously by ASTERIX OS Cartographer
===============================================================================
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class {class_name}Model:
    """Represents a persisted entity for {clean_name}."""
    id: Optional[int] = None
    name: str = ""
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {{
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "metadata": self.metadata,
            "created_at": self.created_at
        }}
'''
        else:
            print(f"  {C_RED}[ERROR] Unknown scaffold type: {scaffold_type}{C_RESET}")
            print("  Available types: route, service, model")
            return

        file_path.write_text(code, encoding="utf-8")
        print(f"  {C_GREEN}✓ Successfully scaffolded:{C_RESET} {file_path}")
        print(f"  {C_DIM}Zero boilerplate needed. Ready for immediate logic implementation.{C_RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="ASTERIX OS Codebase Cartographer & Architecture Synthesizer",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="subcommand")

    # ax map subcommand
    map_parser = subparsers.add_parser("map", help="Scan and analyze codebase architecture")
    map_parser.add_argument("path", nargs="?", default=".", help="Root directory of the project to analyze")
    map_parser.add_argument("--tree", action="store_true", help="Display colored ASCII topology tree")
    map_parser.add_argument("--audit", action="store_true", help="Run deep architectural audit (cycles, orphans, bottlenecks)")
    map_parser.add_argument("--context", "-c", action="store_true", help="Emit ultra-dense architectural blueprint for AI/LLMs")
    map_parser.add_argument("--mermaid", action="store_true", help="Generate Mermaid.js markdown graph")
    map_parser.add_argument("--html", metavar="OUT_FILE", help="Generate interactive zero-dependency HTML dashboard")
    map_parser.add_argument("--json", metavar="OUT_FILE", help="Dump complete topology graph to JSON file")
    map_parser.add_argument("--summary", action="store_true", help="Display summary overview (default)")

    # ax scaffold subcommand
    scaffold_parser = subparsers.add_parser("scaffold", help="Generate pattern-aware architecture boilerplate")
    scaffold_parser.add_argument("type", choices=["route", "api", "service", "controller", "model", "schema"], help="Component type to scaffold")
    scaffold_parser.add_argument("name", help="Name of the component")
    scaffold_parser.add_argument("--dir", default=".", help="Destination directory")

    if len(sys.argv) > 1 and sys.argv[1] not in ("map", "scaffold", "-h", "--help"):
        sys.argv.insert(1, "map")

    args = parser.parse_args()

    if args.subcommand == "scaffold":
        ArchitectureScaffolder.scaffold(args.type, args.name, args.dir)
    else:
        target_path = getattr(args, "path", ".")
        cartographer = CodebaseCartographer(target_path)
        cartographer.scan()

        if getattr(args, "context", False):
            print(cartographer.export_context_blueprint())
        elif getattr(args, "mermaid", False):
            print(cartographer.export_mermaid())
        elif getattr(args, "audit", False):
            cartographer.print_audit()
        elif getattr(args, "tree", False):
            cartographer.print_tree()
        elif getattr(args, "html", None):
            cartographer.export_html_dashboard(args.html)
            print(f"  {C_GREEN}✓ Interactive Architecture Dashboard saved to:{C_RESET} {args.html}")
        elif getattr(args, "json", None):
            data = {
                "nodes": {k: v.to_dict() for k, v in cartographer.nodes.items()},
                "cycles": cartographer.cycles,
                "orphans": cartographer.orphans,
                "bottlenecks": cartographer.bottlenecks
            }
            Path(args.json).write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  {C_GREEN}✓ JSON Topology graph saved to:{C_RESET} {args.json}")
        else:
            cartographer.print_summary()

if __name__ == "__main__":
    main()
