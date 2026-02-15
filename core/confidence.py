# MDM — B.3 Ethical Confidence & Constraint Margin (04_QUALITY_AND_PHASE4_SPEC)
# 3 katman: base_confidence (σ) + margin_factor (sigmoid) → confidence.

import math
from dataclasses import dataclass
from typing import Dict

from config import (
    C_MAX,
    C_MIN,
    CONFIDENCE_ESCALATION_FORCE,
    CONFIDENCE_ESCALATION_SUGGEST,
    CONFIDENCE_MARGIN_K,
    CONFIDENCE_MARGIN_CLAMP,
    H_MAX,
    J_MIN,
    SIGMA_MAX,
)
from .moral_evaluator import MoralScores


@dataclass
class ConfidenceResult:
    confidence: float
    constraint_margin: float
    base_confidence: float
    margin_factor: float
    suggest_escalation: bool
    force_escalation: bool
    confidence_gradient: float  # ∂confidence/∂margin (Phase 4.2 hassasiyet analizi)


def _sigmoid(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 0.0 if x < 0 else 1.0


def _std4(w: float, j: float, h: float, c: float) -> float:
    n = 4
    mean = (w + j + h + c) / n
    var = ((w - mean) ** 2 + (j - mean) ** 2 + (h - mean) ** 2 + (c - mean) ** 2) / n
    return math.sqrt(max(0.0, var))


def _constraint_margin(
    j: float,
    h: float,
    c: float,
    j_min: float,
    h_max: float,
    c_min: float,
    c_max: float,
) -> float:
    j_margin = j - j_min
    h_margin = h_max - h
    c_margin = min(c - c_min, c_max - c)
    return min(j_margin, h_margin, c_margin)


def compute_confidence(
    scores: MoralScores | Dict[str, float],
    j_min: float = J_MIN,
    h_max: float = H_MAX,
    c_min: float = C_MIN,
    c_max: float = C_MAX,
    sigma_max: float = SIGMA_MAX,
    k: float = CONFIDENCE_MARGIN_K,
    margin_clamp: float = CONFIDENCE_MARGIN_CLAMP,
    escalation_suggest: float = CONFIDENCE_ESCALATION_SUGGEST,
    escalation_force: float = CONFIDENCE_ESCALATION_FORCE,
) -> ConfidenceResult:
    """
    Seçilen aksiyonun (W,J,H,C) skorlarından confidence ve constraint margin hesaplar.
    margin soft-clamp ile numeric stabilite; confidence_gradient = ∂confidence/∂margin.
    """
    if isinstance(scores, MoralScores):
        w, j, h, c = scores.W, scores.J, scores.H, scores.C
    else:
        w = scores["W"]
        j = scores["J"]
        h = scores["H"]
        c = scores["C"]

    sigma = _std4(w, j, h, c)
    sigma_norm = sigma / sigma_max if sigma_max > 0 else 0.0
    base_confidence = max(0.0, min(1.0, 1.0 - sigma_norm))

    margin_raw = _constraint_margin(j, h, c, j_min, h_max, c_min, c_max)
    margin = max(-margin_clamp, min(margin_clamp, margin_raw))

    margin_factor = _sigmoid(k * margin)
    confidence = max(0.0, min(1.0, base_confidence * margin_factor))

    suggest_escalation = confidence < escalation_suggest
    force_escalation = confidence < escalation_force

    # ∂confidence/∂margin = base_confidence * k * margin_factor * (1 - margin_factor)
    confidence_gradient = base_confidence * k * margin_factor * (1.0 - margin_factor)

    return ConfidenceResult(
        confidence=confidence,
        constraint_margin=margin_raw,
        base_confidence=base_confidence,
        margin_factor=margin_factor,
        suggest_escalation=suggest_escalation,
        force_escalation=force_escalation,
        confidence_gradient=confidence_gradient,
    )
