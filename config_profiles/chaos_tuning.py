# MDM Phase 4.6 — Chaos-tuning profile.
# Eşikleri bilerek gevşetir; L0 ~50-70%, L1 ~20-35%, L2 ~5-15% bandı için zengin veri.
# Tuning runner ve davranış spektrumu analizi için kullanılır; prod için değil.

from .base import DEFAULT_CONFIG

CONFIG = {
    **DEFAULT_CONFIG,
    "J_MIN": 0.55,
    "H_MAX": 0.55,
    "C_MIN": 0.25,
    "C_MAX": 0.90,
    "J_CRITICAL": 0.35,
    "H_CRITICAL": 0.80,
    "CONFIDENCE_ESCALATION_FORCE": 0.12,
    "SEVERITY_SOFT_MAX": 0.75,
    "INTERVENTION_SOFT_MAX": 0.65,
    "DELAY_SOFT_MIN": 0.20,
    "AS_SOFT_THRESHOLD": 0.25,
    "DIVERGENCE_HARD_THRESHOLD": 0.55,
}
