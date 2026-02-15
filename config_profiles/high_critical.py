# MDM Phase 4.6 — High-critical profile.
# Sıkı eşikler: güvenlik öncelikli, daha fazla Level 1/2.

from .base import DEFAULT_CONFIG

CONFIG = {
    **DEFAULT_CONFIG,
    "J_MIN": 0.85,
    "H_MAX": 0.25,
    "C_MIN": 0.35,
    "C_MAX": 0.75,
    "J_CRITICAL": 0.75,
    "H_CRITICAL": 0.55,
    "SEVERITY_SOFT_MAX": 0.55,
    "INTERVENTION_SOFT_MAX": 0.45,
    "DELAY_SOFT_MIN": 0.35,
    "AS_SOFT_THRESHOLD": 0.35,
    "DIVERGENCE_HARD_THRESHOLD": 0.52,
}
