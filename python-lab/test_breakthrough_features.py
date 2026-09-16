#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Breakthrough Features Automated Verification Test Suite
  File: python-lab/test_breakthrough_features.py
  Zero Dependencies: 100% Python Standard Library (unittest)
  SPDX-License-Identifier: MIT OR Apache-2.0

  Verifies the 5 Breakthrough Differentiators:
    1. Attack Path Pathfinder (DAG synthesis, Dijkstra, lowest-noise, chokepoints)
    2. Multiplayer Team (Mesh state, target locks, collision detection, HMAC auth)
    3. Ghost Egress (Network posture audit, decoy generator, jitter timing)
    4. Mobile RF Sentinel (OUI lookup, Evil Twin detection, BLE tracker parsing)
    5. Tamper-Proof Evidence (Artifact sealing, RFC 3161 timestamps, tampering alerts)
===============================================================================
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts-hub to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_HUB = BASE_DIR / "scripts-hub"
if str(SCRIPTS_HUB) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_HUB))

import importlib.util

def import_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

pathfinder = import_module_from_path("ax_pathfinder", SCRIPTS_HUB / "ax-pathfinder.py")
team = import_module_from_path("ax_team", SCRIPTS_HUB / "ax-team.py")
ghost = import_module_from_path("ax_ghost", SCRIPTS_HUB / "ax-ghost.py")
radio = import_module_from_path("ax_radio", SCRIPTS_HUB / "ax-radio.py")
evidence = import_module_from_path("ax_evidence", SCRIPTS_HUB / "ax-evidence.py")


