<!--
Decision Ecosystem — mdm-engine
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Formulas — mdm-engine

Let x_t be a state vector extracted from raw inputs at time t.

## Proposal scoring (abstract)

```
s_t = f_theta(x_t, c_t)
```

Where:
- `s_t` is a real-valued score (or score vector)
- `c_t` is context (non-domain, operational metadata)
- `f_theta` is a deterministic function under a given profile

## Confidence (abstract)

```
conf_t = sigma(s_t)   (e.g., sigmoid/softmax depending on action space)
```

---

## Reference implementation: moral-scores pipeline (W, J, H, C)

When the engine uses a moral-evaluator pipeline, one concrete formulation is as follows. State: **x_ext** ∈ [0,1]⁴ (e.g. physical, social, context, risk), **x_moral** ∈ [0,1]⁵ (e.g. compassion, justice, harm_sens, responsibility, empathy). Action **a** = [severity, compassion, intervention, delay] ∈ [0,1]⁴.

### Moral scores (all clamped to [0, 1])

- **Wellbeing (W):**  
  harm_contribution = 0.4·severity + 0.3·(1 − compassion) + 0.3·risk  
  intervention_benefit = 0.5·intervention·(1 − delay)  
  **W** = clamp(1 − 0.6·harm_contribution + 0.4·intervention_benefit, 0, 1)

- **Justice (J):**  
  compliance_severity = 1 − 0.5·severity; compliance_compassion = 0.5 + 0.5·compassion  
  compliance_context = 1 − 0.5·max(0, context − intervention) if risk > 0.5 else 1  
  **J** = clamp(min(compliance_severity, compliance_compassion, compliance_context), 0, 1)

- **Harm (H):**  
  physical = 0.5·severity·(1 − compassion); psychological = 0.3·(1 − compassion)·intervention; social = 0.2·social·severity  
  **H** = clamp(physical + psychological + social, 0, 1)

- **Compassion (C):**  
  raw = α·E + β·(1 − physical) − γ·R with **α=0.4, β=0.4, γ=0.2** (E = empathy, R = responsibility)  
  **C** = σ(2·(raw − 0.5)), where **σ(x) = 1/(1+e^(-x))**

### Action score and selection

- **Score** = α·W + β·J − γ·H + δ·C with default **α=0.3, β=0.35, γ=0.2, δ=0.15**
- Selection: Pareto front, then tie-break by margin↑, H↓, J↑, W↑, C↑

### Confidence (from chosen action)

- base_confidence = 1 − (sigma_norm), sigma_norm = std(W,J,H,C) / SIGMA_MAX (e.g. 0.5)
- margin_factor = σ(k·margin), **k = 8**
- **confidence** = base_confidence · margin_factor

### Uncertainty (CUS)

- **CUS** = w1·HI + w2·DE_norm + w3·(1 − AS_norm); default **w = (0.4, 0.35, 0.25)**. If AS_norm is None, use 0.5.

---

## Reference implementation: generic numeric scorer

For a generic reference model that scores proposals from numeric signals (e.g. scale, signal strength, width):

- scale_score = min(1, scale_a/100); signal_score = |s1|; width_penalty = min(1, max(0, 1 − scale_b/1000))
- **raw_score** = 0.4·scale_score + 0.4·signal_score + 0.2·width_penalty
- **confidence** = σ(5·(raw_score − 0.5)), with σ(x) = 1/(1+e^(-x))
- ACT ⇔ confidence ≥ threshold and |s1| ≥ signal_threshold

## Invariants

- `conf_t ∈ [0, 1]`
- `propose(x_t, c_t)` is deterministic for fixed inputs and profile
- exceptions => fail-closed proposal (`Action.HOLD` or `Action.STOP`)

## Feature extraction (generic)

Features are extracted from event dictionaries:

```
x_t = extract_features(event_t, history_t)
```

Where:
- `event_t`: Generic event dictionary (timestamp, values, metadata)
- `history_t`: Historical events for rolling statistics
- `x_t`: Feature vector (numeric values)

## Latency metrics

```
latency_ms = now_ms - event_ts_ms
feature_latency_ms = feature_end_ts - event_ts_ms
mdm_latency_ms = mdm_end_ts - feature_end_ts
```

## Trace packet

```
PacketV2(
    run_id=run_id,
    step=step,
    input=event_dict,  # Redacted
    external=context_dict,  # Redacted
    mdm=proposal_dict,
    final_action=final_decision_dict,
    latency_ms=total_latency_ms,
    mismatch=mismatch_info_dict if any,
    schema_version="0.1.0",
)
```
