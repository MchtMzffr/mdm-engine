# MDM: Auditability & Trace Schema

**Version**: 1.0  
**Last Updated**: 2026-02-13

---

## Trace Schema

### Version

**TRACE_VERSION**: `"1.0"`

Version increments on schema changes. Old traces continue to work with `replay()` (backward compatibility).

---

## Trace Format

### JSONL (JSON Lines)

Each line is a decision trace:

```json
{
  "t": 0,
  "cus": 0.84,
  "raw_action": [0.0, 1.0, 1.0, 0.0],
  "final_action": [0.0, 1.0, 0.58, 0.29],
  "soft_clamp": true,
  "level": 1,
  "human_escalation": false,
  "run_id": 1770968490928,
  "batch_id": 0,
  "profile_state": "chaos",
  "config_profile": "scenario_test",
  "created_at": 1770968490.9358613,
  "latency_ms": 6.49,
  "J": 0.94,
  "H": 0.0,
  "confidence": 0.12
}
```

### CSV Export

CSV format export from dashboard or `tools/csv_export.py`:

**Columns (26 total):**
- Basic: index, t, cus, delta_cus, cus_mean, level, soft_clamp, human_escalation, latency_ms, phase
- Metadata: run_id, batch_id, profile_state, config_profile, created_at
- Model: J, H, confidence
- **Raw action**: raw_severity, raw_intervention, raw_compassion, raw_delay
- **Final action**: final_severity, final_intervention, final_compassion, final_delay

---

## Trace Fields

### Required Fields

- `t`: Timestamp or step index
- `level`: Escalation level (0, 1, or 2)
- `raw_action`: Raw action (initially produced by engine)
- `final_action`: Final action (after clamp)

### Optional Fields

- `cus`: Cumulative Uncertainty Score (for temporal drift)
- `soft_clamp`: Was soft clamp applied? (True/False)
- `human_escalation`: Is human decision required? (True/False)
- `latency_ms`: Decision time (ms)
- `J`, `H`: Justice and Harm scores
- `confidence`: Confidence score
- `run_id`: Test run identifier (timestamp-ms)
- `batch_id`: Batch sequence number
- `profile_state`: State profile (easy/medium/chaos)
- `config_profile`: Config profile (scenario_test/production_safe)
- `created_at`: Wall-clock timestamp

---

## Determinism Contract

MDM guarantees **deterministic behavior** under specific conditions:

### Determinism Guarantee

**When `deterministic=True` (default):**
- Same input state → same output action (exact match)
- Same trace → same replayed action (exact match)
- Floating-point operations use deterministic algorithms
- No external randomness sources (OS entropy, system time, etc.)

### Determinism Scope

**Guaranteed:**
- Action selection (4-element list)
- Escalation level (0, 1, or 2)
- Moral scores (J, H, W, C)
- Confidence scores
- Trace structure and content

**Not guaranteed (by design):**
- Trace timestamps (`created_at`, `latency_ms`) - system-dependent
- Random state generation (if provided by caller)
- External context updates (if modified outside engine)

### Determinism Validation

Replay validation uses **exact match** (no tolerance):
- `replay_trace(trace, validate=True)` compares actions byte-for-byte
- Hash verification (`verify_hash=True`) ensures trace integrity
- Test suite validates determinism across 1000+ scenarios

### Breaking Determinism

Determinism may be broken by:
- Setting `deterministic=False` (explicit opt-out)
- Modifying context dict between calls
- Using non-deterministic state generators
- System-level floating-point precision differences (extremely rare)

## Determinism and Hash

### Deterministic Mode

```python
result = moral_decision_engine(raw_state, deterministic=True)
```

Same `raw_state` → same `action` (reproducible).

### Trace Hash

```python
from engine import compute_trace_hash

hash_value = compute_trace_hash(trace)
```

**Usage:**
- Trace integrity check
- Duplicate detection
- Reference in audit logs

**Format:** SHA-256 hex string (64 characters)

---

## Replay

### Reproduce Same Decision

```python
from mdm_engine import replay

# Reproduce same decision from trace
new_result = replay(trace)

# Compare with new trace
assert new_result["action"] == trace["final_action"]
```

**Limit:** Replay may be inconsistent with non-deterministic mode.

---

## Dashboard and Visualization

### Streamlit Dashboard

```bash
mdm dashboard
```

**Features:**
- JSONL/CSV loading
- CUS timeline, soft clamp map, action drift charts
- Level timeline (L0/L1/L2 distribution)
- Latency analysis
- Soft clamp filter
- CSV export (raw vs final comparison)

**URL:** `http://localhost:8501`

---

## Audit Log Best Practices

### 1. Trace Storage

- **Format**: JSONL (each line is a trace)
- **Encoding**: UTF-8
- **Compression**: Gzip (for long-term storage)

### 2. Trace Retention

- **Production**: At least 90 days (according to legal requirements)
- **Development**: Optional
- **Archive**: Old traces can be moved to `archive/` folder

### 3. Trace Security

- **Encryption**: For traces containing sensitive information
- **Access Control**: Trace access should be restricted
- **GDPR/KVKK**: Legal requirements for traces containing personal data

### 4. Trace Analysis

- **Dashboard**: Visual analysis
- **CSV Export**: With Excel/data analysis tools
- **Python API**: Programmatic analysis with `load_traces_from_jsonl()`

---

## Trace Schema Evolution

### Versioning Strategy

- **MAJOR** (1.0 → 2.0): Breaking changes (old traces cannot be replayed)
- **MINOR** (1.0 → 1.1): New fields added (backward compatible)
- **PATCH** (1.0.0 → 1.0.1): Bug fixes (schema unchanged)

### Migration

Migration scripts are provided for old traces (specified in CHANGELOG.md).

---

## Example Audit Workflow

```python
from mdm_engine import moral_decision_engine, replay, compute_trace_hash
from core.trace_collector import TraceCollector

# Make decision
collector = TraceCollector(jsonl_path="audit.log")
result = moral_decision_engine(raw_state)
trace = build_decision_trace(result)
collector.push(trace)

# Integrity check with hash
hash_val = compute_trace_hash(trace)
print(f"Trace hash: {hash_val}")

# Verification with replay
replayed = replay(trace)
assert replayed["action"] == trace["final_action"]
```

---

## Compliance

### GDPR/KVKK

- Traces may contain personal data → **domain adapter responsibility**
- Trace retention policy must be applied
- Right to deletion: Traces must be deletable

### Audit Requirements

- **Trace completeness**: Every decision must be traced
- **Trace integrity**: Can be checked with hash
- **Trace accessibility**: Accessible via Dashboard/CSV

---

**Last Updated**: 2026-02-13
