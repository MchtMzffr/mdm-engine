# MDM Packaging Guide

**Version**: 1.0  
**Last Updated**: 2026-02-13

---

## Package Structure

Packaging is done while preserving the existing structure:

```
mdm-engine/
├── mdm_engine/          # Public API wrapper
│   ├── __init__.py      # Public exports
│   └── cli.py           # CLI entry point
├── core/                # Core modules (internal)
├── config_profiles/     # Config profiles
├── visualization/       # Dashboard
├── tools/               # Utility scripts
├── learning/            # Learning modules
├── simulation/          # Simulation modules
├── tests/               # Test suite
├── engine.py            # Main engine (backward compatibility)
├── config.py            # Config (backward compatibility)
├── pyproject.toml       # Package metadata
├── MANIFEST.in          # Include files
└── README.md            # Documentation
```

---

## Installation (Development)

### 1. Editable Install (Development)

```bash
pip install -e .
```

This way code changes are reflected immediately.

### 2. Normal Install

```bash
pip install .
```

---

## Package Building (Distribution)

### 1. Source Distribution (sdist)

```bash
python -m build --sdist
```

Output: `dist/mdm-engine-1.0.0.tar.gz`

### 2. Wheel Distribution

```bash
python -m build --wheel
```

Output: `dist/mdm_engine-1.0.0-py3-none-any.whl`

### 3. Both Together

```bash
python -m build
```

---

## Publishing to PyPI

### 1. TestPyPI (Test First)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ mdm-engine
```

### 2. Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*
```

**Note:** PyPI account and API token required.

---

## CLI Usage

After installation:

```bash
# Start dashboard
mdm dashboard

# Live test
mdm realtime --duration 90 --profile scenario_test

# Test suite
mdm tests
```

---

## Public API

```python
from mdm_engine import (
    moral_decision_engine,
    replay,
    TraceCollector,
    build_decision_trace,
    get_config,
    list_profiles,
)
```

---

## Backward Compatibility

Existing code continues to work:

```python
# Old imports still work (root files are preserved)
from engine import moral_decision_engine
from config_profiles import get_config
```

---

## Versioning

SemVer is used: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Version is specified in `pyproject.toml` as `version = "1.0.0"`.

---

## Documentation Files

The following files are included in the package (via MANIFEST.in):

- README.md
- LICENSE
- USAGE_POLICY.md
- SAFETY_LIMITATIONS.md
- AUDITABILITY.md
- CHANGELOG.md

---

## Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest
- pytest-cov
- black
- ruff

---

## Testing

```bash
# Run test suite
mdm tests

# or directly
python run_all_tests.py
```

---

## Troubleshooting

### Import Error

If `mdm_engine` cannot be imported:

```bash
# Do editable install
pip install -e .
```

### CLI Not Working

```bash
# Check PATH
which mdm

# Reinstall
pip install --force-reinstall -e .
```

---

**Last Updated**: 2026-02-13
