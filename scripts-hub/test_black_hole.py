import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from black_hole import BlackHole, default_policy
except ModuleNotFoundError as exc:
    raise AssertionError(f"black_hole module is missing: {exc}")


def test_policy_has_core_controls():
    policy = default_policy()
    assert "network" in policy
    assert "device_scan" in policy
    assert "hidden_device_detection" in policy


def test_blackhole_status_report_contains_required_sections():
    tool = BlackHole()
    report = tool.status_report()
    assert "privacy" in report
    assert "surveillance" in report
    assert "device_scan" in report


def test_blackhole_deep_probe_has_government_style_fields():
    tool = BlackHole()
    probe = tool.deep_probe()
    assert "risk_score" in probe
    assert "wifi_beacons" in probe
    assert "signal_summary" in probe
    assert "network_exposure" in probe
    assert "trace_assessment" in probe


def test_blackhole_verbose_report_includes_action_plan():
    tool = BlackHole()
    text = tool.verbose_report()
    assert "Action plan" in text or "Hostile surveillance" in text


def test_blackhole_has_aggressive_tracking_metrics():
    tool = BlackHole()
    probe = tool.deep_probe()
    assert "wifi_fingerprints" in probe
    assert "signal_intensity" in probe
    assert "risk_trend" in probe


def test_blackhole_usb_suspicion_and_verdict_fields():
    tool = BlackHole()
    probe = tool.deep_probe()
    assert "usb_device_check" in probe
    assert "targeted_surveillance_verdict" in probe
    assert "status" in probe["targeted_surveillance_verdict"]
    assert "samples" in probe["risk_trend"]


def test_blackhole_total_masking_is_best_effort_and_reports_hardening():
    tool = BlackHole()
    payload = tool.mask_internet(disconnect=True, aggressive=True)
    assert payload["total_masking"] is True
    assert "hardening_actions" in payload
    assert "best_effort" in payload["masking_guarantee"].lower()


if __name__ == "__main__":
    test_policy_has_core_controls()
    test_blackhole_status_report_contains_required_sections()
    test_blackhole_deep_probe_has_government_style_fields()
    test_blackhole_verbose_report_includes_action_plan()
    test_blackhole_has_aggressive_tracking_metrics()
    test_blackhole_usb_suspicion_and_verdict_fields()
    test_blackhole_total_masking_is_best_effort_and_reports_hardening()
    print("Black Hole tests passed")
