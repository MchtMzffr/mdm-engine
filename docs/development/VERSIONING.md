# Versioning Policy

MDM follows [Semantic Versioning (SemVer)](https://semver.org/) for all releases.

## Version Format

`MAJOR.MINOR.PATCH` (e.g., `1.0.0`)

- **MAJOR**: Breaking changes to the public API
- **MINOR**: New features, backward-compatible
- **PATCH**: Bug fixes, backward-compatible

## Public API Stability

The following are considered **stable public API** and follow SemVer:

### Core Functions
- `mdm_engine.decide(raw_state, profile, deterministic, context)` → `Dict[str, Any]`
- `mdm_engine.replay_trace(trace, validate, verify_hash)` → `Dict[str, Any]`

### Types
- `mdm_engine.trace_types.DecisionTrace` (TypedDict)
- `mdm_engine.trace_types.EngineResult` (TypedDict)
- `mdm_engine.trace_types.TRACE_VERSION` (str)

### CLI Commands
- `mdm dashboard [--port PORT]`
- `mdm realtime [--duration SEC] [--profile PROFILE]`
- `mdm tests [-v]`
- `mdm demo [--steps N] [--profile PROFILE] [--out FILE]`

### Advanced API (also stable)
- `mdm_engine.moral_decision_engine(...)`
- `mdm_engine.replay(...)`
- `mdm_engine.TraceCollector`
- `mdm_engine.build_decision_trace(...)`
- `mdm_engine.get_config(profile_name)`
- `mdm_engine.list_profiles()`

## Trace Schema Versioning

Trace schema versioning is **independent** of package versioning:

- **Format**: `MAJOR.MINOR` (e.g., `1.0`, `1.1`, `2.0`)
- **Current**: `1.0` (defined in `mdm_engine.trace_types.TRACE_VERSION`)

### Version Rules

1. **PATCH changes** (package): Trace schema unchanged
   - Bug fixes, performance improvements
   - Example: `1.0.0` → `1.0.1`

2. **MINOR changes** (package): Trace schema MINOR increment
   - New optional fields added to `DecisionTrace`
   - Backward-compatible schema extensions
   - Example: `1.0.0` → `1.1.0`, trace schema `1.0` → `1.1`

3. **MAJOR changes** (package): Trace schema MAJOR increment
   - Required fields added/removed from `DecisionTrace`
   - Breaking changes to trace structure
   - Example: `1.0.0` → `2.0.0`, trace schema `1.0` → `2.0`

### Trace Schema Compatibility

- **v1.x**: All versions backward-compatible within major version
  - Readers must ignore unknown fields
  - Writers must include all required fields for their version
- **v2.0+**: Breaking changes require migration guide

## Breaking Changes Policy

### What Constitutes a Breaking Change?

1. **Function signature changes**
   - Removing parameters
   - Changing parameter types (without backward compat)
   - Changing return type structure

2. **Trace schema breaking changes**
   - Removing required fields
   - Changing field types
   - Changing field semantics

3. **CLI command removal or incompatible changes**

### Migration Strategy

- **MAJOR releases** include:
  - `MIGRATION.md` guide
  - Deprecation warnings in previous MINOR releases
  - Clear upgrade path

## Version History

- `1.0.0` (2025-02-13): Initial stable release
  - Trace schema `1.0`
  - Public API: `decide()`, `replay_trace()`
  - CLI: `dashboard`, `realtime`, `tests`, `demo`

## Release Process

1. Update `pyproject.toml` version
2. Update `mdm_engine/__init__.py` `__version__`
3. Update `CHANGELOG.md` with changes
4. Update `docs/development/VERSIONING.md` if schema changes
5. Create Git tag: `v1.0.0`
6. Build and test: `python -m build && twine check dist/*`
7. Release on GitHub (with release notes)
8. Optionally publish to PyPI

## Backward Compatibility Guarantee

- **Within MAJOR version**: Full backward compatibility
- **Between MAJOR versions**: Migration guide provided
- **Deprecated APIs**: Warning period of at least one MINOR release before removal
