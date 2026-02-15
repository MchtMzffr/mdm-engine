# PyPI Migration: legacy package → mdm-engine

**Audience:** Maintainers releasing MDM to PyPI.

## Situation

- **New package name:** `mdm-engine` (Model Oversight Engine).
- **Legacy package name (if it was ever published):** See project history; PyPI does not support renaming.

Publishing as `mdm-engine` creates a **new** package.

## What to do

### 1. Publish `mdm-engine`

- Build and upload as usual: `python -m build`, `twine upload dist/*` (or to TestPyPI first).
- Package name in `pyproject.toml` is already `name = "mdm-engine"`.

### 2. If the legacy package exists on PyPI

- **Option A (recommended):** On the legacy project page, add a short note in the description:
  - *"This project has been renamed and migrated to **mdm-engine**. Install with: pip install mdm-engine. See: https://github.com/MeetlyTR/mdm-engine."*
- **Option B:** Release a final legacy version that depends on `mdm-engine` and re-exports it, so existing installs continue to work.

### 3. This repo

- **MDM-only:** Use `mdm_engine` and `mdm` only. Env: `MDM_CONFIG_PROFILE`.
- For **discovery** on PyPI: if the legacy package exists, point users to `mdm-engine` (see Option A/B above).

---

*Last updated: 2026-02-15*