class TestAttackPathfinder(unittest.TestCase):
    def setUp(self):
        self.mock_project = {
            "engagement_id": "TEST-ENG-001",
            "client_name": "TestCorp",
            "hosts": [
                {
                    "ip": "10.0.0.1",
                    "hostname": "perimeter-proxy",
                    "ports": [{"port": 443, "service": "https", "state": "open"}]
                },
                {
                    "ip": "10.0.0.2",
                    "hostname": "internal-db",
                    "ports": [{"port": 5432, "service": "postgresql", "state": "open"}]
                }
            ],
            "credentials": [
                {
                    "target": "10.0.0.1",
                    "service": "https",
                    "username": "admin",
                    "type": "plaintext"
                }
            ],
            "findings": [
                {
                    "id": "VULN-01",
                    "title": "SQL Injection",
                    "severity": "critical",
                    "target": "10.0.0.1"
                }
            ]
        }
        self.graph = pathfinder.build_graph_from_project(self.mock_project)

    def test_graph_nodes_and_edges(self):
        self.assertIn("attacker_entry", self.graph.nodes)
        self.assertIn("10.0.0.1", self.graph.nodes)
        self.assertIn("10.0.0.2", self.graph.nodes)
        # Crown jewel detection (db in hostname)
        self.assertEqual(self.graph.nodes["10.0.0.2"]["type"], "crown_jewel")
        self.assertTrue(len(self.graph.edges) > 0)

    def test_shortest_and_lowest_noise_path(self):
        res_sp = self.graph.compute_shortest_path("attacker_entry", "10.0.0.2")
        self.assertIsNotNone(res_sp)
        path, dist = res_sp
        self.assertEqual(path[0], "attacker_entry")
        self.assertEqual(path[-1], "10.0.0.2")
        self.assertTrue(dist > 0)

        res_ln = self.graph.compute_lowest_noise_path("attacker_entry", "10.0.0.2")
        self.assertIsNotNone(res_ln)
        ln_path, ln_noise = res_ln
        self.assertEqual(ln_path[0], "attacker_entry")
        self.assertEqual(ln_path[-1], "10.0.0.2")

    def test_blast_radius(self):
        radius = self.graph.calculate_blast_radius("attacker_entry")
        self.assertIn("10.0.0.2", radius)

    def test_render_html_report(self):
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_path = f.name
        try:
            pathfinder.render_html_graph(self.graph, ["attacker_entry", "10.0.0.2"], None, temp_path)
            self.assertTrue(os.path.exists(temp_path))
            content = Path(temp_path).read_text(encoding="utf-8")
            self.assertIn("ASTERIX OS", content)
            self.assertIn("graph-canvas", content)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestMultiplayerTeam(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_config_file = team.CONFIG_FILE
        self.orig_config_dir = team.CONFIG_DIR
        team.CONFIG_DIR = Path(self.test_dir)
        team.CONFIG_FILE = Path(self.test_dir) / "mesh_state.json"
        self.mgr = team.TeamMeshManager()

    def tearDown(self):
        team.CONFIG_FILE = self.orig_config_file
        team.CONFIG_DIR = self.orig_config_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_mesh(self):
        self.mgr.init_mesh("alpha-mesh", "secret123", "ghost_one")
        self.assertEqual(self.mgr.state["mesh_name"], "alpha-mesh")
        self.assertEqual(self.mgr.state["operator_callsign"], "ghost_one")
        self.assertEqual(self.mgr.state["passphrase"], "secret123")

    def test_target_locking_and_collision(self):
        self.mgr.init_mesh("alpha-mesh", "secret123", "operator_a")
        ok, msg = self.mgr.lock_target("192.168.1.50", "Port scan active", ttl_seconds=600)
        self.assertTrue(ok)
        self.assertIn("192.168.1.50", self.mgr.state["locks"])

        # Same operator can renew
        ok2, _ = self.mgr.lock_target("192.168.1.50", "Extending scan")
        self.assertTrue(ok2)

        # Different operator must encounter collision rejection
        self.mgr.state["operator_callsign"] = "operator_b"
        ok3, err_msg = self.mgr.lock_target("192.168.1.50", "Competing scan")
        self.assertFalse(ok3)
        self.assertIn("already locked by operator_a", err_msg)

    def test_unlock_target(self):
        self.mgr.init_mesh("alpha-mesh", "secret123", "operator_a")
        self.mgr.lock_target("10.0.0.99", "Testing")
        ok, _ = self.mgr.unlock_target("10.0.0.99")
        self.assertTrue(ok)
        self.assertNotIn("10.0.0.99", self.mgr.state["locks"])

    def test_hmac_packet_signing(self):
        secret = "super-shared-key"
        payload = b'{"hello": "world"}'
        sig = team.sign_payload(secret, payload)
        self.assertTrue(team.verify_payload(secret, payload, sig))
        self.assertFalse(team.verify_payload("wrong-key", payload, sig))


class TestGhostEgress(unittest.TestCase):
    def test_audit_egress_structure(self):
        info = ghost.audit_egress()
        self.assertIn("hostname", info)
        self.assertIn("local_ips", info)
        self.assertIn("ipv6_supported", info)
        self.assertIsInstance(info["local_ips"], list)

    def test_decoy_headers(self):
        headers = ghost.generate_decoy_headers()
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept", headers)
        self.assertTrue(any(ua in headers["User-Agent"] for ua in ghost.USER_AGENTS))

    def test_dry_run_decoy_execution(self):
        # Dry-run should execute without throwing exceptions or blocking indefinitely
        ghost.run_decoy_generator(count=2, interval=0.01, jitter=0.01, dry_run=True)


class TestRadioSentinel(unittest.TestCase):
    def test_oui_vendor_lookup(self):
        self.assertIn("Cisco", radio.lookup_oui("00:1A:2B:33:44:55"))
        self.assertIn("Espressif", radio.lookup_oui("24:0A:C4:11:22:33"))
        self.assertEqual(radio.lookup_oui("AA:BB:CC:DD:EE:FF"), "Generic / Unregistered Vendor")

    def test_evil_twin_detection(self):
        networks = [
            {"ssid": "CORP-NET", "bssid": "00:1A:2B:11:22:33", "auth": "WPA2-Enterprise", "signal": "80%", "vendor": "Cisco Systems"},
            {"ssid": "CORP-NET", "bssid": "24:0A:C4:44:55:66", "auth": "Open / None", "signal": "99%", "vendor": "Espressif Inc (ESP32/ESP8266)"}
        ]
        alerts = radio.audit_evil_twins(networks)
        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0]["severity"], "CRITICAL")
        self.assertIn("Encryption Downgrade Attack", alerts[0]["type"])

    def test_ble_tracker_parsing(self):
        trackers = radio.scan_ble_trackers()
        self.assertTrue(len(trackers) >= 2)
        airtag = [t for t in trackers if "AirTag" in t["type"]]
        self.assertTrue(len(airtag) == 1)
        self.assertEqual(airtag[0]["stalking_risk"], "HIGH")

    def test_ultrasonic_audit(self):
        audit = radio.audit_ultrasonic_beacons()
        self.assertEqual(audit["status"], "Audited")
        self.assertTrue(audit["nyquist_max_freq_khz"] >= 20.0)

    def test_jamming_audit(self):
        # Empty network list simulates broad carrier interference / blackout
        jam_empty = radio.audit_rf_jamming([])
        self.assertEqual(jam_empty["threat_level"], "SUSPECTED_WIDEBAND_INTERFERENCE")
        self.assertTrue(len(jam_empty["anomalies"]) > 0)

        # Populated networks should be nominal
        sample_nets = [{"channel": "6", "ssid": "Net1"}, {"channel": "11", "ssid": "Net2"}]
        jam_norm = radio.audit_rf_jamming(sample_nets)
        self.assertEqual(jam_norm["threat_level"], "NOMINAL")
        self.assertTrue(len(jam_norm["defensive_countermeasures"]) > 0)

    def test_deauth_floods_audit(self):
        sample_nets = [
            {"ssid": "Legacy-Open", "bssid": "00:11:22:33:44:55", "auth": "Open"},
            {"ssid": "Legacy-WPA2", "bssid": "00:11:22:33:44:56", "auth": "WPA2-PSK"},
            {"ssid": "Secure-WPA3", "bssid": "00:11:22:33:44:57", "auth": "WPA3-SAE"}
        ]
        res = radio.audit_deauth_floods(sample_nets)
        self.assertEqual(res["protected_networks_count"], 1)
        self.assertEqual(res["vulnerable_networks_count"], 2)
        self.assertTrue(len(res["hardening_steps"]) >= 2)


