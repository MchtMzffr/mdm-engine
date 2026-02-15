# MDM Phase 5 — Temporal Drift Monitor.
# ΔCUS ve CUS_mean ile preemptive escalation.

from dataclasses import dataclass
from typing import List


@dataclass
class DriftResult:
    delta_cus: float | None
    cus_mean: float
    preemptive_escalation: bool


def update_cus_history(history: List[float], cus: float, window_size: int) -> List[float]:
    """Yeni CUS ekler, en fazla window_size eleman döndürür."""
    new_list = list(history) + [float(cus)]
    return new_list[-window_size:] if window_size > 0 else new_list


def compute_temporal_drift(
    cus: float,
    history: List[float],
    delta_threshold: float,
    mean_threshold: float,
) -> DriftResult:
    """
    history: güncel CUS eklenmiş liste (update_cus_history sonrası).
    delta_cus = cus - previous_cus (history'de en az 2 eleman varsa).
    preemptive_escalation = (delta_cus > delta_threshold) or (cus_mean > mean_threshold).
    """
    cus_mean = sum(history) / len(history) if history else cus
    if len(history) >= 2:
        delta_cus = cus - history[-2]
    else:
        delta_cus = None

    preemptive = False
    if delta_cus is not None and delta_cus > delta_threshold:
        preemptive = True
    if cus_mean > mean_threshold:
        preemptive = True

    return DriftResult(
        delta_cus=delta_cus,
        cus_mean=cus_mean,
        preemptive_escalation=preemptive,
    )


def should_preemptively_escalate(
    drift_result: DriftResult,
    *,
    history_len: int = 999,
    min_history: int = 0,
) -> bool:
    """Warmup: history_len < min_history ise preemptive devreye girmez."""
    if history_len < min_history:
        return False
    return drift_result.preemptive_escalation
