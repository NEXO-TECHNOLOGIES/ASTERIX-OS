import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from user_input_learner import (
    load_profile,
    learn_from_memory_events,
    analyze_emotional_state,
    continue_training_until_quota,
    build_adaptive_response,
    run_continuous_training_loop,
    live_profile_snapshot,
    self_evolve_decision,
    apply_self_evolution_update,
)
from code_healer import ProjectRepairPlanner, RepairVerifier


def test_live_profile_snapshot_reports_real_ai_state():
    snapshot = live_profile_snapshot()

    assert "mood" in snapshot
    assert "training_completed" in snapshot
    assert "learning_quota" in snapshot
    assert "response_style" in snapshot


def test_run_continuous_training_loop_keeps_learning_while_active():
    loop_state = run_continuous_training_loop(
        [
            {"problem": "grub is broken", "action": "repair bootloader", "result": "system booted again"},
            {"problem": "terminal broke", "action": "fix shell config", "result": "terminal works"},
        ],
        max_cycles=2,
    )

    assert loop_state["active"] is True
    assert loop_state["cycles_completed"] >= 2
    assert loop_state["last_status"] in {"learning", "quota_reached", "watching"}


def test_build_adaptive_response_switches_style_for_urgent_user():
    response = build_adaptive_response("Please hurry, this is driving me crazy and I need this now")

    assert response["style"] in {"empathetic-direct", "urgent-priority"}
    assert response["confidence"] >= 0.5
    assert "hurry" in response["message"].lower() or "fix" in response["message"].lower()


def test_continue_training_until_quota_reaches_target():
    profile = continue_training_until_quota([
        {"problem": "boot repair needed", "action": "repair grub", "result": "system recovered"},
        {"problem": "code fix needed", "action": "repair python compilation", "result": "code runs"},
        {"problem": "terminal boot issue", "action": "validate desktop launch", "result": "desktop opened"},
    ], quota=3)

    assert profile["training_mode"] == "quota_reached"
    assert profile["training_completed"] >= 3


def test_analyze_emotional_state_detects_frustration_and_urgency():
    mood = analyze_emotional_state("Please hurry, this is driving me crazy and I am really annoyed")

    assert mood["primary_mood"] in {"frustrated", "stressed", "urgent"}
    assert mood["urgency"] >= 2
    assert mood["frustration"] >= 2


def test_learn_from_memory_events_tracks_realistic_preferences():
    profile_before = load_profile()
    original_count = profile_before.get("interaction_count", 0)
    original_healing = profile_before.get("interest_weights", {}).get("autonomous_healing", 0)

    events = [
        {
            "problem": "Kali dual-boot menu failed after reinstall and bootloader mismatch",
            "action": "repair grub config and validate boot order",
            "result": "dual-boot booted into Kali desktop successfully",
        },
        {
            "problem": "Python script had syntax error and failed to compile",
            "action": "fix the code and keep the repair in memory for future runs",
            "result": "syntax corrected and code launched cleanly",
        },
    ]

    profile_after = learn_from_memory_events(events)

    assert profile_after["interaction_count"] >= original_count + 2
    assert profile_after["interest_weights"]["autonomous_healing"] >= original_healing + 1
    assert len(profile_after["learned_facts"]) >= 2
    assert any("boot" in fact["fact"].lower() for fact in profile_after["learned_facts"])


def test_project_repair_planner_ranks_related_files(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "app.py").write_text(
        "from utils import helper\n\n\ndef run():\n    return helper()\n",
        encoding="utf-8",
    )
    (project_dir / "utils.py").write_text(
        "def helper():\n    return 'ok'\n",
        encoding="utf-8",
    )

    planner = ProjectRepairPlanner(str(project_dir))
    plan = planner.plan_repair("helper is failing in the app path", target_files=["app.py"])

    assert plan["target_files"]
    assert "app.py" in plan["target_files"][0]
    assert plan["root_cause"]
    assert plan["confidence"] >= 0.3


def test_repair_verifier_checks_python_syntax(tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    file_path = project_dir / "app.py"
    file_path.write_text("print('ok')\n", encoding="utf-8")

    verifier = RepairVerifier(str(project_dir))
    result = verifier.verify_files([str(file_path)])

    assert result["passed"] is True
    assert result["results"][0]["status"] == "passed"
    assert "py_compile" in result["results"][0]["check"]


def test_self_evolution_allows_safe_learning_but_blocks_os_mutation():
    safe_decision = self_evolve_decision("memory-learning", "memory")
    blocked_decision = self_evolve_decision("rewrite bootloader", "system")

    assert safe_decision["allowed"] is True
    assert blocked_decision["allowed"] is False
    assert blocked_decision["requires_approval"] is True

    result = apply_self_evolution_update("The user prefers fast, no-nonsense repair advice", "memory")

    assert result["updated"] is True
    assert "user prefers fast" in result["fact"].lower()
