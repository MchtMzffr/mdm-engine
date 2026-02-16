# MDM — Core Model Structure and User Manual (English)

This document describes the full **Core Model** structure (Justice, Compassion, Harm, Wellbeing, etc.) with mathematical formulas and a **detailed user manual** (what each part does, why, and examples).

---

# PART A — CORE MODEL STRUCTURE

## A.1 Overall Pipeline

The model runs a single decision cycle with these steps:

1. **Raw state (raw_state)** → **State Encoder** → encoded state **x_t**
2. **x_t** → **Action Generator** → candidate actions **A**
3. For each **(x_t, a)** → **Moral Evaluator** → scores **W, J, H, C**
4. **Constraint Validator** → valid candidates (J ≥ J_min, H ≤ H_max, C ∈ [C_min, C_max])
5. **Fail-Safe** → if J < J_crit or H > H_crit: safe action + human review
6. **Action Selector** → Pareto front + tie-break → chosen **a***
7. **Confidence** → confidence score and constraint margin for chosen action
8. **Uncertainty** → HI, DE, AS, CUS, divergence
9. **Soft Override** → L0 / L1 / L2 from confidence, harm, divergence
10. **Temporal Drift** → CUS history and preemptive escalation (optional)
11. **Soft Clamp** (L1) → shape action toward safety using CUS

---

## A.2 State Space

### Input: Raw state

Dictionary; each key is a numeric value in [0, 1]. Missing or invalid fields are filled with **0.5** (DEFAULT_UNKNOWN).

| Field | Description |
|-------|-------------|
| **physical** | Physical robustness (high = more robust; in C formula vulnerability = 1 − physical) |
| **social** | Social context |
| **context** | General context (high = intervention may be needed) |
| **risk** | Risk level |
| **compassion** | State compassion component |
| **justice** | State justice component |
| **harm_sens** | Harm sensitivity |
| **responsibility** | Responsibility (R) |
| **empathy** | Empathy (E) |

### Encoded state: State

- **x_ext** = (physical, social, context, risk) — 4 dimensions  
- **x_moral** = (compassion, justice, harm_sens, responsibility, empathy) — 5 dimensions  

```
x_ext  ∈ [0,1]^4
x_moral ∈ [0,1]^5
```

### Input quality

- **missing_mask**: For each STATE_KEY, is the field present and valid? (True/False)  
- **missing_ratio** = 1 − (count present / total)  
- **input_quality** = 1 − missing_ratio (or value from adapter)  
- **evidence_consistency** ∈ [0,1] (1 = consistent; from adapter or 1.0)  

---

## A.3 Action Space

Each action is a **4-dimensional** vector:

**a = [severity, compassion, intervention, delay]** ∈ [0,1]⁴

| Component | Meaning |
|-----------|---------|
| **severity** | Severity of response |
| **compassion** | Compassion level |
| **intervention** | Degree of intervention |
| **delay** | Delay (1 = maximum delay, "wait") |

The "do nothing" action **[0, 0, 0, 1]** is always in the candidate list.

### Grid generation

Default **ACTION_GRID_RESOLUTION** = [0.0, 0.5, 1.0]. All (severity, compassion, intervention, delay) combinations plus [0,0,0,1]. Coarse-to-fine: extra points around best candidates with ±step (e.g. 0.25).

---

## A.4 Moral Scores (W, J, H, C)

For a given **state** and **action a**, four scores are computed; all clamped to **[0, 1]**.

### 1) Wellbeing (W)

- **harm_contribution** = 0.4·severity + 0.3·(1 − compassion) + 0.3·risk  
- **intervention_benefit** = 0.5·intervention·(1 − delay)  
- **W** = 1 − 0.6·harm_contribution + 0.4·intervention_benefit  
- **W** = clamp(W, 0, 1)  

### 2) Justice (J)

- **compliance_severity** = 1 − 0.5·severity  
- **compliance_compassion** = 0.5 + 0.5·compassion  
- **compliance_context** = 1 − 0.5·max(0, context − intervention)  if risk > 0.5; else 1  
- **J** = min(compliance_severity, compliance_compassion, compliance_context)  
- **J** = clamp(J, 0, 1)  

### 3) Harm (H)

- **physical** = 0.5·severity·(1 − compassion)  
- **psychological** = 0.3·(1 − compassion)·intervention  
- **social** = 0.2·social·severity  (social = state.x_ext[1])  
- **H** = physical + psychological + social  
- **H** = clamp(H, 0, 1)  

### 4) Compassion (C)

- **E** = empathy (state.x_moral[4]), **R** = responsibility (state.x_moral[3])  
- **vulnerability** = 1 − physical (state.x_ext[0])  
- **raw** = α·E + β·vulnerability − γ·R  
- **C** = σ(2·(raw − 0.5))  

Defaults: **α = 0.4**, **β = 0.4**, **γ = 0.2**. **σ(x)** = 1/(1+e^(-x)).

---

## A.5 Constraints and Fail-Safe

- **J ≥ J_min**, **H ≤ H_max**, **C_min ≤ C ≤ C_max**. **margin** = min(J−J_min, H_max−H, C_band).  
- **Fail-Safe:** J < J_crit or H > H_crit → **safe_action** = [0, 0.5, 0, 1], human_escalation = True, L2.

---

## A.6 Score and Action Selection

- **Score** = α·W + β·J − γ·H + δ·C (default α=0.3, β=0.35, γ=0.2, δ=0.15).  
- **Pareto front** then tie-break: **margin** max, **H** min, **J** max, **W** max, **C** max; pick first.

---

## A.7 Confidence

