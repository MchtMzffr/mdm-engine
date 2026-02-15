# MDM v1.0.0 Release Notes

**Release Date**: 2026-02-13

---

## What's in 1.0.0

### Core Features

- **Simplified Public API**: `decide()` and `replay_trace()` functions for easy integration
- **Full API**: `moral_decision_engine()`, `replay()`, `TraceCollector`, `build_decision_trace()`, `get_config()`, `list_profiles()`
- **CLI Tools**: `mdm dashboard`, `mdm realtime`, `mdm tests`
- **Trace Schema v1.0**: JSONL/CSV export with raw vs final action comparison
- **Dashboard**: Streamlit-based observability dashboard with real-time visualization
- **Config Profiles**: scenario_test, production_safe, high_critical, chaos_tuning, clamp_test
- **Soft Clamp**: Softly constrains raw outputs that exceed safety boundaries
- **L0/L1/L2 Escalation**: Automatic decision → Soft clamp → Human escalation
- **Temporal Drift**: Uncertainty tracking over time via CUS (Cumulative Uncertainty Score)
- **Auditability**: Trace hash, replay, CSV export for compliance

### Examples

- `examples/hello_world.py`: Simplest usage example
- `examples/replay_example.py`: Trace replay demonstration
- `examples/trace_collection.py`: Collecting multiple traces

### Documentation

- **README.md**: Complete overview and quick start guide
- **USAGE_POLICY.md**: Usage policy and prohibited uses
- **SAFETY_LIMITATIONS.md**: Safety boundaries and technical limits
- **AUDITABILITY.md**: Trace schema and auditability guide
- **SECURITY.md**: Security policy and vulnerability reporting
- **CHANGELOG.md**: Version history

---

## Stability Contract

**Public API** (stable, will not break in 1.x releases):
- `mdm_engine.decide()` - Main decision function
- `mdm_engine.replay_trace()` - Trace replay function
- `mdm_engine.moral_decision_engine()` - Full API (advanced)
- `mdm_engine.replay()` - Full replay API (advanced)
- `mdm_engine.get_config()` - Config profile loader
- `mdm_engine.list_profiles()` - List available profiles

**Internal API** (may change):
- `core/*` modules
- `config_profiles/*` internal structure
- `visualization/*` dashboard internals

---

## Safety Note

**MDM is a decision support / deterministic audit kernel, not an autonomous decision maker.**

- It provides ethical scoring and escalation recommendations
- L2 level requires mandatory human decision
- Domain-specific knowledge must come from adapter layers
- See USAGE_POLICY.md and SAFETY_LIMITATIONS.md for details

---

## Installation

```bash
pip install mdm
```

## Quick Start

```python
from mdm_engine import decide

raw_state = {
    "risk": 0.7,
    "severity": 0.8,
    "physical": 0.6,
    "social": 0.5,
    "context": 0.4,
    "compassion": 0.5,
    "justice": 0.9,
    "harm_sens": 0.5,
    "responsibility": 0.7,
    "empathy": 0.6,
}

result = decide(raw_state, profile="scenario_test")
print(f"Action: {result['action']}")
print(f"Level: L{result['escalation']}")
print(f"Human escalation: {result['human_escalation']}")
```

## CLI Usage

```bash
# Start dashboard
mdm dashboard

# Run live test
mdm realtime --duration 90 --profile scenario_test

# Run test suite
mdm tests
```

---

## Breaking Changes

None. This is the first stable release.

---

## Migration Guide

If you were using the codebase directly before packaging:

1. **Import changes**: Use `from mdm_engine import decide` instead of `from engine import moral_decision_engine`
2. **Config profiles**: Use `profile="scenario_test"` parameter instead of `config_override=get_config("scenario_test")`
3. **CLI**: Use `mdm` command instead of running scripts directly

---

## Known Issues

- None reported yet

---

## Contributors

- Mucahit Muzaffer (mucahit.muzaffer@gmail.com)

---

## Links

- **Repository**: https://github.com/MeetlyTR/mdm
- **Documentation**: https://github.com/MeetlyTR/mdm/blob/main/README.md
- **Issues**: https://github.com/MeetlyTR/mdm/issues
- **Security**: See SECURITY.md

---

**License**: Apache-2.0
