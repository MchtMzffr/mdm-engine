# MDM Repository Structure

**Last Updated**: 2026-02-13

---

## Overview

This document describes the organization of the MDM (Model Oversight Engine) repository for developers and contributors.

---

## Root Directory

### Core Files
- `README.md` - Main project documentation
- `LICENSE` - Apache-2.0 license
- `pyproject.toml` - Package configuration
- `MANIFEST.in` - Package file inclusion rules
- `.gitignore` - Git ignore rules

### Policy & Legal
- `USAGE_POLICY.md` - Usage policy and prohibited uses
- `SAFETY_LIMITATIONS.md` - Safety boundaries and technical limits
- `AUDITABILITY.md` - Trace schema and auditability guide
- `SECURITY.md` - Security policy and vulnerability reporting
- `CONTRIBUTING.md` - Contribution guidelines

### Version & Release
- `CHANGELOG.md` - Version history
- `REPOSITORY_STRUCTURE.md` - This file

### Source Code
- `engine.py` - Main decision engine (backward compatibility)
- `config.py` - Configuration defaults
- `run_all_tests.py` - Test runner

### Requirements
- `requirements-dashboard.txt` - Dashboard dependencies (legacy, see pyproject.toml)

---

## Source Code Directories

### `/mdm_engine/`
**Public API Package** - User-facing interface:
- `__init__.py` - Public API exports
- `api.py` - Simplified API (`decide()`, `replay_trace()`)
- `cli.py` - Command-line interface entry point

### `/core/`
**Core Engine Modules** - Internal implementation:
- `state_encoder.py` - State encoding
- `action_generator.py` - Action generation
- `moral_evaluator.py` - Moral scoring (W, J, H, C)
- `constraint_validator.py` - Constraint validation
- `fail_safe.py` - Fail-safe mechanisms
- `action_selector.py` - Action selection
- `trace_logger.py` - Trace logging
- `confidence.py` - Confidence computation
- `uncertainty.py` - Uncertainty computation
- `soft_clamp.py` - Soft clamp mechanism
- `soft_override.py` - Soft override mechanism
- `temporal_drift.py` - Temporal drift tracking
- `trace_collector.py` - Trace collection utilities

### `/config_profiles/`
**Configuration Profiles** - Pre-defined threshold configurations:
- `base.py` - Default/base configuration
- `production_safe.py` - Production-safe thresholds
- `high_critical.py` - High-criticality thresholds
- `chaos_tuning.py` - Chaos testing configuration
- `scenario_test.py` - Scenario testing configuration
- `clamp_test.py` - Clamp testing configuration

### `/learning/`
**Learning & Optimization** - Offline learning modules:
- `feedback_metrics.py` - Feedback metric computation
- `loss.py` - Loss functions
- `safety_gate.py` - Safety gate for learning
- `policy_optimizer.py` - Policy optimization
- `offline_loop.py` - Offline learning loop
- `run_optimization_loop.py` - Optimization runner

### `/simulation/`
**Simulation** - Scenario generation:
- `scenario_generator.py` - Scenario generation utilities

### `/visualization/`
**Dashboard & Visualization** - Streamlit dashboard:
- `dashboard.py` - Main dashboard application
- `i18n.py` - Internationalization (English/Turkish)
- `plots/` - Plotly visualization modules:
  - `cus_timeline.py` - CUS timeline plot
  - `action_drift.py` - Action drift visualization
  - `soft_clamp_map.py` - Soft clamp map
  - `level_timeline.py` - Level timeline
  - `chaos_scatter.py` - Chaos scatter plot
  - `decision_boundary.py` - Decision boundary
  - `drift_panel.py` - Drift panel
  - `latency_timeline.py` - Latency timeline
  - `learning_evolution.py` - Learning evolution
  - `cus_vs_latency.py` - CUS vs latency

### `/tools/`
**Utility Scripts** - Development and testing tools:
- `csv_export.py` - CSV export utilities
- `realtime_10min.py` - Live test runner (10 min default)
- `realtime_demos.py` - Demo scenarios
- `realtime_pilot.py` - Pilot test runner
- `realtime_smoke.py` - Smoke test runner
- `run_offline_learning.py` - Offline learning runner
- `tune_thresholds.py` - Threshold tuning utility

