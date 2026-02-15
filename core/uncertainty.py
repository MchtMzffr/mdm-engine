# MDM — Phase 4.4 Cognitive Uncertainty Engine (06_PHASE_44)
# HI, DE, AS, CUS, divergence; overflow-safe softmax, log(0) clamp.

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

import config as _config


@dataclass
class UncertaintyResult:
    hi: float
    de: float
    de_norm: float
    as_: float
    as_norm: Optional[float]  # None = hesaplanamadı (örn. <2 aday) → as_norm_low tetiklenmez
    cus: float
    divergence: float

    def to_dict(self) -> dict:
        return {
            "hi": self.hi,
            "de": self.de,
            "de_norm": self.de_norm,
            "as_": self.as_,
            "as_norm": self.as_norm,
            "cus": self.cus,
            "divergence": self.divergence,
        }


def _sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    t = math.exp(x)
    return t / (1.0 + t)


def hesitation_index(
    confidence: float,
    constraint_margin: float,
    k: Optional[float] = None,
) -> float:
    """HI = (1 - confidence) * (1 + sigmoid(-k * margin)) / 2. Aralık [0, 1]."""
    k = k if k is not None else getattr(_config, "UNCERTAINTY_MARGIN_K", 5.0)
    hi_base = 1.0 - max(0.0, min(1.0, confidence))
    margin_factor = (1.0 + _sigmoid(-k * constraint_margin)) / 2.0
    return hi_base * margin_factor


def decision_entropy(
    scores: List[float],
    temperature: float = 1.0,
) -> Tuple[float, float]:
    """
    Softmax + entropy. Overflow-safe: subtract max before exp.
    Returns (DE, DE_norm). DE_norm = DE / log(N) ∈ [0, 1]; N=1 → (0, 0).
    """
    if not scores:
        return 0.0, 0.0
    if len(scores) == 1:
        return 0.0, 0.0
    s = [x / max(temperature, 1e-12) for x in scores]
    m = max(s)
    exp_s = [math.exp(x - m) for x in s]
    z = sum(exp_s)
    if z <= 0:
        return 0.0, 0.0
    probs = [e / z for e in exp_s]
    de = 0.0
    for p in probs:
        if p > 0:
            de -= p * math.log(p)
    n = len(scores)
    de_max = math.log(n)
    de_norm = de / de_max if de_max > 0 else 0.0
    de_norm = max(0.0, min(1.0, de_norm))
    return de, de_norm


def action_spread(
    scores: List[float],
    lambda_norm: Optional[float] = None,
) -> Tuple[float, Optional[float]]:
    """
    AS = best - second_best (≥2 aday). AS_norm = 1 - exp(-λ*AS).
    Tek aday veya boş → (0, None); as_norm=None ile as_norm_low tetiklenmez (sinyal yok).
    """
    lam = lambda_norm if lambda_norm is not None else getattr(_config, "UNCERTAINTY_AS_LAMBDA", 2.0)
    if not scores or len(scores) < 2:
        return 0.0, None
    sorted_scores = sorted(scores, reverse=True)
    as_raw = sorted_scores[0] - sorted_scores[1]
    as_raw = max(0.0, as_raw)
    as_norm = 1.0 - math.exp(-lam * as_raw)
    as_norm = max(0.0, min(1.0, as_norm))
    return as_raw, as_norm


def combined_uncertainty_score(
    hi: float,
    de_norm: float,
    as_norm: Optional[float],
    weights: Optional[Tuple[float, float, float]] = None,
) -> float:
    """CUS = w1*HI + w2*DE_norm + w3*(1 - AS_norm). as_norm=None ise nötr 0.5 kullanılır."""
    w = weights or getattr(_config, "CUS_WEIGHTS", (0.4, 0.35, 0.25))
    w1, w2, w3 = w[0], w[1], w[2]
    as_term = (1.0 - as_norm) if as_norm is not None else 0.5
    cus = w1 * hi + w2 * de_norm + w3 * as_term
    return max(0.0, min(1.0, cus))


def confidence_uncertainty_divergence(confidence: float, de_norm: float) -> float:
    """D = | confidence - (1 - DE_norm) |."""
    return abs(confidence - (1.0 - de_norm))


def compute_uncertainty(
    confidence: float,
    constraint_margin: float,
    candidate_scores: List[float],
    config: Optional[dict] = None,
) -> UncertaintyResult:
    """
    Tek çağrıda tüm belirsizlik metrikleri.
    candidate_scores: aday aksiyonların skorları (Score = α*W+β*J−γ*H+δ*C).
    config: opsiyonel override (k, lambda_norm, cus_weights).
    """
    co = config or {}
    k = co.get("UNCERTAINTY_MARGIN_K", getattr(_config, "UNCERTAINTY_MARGIN_K", 5.0))
    lam = co.get("UNCERTAINTY_AS_LAMBDA", getattr(_config, "UNCERTAINTY_AS_LAMBDA", 2.0))
    cus_weights = co.get("CUS_WEIGHTS", getattr(_config, "CUS_WEIGHTS", (0.4, 0.35, 0.25)))

    hi = hesitation_index(confidence, constraint_margin, k=k)
    de, de_norm = decision_entropy(candidate_scores)
    as_raw, as_norm = action_spread(candidate_scores, lambda_norm=lam)
    cus = combined_uncertainty_score(hi, de_norm, as_norm, weights=cus_weights)
    divergence = confidence_uncertainty_divergence(confidence, de_norm)

    return UncertaintyResult(
        hi=hi,
        de=de,
        de_norm=de_norm,
        as_=as_raw,
        as_norm=as_norm,
        cus=cus,
        divergence=divergence,
    )
