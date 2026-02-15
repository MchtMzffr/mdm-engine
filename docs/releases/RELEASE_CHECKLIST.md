# MDM Release Checklist

**Version**: 1.0.0  
**Target Date**: 2026-02-13

---

## ✅ Completed Steps

### 1. Packaging Infrastructure
- [x] `pyproject.toml` created (setuptools, SemVer 1.0.0)
- [x] `MANIFEST.in` created (documentation files included)
- [x] `LICENSE` (Apache-2.0) added
- [x] `mdm_engine/__init__.py` (Public API wrapper) created
- [x] `mdm_engine/cli.py` (CLI entry point) created

### 2. Documentation
- [x] `README.md` (overview, installation, quick start)
- [x] `USAGE_POLICY.md` (prohibited uses, human-in-the-loop)
- [x] `SAFETY_LIMITATIONS.md` (safety boundaries, technical limits)
- [x] `AUDITABILITY.md` (trace schema, replay, hash)
- [x] `CHANGELOG.md` (version history)
- [x] `PACKAGING_GUIDE.md` (packaging guide)

### 3. Public API Stabilization
- [x] `moral_decision_engine()` exported
- [x] `replay()` exported
- [x] `TraceCollector`, `build_decision_trace` exported
- [x] `get_config()`, `list_profiles()` exported

### 4. CLI
- [x] `mdm dashboard` command
- [x] `mdm realtime` command
- [x] `mdm tests` command

---

## 🔄 To Do (Pre-Release)

### 1. Testing and Validation
- [ ] Test editable install with `pip install -e .`
- [ ] Does `mdm dashboard` work?
- [ ] Does `mdm realtime --duration 10` work?
- [ ] Does `mdm tests` work?
- [ ] Do public API imports work?

### 2. PyPI Preparation
- [ ] Update GitHub repository URLs (in `pyproject.toml`)
- [ ] Create PyPI account (or use existing account)
- [ ] Create API token (PyPI → Account Settings → API tokens)

### 3. Build and Test
- [ ] Build package with `python -m build`
- [ ] Check with `python -m twine check dist/*`
- [ ] Upload to TestPyPI and test
- [ ] Install from TestPyPI and run

### 4. Final Release
- [ ] Upload to production PyPI
- [ ] Create GitHub release
- [ ] Update documentation (if needed)

---

## 📋 Release Notes

### Version 1.0.0 (2026-02-13)

**First Stable Release**

- Public API stabilized
- CLI added
- Documentation completed
- Packaging infrastructure ready

---

## 🚀 Quick Start (Post-Release)

```bash
# Installation
pip install mdm-engine

# Dashboard
mdm dashboard

# Test
mdm tests
```

---

**Last Updated**: 2026-02-13
