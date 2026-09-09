#!/usr/bin/env python3
"""ASTERIX OS self-learning loop.

This script reads recent memory.log entries, tells the user_input_learner about
what happened, and then asks the local Ollama model to generate 3 new IF/THEN
rules for the weekly knowledge base.
"""

import json
from pathlib import Path

from ai_brain import learning_mode
from user_input_learner import ingest_query, teach_fact, learn_from_memory_events


def load_recent_events(path: str = "memory.log", limit: int = 200):
    """Return the latest memory entries as a list of dictionaries."""
    file_path = Path(path)
    if not file_path.exists():
        return []

    events = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                events.append(entry)
            except Exception:
                continue
    return events[-limit:]


def run_self_learning(memory_log: str = "memory.log") -> str:
    """Train the profile from memory and generate rules for later use."""
    events = load_recent_events(memory_log, limit=500)
    if not events:
        print("[ASTERIX] No memory events found yet. Nothing to learn.")
        return "suggested_rules.txt"

    # feed every event back through memory analysis to create stronger, persistent preferences
    learn_from_memory_events(events)

    for event in events:
        problem = event.get("problem", "")
        action = event.get("action", "")
        result = event.get("result", "")
        summary = f"Problem: {problem}. Action: {action}. Result: {result}."
        ingest_query(summary)
        teach_fact(summary)

    rules_path = learning_mode(memory_log, "suggested_rules.txt")
    print(f"[ASTERIX] Self-learning complete. Rules saved to {rules_path}")
    return rules_path


if __name__ == "__main__":
    run_self_learning()
