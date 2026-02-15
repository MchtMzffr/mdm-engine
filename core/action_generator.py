# MDM — Action Generator (Phase 2 spec §1.2)
# Verilen state için aday aksiyon kümesi üretir; kural tabanlı, deterministik.
# Tavsiye §2: coarse-to-fine — en iyi adaylar etrafında yerel refine.

from typing import List, Set, Tuple

from config import ACTION_GRID_RESOLUTION
from .state_encoder import State


def generate_actions(
    x_t: State,
    resolution: List[float] | None = None,
) -> List[List[float]]:
    """
    Grid tabanlı aday aksiyon listesi. Her a = [severity, compassion, intervention, delay] ∈ [0,1]^4.
    'Hiçbir şey yapma' [0,0,0,1] her zaman dahil.
    """
    grid = resolution or ACTION_GRID_RESOLUTION
    A: List[List[float]] = []
    for severity in grid:
        for compassion in grid:
            for intervention in grid:
                for delay in grid:
                    A.append([float(severity), float(compassion), float(intervention), float(delay)])
    A.append([0.0, 0.0, 0.0, 1.0])
    return A


def _round_action(a: List[float], ndigits: int = 6) -> Tuple[float, ...]:
    return tuple(round(float(x), ndigits) for x in a)


def refine_actions_around(
    actions: List[List[float]],
    step: float = 0.25,
    ndim: int = 4,
) -> List[List[float]]:
    """
    Verilen aksiyonların çevresinde ±step ile yeni noktalar üretir (coarse-to-fine).
    [0,1]^ndim içinde clamp; tekrarlar çıkarılır.
    """
    seen: Set[Tuple[float, ...]] = set()
    out: List[List[float]] = []
    for a in actions:
        base = [float(a[i]) if i < len(a) else 0.0 for i in range(ndim)]
        key = _round_action(base)
        if key not in seen:
            seen.add(key)
            out.append(base)
        for i in range(ndim):
            for delta in (-step, step):
                v = base[i] + delta
                v = max(0.0, min(1.0, v))
                neighbor = base[:]
                neighbor[i] = v
                k = _round_action(neighbor)
                if k not in seen:
                    seen.add(k)
                    out.append(neighbor)
    return out
