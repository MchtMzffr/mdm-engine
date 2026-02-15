# Phase 6.0 — Loss: L = w1*fail_safe_rate + w2*mean_cus + w3*clamp_distortion
# Phase 6.3 — L'den w4*non_fail_reward çıkarılır (iyi davranış ödülü)

from typing import Dict, Tuple

# Önerilen ağırlıklar (spec 15 + Phase 6.3)
# w4: non_fail_reward (L0→1, L1→0.5, L2→0); L'yi düşürür
DEFAULT_WEIGHTS: Tuple[float, ...] = (1.5, 1.0, 0.5, 0.8)  # w1, w2, w3, w4


def compute_loss(
    metrics: Dict[str, float],
    weights: Tuple[float, ...] = DEFAULT_WEIGHTS,
) -> float:
    """
    L = w1*fail_safe_rate + w2*mean_cus + w3*clamp_distortion - w4*non_fail_reward
    Amaç: L'yi minimize etmek (L0/L1 ödüllendirilir).
    """
    w1 = weights[0] if len(weights) > 0 else 1.5
    w2 = weights[1] if len(weights) > 1 else 1.0
    w3 = weights[2] if len(weights) > 2 else 0.5
    w4 = weights[3] if len(weights) > 3 else 0.8
    base = (
        w1 * metrics.get("fail_safe_rate", 0)
        + w2 * metrics.get("mean_cus", 0)
        + w3 * metrics.get("clamp_distortion", 0)
    )
    reward = metrics.get("non_fail_reward", 0.0)
    return base - w4 * reward
