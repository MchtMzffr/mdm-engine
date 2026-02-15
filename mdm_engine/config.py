# MDM — Phase 3: Yapılandırma
# Tüm sabitler ve ağırlıklar tek yerde (Phase 1–2 referanslı).

from dataclasses import dataclass
from typing import List

# Varsayılan bilinmeyen değer (State Encoder)
DEFAULT_UNKNOWN = 0.5

# Aksiyon grid çözünürlüğü (0, 0.5, 1 vb.)
ACTION_GRID_RESOLUTION: List[float] = [0.0, 0.5, 1.0]

# Etik kısıtlar (Phase 1)
J_MIN = 0.85
H_MAX = 0.30
C_MIN = 0.35
C_MAX = 0.75

# Fail-safe eşikleri (Phase 1–2)
J_CRITICAL = 0.7
H_CRITICAL = 0.6

# Güvenli aksiyon (fail-safe override)
SAFE_ACTION: List[float] = [0.0, 0.5, 0.0, 1.0]

# Skor ağırlıkları: Score = α*W + β*J - γ*H + δ*C
@dataclass(frozen=True)
class ScoringWeights:
    alpha: float  # W (wellbeing)
    beta: float   # J (justice)
    gamma: float  # H (harm) — ceza
    delta: float  # C (compassion)

DEFAULT_WEIGHTS = ScoringWeights(alpha=0.3, beta=0.35, gamma=0.2, delta=0.15)

# Compassion formülü: C = σ(α*E + β*vulnerability - γ*R)
COMPASSION_ALPHA = 0.4
COMPASSION_BETA = 0.4
COMPASSION_GAMMA = 0.2

# B.3 — Ethical Confidence (04_QUALITY_AND_PHASE4_SPEC)
SIGMA_MAX = 0.5
CONFIDENCE_MARGIN_K = 8.0
CONFIDENCE_ESCALATION_SUGGEST = 0.35
CONFIDENCE_ESCALATION_FORCE = 0.20
CONFIDENCE_LOW_ESCALATION_LEVEL = 2  # confidence_low tetikleyince seviye: 2=L2, 1=L1 (profil ile yumuşatılabilir)
CONFIDENCE_MARGIN_CLAMP = 1.0  # margin ∈ [-M, +M] → numeric stability, chaos test

# Phase 4.4 — Cognitive Uncertainty (06_PHASE_44)
UNCERTAINTY_MARGIN_K = 5.0
UNCERTAINTY_AS_LAMBDA = 2.0
CUS_WEIGHTS = (0.4, 0.35, 0.25)  # (w1 HI, w2 DE_norm, w3 (1 - AS_norm))

# Phase 4.5 — Soft Override & Safety Envelope (07_PHASE_45)
SEVERITY_SOFT_MAX = 0.6
INTERVENTION_SOFT_MAX = 0.5
DELAY_SOFT_MIN = 0.3
AS_SOFT_THRESHOLD = 0.3
DIVERGENCE_HARD_THRESHOLD = 0.5
ESCALATION_HYSTERESIS = 0.02

# Phase 4.6.1 — Adaptive Soft Clamp (Level 1 behavioral shaping)
SOFT_CLAMP_ALPHA = 0.60
SOFT_CLAMP_BETA = 0.50
SOFT_CLAMP_GAMMA = 0.35

# Phase 5 — Temporal Drift Monitor
DELTA_CUS_THRESHOLD = 0.15
CUS_MEAN_WINDOW = 60   # >= DRIFT_MIN_HISTORY (30) olmalı; warmup bitip drift tetikleyicileri devreye girsin
CUS_MEAN_THRESHOLD = 0.65
DRIFT_MIN_HISTORY = 30  # warmup: bu kadar CUS noktası olmadan preemptive devreye girmez
