#!/usr/bin/env python3
"""
ASTERIX OS lightweight memory logger.

This module keeps a small buffer in RAM and only writes to disk every
N events. That keeps Termux/Android I/O lag low while still preserving
system memory for later learning and troubleshooting.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class MemoryLogger:
    """Log system events as JSON lines to a memory.log file."""

    def __init__(self, path: str = "memory.log", flush_every: int = 20):
        self.path = Path(path)
        self.flush_every = max(1, int(flush_every))
        self.buffer: List[Dict[str, Any]] = []

        # Make sure the parent folder exists so this works from Termux or Linux.
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file if it does not exist.
        if not self.path.exists():
            self.path.touch()

    def remember(self, problem: str, action: str, result: str) -> None:
        """Store one decision in RAM and flush to disk periodically."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "problem": str(problem),
            "action": str(action),
            "result": str(result),
        }
        self.buffer.append(entry)

        if len(self.buffer) >= self.flush_every:
            self.flush()

    def flush(self) -> None:
        """Write all buffered entries to memory.log as JSON lines."""
        if not self.buffer:
            return

        try:
            with self.path.open("a", encoding="utf-8") as handle:
                for item in self.buffer:
                    handle.write(json.dumps(item, ensure_ascii=False) + "\n")
            self.buffer.clear()
        except Exception:
            # Keep the app alive even if storage is briefly unavailable.
            # Failing silently is safer than crashing the AI loop.
            pass

    def close(self) -> None:
        """Flush any remaining events before shutdown."""
        self.flush()


if __name__ == "__main__":
    logger = MemoryLogger()
    logger.remember("low battery", "save power mode", "battery saver enabled")
    logger.remember("cpu spike", "check process list", "processes normalized")
    logger.flush()
    print("memory log written")
