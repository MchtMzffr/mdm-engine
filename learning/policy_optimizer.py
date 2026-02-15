# Phase 6.0 — Parametre sınırları ve aday config üretimi

import random
from typing import Any, Dict, List

# Spec 15: güvenlik sınırları (min, max)
PARAM_BOUNDS: Dict[str, tuple] = {
    "J_MIN": (0.50, 0.95),
    "H_MAX": (0.15, 0.50),
    "SOFT_CLAMP_ALPHA": (0.3, 0.9),
    "SOFT_CLAMP_BETA": (0.3, 0.9),
    "SOFT_CLAMP_GAMMA": (0.2, 0.6),
    "DELTA_CUS_THRESHOLD": (0.05, 0.25),
    "CUS_MEAN_THRESHOLD": (0.50, 0.85),
}


def clamp_param(value: float, key: str) -> float:
    """Değeri parametre sınırları içine alır."""
    lo, hi = PARAM_BOUNDS.get(key, (0.0, 1.0))
    return max(lo, min(hi, value))


def suggest_candidates(
    current_config: Dict[str, Any],
    num_candidates: int = 5,
    step_scale: float = 0.1,
    seed: int = 42,
) -> List[Dict[str, Any]]:
    """
    Mevcut config etrafında rastgele aday config'ler üretir.
    Her parametre bounds içinde kalır; step_scale ile pertürbasyon büyüklüğü ayarlanır.
    """
    rng = random.Random(seed)
    candidates = []
    keys = [k for k in PARAM_BOUNDS if k in current_config]
    if not keys:
        keys = list(PARAM_BOUNDS.keys())
        for k in keys:
            current_config.setdefault(k, (PARAM_BOUNDS[k][0] + PARAM_BOUNDS[k][1]) / 2)

    for _ in range(num_candidates):
        candidate = dict(current_config)
        for key in keys:
            lo, hi = PARAM_BOUNDS[key]
            curr = candidate.get(key)
            if curr is None:
                curr = (lo + hi) / 2
            delta = (hi - lo) * step_scale * (rng.random() * 2 - 1)
            candidate[key] = round(clamp_param(curr + delta, key), 4)
        candidates.append(candidate)
    return candidates
