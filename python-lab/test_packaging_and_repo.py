#!/usr/bin/env python3
"""
===============================================================================
  ASTERIX OS — Automated Unit & Integration Tests: Packaging & APT Repository
  Zero Dependencies: 100% Python Standard Library unittest
===============================================================================
"""

import sys
import os
import shutil
import tempfile
import unittest
import hashlib
from pathlib import Path

# Add scripts-hub to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts-hub"))

from importlib import import_module
deb_builder = import_module("ax-deb-builder")
apt_repo = import_module("ax-apt-repo")


class TestDebPackagingAndRepo(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ax_pkg_test_"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_single_deb(self):
        """Test building a single Debian package and inspecting its ar structure."""
        out_deb = self.temp_dir / "test-pkg_1.0.0_all.deb"
        created = deb_builder.build_deb(
            package_name="test-pkg",
            version="1.0.0",
            description="Test Package\n Long description test line.",
            depends="curl, wget",
            output_path=out_deb
        )
        self.assertTrue(out_deb.exists())
        self.assertGreater(out_deb.stat().st_size, 100)

        # Inspect ar magic
        with out_deb.open("rb") as f:
            magic = f.read(8)
            self.assertEqual(magic, b"!<arch>\n")

    def test_extract_control(self):
        """Test parsing control metadata from an ar-packaged .deb file."""
        out_deb = self.temp_dir / "meta-test_2.0.0_all.deb"
        deb_builder.build_deb(
            package_name="meta-test",
            version="2.0.0",
            description="Short summary\n Extended details line 1.",
            depends="nmap, masscan",
            section="net",
            priority="optional",
            output_path=out_deb
        )
        control_fields = apt_repo.extract_deb_control(out_deb)
        self.assertEqual(control_fields.get("Package"), "meta-test")
        self.assertEqual(control_fields.get("Version"), "2.0.0")
        self.assertEqual(control_fields.get("Depends"), "nmap, masscan")
        self.assertEqual(control_fields.get("Section"), "net")
        self.assertEqual(control_fields.get("Priority"), "optional")

    def test_build_all_metapackages(self):
        """Test building all curated Kali-style metapackages."""
        pkg_dir = self.temp_dir / "metas"
        built = deb_builder.build_all_metapackages(pkg_dir, version="2.1.0")
        self.assertEqual(len(built), len(deb_builder.STANDARD_METAPACKAGES))
        for deb in built:
            self.assertTrue(deb.exists())

    def test_generate_apt_repository(self):
        """Test generating a full APT repository from a collection of .deb files."""
        src_dir = self.temp_dir / "debs"
        repo_dir = self.temp_dir / "repo"

        # Build 2 packages
        deb_builder.build_deb("pkg-a", "1.0.0", "Package A", depends="bash", output_path=src_dir / "pkg-a.deb")
        deb_builder.build_deb("pkg-b", "1.0.0", "Package B", depends="python3", output_path=src_dir / "pkg-b.deb")

        apt_repo.generate_apt_repository(src_dir, repo_dir, codename="phantom", suite="stable")

        # Verify pool
        self.assertTrue((repo_dir / "pool" / "main" / "pkg-a.deb").exists())
        self.assertTrue((repo_dir / "pool" / "main" / "pkg-b.deb").exists())

        # Verify Packages & Packages.gz
        packages_file = repo_dir / "dists" / "stable" / "main" / "binary-all" / "Packages"
        packages_gz = repo_dir / "dists" / "stable" / "main" / "binary-all" / "Packages.gz"
        release_file = repo_dir / "dists" / "stable" / "Release"

        self.assertTrue(packages_file.exists())
        self.assertTrue(packages_gz.exists())
        self.assertTrue(release_file.exists())

        # Verify content in Packages file
        text = packages_file.read_text(encoding="utf-8")
        self.assertIn("Package: pkg-a", text)
        self.assertIn("Package: pkg-b", text)
        self.assertIn("Depends: bash", text)
        self.assertIn("Depends: python3", text)

        # Verify Release file indexes
        rel_text = release_file.read_text(encoding="utf-8")
        self.assertIn("Origin: ASTERIX OS", rel_text)
        self.assertIn("Suite: stable", rel_text)
        self.assertIn("Codename: phantom", rel_text)
        self.assertIn("main/binary-all/Packages", rel_text)


if __name__ == "__main__":
    unittest.main()
