## 📝 Description

Please provide a brief summary of the changes introduced in this pull request and the rationale behind them.

Fixes / Closes #(issue number)

---

## 🔍 Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 🔒 Security hardening / vulnerability remediation
- [ ] 📦 Packaging / APT repository enhancement
- [ ] 📚 Documentation update / test suite expansion
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)

---

## 🧪 Testing & Verification

- [ ] Ran `python python-lab/test_debian_rootless.py` (All tests passing)
- [ ] Ran `python python-lab/test_packaging_and_repo.py` (All tests passing)
- [ ] Ran `python scripts-hub/ax-release-verify.py` (Signatures match)
- [ ] Verified shell scripts pass ShellCheck without fatal warnings
- [ ] Tested on target environment (Termux PRoot, Android 15 AVF, Docker, or Host Linux)

---

## ⚖️ Checklist

- [ ] My code adheres to the zero-dependency Python policy in core scripts
- [ ] I have included unit/integration tests covering new functionality
- [ ] I have updated corresponding documentation in `docs/tools/`
- [ ] I have read and agree to the [Code of Conduct](CODE_OF_CONDUCT.md)
