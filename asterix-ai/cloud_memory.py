#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Autonomous Cloud & Cognitive Memory Bridge (Supabase / REST / Local)
  Empowers Asterix AI with persistent vector/semantic cloud memory and local cache.
  Zero External Dependencies: 100% Python Standard Library (sqlite3, urllib, json).
  SPDX-License-Identifier: MIT OR Apache-2.0
===============================================================================
"""

import os
import sys
import re
import json
import time
import math
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Configuration paths
HOME_DIR = Path.home()
ASTERIX_DIR = Path(os.getenv("ASTERIX_ROOT", str(HOME_DIR / "ASTERIX-OS")))
CONFIG_PATH = ASTERIX_DIR / "asterix-ai" / "cloud_config.json"
DEFAULT_DB_PATH = ASTERIX_DIR / "asterix-ai" / "cognitive_memory.db"


class CloudMemoryBridge:
    """Manages local cognitive memory with seamless Supabase & REST cloud synchronization."""

    def __init__(self, db_path: Optional[Any] = None, config_path: Optional[Any] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.config_path = Path(config_path) if config_path else CONFIG_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.supabase_url: Optional[str] = os.getenv("ASTERIX_SUPABASE_URL")
        self.supabase_key: Optional[str] = os.getenv("ASTERIX_SUPABASE_KEY")
        self.cloud_table: str = os.getenv("ASTERIX_SUPABASE_TABLE", "asterix_memory")
        self._load_config()
        self._init_db()

    @contextmanager
    def _get_db(self):
        """Context manager for SQLite that guarantees commits and connection closure on all platforms."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _load_config(self):
        """Loads Supabase configuration from local config file if environment variables aren't set."""
        cfg_file = self.config_path if hasattr(self, "config_path") else CONFIG_PATH
        if not self.supabase_url and cfg_file.exists():
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
                self.supabase_url = data.get("supabase_url")
                self.supabase_key = data.get("supabase_key")
                self.cloud_table = data.get("table", self.cloud_table)
            except Exception:
                pass

    def load_config(self) -> Dict[str, Any]:
        """Returns the loaded Supabase configuration."""
        self._load_config()
        return {
            "supabase_url": self.supabase_url,
            "supabase_key": self.supabase_key,
            "table": self.cloud_table
        }

    def save_config(self, supabase_url: str, supabase_key: str, table: str = "asterix_memory"):
        """Persists Supabase credentials into config file."""
        self.supabase_url = supabase_url.strip().rstrip("/")
        self.supabase_key = supabase_key.strip()
        self.cloud_table = table.strip()
        cfg_file = self.config_path if hasattr(self, "config_path") else CONFIG_PATH
        cfg_file.parent.mkdir(parents=True, exist_ok=True)
        now_utc = datetime.now(timezone.utc).isoformat()
        cfg_file.write_text(json.dumps({
            "supabase_url": self.supabase_url,
            "supabase_key": self.supabase_key,
            "table": self.cloud_table,
            "updated_at": now_utc
        }, indent=2), encoding="utf-8")

    def _init_db(self):
        """Initializes high-performance local SQLite memory schema."""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 1,
                    synced INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    session_id TEXT DEFAULT 'default',
                    timestamp TEXT NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_topic ON memories(topic)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_synced ON memories(synced)")

    # ─────────────────────────────────────────────────────────────────────────
    # Local Memory Storage & Retrieval
    # ─────────────────────────────────────────────────────────────────────────

    def remember(
        self,
        topic: Optional[str] = None,
        content: Optional[str] = None,
        category: str = "general",
        importance: int = 1,
        tags: Optional[List[str]] = None,
        source: str = "user"
    ) -> int:
        """Stores a new fact, rule, or learned pattern in local cognitive memory."""
        if content is None:
            if topic is not None:
                body = topic
                subj = tags[0] if tags else category
            else:
                body = ""
                subj = "general"
        else:
            subj = topic if topic is not None else (tags[0] if tags else category)
            body = content

        now = datetime.now(timezone.utc).isoformat()
        mem_id = 0
        with self._get_db() as conn:
            cursor = conn.cursor()
            # Check if this exact memory already exists
            cursor.execute("SELECT id FROM memories WHERE topic = ? AND content = ?", (subj, body))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
            cursor.execute("""
                INSERT INTO memories (topic, content, category, importance, synced, created_at)
                VALUES (?, ?, ?, ?, 0, ?)
            """, (subj, body, category, importance, now))
            mem_id = cursor.lastrowid or 0

        # Try non-blocking background cloud sync if configured
        if self.is_cloud_connected():
            try:
                self.sync_entry_to_cloud(mem_id, subj, body, category, importance, now)
            except Exception:
                pass

        return mem_id

    def log_dialogue(self, role: str, message: str, session_id: str = "default"):
        """Logs conversation turns for contextual dialog recall."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (role, message, session_id, timestamp)
                VALUES (?, ?, ?, ?)
            """, (role, message, session_id, now))

    def get_recent_dialogue(self, limit: int = 8, session_id: str = "default") -> List[Dict[str, str]]:
        """Fetches the last N turns of the dialogue."""
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, message FROM conversations
                WHERE session_id = ? ORDER BY id DESC LIMIT ?
            """, (session_id, limit))
            rows = cursor.fetchall()
        rows.reverse()
        return [{"role": r[0], "message": r[1]} for r in rows]

    def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Semantic & token similarity search across stored memories."""
        query_tokens = set(re.findall(r'\w+', query.lower()))
        if not query_tokens:
            return []

        rows = []
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, topic, content, category, importance, created_at FROM memories")
            rows = cursor.fetchall()

        results = []
        for row in rows:
            mid, topic, content, category, imp, created = row
            text = f"{topic} {content} {category}".lower()
            tokens = set(re.findall(r'\w+', text))
            intersection = query_tokens.intersection(tokens)
            if intersection:
                score = (len(intersection) / math.sqrt(len(query_tokens) * len(tokens) + 1e-5)) * (1.0 + 0.2 * imp)
                results.append({
                    "id": mid,
                    "topic": topic,
                    "content": content,
                    "category": category,
                    "score": score,
                    "created_at": created
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def recall(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Alias for search_memories."""
        return self.search_memories(query, limit=limit)

    def get_context_block(self, query: str = "") -> str:
        """Constructs an augmented memory block to feed into AI reasoning."""
        memories = self.search_memories(query, limit=4) if query else []
        if not memories:
            # Fallback to top important general memories
            with self._get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT topic, content FROM memories
                    ORDER BY importance DESC, id DESC LIMIT 3
                """)
                memories = [{"topic": r[0], "content": r[1]} for r in cursor.fetchall()]

        if not memories:
            return ""

        lines = ["[ RECALLED COGNITIVE MEMORY CONTEXT ]"]
        for m in memories:
            lines.append(f" • [{m.get('topic', 'Fact')}]: {m['content']}")
        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # Supabase & Cloud Synchronization
    # ─────────────────────────────────────────────────────────────────────────

    def is_cloud_connected(self) -> bool:
        """Returns True if Supabase credentials are configured."""
        return bool(self.supabase_url and self.supabase_key)

    def sync_entry_to_cloud(self, mem_id: int, topic: str, content: str, category: str, importance: int, created_at: str):
        """Pushes a single memory record to Supabase via PostgREST."""
        if not self.is_cloud_connected():
            return False

        endpoint = f"{self.supabase_url}/rest/v1/{self.cloud_table}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
        payload = {
            "topic": topic,
            "content": content,
            "category": category,
            "importance": importance,
            "created_at": created_at
        }
        req = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status in (200, 201, 204):
                    with self._get_db() as conn:
                        conn.cursor().execute("UPDATE memories SET synced = 1 WHERE id = ?", (mem_id,))
                    return True
        except Exception:
            pass
        return False

    def sync_cloud(self) -> Dict[str, Any]:
        """Performs bidirectional memory synchronization with Supabase."""
        if not self.is_cloud_connected():
            return {
                "status": "offline",
                "message": "Cloud sync deferred: Supabase URL or Key not configured. Using local cognitive cache."
            }

        # 1. Push unsynced memories
        pushed = 0
        with self._get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, topic, content, category, importance, created_at FROM memories WHERE synced = 0")
            unsynced = cursor.fetchall()

        for row in unsynced:
            if self.sync_entry_to_cloud(row[0], row[1], row[2], row[3], row[4], row[5]):
                pushed += 1

        # 2. Pull remote memories from Supabase
        pulled = 0
        endpoint = f"{self.supabase_url}/rest/v1/{self.cloud_table}?select=topic,content,category,importance,created_at&limit=100"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Accept": "application/json"
        }
        req = urllib.request.Request(endpoint, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=6) as resp:
                remote_records = json.loads(resp.read().decode("utf-8"))
                with self._get_db() as conn:
                    c = conn.cursor()
                    for r in remote_records:
                        c.execute("SELECT id FROM memories WHERE topic = ? AND content = ?", (r["topic"], r["content"]))
                        if not c.fetchone():
                            now_str = datetime.now(timezone.utc).isoformat()
                            c.execute("""
                                INSERT INTO memories (topic, content, category, importance, synced, created_at)
                                VALUES (?, ?, ?, ?, 1, ?)
                            """, (r["topic"], r["content"], r.get("category", "cloud"), r.get("importance", 1), r.get("created_at", now_str)))
                            pulled += 1
        except Exception as e:
            return {"status": "partial", "pushed": pushed, "pulled": pulled, "error": str(e)}

        return {"status": "success", "pushed": pushed, "pulled": pulled}

    def get_stats(self) -> Dict[str, Any]:
        """Returns overview stats of stored memories."""
        with self._get_db() as conn:
            c = conn.cursor()
            c.execute("SELECT count(*) FROM memories")
            total_mems = c.fetchone()[0]
            c.execute("SELECT count(*) FROM memories WHERE synced = 1")
            synced_mems = c.fetchone()[0]
            c.execute("SELECT count(*) FROM conversations")
            conv_count = c.fetchone()[0]
        unsynced_mems = total_mems - synced_mems
        return {
            "total_memories": total_mems,
            "synced_to_cloud": synced_mems,
            "unsynced_count": unsynced_mems,
            "dialogue_turns": conv_count,
            "dialogue_count": conv_count,
            "cloud_connected": self.is_cloud_connected(),
            "cloud_url": self.supabase_url or "Not Configured"
        }


# Global memory singleton instance
memory_hub = CloudMemoryBridge()

if __name__ == "__main__":
    hub = CloudMemoryBridge()
    hub.remember("Kernel Paging", "x86_64 paging uses 4-level PML4 translation tables.", "kernel", 2)
    hub.remember("Termux Optimization", "Termux storage is constrained; run ax mobile-sys clean regularly.", "termux", 2)
    print("Memory Hub Stats:", hub.get_stats())
    print("Context Search Test:", hub.get_context_block("paging in kernel"))
