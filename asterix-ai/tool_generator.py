#!/usr/bin/env python3
"""ASTERIX OS project-safe tool generator.

This module lets the AI generate safe internal tools for ASTERIX project work,
including UI, dashboard, memory, boot, and project-scoped automation modules.
It explicitly blocks unsafe system-level or destructive tool generation.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

REGISTRY_PATH = Path(__file__).resolve().with_name("tool_registry.json")

SAFE_CATEGORIES = {
    "ui", "dashboard", "boot", "theme", "monitor", "memory", "learning",
    "repair", "security", "automation", "shell", "config", "doc", "debugger"
}

BLOCKED_CATEGORIES = {
    "kernel", "bootloader", "firmware", "hardware", "system", "device",
    "partition", "registry", "service", "sudo", "exploit", "payload", "malware"
}

TOOL_LIBRARY = {
    "created": [],
    "blocked": [],
}


def load_registry() -> Dict[str, Any]:
    default_registry = {"tools": [], "pending": [], "approved": []}
    if not REGISTRY_PATH.exists():
        save_registry(default_registry)
        return default_registry
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            save_registry(default_registry)
            return default_registry
        normalized = {**default_registry, **data}
        normalized["tools"] = list(data.get("tools", []))
        normalized["pending"] = list(data.get("pending", []))
        normalized["approved"] = list(data.get("approved", []))
        save_registry(normalized)
        return normalized
    except Exception:
        save_registry(default_registry)
        return default_registry


def save_registry(registry: Dict[str, Any]) -> Dict[str, Any]:
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    safe_registry = {
        "tools": list(registry.get("tools", [])),
        "pending": list(registry.get("pending", [])),
        "approved": list(registry.get("approved", [])),
    }
    with open(REGISTRY_PATH, "w", encoding="utf-8") as handle:
        json.dump(safe_registry, handle, indent=2)
    return safe_registry


def register_tool(tool_name: str, tool_type: str, description: str, status: str = "pending", project_scope: str = "project") -> Dict[str, Any]:
    registry = load_registry()
    tool_path = str(Path(__file__).resolve().parent / f"{tool_name}.py")
    entry = {
        "name": tool_name,
        "type": tool_type,
        "description": description,
        "status": status,
        "project_scope": project_scope,
        "approval": "manual" if status == "pending" else "approved",
        "path": tool_path,
    }
    registry.setdefault("tools", [])
    registry["tools"].append(entry)
    if status == "pending":
        registry.setdefault("pending", []).append(tool_name)
    else:
        registry.setdefault("approved", []).append(tool_name)
    return save_registry(registry)


def approve_tool(tool_name: str) -> Dict[str, Any]:
    registry = load_registry()
    for entry in registry.get("tools", []):
        if entry.get("name") == tool_name:
            entry["status"] = "approved"
            entry["approval"] = "approved"
            entry.setdefault("path", str(Path(__file__).resolve().parent / f"{tool_name}.py"))
            if tool_name in registry.get("pending", []):
                registry["pending"] = [name for name in registry["pending"] if name != tool_name]
            if tool_name not in registry.get("approved", []):
                registry.setdefault("approved", []).append(tool_name)
            save_registry(registry)
            return entry
    return {"status": "not_found", "name": tool_name}


def _safe_tool_template(tool_type: str, name: str, description: str) -> str:
    return f'''#!/usr/bin/env python3
"""ASTERIX OS generated tool: {name}

Purpose: {description}
This tool is project-scoped and approved for ASTERIX work only.
"""

from pathlib import Path


def run():
    """Primary tool entry point."""
    print(f"[ASTERIX] {tool_type}: {name} ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
'''


def _blocked_reason(tool_type: str, reason: str) -> str:
    return (
        f"Blocked: unsafe {tool_type} generation rejected. "
        f"Reason: {reason}. This system only authorizes project-safe internal tooling."
    )


def generate_safe_tool(tool_type: str, description: str, categories=None, project_scope: str = "project") -> Dict[str, Any]:
    """Generate a safe ASTERIX internal tool and persist it in the local project workspace.

    The generator blocks any system-level, destructive, or bootloader/hardware mutation requests.
    """
    categories = set((categories or []) + [tool_type.lower()])
    scope = str(project_scope or "project").lower()
    tool_name = re.sub(r"[^a-z0-9_-]+", "_", str(tool_type).lower()).strip("_") or "asterix_tool"
    safety = "safe"

    if not tool_name:
        return {"status": "blocked", "reason": "Blocked: empty tool name", "safety": "unsafe"}

    if any(category in BLOCKED_CATEGORIES for category in categories):
        reason = "contains blocked system or destructive categories"
        TOOL_LIBRARY["blocked"].append(tool_name)
        return {
            "status": "blocked",
            "tool_type": tool_type,
            "file_name": f"{tool_name}.py",
            "reason": _blocked_reason(tool_type, reason),
            "safety": "unsafe",
            "project_scope": scope,
        }

    if scope not in {"project", "workspace", "repo", "codebase", "memory", "learning", "ai", "repair", "ui", "dashboard", "boot", "config", "debugger"}:
        reason = "project_scope outside approved safe domain"
        TOOL_LIBRARY["blocked"].append(tool_name)
        return {
            "status": "blocked",
            "tool_type": tool_type,
            "file_name": f"{tool_name}.py",
            "reason": _blocked_reason(tool_type, reason),
            "safety": "unsafe",
            "project_scope": scope,
        }

    if any(category in BLOCKED_CATEGORIES for category in categories):
        reason = "contains blocked categories"
        TOOL_LIBRARY["blocked"].append(tool_name)
        return {
            "status": "blocked",
            "tool_type": tool_type,
            "file_name": f"{tool_name}.py",
            "reason": _blocked_reason(tool_type, reason),
            "safety": "unsafe",
            "project_scope": scope,
        }

    target_dir = Path(__file__).resolve().parent
    file_name = f"{tool_name}.py"
    target_path = target_dir / file_name

    code = _safe_tool_template(tool_type, tool_name, description)
    target_path.write_text(code, encoding="utf-8")

    TOOL_LIBRARY["created"].append(file_name)
    register_tool(tool_name, tool_type, description, status="pending", project_scope=scope)

    return {
        "status": "created",
        "tool_type": tool_type,
        "file_name": file_name,
        "path": str(target_path),
        "safety": safety,
        "reason": "project-safe tool creation queued for approval",
        "code": code,
        "project_scope": scope,
        "approval": "pending",
    }


def generate_dashboard_tool(name: str, description: str) -> Dict[str, Any]:
    return generate_safe_tool("dashboard", description, categories=["ui", "dashboard"], project_scope="dashboard")


def generate_boot_ui_tool(name: str, description: str) -> Dict[str, Any]:
    return generate_safe_tool("boot", description, categories=["ui", "boot"], project_scope="boot")


def generate_learning_tool(name: str, description: str) -> Dict[str, Any]:
    return generate_safe_tool("learning", description, categories=["learning", "memory"], project_scope="learning")


if __name__ == "__main__":
    sample = generate_safe_tool("dashboard", "mood dashboard panel", categories=["ui", "dashboard"], project_scope="project")
    print(json.dumps({"sample": sample}, indent=2))