- **sigma** = std(W, J, H, C); **sigma_norm** = sigma / SIGMA_MAX (0.5); **base_confidence** = 1 − sigma_norm.  
- **margin_factor** = σ(k·margin), k = 8; **confidence** = base_confidence · margin_factor.  
- suggest_escalation = (confidence < 0.35); force_escalation = (confidence < 0.20).

---

## A.8 Uncertainty

- **HI** = (1 − confidence) · (1 + σ(−k·margin)) / 2  
- **DE_norm** = DE / log(N); **AS_norm** = 1 − exp(−λ·AS), λ = 2 (None if &lt; 2 candidates)  
- **CUS** = w1·HI + w2·DE_norm + w3·(1 − AS_norm); default w = (0.4, 0.35, 0.25). If AS_norm is None, use 0.5.  
- **Divergence** = |confidence − (1 − DE_norm)|

---

## A.9 Escalation Level (L0 / L1 / L2)

Order: H &gt; H_crit → L2; confidence &lt; force → L2 or L1; divergence high → L2; H_high / constraint_violation / as_norm_low → L1; else L0.

---

## A.10 Soft Clamp (L1)

- **severity'** = severity · (1 − α·CUS), α = 0.60  
- **intervention'** = intervention · (1 − β·CUS), β = 0.50  
- **delay'** = delay + γ·CUS, γ = 0.35  
- **compassion'** = compassion (unchanged)

---

## A.11 Temporal Drift

CUS history; **delta_cus**, **cus_mean**; **preemptive_escalation** after warmup (history_len ≥ DRIFT_MIN_HISTORY).

---

## A.12 Driver Priority

1. fail_safe 2. no_valid_candidates 3. h_critical 4. constraint_violation 5. as_norm 6. temporal_drift 7. confidence 8. other

---

## A.13–A.16

Monotonicity expectations (risk↑⇒H↑/W↓; severity↑⇒H↑J↓; compassion↑⇒H↓J↑C↑). Core vs policy reason (engine_reason vs final_action_reason). Invariants (hard/soft). Parameter profiles: **wiki_calibrated** (J_MIN=0.65, H_MAX=0.55, H_CRITICAL=0.95), **production_safe** (stricter).

---

# PART B — USER MANUAL (WHAT IT DOES, WHY, EXAMPLES)

## B.1 State Encoder

**What:** raw_state → (x_ext, x_moral). **Why:** Model needs numeric vectors; missing → 0.5. **Example:** physical=0.2, social=0.8, risk=0.9, others missing → x_ext=(0.2, 0.8, 0.5, 0.9), x_moral=(0.5, …, 0.5). input_quality ≈ 0.33 (3/9 present).

## B.2 Action Generator

**What:** Grid (severity, compassion, intervention, delay) + [0,0,0,1]. **Why:** Finite deterministic search. **Example:** resolution=[0, 0.5, 1] → 82 candidates.

## B.3 W, J, H, C

**What:** Four moral scores per (state, action). **Why:** Constraints and fail-safe depend on them. **Example:** severity=1, compassion=0, risk=0.8 → high H, low J; possible fail-safe.

## B.4 Constraint Margin and Confidence

**What:** margin = min(J−J_min, H_max−H, C_band); confidence = base_confidence · σ(k·margin). **Why:** Negative margin → L1; very low confidence → L2. **Example:** J=0.9, H=0.2 → L0. J=0.8 below J_min=0.85 → L1.

## B.5 Fail-Safe

**What:** J &lt; J_crit or H &gt; H_crit → safe_action [0, 0.5, 0, 1], L2. **Why:** No automatic decision under extreme risk. **Example:** H=0.65, H_crit=0.6 → override, L2.

## B.6 Pareto and Tie-Break

**What:** Pareto front then sort by margin↑, H↓, J↑, W↑, C↑; pick first. **Why:** Safest and fairest choice. **Example:** Two Score=0.7; one H=0.25 margin=0.05 wins.

## B.7 Uncertainty (CUS, HI, DE, AS)

**What:** HI, DE, AS_norm, CUS. **Why:** High CUS → L1 or drift. **Example:** Two candidates very close → low AS → high CUS → as_norm_low → L1.

## B.8 Soft Clamp (L1)

**What:** At L1, reduce severity/intervention by CUS, increase delay. **Why:** Soften not block. **Example:** a=[0.5, 0.5, 0.5, 0.3], CUS=0.7 → severity'≈0.29, delay'≈0.545.

## B.9 Temporal Drift

**What:** CUS history → preemptive L1/L2 when delta_cus or cus_mean exceeds thresholds (after warmup). **Why:** Rising uncertainty → early escalation.

## B.10 Profiles

**What:** J_MIN, H_MAX, J_CRITICAL, H_CRITICAL, AS_SOFT_THRESHOLD, etc. **Why:** Different safety per domain. **Example:** wiki_calibrated → more L0/L1.

## B.11 Summary Table

| Concept | Role | Why |
|--------|------|-----|
| State (x_ext, x_moral) | Encodes input | Model uses numbers |
| W, J, H, C | Four moral scores | Constraints + fail-safe |
| Constraint margin | Slack inside box | L1 decision |
| Confidence | base × σ(k·margin) | L2 when very low |
| Fail-safe | J/H critical → safe_action | L2 human review |
| Pareto + tie-break | Best candidate | Consistent choice |
| CUS / HI / DE / AS | Uncertainty | L1 / drift triggers |
| Soft clamp | Soften by CUS | Shape at L1 |
| Temporal drift | Preemptive L1/L2 | Rising risk over time |

---

*Based on MDM core code (state_encoder, moral_evaluator, action_selector, confidence, uncertainty, fail_safe, soft_override, temporal_drift). Constants: mdm_engine.config and config_profiles.*
