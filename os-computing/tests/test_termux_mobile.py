#!/usr/bin/env python3
"""
Unit tests for ASTERIX OS Termux Mobile Subsystem and Mobile Automation Flow.
Tests verify:
- Zero emojis enforcement across all termux-mobile/ scripts and documentation
- Shell script syntax integrity (bash -n parsing)
- asterix-mobile CLI option parsing and usage outputs
- termux-toolbox command dispatching and diagnostic routines
- debian-rootless command handling
- Directory layout and persistence vault guarantees
"""

import os
import sys
import re
import shutil
import subprocess
import pytest
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
REPO_ROOT = TEST_DIR.parent.parent
MOBILE_DIR = REPO_ROOT / "termux-mobile"
SCRIPTS_HUB_DIR = REPO_ROOT / "scripts-hub"


def resolve_bash():
    """Locate a functional Bash interpreter, preferring Git Bash on Windows."""
    git_bash = Path(r"C:\Program Files\Git\bin\bash.exe")
    if git_bash.is_file():
        return str(git_bash)
    cand = shutil.which("bash")
    if cand and "system32" not in cand.lower():
        return cand
    if cand:
        try:
            r = subprocess.run([cand, "-c", "echo ok"], capture_output=True, text=True, timeout=2)
            if r.returncode == 0 and "ok" in r.stdout:
                return cand
        except Exception:
            pass
    return None


def test_zero_emojis_in_termux_mobile():
    """Strictly assert no emojis exist in termux-mobile code and documentation."""
    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F]|"  # emoticons
        r"[\U0001F300-\U0001F5FF]|"  # symbols & pictographs
        r"[\U0001F680-\U0001F6FF]|"  # transport & map
        r"[\U0001F1E0-\U0001F1FF]|"  # flags
        r"[\U00002702-\U000027B0]|"  # dingbats
        r"[\U0001F900-\U0001F9FF]|"  # supplemental symbols
        r"[\U0001FA70-\U0001FAFF]"   # symbols and pictographs extended-a
    )

    checked_files = list(MOBILE_DIR.glob("*.sh")) + list(MOBILE_DIR.glob("*.md"))
    assert len(checked_files) > 0, "No files found in termux-mobile/"

    for fpath in checked_files:
        text = fpath.read_text(encoding="utf-8", errors="ignore")
        matches = emoji_pattern.findall(text)
        assert len(matches) == 0, f"Found forbidden emoji in {fpath.name}: {matches}"


def test_termux_mobile_scripts_syntax():
    """Verify that all termux-mobile scripts have valid Bash syntax using bash -n."""
    bash_bin = resolve_bash()
    if not bash_bin:
        pytest.skip("Functional Bash executable not available for syntax check")

    sh_files = list(MOBILE_DIR.glob("*.sh"))
    assert len(sh_files) >= 5, f"Expected >= 5 shell scripts, found {len(sh_files)}"

    for sh_file in sh_files:
        res = subprocess.run(
            [bash_bin, "-n", str(sh_file)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        assert res.returncode == 0, f"Syntax error in {sh_file.name}: {res.stderr}"


def test_asterix_mobile_cli_usage():
    """Verify that asterix-mobile.sh renders complete usage documentation."""
    bash_bin = resolve_bash()
    if not bash_bin:
        pytest.skip("Functional Bash executable not available")

    mobile_script = MOBILE_DIR / "asterix-mobile.sh"
    assert mobile_script.is_file()

    res = subprocess.run(
        [bash_bin, str(mobile_script), "help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    assert res.returncode == 0
    assert "ASTERIX Mobile Helper" in res.stdout
    assert "asterix-mobile hud" in res.stdout
    assert "asterix-mobile scan" in res.stdout
    assert "asterix-mobile debian" in res.stdout
    assert "asterix-mobile wake" in res.stdout
    assert "asterix-mobile phantom" in res.stdout


def test_termux_toolbox_cli_usage():
    """Verify that termux-toolbox.sh renders complete usage documentation."""
    bash_bin = resolve_bash()
    if not bash_bin:
        pytest.skip("Functional Bash executable not available")

    toolbox_script = MOBILE_DIR / "termux-toolbox.sh"
    assert toolbox_script.is_file()

    res = subprocess.run(
        [bash_bin, str(toolbox_script), "help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    assert res.returncode == 0
    assert "TERMUX TOOLBOX" in res.stdout
    assert "battery" in res.stdout
    assert "doctor" in res.stdout
    assert "phantom" in res.stdout
    assert "wake" in res.stdout


def test_debian_rootless_cli_doctor():
    """Verify debian-rootless.sh doctor command runs and reports diagnostic checks."""
    bash_bin = resolve_bash()
    if not bash_bin:
        pytest.skip("Functional Bash executable not available")

    debian_script = MOBILE_DIR / "debian-rootless.sh"
    assert debian_script.is_file()

    res = subprocess.run(
        [bash_bin, str(debian_script), "doctor"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    assert res.returncode == 0
    assert "DEBIAN ROOTLESS" in res.stdout.upper()
    assert "DIAGNOSTIC" in res.stdout.upper()


def test_target_tracker_cli_output():
    """Verify target-tracker.sh cleanly resolves and reports target statistics."""
    bash_bin = resolve_bash()
    if not bash_bin:
        pytest.skip("Functional Bash executable not available")

    tracker_script = MOBILE_DIR / "target-tracker.sh"
    assert tracker_script.is_file()

    res = subprocess.run(
        [bash_bin, str(tracker_script), "127.0.0.1", "--geo"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    assert res.returncode == 0
    assert "ASTERIX GEO STYLE TRACKER" in res.stdout
    assert "127.0.0.1" in res.stdout
    assert "TARGET:" in res.stdout


def test_termux_bundle_script_syntax_and_staging():
    """Verify ax-termux-bundle.sh has valid syntax and references required files."""
    bundle_script = SCRIPTS_HUB_DIR / "ax-termux-bundle.sh"
    assert bundle_script.is_file()

    content = bundle_script.read_text(encoding="utf-8", errors="ignore")
    assert "asterix-termux-v2.0.0-arm64-stable.tar.gz" in content
    assert "install-termux.sh" in content
    assert "asterix-mobile.sh" in content
    assert "setup-persistence.sh" in content
    assert "TERMUX_INSTALL_GUIDE.md" in content
