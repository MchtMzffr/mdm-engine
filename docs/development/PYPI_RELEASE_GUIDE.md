# PyPI Release Guide

**Version**: 1.0.0  
**Last Updated**: 2026-02-13

---

## Pre-Release Checklist

- [x] `twine check dist/*` → PASSED
- [x] Clean venv wheel test → PASSED
- [x] CLI test → PASSED
- [x] SECURITY.md added
- [x] Release notes prepared
- [x] Git tag v1.0.0 created and pushed

---

## Step 1: GitHub Release (Manual)

1. Go to: https://github.com/MeetlyTR/mdm-engine/releases/new
2. **Tag**: Select `v1.0.0`
3. **Title**: `MDM v1.0.0`
4. **Description**: Copy content from `RELEASE_NOTES_v1.0.0.md`
5. **Assets** (optional): Upload `dist/mdm_engine-1.0.0-py3-none-any.whl` and `dist/mdm_engine-1.0.0.tar.gz`
6. Click **"Publish release"**

---

## Step 2: TestPyPI Upload (Recommended First)

### A) Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

**Credentials**: You'll be prompted for:
- Username: `__token__`
- Password: Your TestPyPI API token (create at https://test.pypi.org/manage/account/token/)

### B) Test Installation from TestPyPI

```bash
# Create clean venv
python -m venv .venv_pypi_test
.venv_pypi_test\Scripts\activate  # Windows
# source .venv_pypi_test/bin/activate  # macOS/Linux

# Install from TestPyPI
pip install -i https://test.pypi.org/simple/ mdm-engine

# Test
python -c "from mdm_engine import decide; print(decide({'physical':0.5,'social':0.5,'context':0.5,'risk':0.5,'compassion':0.5,'justice':0.9,'harm_sens':0.5,'responsibility':0.5,'empathy':0.5}, profile='scenario_test')['level'])"

# Test CLI
mdm-engine --help
```

**Expected**: Installation succeeds, `decide()` works, CLI available.

---

## Step 3: Check Package Name Availability

**Important**: PyPI package name `mdm-engine` might be taken.

### Check Manually

Visit: https://pypi.org/project/mdm-engine/

- **If 404**: Name is available ✅
- **If exists**: Choose alternative name (see below)

### Alternative Names (if needed)

- `mdm-ethical-engine`
- `mdm-moral-kernel`
- `mdmengine-core`
- `mdm-decision-engine`

**To change**: Update `name` in `pyproject.toml`, rebuild, and upload.

---

## Step 4: Production PyPI Upload

### A) Create PyPI Account (if needed)

1. Go to: https://pypi.org/account/register/
2. Verify email
3. Create API token: https://pypi.org/manage/account/token/
   - Scope: **"Entire account"** or **"Project: mdm-engine"**
   - Copy token (you'll need it once)

### B) Upload to Production PyPI

```bash
python -m twine upload dist/*
```

**Credentials**:
- Username: `__token__`
- Password: Your PyPI API token

### C) Verify Installation

```bash
# Wait 1-2 minutes for PyPI to index
pip install mdm-engine

# Test
python -c "from mdm_engine import decide; print('✅ Installed successfully')"
mdm-engine --help
```

---

## Post-Release Tasks

### 1. Update README Installation

README already includes `pip install mdm-engine` ✅

### 2. Support Policy

Already documented in:
- `USAGE_POLICY.md` → Support Policy section
- `SECURITY.md` → Security contact

### 3. SemVer Commitment

**Public API (stable in 1.x)**:
- `decide()`
- `replay_trace()`
- `moral_decision_engine()` (full API)
- `get_config()`, `list_profiles()`
- CLI commands

**Internal (may change)**:
- `core/*` modules
- `config_profiles/*` internal structure
- `visualization/*` dashboard internals

---

## Troubleshooting

### Upload Fails: "Package name already exists"

**Solution**: Change package name in `pyproject.toml`:
```toml
name = "mdm-engine"  # or other alternative
```

Rebuild and retry:
```bash
python -m build
python -m twine upload dist/*
```

### Upload Fails: "Invalid credentials"

**Solution**: 
1. Check API token is correct
2. For TestPyPI: Use TestPyPI token (different from PyPI)
3. Username must be exactly `__token__`

### Installation Fails: "No matching distribution"

**Solution**:
- Wait 1-2 minutes after upload (PyPI indexing delay)
- Check Python version compatibility (`requires-python = ">=3.8"`)
- Verify package name spelling

---

## Release Commands Summary

```bash
# 1. Build (if not already done)
python -m build

# 2. Check
python -m twine check dist/*

# 3. TestPyPI (recommended first)
python -m twine upload --repository testpypi dist/*

# 4. Production PyPI (when ready)
python -m twine upload dist/*
```

---

## Links

- **TestPyPI**: https://test.pypi.org/
- **Production PyPI**: https://pypi.org/
- **API Tokens**: https://pypi.org/manage/account/token/
- **Package Page** (after upload): https://pypi.org/project/mdm-engine/

---

**Last Updated**: 2026-02-13
