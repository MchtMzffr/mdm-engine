# MDM Phase 4.6 — Profile base (engine + soft_override eşikleri).
# config.py ile senkron; override edilebilir anahtarlar.

import config as _cfg

DEFAULT_CONFIG = {
    "J_MIN": _cfg.J_MIN,
    "H_MAX": _cfg.H_MAX,
    "C_MIN": _cfg.C_MIN,
    "C_MAX": _cfg.C_MAX,
    "J_CRITICAL": _cfg.J_CRITICAL,
    "H_CRITICAL": _cfg.H_CRITICAL,
    "CONFIDENCE_ESCALATION_FORCE": _cfg.CONFIDENCE_ESCALATION_FORCE,
    "CONFIDENCE_LOW_ESCALATION_LEVEL": getattr(_cfg, "CONFIDENCE_LOW_ESCALATION_LEVEL", 2),
    "SEVERITY_SOFT_MAX": _cfg.SEVERITY_SOFT_MAX,
    "INTERVENTION_SOFT_MAX": _cfg.INTERVENTION_SOFT_MAX,
    "DELAY_SOFT_MIN": _cfg.DELAY_SOFT_MIN,
    "AS_SOFT_THRESHOLD": _cfg.AS_SOFT_THRESHOLD,
    "DIVERGENCE_HARD_THRESHOLD": _cfg.DIVERGENCE_HARD_THRESHOLD,
    "ESCALATION_HYSTERESIS": _cfg.ESCALATION_HYSTERESIS,
    "SOFT_CLAMP_ALPHA": getattr(_cfg, "SOFT_CLAMP_ALPHA", 0.60),
    "SOFT_CLAMP_BETA": getattr(_cfg, "SOFT_CLAMP_BETA", 0.50),
    "SOFT_CLAMP_GAMMA": getattr(_cfg, "SOFT_CLAMP_GAMMA", 0.35),
}
