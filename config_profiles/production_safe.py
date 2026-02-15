# MDM Phase 4.6 — Production-safe profile.
# Daha gevşek eşikler: Level 0 ağırlıklı, az Level 2.

from .base import DEFAULT_CONFIG

CONFIG = {
    **DEFAULT_CONFIG,
    "J_MIN": 0.65,
    "H_MAX": 0.40,
    "C_MIN": 0.30,
    "C_MAX": 0.80,
    "J_CRITICAL": 0.55,
    "H_CRITICAL": 0.70,
    "SEVERITY_SOFT_MAX": 0.65,
    "INTERVENTION_SOFT_MAX": 0.55,
    "DELAY_SOFT_MIN": 0.25,
    "AS_SOFT_THRESHOLD": 0.28,
    "DIVERGENCE_HARD_THRESHOLD": 0.48,
}
