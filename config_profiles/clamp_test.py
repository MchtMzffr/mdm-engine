# MDM Phase 6.3 — Clamp test profili.
# Fail-safe zorlaşır; soft clamp aktif davranış üretir (dashboard + learning için, production'a girmez).

from .base import DEFAULT_CONFIG

CONFIG = {
    **DEFAULT_CONFIG,
    "J_CRITICAL": 0.45,
    "H_CRITICAL": 0.85,
    "SOFT_CLAMP_ALPHA": 0.6,
}
