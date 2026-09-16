#!/usr/bin/env python3
"""
Unit tests for Asterix Peak AI and Cloud Memory Bridge.
Validates:
  - CloudMemoryBridge: local SQLite database, vector indexing, keyword search, dialogue logging
  - PeakCognitiveEngine: autonomous reasoning, fallback matrix, technical query synthesis
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cloud_memory import CloudMemoryBridge
from peak_brain import PeakCognitiveEngine, PEAK_KNOWLEDGE_TOPICS


def test_cloud_memory_local_crud():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        bridge = CloudMemoryBridge(db_path=db_path)

        # Store memory
        mid = bridge.remember(
            content="Microkernel uses int 0x80 for user-space system calls.",
            category="kernel",
            tags=["kernel", "syscall", "microkernel"],
            source="unit_test"
        )
        assert mid > 0

        # Query memory
        results = bridge.recall("syscall microkernel", limit=5)
        assert len(results) >= 1
        assert "int 0x80" in results[0]["content"]

        # Statistics
        stats = bridge.get_stats()
        assert stats["total_memories"] == 1
        assert stats["unsynced_count"] == 1
        assert stats["dialogue_count"] == 0


def test_cloud_memory_dialogue_logging():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        bridge = CloudMemoryBridge(db_path=db_path)

        bridge.log_dialogue("user", "Explain GDT setup in x86")
        bridge.log_dialogue("assistant", "The Global Descriptor Table defines memory segments.")

        history = bridge.get_recent_dialogue(limit=10)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert "GDT" in history[0]["message"]
        assert history[1]["role"] == "assistant"


def test_cloud_memory_config_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "cloud_config.json"
        db_path = Path(tmpdir) / "test_memory.db"

        # Monkeypatch CONFIG_PATH
        import cloud_memory
        orig_config_path = cloud_memory.CONFIG_PATH
        cloud_memory.CONFIG_PATH = config_path

        try:
            bridge = CloudMemoryBridge(db_path=db_path)
            bridge.save_config("https://xyzcompany.supabase.co", "anon-key-12345")

            loaded = bridge.load_config()
            assert loaded["supabase_url"] == "https://xyzcompany.supabase.co"
            assert loaded["supabase_key"] == "anon-key-12345"
        finally:
            cloud_memory.CONFIG_PATH = orig_config_path


def test_peak_ai_reasoning_microkernel(monkeypatch):
    engine = PeakCognitiveEngine()
    monkeypatch.setattr(engine, "query_ollama", lambda *args, **kwargs: None)
    response = engine.reason("How does the ASTERIX microkernel handle interrupts and syscalls?")
    assert len(response) > 50
    assert "IDT" in response or "0x80" in response or "Microkernel" in response


def test_peak_ai_reasoning_assembly(monkeypatch):
    engine = PeakCognitiveEngine()
    monkeypatch.setattr(engine, "query_ollama", lambda *args, **kwargs: None)
    response = engine.reason("Show me how to write an x86_64 assembly bootloader with protected mode")
    assert len(response) > 50
    assert "asm" in response.lower() or "mov" in response.lower() or "cr0" in response.lower()


def test_peak_ai_reasoning_c_crypto(monkeypatch):
    engine = PeakCognitiveEngine()
    monkeypatch.setattr(engine, "query_ollama", lambda *args, **kwargs: None)
    response = engine.reason("Explain ChaCha20 Poly1305 and AES symmetric cryptography in C")
    assert len(response) > 50
    assert "ChaCha20" in response or "crypto" in response.lower()


def test_peak_ai_general_fallback(monkeypatch):
    engine = PeakCognitiveEngine()
    monkeypatch.setattr(engine, "query_ollama", lambda *args, **kwargs: None)
    response = engine.reason("What is the speed of light in vacuum?")
    assert len(response) > 20
    assert "speed of light" in response.lower() or "ASTERIX" in response
