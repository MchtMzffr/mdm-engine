# MDM: Academic Presentation

**Title**: Ethical Governance for AI Decisions: A Deterministic Reference Engine  
**Duration**: 15-20 minutes  
**Audience**: Academic researchers, ethics committees, AI governance researchers

---

## Slide 1: Title & Motivation

### Ethical Governance for AI Decisions
**A Deterministic Reference Engine**

**Problem**: AI systems make decisions affecting human welfare, but lack:
- Deterministic auditability
- Human oversight integration
- Ethical constraint enforcement
- Uncertainty quantification

**Solution**: MDM — A reference implementation of ethical governance kernel

---

## Slide 2: What It Is / What It Is Not

### What MDM IS

✅ **Decision Governance Layer**: Regulates and constrains AI decisions  
✅ **Safety Envelope**: Enforces ethical boundaries  
✅ **Human-in-the-Loop**: Mandatory escalation at L2  
✅ **Auditable**: Full trace with deterministic replay  
✅ **Domain-Agnostic**: Works with any domain via adapter pattern

### What MDM IS NOT

❌ **Decision Maker**: Does not make domain-specific decisions  
❌ **Data Collector**: Does not collect or surveil data  
❌ **Autonomous System**: Requires human oversight at critical levels  
❌ **Black Box**: Fully deterministic and explainable

---

## Slide 3: Architecture Overview

```
┌─────────────────┐
│  Domain Input   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Adapter Layer  │ → raw_state
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│      MDM Core            │
│  ┌───────────────────────────┐  │
│  │ State Encoder             │  │
│  │ Action Generator          │  │
│  │ Moral Evaluator (W,J,H,C) │  │
│  │ Constraint Validator      │  │
│  │ Fail-Safe Controller      │  │
│  │ Action Selector           │  │
│  │ Soft Clamp                │  │
│  └───────────────────────────┘  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Adapter Layer  │ ← action + trace
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Domain Output  │
└─────────────────┘
```

**Key**: Domain-agnostic governance layer

---

## Slide 4: CUS & Escalation Levels

### Cumulative Uncertainty Score (CUS)

- **Tracks**: Decision uncertainty over time
- **Computation**: Based on confidence, constraint margins, temporal drift
- **Use**: Preemptive escalation when uncertainty increases

### L0/L1/L2 Escalation Framework

- **L0**: Automatic decision — Engine produced safe action
- **L1**: Soft clamp applied — Raw output constrained, continues automatically
- **L2**: Human escalation — **Mandatory human decision required**

**Trace Example**:
```json
{
  "level": 1,
  "cus": 0.84,
  "soft_clamp": true,
  "human_escalation": false
}
```

---

## Slide 5: Fail-Safe & Replay

### Fail-Safe Mechanisms

- **Constraint Violation**: Automatic fail-safe activation
- **Safe Action**: Pre-computed safe default action
- **Human Escalation**: Mandatory at L2 level
- **Trace Logging**: Every decision fully traced

### Deterministic Replay

```python
from mdm_engine import decide, replay_trace

# Make decision
result = decide(raw_state, profile="scenario_test")

# Replay (same input → same output)
replayed = replay_trace(result["trace"], validate=True)
assert replayed["action"] == result["action"]  # ✅ Deterministic
```

**Value**: Full auditability and research reproducibility

---

## Slide 6: Dashboard (Proof)

### Real-time Observability

- **Live Trace Visualization**: CUS timeline, action drift, level distribution
- **Soft Clamp Map**: Visual representation of constraint enforcement
- **Latency Analysis**: Performance monitoring
- **CSV Export**: Raw vs final action comparison

**URL**: `mdm dashboard` → http://localhost:8501

**Proof**: 10-minute live test generates 60 traces with full audit trail

---

## Slide 7: Scenarios & Use Cases

### Healthcare
- Treatment recommendation governance
- Risk escalation to clinician
- Regulatory compliance audit trail

### Education
- Content moderation safety
- Student support escalation
- Policy compliance tracking

### Operations
- Process control governance
- Safety system fail-safes
- Compliance-ready decision logs

**Common Pattern**: Domain adapter → MDM → Human escalation when needed

---

## Slide 8: Limitations

### Technical Limitations

- **Domain Knowledge**: Requires adapter layer (not included)
- **Action Space**: Fixed 4-component vector
- **Config Profiles**: Pre-defined; custom requires code modification

### Scope Limitations

- **Not a Decision Maker**: Provides governance, not domain decisions
- **Not a Data Processor**: Does not handle personal data directly
- **Not Autonomous**: Requires human oversight at L2

**These are intentional design choices for safety and clarity.**

---

## Slide 9: Research Contributions

### Methodological Contributions

1. **Deterministic Governance Framework**: L0/L1/L2 escalation model
2. **CUS Computation**: Temporal uncertainty tracking methodology
3. **Replay Validation**: Deterministic audit trail approach
4. **Test Methodology**: Chaos testing and invariant verification

### Practical Contributions

1. **Reference Implementation**: Complete, working codebase
2. **Validation Framework**: Comprehensive test suite
3. **Observability Tools**: Dashboard and trace visualization
4. **Documentation**: Complete specification and usage guides

---

## Slide 10: Collaboration & Next Steps

### Collaboration Opportunities

- **Academic**: Joint publications, research extensions, student projects
- **Industry**: Domain adapters, custom profiles, integration support
- **Open Source**: Contributions welcome (see CONTRIBUTING.md)

### Resources

- **GitHub**: https://github.com/MeetlyTR/mdm
- **PyPI**: `pip install mdm`
- **Documentation**: Complete (README, USAGE_POLICY, SAFETY_LIMITATIONS, AUDITABILITY)
- **Contact**: mucahit.muzaffer@gmail.com

### Next Steps

1. **Review**: Explore GitHub repository and documentation
2. **Test**: Run examples and dashboard
3. **Discuss**: Schedule technical discussion
4. **Collaborate**: Identify joint research/industry opportunities

---

## Q&A Preparation

### Expected Questions

**Q: How does this differ from existing ethical AI frameworks?**  
A: Focus on deterministic governance layer with mandatory human escalation, not decision-making itself.

**Q: Can this be used in production?**  
A: Yes, with domain adapter and appropriate config profile. See USAGE_POLICY.md for guidelines.

**Q: What's the performance impact?**  
A: ~1-5ms per decision including trace generation. Suitable for real-time systems.

**Q: How do you ensure safety?**  
A: Fail-safe mechanisms, human escalation at L2, comprehensive testing, and clear limitations documentation.

---

**Presentation prepared**: 2026-02-13  
**Version**: 1.0.0
