# MDM — Action Selector (Phase 2 spec §1.6)
# Fail-safe varsa onu döndürür; yoksa Score = α*W + β*J - γ*H + δ*C ile argmax.
# Tavsiye §3: Pareto front + tie-break (constraint margin → H min → J max → W, C).

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from config import DEFAULT_WEIGHTS, ScoringWeights
from .fail_safe import FailSafeResult
from .moral_evaluator import MoralScores


@dataclass
class SelectionResult:
    action: List[float]
    score: float | None
    reason: str
    frontier_size: Optional[int] = None  # Pareto front boyutu
    pareto_gap: Optional[float] = None   # seçilen ile bir sonraki arası skor farkı (belirsizlik sinyali)


def _score(s: MoralScores, w: ScoringWeights) -> float:
    return w.alpha * s.W + w.beta * s.J - w.gamma * s.H + w.delta * s.C


def _constraint_margin(
    j: float, h: float, c: float,
    j_min: float, h_max: float, c_min: float, c_max: float,
) -> float:
    j_m = j - j_min
    h_m = h_max - h
    c_m = min(c - c_min, c_max - c)
    return min(j_m, h_m, c_m)


def _is_dominated(i: int, candidates: List[Tuple[List[float], MoralScores]]) -> bool:
    """i, başka bir j tarafından domine ediliyor mu? (W,J yüksek; H düşük; C yüksek arzu edilir.)"""
    si = candidates[i][1]
    for j in range(len(candidates)):
        if j == i:
            continue
        sj = candidates[j][1]
        if sj.W >= si.W and sj.J >= si.J and sj.H <= si.H and sj.C >= si.C:
            if sj.W > si.W or sj.J > si.J or sj.H < si.H or sj.C > si.C:
                return True
    return False


def select_action(
    candidates: List[Tuple[List[float], MoralScores]],
    fail_safe_result: FailSafeResult,
    weights: ScoringWeights | None = None,
    config: Optional[Dict[str, Any]] = None,
    use_pareto: bool = True,
) -> SelectionResult:
    """
    Fail-safe override ise safe_action; değilse:
    use_pareto=True: Pareto front → tie-break (margin desc, H asc, J desc, W desc, C desc).
    use_pareto=False: tek skor ile argmax (orijinal davranış).
    """
    w = weights or DEFAULT_WEIGHTS
    co = config or {}
    j_min = co.get("J_MIN", 0.85)
    h_max = co.get("H_MAX", 0.30)
    c_min = co.get("C_MIN", 0.35)
    c_max = co.get("C_MAX", 0.75)

    if fail_safe_result.override and fail_safe_result.safe_action is not None:
        return SelectionResult(
            action=fail_safe_result.safe_action,
            score=None,
            reason="fail_safe",
            frontier_size=None,
            pareto_gap=None,
        )
    if not candidates:
        fallback = fail_safe_result.safe_action if fail_safe_result.safe_action else [0.0, 0.5, 0.0, 1.0]
        return SelectionResult(action=fallback, score=None, reason="no_valid_fallback", frontier_size=0, pareto_gap=None)

    if use_pareto and len(candidates) > 1:
        pareto_idx = [i for i in range(len(candidates)) if not _is_dominated(i, candidates)]
        if not pareto_idx:
            pareto_idx = list(range(len(candidates)))
        # Tie-break: constraint_margin max, then H min, then J max, then W, then C
        def sort_key(idx: int) -> Tuple[float, float, float, float, float]:
            _, s = candidates[idx][0], candidates[idx][1]
            margin = _constraint_margin(s.J, s.H, s.C, j_min, h_max, c_min, c_max)
            return (-margin, s.H, -s.J, -s.W, -s.C)
        pareto_idx.sort(key=sort_key)
        best_idx = pareto_idx[0]
        best = candidates[best_idx]
        frontier_size = len(pareto_idx)
        if len(pareto_idx) >= 2:
            score_best = _score(best[1], w)
            score_second = _score(candidates[pareto_idx[1]][1], w)
            pareto_gap = float(score_best - score_second) if score_best is not None and score_second is not None else None
        else:
            pareto_gap = None
        return SelectionResult(
            action=best[0],
            score=_score(best[1], w),
            reason="pareto_tiebreak",
            frontier_size=frontier_size,
            pareto_gap=pareto_gap,
        )

    best = max(candidates, key=lambda item: _score(item[1], w))
    return SelectionResult(
        action=best[0],
        score=_score(best[1], w),
        reason="max_score",
        frontier_size=None,
        pareto_gap=None,
    )
