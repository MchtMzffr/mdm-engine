# Changelog

All notable changes to MDM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-02-13

### Migration (rebrand to MDM)

This release uses **MDM (Model Oversight Engine)** only:

| Old | New |
|-----|-----|
| Old package import | `from mdm_engine import decide` |
| Old package install | `pip install mdm-engine` |
| Old CLI | `mdm dashboard` |

**Quick migrate:** Use `mdm_engine`, `mdm` CLI, env `MDM_CONFIG_PROFILE`. Dashboard requires schema v2.0 (`mdm` packet key, `mdm_*` columns).

---

### Added

- **Public API**: `moral_decision_engine()`, `replay()`, `TraceCollector`, `build_decision_trace()`, `get_config()`, `list_profiles()`
- **CLI**: `mdm dashboard`, `mdm realtime`, `mdm tests`
- **Trace Schema v1.0**: JSONL/CSV export, raw vs final action comparison
- **Dashboard**: Streamlit-based observability dashboard
- **Config Profiles**: scenario_test, production_safe, high_critical, chaos_tuning, clamp_test
- **Soft Clamp**: Softly constrains raw outputs that exceed safety boundaries
- **L0/L1/L2 Escalation**: Automatic decision → Soft clamp → Human escalation
- **Temporal Drift**: Uncertainty tracking over time via CUS (Cumulative Uncertainty Score)
- **Auditability**: Trace hash, replay, CSV export
- **Documentation**: README, USAGE_POLICY, SAFETY_LIMITATIONS, AUDITABILITY

### Changed

- **Trace Format**: Versioned trace schema (TRACE_VERSION = "1.0")
- **CSV Export**: Raw columns added (raw_severity, raw_intervention, raw_compassion, raw_delay)
- **Dashboard**: Soft clamp filter, level timeline, clamp effect metrics

### Fixed

- JSONL parse error handling (row skipping for robustness)
- Missing raw columns in CSV export issue

### Security

- **Fail-Safe**: Aggressive fail-safe triggering by default
- **Human Escalation**: Mandatory human decision at L2 level
- **Input Validation**: Wrong format → fail-safe + human_escalation

---

## [Unreleased]

### Planned

- Trace schema v2.0 (backward compatible migration)
- Additional config profiles
- Performance optimizations
- Extended dashboard features

---

## Versioning

- **MAJOR** (1.0 → 2.0): Breaking changes
- **MINOR** (1.0 → 1.1): New features (backward compatible)
- **PATCH** (1.0.0 → 1.0.1): Bug fixes

---

**Format**: [Version] - YYYY-MM-DD

**Categories**: Added, Changed, Deprecated, Removed, Fixed, Security
