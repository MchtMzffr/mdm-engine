# MDM — Moral Evaluation Engine (Phase 2 spec §1.3)
# Her (x_t, a) için W, J, H, C skorlarını deterministik hesaplar.

from dataclasses import dataclass
from math import exp
from typing import List

from config import COMPASSION_ALPHA, COMPASSION_BETA, COMPASSION_GAMMA
from .state_encoder import State


@dataclass(frozen=True)
class MoralScores:
    W: float
    J: float
    H: float
    C: float


def _sigmoid(x: float) -> float:
    """[0,1] aralığına sıkıştırılmış sigmoid benzeri."""
    try:
        y = 1.0 / (1.0 + exp(-x))
    except OverflowError:
        y = 0.0 if x < 0 else 1.0
    return max(0.0, min(1.0, y))


def compute_wellbeing(state: State, a: List[float]) -> float:
    """W = toplumsal iyilik hali. Basit model: zarar tersi + müdahale faydası."""
    severity, compassion, intervention, delay = a[0], a[1], a[2], a[3]
    risk = state.x_ext[3]
    harm_contribution = 0.4 * severity + 0.3 * (1.0 - compassion) + 0.3 * risk
    intervention_benefit = 0.5 * intervention * (1.0 - delay)
    w = 1.0 - 0.6 * harm_contribution + 0.4 * intervention_benefit
    return max(0.0, min(1.0, w))


def compute_justice(state: State, a: List[float]) -> float:
    """J = min_k compliance_k. En zayıf kural uyumu skoru belirler."""
    severity, compassion, intervention, delay = a[0], a[1], a[2], a[3]
    # Kural 1: Aşırı sertlik adaleti düşürür
    compliance_severity = 1.0 - 0.5 * severity
    # Kural 2: Merhamet yoksa adalet düşer
    compliance_compassion = 0.5 + 0.5 * compassion
    # Kural 3: Bağlam (context) yüksekse müdahale gerekir; çok düşük müdahale + yüksek risk = uyumsuzluk
    context = state.x_ext[2]
    risk = state.x_ext[3]
    compliance_context = 1.0 - 0.5 * max(0, context - intervention) if risk > 0.5 else 1.0
    j = min(compliance_severity, compliance_compassion, compliance_context)
    return max(0.0, min(1.0, j))


def compute_harm(state: State, a: List[float]) -> float:
    """H = beklenen zarar; [0,1] normalize."""
    severity, compassion, intervention, delay = a[0], a[1], a[2], a[3]
    physical = 0.5 * severity * (1.0 - compassion)
    psychological = 0.3 * (1.0 - compassion) * intervention
    social = 0.2 * state.x_ext[1] * severity
    h = physical + psychological + social
    return max(0.0, min(1.0, h))


def compute_compassion(state: State, a: List[float]) -> float:
    """C = σ(α*E + β*vulnerability - γ*R)."""
    E = state.x_moral[4]
    R = state.x_moral[3]
    vulnerability = 1.0 - state.x_ext[0]
    raw = COMPASSION_ALPHA * E + COMPASSION_BETA * vulnerability - COMPASSION_GAMMA * R
    return _sigmoid(2.0 * (raw - 0.5))


def evaluate_moral(state: State, a: List[float]) -> MoralScores:
    """Tek aksiyon için W, J, H, C hesaplar."""
    return MoralScores(
        W=compute_wellbeing(state, a),
        J=compute_justice(state, a),
        H=compute_harm(state, a),
        C=compute_compassion(state, a),
    )
