#!/usr/bin/env python3
"""
Unit and Integration Tests for ASTERIX OS Debian Rootless Subsystem & Folder Engine
"""

import os
import sys
import shutil
import tempfile
import unittest
from pathlib import Path

# Add scripts-hub to sys.path and load ax-debian-manager.py
REPO_ROOT = Path(__file__).parent.parent
mgr_path = REPO_ROOT / "scripts-hub" / "ax-debian-manager.py"

import importlib.util
spec = importlib.util.spec_from_file_location("ax_debian_manager", str(mgr_path))
ax_debian_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ax_debian_manager)

DebianHardener = ax_debian_manager.DebianHardener
FolderEngine = ax_debian_manager.FolderEngine
DebianEnvironment = ax_debian_manager.DebianEnvironment
STANDARD_PERSISTENT_FOLDERS = ax_debian_manager.STANDARD_PERSISTENT_FOLDERS
FOLDER_TEMPLATES = ax_debian_manager.FOLDER_TEMPLATES


class TestFolderEngine(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="ax_test_persist_"))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_ensure_standard_folders(self):
        result = FolderEngine.ensure_standard_folders(base_dir=self.test_dir)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["created"]), len(STANDARD_PERSISTENT_FOLDERS))

        for f in STANDARD_PERSISTENT_FOLDERS:
            folder_path = self.test_dir / f
            self.assertTrue(folder_path.is_dir(), f"Folder '{f}' should exist")
            keep_file = folder_path / ".keep"
            self.assertTrue(keep_file.is_file(), f"Keep file in '{f}' should exist")

    def test_create_folder_with_template(self):
        # Test recon template
        res = FolderEngine.create_folder(
            name="target_alpha",
            template="recon",
            parent_dir=str(self.test_dir)
        )
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["write_verified"])

        created_dir = Path(res["path"])
        self.assertTrue(created_dir.is_dir())
        self.assertTrue((created_dir / "README.md").is_file())

        for expected_sub in FOLDER_TEMPLATES["recon"]["subdirs"]:
            self.assertTrue(
                (created_dir / expected_sub).is_dir(),
                f"Subdirectory '{expected_sub}' missing"
            )

    def test_create_folder_exploit_template(self):
        res = FolderEngine.create_folder(
            name="cve_2026_test",
            template="exploit",
            parent_dir=str(self.test_dir)
        )
        self.assertEqual(res["status"], "ok")
        created_dir = Path(res["path"])
        for expected_sub in FOLDER_TEMPLATES["exploit"]["subdirs"]:
            self.assertTrue((created_dir / expected_sub).is_dir())

    def test_fix_permissions_and_locks(self):
        sub = self.test_dir / "proj1"
        sub.mkdir(parents=True, exist_ok=True)
        test_file = sub / "test.txt"
        test_file.write_text("hello", encoding="utf-8")
        stale_lock = sub / "build.lock"
        stale_lock.write_text("lock", encoding="utf-8")

        res = FolderEngine.fix_permissions(self.test_dir)
        self.assertEqual(res["status"], "ok")
        self.assertGreaterEqual(res["cleaned_locks"], 1)
        self.assertFalse(stale_lock.exists(), "Stale lock file should be deleted")
        self.assertTrue(test_file.exists(), "Normal file should remain")

    def test_generate_tree(self):
        FolderEngine.ensure_standard_folders(base_dir=self.test_dir)
        tree_str = FolderEngine.generate_tree(self.test_dir, max_depth=2)
        self.assertIn("projects/", tree_str)
        self.assertIn("scans/", tree_str)
        self.assertIn("loot/", tree_str)


class TestDebianHardener(unittest.TestCase):
    def setUp(self):
        self.test_rootfs = Path(tempfile.mkdtemp(prefix="ax_test_rootfs_"))

    def tearDown(self):
        shutil.rmtree(self.test_rootfs, ignore_errors=True)

    def test_repair_all(self):
        repairs = DebianHardener.repair_all(custom_rootfs=self.test_rootfs)
        self.assertGreater(len(repairs), 0)

        # 1. Check APT Sandbox Config
        apt_file = self.test_rootfs / "etc/apt/apt.conf.d/99termux-rootless"
        self.assertTrue(apt_file.exists())
        content = apt_file.read_text(encoding="utf-8")
        self.assertIn('APT::Sandbox::User "root";', content)

        # 2. Check resolv.conf
        resolv_file = self.test_rootfs / "etc/resolv.conf"
        self.assertTrue(resolv_file.exists())
        r_content = resolv_file.read_text(encoding="utf-8")
        self.assertIn("nameserver 1.1.1.1", r_content)
        self.assertIn("nameserver 8.8.8.8", r_content)

        # 3. Check policy-rc.d
        policy_file = self.test_rootfs / "usr/sbin/policy-rc.d"
        self.assertTrue(policy_file.exists())
        p_content = policy_file.read_text(encoding="utf-8")
        self.assertIn("exit 101", p_content)

        # 4. Check /tmp and /dev/shm
        self.assertTrue((self.test_rootfs / "tmp").is_dir())
        self.assertTrue((self.test_rootfs / "dev/shm").is_dir())

        # 5. Check /etc/environment and hosts
        env_file = self.test_rootfs / "etc/environment"
        self.assertTrue(env_file.exists())
        self.assertIn("LANG=C.UTF-8", env_file.read_text(encoding="utf-8"))

        hosts_file = self.test_rootfs / "etc/hosts"
        self.assertTrue(hosts_file.exists())
        self.assertIn("127.0.0.1 localhost", hosts_file.read_text(encoding="utf-8"))

    def test_run_doctor_after_repair(self):
        # Run repair on mock rootfs
        DebianHardener.repair_all(custom_rootfs=self.test_rootfs)
        # Mock bin/sh
        sh_bin = self.test_rootfs / "bin/sh"
        sh_bin.parent.mkdir(parents=True, exist_ok=True)
        sh_bin.write_text("#!/bin/sh\n", encoding="utf-8")

        # Temporarily mock get_debian_rootfs
        orig_get_rootfs = DebianEnvironment.get_debian_rootfs
        try:
            DebianEnvironment.get_debian_rootfs = lambda: self.test_rootfs
            doc_res = DebianHardener.run_doctor(auto_fix=False)
            self.assertTrue(doc_res["overall_healthy"])
            for check in doc_res["checks"]:
                self.assertTrue(check["passed"], f"Check failed: {check['name']} - {check['detail']}")
        finally:
            DebianEnvironment.get_debian_rootfs = orig_get_rootfs


if __name__ == "__main__":
    unittest.main(verbosity=2)
