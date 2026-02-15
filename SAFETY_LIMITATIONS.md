# MDM: Safety & Limitations

**Version**: 1.0  
**Last Updated**: 2026-02-13

---

## Safety Boundaries

### 1. Does Not Make Clinical/Operational Decisions Without Domain Data

MDM is a **domain-agnostic** decision regulator. For clinical or operational decisions:

- ✅ **Required**: Domain expert + adapter layer
- ❌ **Insufficient**: MDM alone

**Example:** To make a decision for a patient condition:
- Domain adapter: Converts medical data → risk scores
- MDM: Determines escalation level from risk scores
- Domain adapter: Applies medical protocol based on escalation level

### 2. This Is a Decision REGULATOR; Not a Domain Decision

MDM answers **"how to decide"**, not **"what decision to make"**.

- ✅ **Does**: Ethical scoring, escalation, safety boundaries
- ❌ **Does not**: Domain-specific decision logic (e.g., "which drug for this patient?")

### 3. Default Config Is Intentionally Strict

The `base` config profile is set to **security-focused**:

- High thresholds (J_MIN, H_MAX)
- Aggressive fail-safe triggering
- Low confidence thresholds

**For production:** Use `production_safe` or domain-specific config.

---

## Technical Limitations

### 1. Determinism and Replay

- **Deterministic mode**: Same input → same output with `deterministic=True`
- **Replay**: Reproduce the same decision with `replay(trace)`
- **Hash**: Trace integrity can be checked with `compute_trace_hash(trace)`

**Limit:** Replay may be inconsistent with non-deterministic mode (`deterministic=False`).

### 2. Temporal Drift (CUS)

- **CUS History**: Uncertainty tracking over time with `context={"cus_history": [...]}`
- **Preemptive Escalation**: Early escalation on high CUS increase

**Limit:** Temporal drift cannot be calculated if CUS history is missing.

### 3. Soft Clamp

- **Effect**: Pulls raw output to safety boundaries
- **No Guarantee**: Soft clamp may not always make a difference (if raw output is already at boundary)

**Limit:** No 100% clamp guarantee; check `soft_clamp=True` and `raw_action != final_action` in traces.

---

## Known Limitations

### 1. Action Space

- **Fixed size**: 4 components (severity, intervention, compassion, delay)
- **Value range**: [0, 1] (normalized)

**Domain compatibility:** Domain adapter must convert this format to domain.

### 2. Config Override

- **String profile**: `config_override="scenario_test"` → calls `get_config()`
- **Dict override**: `config_override={"J_MIN": 0.3, ...}` → used directly

**Limit:** No partial override; either full dict or profile name.

### 3. Trace Schema Versioning

- **Current**: `TRACE_VERSION = "1.0"`
- **Change**: Version increments if schema changes

**Compatibility:** Old traces continue to work with `replay()` (backward compatibility).

---

## Security Warnings

### 1. Input Validation

MDM **assumes** `raw_state` format. Wrong format:

- Fail-safe is triggered
- Returns `human_escalation=True`
- Produces safe default action

**Recommendation:** Perform input validation in domain adapter.

### 2. Output Validation

MDM's produced `action` is always in [0,1]⁴ range. But:

- Domain adapter must interpret these values **appropriately for domain**
- **Human review is mandatory** at L2 level

### 3. Trace Security

Traces **may contain sensitive information** (raw_state from domain adapter).

- **Security**: Store traces securely (encryption, access control)
- **GDPR/KVKK**: Legal requirements apply for traces containing personal data

---

## Performance Limits

- **Latency**: Average 1-5ms (including trace)
- **Throughput**: 100-1000 decisions per second (hardware dependent)
- **Memory**: ~1KB/trace for trace buffer

**Measurement:** Real performance can be monitored via `latency_ms` field in traces.

---

## Support and Updates

- **Breaking Changes**: On MAJOR version increment (e.g., 1.0 → 2.0)
- **Backward Compatibility**: Maintained in MINOR/PATCH versions
- **Deprecation**: Old APIs can be used with warnings for one MINOR version

See **CHANGELOG.md** for details.

---

**Last Updated**: 2026-02-13