### `/examples/`
**Example Scripts** - Usage examples:
- `hello_world.py` - Simplest usage example
- `replay_example.py` - Trace replay demonstration
- `trace_collection.py` - Trace collection example
- `README.md` - Examples documentation

### `/tests/`
**Test Suite** - Comprehensive test coverage:
- `test_scenarios.py` - Basic scenario tests
- `test_dashboard_scenarios.py` - Dashboard scenario tests
- `inspect_dashboard_data.py` - Dashboard data inspection
- `/adversarial/` - Adversarial test scenarios
- `/chaos/` - Chaos testing
- `/learning/` - Learning module tests
- `/monte_carlo/` - Monte Carlo tests
- `/simulation/` - Simulation tests
- `/soft_clamp/` - Soft clamp tests
- `/soft_override/` - Soft override tests
- `/temporal_drift/` - Temporal drift tests
- `/trace_collector/` - Trace collector tests
- `/uncertainty/` - Uncertainty tests

---

## Documentation Directories

### `/docs/`
**Documentation Root** - All documentation organized by category:

#### `/docs/specs/`
**Specification Documents** - Design and architecture specs:
- Phase 0-6 specifications (00_*.txt through 06_*.txt)
- Original design documents

#### `/docs/reports/`
**Analysis Reports** - Testing and analysis reports:
- CSV export reports
- Cleanup analysis reports

#### `/docs/releases/`
**Release Documentation** - Release notes and checklists:
- Release notes (v1.0.0)
- Release checklists

#### `/docs/development/`
**Development Guides** - Developer documentation:
- Packaging guide
- PyPI release guide
- Test execution guide
- Quick command reference

#### `/docs/archive/`
**Archived Documents** - Historical reference documents:
- Academic presentations
- Legacy documents

#### `/docs/` (Root)
**Status & Reference** - Current status documents:
- Architecture status
- Dashboard guides
- System checkup notes
- Phase-specific specifications (05_*.txt through 27_*.txt)

---

## Build Artifacts (Not in Repository)

These directories are generated and should not be committed:
- `/dist/` - Distribution packages (wheel, sdist)
- `/build/` - Build artifacts
- `/*.egg-info/` - Package metadata
- `/__pycache__/` - Python bytecode cache
- `/.venv*/` - Virtual environments
- `/archive/` - Trace archives (runtime)

---

## File Naming Conventions

### Python Files
- `snake_case.py` - Module files
- `test_*.py` - Test files
- `*_spec.py` - Specification test files

### Documentation Files
- `UPPERCASE.md` - Policy/legal documents (USAGE_POLICY.md, etc.)
- `lowercase.md` - Guides and references (README.md, changelog.md)
- `NN_NAME.txt` - Specification documents (00_BOOTSTRAP.txt, etc.)

### Configuration Files
- `pyproject.toml` - Package configuration
- `MANIFEST.in` - Package file inclusion
- `.gitignore` - Git ignore rules

---

## Key Entry Points

### For Users
- `from mdm_engine import decide` - Main API
- `mdm dashboard` - CLI dashboard
- `examples/hello_world.py` - Quick start example

### For Developers
- `engine.py` - Core engine (backward compatibility)
- `run_all_tests.py` - Run all tests
- `docs/development/` - Development guides

### For Researchers
- `docs/specs/` - Complete specifications
- `AUDITABILITY.md` - Trace schema documentation
- `docs/reports/` - Analysis reports

---

## Maintenance Notes

- **Public API**: Defined in `mdm_engine/__init__.py` and `mdm_engine/api.py`
- **Internal API**: All modules in `core/` are considered internal
- **Breaking Changes**: Require major version bump and migration guide
- **Documentation**: Keep README.md, USAGE_POLICY.md, SAFETY_LIMITATIONS.md up to date

---

**For questions about repository structure, open an issue or contact**: mucahit.muzaffer@gmail.com
