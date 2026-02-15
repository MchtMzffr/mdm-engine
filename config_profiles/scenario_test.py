# MDM Phase 6.2 — Scenario / curriculum test profili.
# Fail-safe grid worst-case'i tetiklemesin (worst_J=0.5, worst_H~0.96); L0/L1/L2 dağılımı görünsün.

from .base import DEFAULT_CONFIG

# Grid'de severity=1 → J en az 0.5; bazı aksiyonlar H~0.96. Bu yüzden fail_safe için:
# J_CRITICAL <= 0.5, H_CRITICAL >= 0.96 → override tetiklenmez, escalation L0/L1/L2 confidence'dan gelir.
CONFIG = {
    **DEFAULT_CONFIG,
    "J_MIN": 0.55,
    "H_MAX": 0.50,
    "J_CRITICAL": 0.45,
    "H_CRITICAL": 0.98,
    "C_MIN": 0.30,
    "C_MAX": 0.80,
    "CONFIDENCE_ESCALATION_FORCE": 0.10,
}
