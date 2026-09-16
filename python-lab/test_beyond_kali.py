#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Automated Test Suite for "Beyond Kali" Architecture
  Zero Dependencies: 100% Python Standard Library unittest
===============================================================================
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts-hub to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts-hub"))

from importlib import import_module
eng_mod = import_module("ax-engagement")
sandbox_mod = import_module("ax-sandbox")
attest_mod = import_module("ax-attestation")
sync_mod = import_module("ax-mobile-sync")


class TestBeyondKaliArchitecture(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ax_beyond_kali_test_"))
        # Patch engagement manager base directory to temp directory
        self.orig_base = eng_mod.get_base_persistent_dir
        eng_mod.get_base_persistent_dir = lambda: self.temp_dir
        self.orig_overlay_base = sandbox_mod.get_overlay_base
        sandbox_mod.get_overlay_base = lambda: self.temp_dir / "overlay"
        self.orig_log_file = attest_mod.TransparencyLog.get_log_file
        attest_mod.TransparencyLog.get_log_file = lambda: self.temp_dir / "test_transparency.jsonl"

    def tearDown(self):
        eng_mod.get_base_persistent_dir = self.orig_base
        sandbox_mod.get_overlay_base = self.orig_overlay_base
        attest_mod.TransparencyLog.get_log_file = self.orig_log_file
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unified_schema_exists_and_valid(self):
        """Test unified project schema JSON structure."""
        schema_path = REPO_ROOT / "schemas" / "asterix_project_schema.json"
        self.assertTrue(schema_path.exists())
        with schema_path.open("r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertEqual(schema["title"], "ASTERIX OS Unified Project Data Model")
        self.assertIn("engagement_id", schema["required"])
        self.assertIn("scope", schema["required"])
        self.assertIn("hosts", schema["required"])
        self.assertIn("findings", schema["required"])

    def test_engagement_workspace_and_scope_gating(self):
        """Test engagement creation and CIDR/domain scope enforcement."""
        mgr = eng_mod.EngagementManager()
        eng_dir = mgr.create_engagement(
            client="Cyberdyne",
            job_id="ENG-TEST-001",
            cidrs=["10.10.0.0/16", "172.16.5.0/24"],
            domains=["cyberdyne.corp", "api.cyberdyne.corp"]
        )
        self.assertTrue((eng_dir / "project.json").exists())
        self.assertTrue((eng_dir / "scope" / "scope.json").exists())

        # Test in-scope targets
        in_scope_ip, msg1 = mgr.is_target_in_scope("10.10.42.1")
        self.assertTrue(in_scope_ip)
        self.assertIn("authorized CIDR", msg1)

        in_scope_dom, msg2 = mgr.is_target_in_scope("auth.api.cyberdyne.corp")
        self.assertTrue(in_scope_dom)

        # Test out-of-scope targets
        out_scope_ip, msg3 = mgr.is_target_in_scope("8.8.8.8")
        self.assertFalse(out_scope_ip)
        self.assertIn("OUT OF SCOPE", msg3)

        out_scope_dom, msg4 = mgr.is_target_in_scope("evilcorp.com")
        self.assertFalse(out_scope_dom)

    def test_lab_vs_engagement_modes(self):
        """Test dual mode switching."""
        eng_mod.set_system_mode("lab")
        self.assertEqual(eng_mod.get_system_mode(), "lab")

        eng_mod.set_system_mode("engagement")
        self.assertEqual(eng_mod.get_system_mode(), "engagement")

        with self.assertRaises(ValueError):
            eng_mod.set_system_mode("invalid_mode")

    def test_host_finding_and_report_generation(self):
        """Test recording hosts, findings, and compiling automated report."""
        mgr = eng_mod.EngagementManager()
        mgr.create_engagement("UmbrellaCorp", "JOB-99", cidrs=["192.168.1.0/24"], domains=["umbrella.com"])

        # Add Host
        mgr.add_host("192.168.1.50", hostname="dc01.umbrella.com", ports=[{"port": 445, "proto": "tcp", "service": "smb"}])
        # Add Finding
        f_id = mgr.add_finding("EternalBlue SMB Vulnerability", "critical", "192.168.1.50:445", "Remote Code Execution via SMBv1", remediation="Disable SMBv1", cve="CVE-2017-0144")
        self.assertTrue(f_id.startswith("FIND-"))

        # Generate report
        report_file = self.temp_dir / "test_report.md"
        mgr.generate_report(report_file)
        self.assertTrue(report_file.exists())

        content = report_file.read_text(encoding="utf-8")
        self.assertIn("UmbrellaCorp", content)
        self.assertIn("JOB-99", content)
        self.assertIn("EternalBlue SMB Vulnerability", content)
        self.assertIn("CVE-2017-0144", content)
        self.assertIn("192.168.1.50", content)

    def test_overlayfs_rollback_simulation(self):
        """Test immutable base with mutable overlay and instant rollback."""
        ov = sandbox_mod.OverlayManager()
        # Simulate mutable changes in upperdir
        test_file = ov.upper_dir / "sketchy_tool_artifact.bin"
        test_file.write_text("compromised/malicious change", encoding="utf-8")
        st_before = ov.get_status()
        self.assertGreaterEqual(st_before["modified_file_count"], 1)

        # Rollback
        purged = ov.rollback()
        self.assertGreaterEqual(purged, 1)
        st_after = ov.get_status()
        self.assertEqual(st_after["modified_file_count"], 0)
        self.assertFalse(test_file.exists())

    def test_tpm_attestation_and_sbom(self):
        """Test TPM measured boot attestation and CycloneDX SBOM generator."""
        att = attest_mod.MeasuredBootEngine.measure_system()
        self.assertEqual(att["attestation_status"], "VALID_MEASURED_CHAIN")
        self.assertTrue(att["chain_of_custody_token"].startswith("AX-ATTEST-"))
        self.assertIn("PCR_00_KERNEL_CORE", att["pcr_measurements"])

        sbom_path = self.temp_dir / "test_sbom.json"
        data = attest_mod.SbomGenerator.generate_cyclonedx(sbom_path)
        self.assertEqual(data["bomFormat"], "CycloneDX")
        self.assertEqual(data["specVersion"], "1.5")
        self.assertGreater(len(data["components"]), 2)
        self.assertTrue(sbom_path.exists())

    def test_transparency_merkle_log(self):
        """Test append-only Merkle-linked package transparency log."""
        # Append 2 entries
        e1 = attest_mod.TransparencyLog.append_entry("asterix-core", "2.1.0", "abc123hash")
        self.assertEqual(e1["index"], 1)
        e2 = attest_mod.TransparencyLog.append_entry("asterix-tools-network", "2.1.0", "def456hash")
        self.assertEqual(e2["index"], 2)
        self.assertEqual(e2["prev_hash"], e1["entry_hash"])

        # Verify intact
        ok, count, msg = attest_mod.TransparencyLog.verify_log()
        self.assertTrue(ok)
        self.assertEqual(count, 2)

    def test_thermal_battery_governor(self):
        """Test governor throttle calculation."""
        gov = sync_mod.ThermalBatteryGovernor.calculate_throttle(max_threads=16)
        self.assertIn(gov["status"], ("OPTIMAL", "MODERATE_THROTTLE", "HEAVY_THROTTLE"))
        self.assertGreaterEqual(gov["recommended_threads"], 1)
        self.assertLessEqual(gov["recommended_threads"], 16)
        self.assertIn("battery_percent", gov)
        self.assertIn("cpu_temp_celsius", gov)


if __name__ == "__main__":
    unittest.main()