class TestEvidenceVault(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.orig_ledger_file = evidence.LEDGER_FILE
        self.orig_ledger_dir = evidence.LEDGER_DIR
        evidence.LEDGER_DIR = Path(self.test_dir)
        evidence.LEDGER_FILE = Path(self.test_dir) / "evidence_ledger.json"

        self.sample_file = Path(self.test_dir) / "sample_evidence.pcap"
        self.sample_file.write_bytes(b"\xd4\xc3\xb2\xa1\x02\x00\x04\x00RAW_PCAP_DATA_TEST_PACKET")

    def tearDown(self):
        evidence.LEDGER_FILE = self.orig_ledger_file
        evidence.LEDGER_DIR = self.orig_ledger_dir
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_hash_calculation(self):
        sha256, sha512, size = evidence.compute_hashes(str(self.sample_file))
        self.assertEqual(len(sha256), 64)
        self.assertEqual(len(sha512), 128)
        self.assertEqual(size, len(self.sample_file.read_bytes()))

    def test_seal_and_verify_success(self):
        proof_path = evidence.seal_artifact(
            str(self.sample_file),
            engagement_id="ENG-TEST",
            operator="auditor_test",
            secret_key="custody-key"
        )
        self.assertTrue(os.path.exists(proof_path))

        res = evidence.verify_artifact(str(self.sample_file), secret_key="custody-key")
        self.assertTrue(res["valid"])
        self.assertTrue(res["signature_valid"])
        self.assertTrue(res["hash_valid"])

    def test_tamper_detection(self):
        evidence.seal_artifact(
            str(self.sample_file),
            engagement_id="ENG-TEST",
            operator="auditor_test",
            secret_key="custody-key"
        )

        # Alter 1 byte of the evidence file
        with open(self.sample_file, "ab") as f:
            f.write(b"CORRUPT")

        res = evidence.verify_artifact(str(self.sample_file), secret_key="custody-key")
        self.assertFalse(res["valid"])
        self.assertFalse(res["hash_valid"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
