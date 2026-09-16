#!/usr/bin/env python3
"""
Unit tests for ASTERIX OS-Computing, Dual-OS Merge Engine & Unified Rebuild Pipeline.
Tests verify:
- Host telemetry gathering
- Cross-OS tool collaboration & shims
- Dual-OS Merge Engine (WSL/host bridging, unified environment generation, manifest)
- End-to-end 8-phase rebuild pipeline and cryptographic master manifest (BUILD_MANIFEST.json)
- Fast-path 's' CLI aliases (s, s.cmd, s.ps1)
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add os-computing to sys.path
TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent.parent
OS_COMP_DIR = REPO_ROOT / "os-computing"
sys.path.insert(0, str(OS_COMP_DIR))

import os_bridge


def test_get_host_info():
    """Verify that host telemetry gathers required hardware and OS attributes."""
    info = os_bridge.get_host_info()
    assert isinstance(info, dict)
    assert "os_type" in info
    assert "distro" in info
    assert "architecture" in info
    assert "cpu_count" in info
    assert info["cpu_count"] >= 1
    assert "runtimes" in info
    assert isinstance(info["runtimes"], dict)


def test_cmd_collaborate():
    """Verify collaborate bridge creates vault directories and environment profiles."""
    os_bridge.cmd_collaborate()
    assert os.path.isdir(os_bridge.BIN_BRIDGE)
    assert os.path.isdir(os_bridge.WORDLISTS_BRIDGE)
    assert os.path.isfile(os_bridge.STATE_FILE)
    
    with open(os_bridge.STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    assert "host_distro" in state
    assert "total_bridged" in state


def test_cmd_merge():
    """Verify Dual-OS merge engine creates merged bin, shims, environment files, and manifest."""
    manifest = os_bridge.cmd_merge()
    assert isinstance(manifest, dict)
    assert "fusion_engine" in manifest
    assert "primary_host" in manifest
    assert "metrics" in manifest
    assert "paths" in manifest

    # Check merged bin directory exists
    assert os.path.isdir(os_bridge.MERGED_BIN)
    assert os.path.isdir(os_bridge.MERGED_WORDLISTS)
    assert os.path.isfile(os_bridge.MERGED_STATE)

    # Check core ASTERIX shims exist in merged_bin
    exts = [".cmd", ".ps1"] if sys.platform == "win32" else [""]
    for core_tool in ["ax", "s", "ax-ai"]:
        found = any(os.path.isfile(os.path.join(os_bridge.MERGED_BIN, core_tool + ext)) for ext in exts)
        assert found, f"Core tool {core_tool} shim missing from {os_bridge.MERGED_BIN}"

    # Check environment files
    env_ps1 = os.path.join(os_bridge.MERGED_DIR, "merge-env.ps1")
    env_sh = os.path.join(os_bridge.MERGED_DIR, "merge-env.sh")
    env_bat = os.path.join(os_bridge.MERGED_DIR, "merge-env.bat")
    assert os.path.isfile(env_ps1)
    assert os.path.isfile(env_sh)
    assert os.path.isfile(env_bat)

    with open(env_ps1, "r", encoding="utf-8") as f:
        ps1_content = f.read()
    assert "ASTERIX_MERGED" in ps1_content
    assert "ASTERIX_ROOT" in ps1_content


def test_cmd_rebuild():
    """Verify 8-phase rebuild pipeline executes cleanly and generates BUILD_MANIFEST.json."""
    manifest_data = os_bridge.cmd_rebuild()
    assert isinstance(manifest_data, dict)
    assert manifest_data["system"] == "ASTERIX OS"
    assert manifest_data["codename"] == "Phantom"
    assert "phases" in manifest_data
    assert len(manifest_data["phases"]) == 8

    # Verify build manifest exists in project root
    assert os.path.isfile(os_bridge.BUILD_MANIFEST)
    with open(os_bridge.BUILD_MANIFEST, "r", encoding="utf-8") as f:
        disk_manifest = json.load(f)

    assert "cryptographic_signatures" in disk_manifest
    signatures = disk_manifest["cryptographic_signatures"]
    assert "kernel/src/boot.asm" in signatures
    assert "boot-asm/asterix-stage2-loader.asm" in signatures
    assert "core-utils-c/src/asterix-crypto-core.c" in signatures
    assert "asterix-ai/cloud_memory.py" in signatures
    assert "bin/ax" in signatures
    assert len(signatures["bin/ax"]) == 64  # SHA-256 hex string


def test_s_entrypoints_exist():
    """Verify that 's' fast-path entrypoints exist and forward to 'ax'."""
    bin_dir = REPO_ROOT / "bin"
    s_sh = bin_dir / "s"
    s_cmd = bin_dir / "s.cmd"
    s_ps1 = bin_dir / "s.ps1"

    assert s_sh.is_file(), "bin/s bash script missing"
    assert s_cmd.is_file(), "bin/s.cmd batch script missing"
    assert s_ps1.is_file(), "bin/s.ps1 PowerShell script missing"

    with open(s_sh, "r", encoding="utf-8") as f:
        assert "ax" in f.read()

    with open(s_cmd, "r", encoding="utf-8") as f:
        assert "ax.cmd" in f.read()

    with open(s_ps1, "r", encoding="utf-8") as f:
        assert "ax.ps1" in f.read()
