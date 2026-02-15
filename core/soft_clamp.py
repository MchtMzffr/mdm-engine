# MDM Phase 4.6.1 — Adaptive Soft Clamp.
# Level 1: aksiyonu yasaklamak yerine CUS ile sürekli güvenli tarafa şekillendirir.

from typing import List


def soft_clamp_action(
    action: List[float],
    cus: float,
    alpha: float,
    beta: float,
    gamma: float,
) -> List[float]:
    """
    a = [severity, compassion, intervention, delay].
    severity' = severity * (1 - α*CUS), intervention' = intervention * (1 - β*CUS),
    delay' = delay + γ*CUS, compassion' = compassion.
    Tüm çıktılar [0, 1] clamp edilir.
    """
    if len(action) < 4:
        return list(action)
    cus = max(0.0, min(1.0, cus))
    severity, compassion, intervention, delay = action[0], action[1], action[2], action[3]
    s = max(0.0, min(1.0, severity * (1.0 - alpha * cus)))
    i = max(0.0, min(1.0, intervention * (1.0 - beta * cus)))
    d = max(0.0, min(1.0, delay + gamma * cus))
    return [s, compassion, i, d]
