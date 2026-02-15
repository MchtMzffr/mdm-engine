# Phase 6.0 — Offline bir adım: state seti + aday config'ler → en iyi config ve L

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.trace_collector import build_decision_trace
from engine import moral_decision_engine
from learning.feedback_metrics import compute_metrics
from learning.loss import compute_loss, DEFAULT_WEIGHTS
from learning.policy_optimizer import PARAM_BOUNDS


def run_engine_on_states(
    states: List[Dict[str, Any]],
    config_override: Dict[str, Any],
    use_context: bool = True,
) -> List[Dict[str, Any]]:
    """
    Verilen state listesi üzerinde engine'i config_override ile çalıştırır;
    her karar için DecisionTrace üretir, listeyi döndürür.
    """
    traces = []
    context = {"cus_history": []} if use_context else None
    for state in states:
        result = moral_decision_engine(
            state,
            context=context,
            config_override=config_override,
        )
        entry = build_decision_trace(result)
        traces.append(entry)
    return traces


def run_offline_step(
    states: List[Dict[str, Any]],
    current_config: Dict[str, Any],
    candidate_configs: Optional[List[Dict[str, Any]]] = None,
    weights: tuple = DEFAULT_WEIGHTS,
    base_config: Optional[Dict[str, Any]] = None,
) -> Tuple[Dict[str, Any], float, Dict[str, float]]:
    """
    Tüm aday config'ler (veya sadece current_config) için engine çalıştırır,
    trace'lerden L hesaplar; en düşük L'ye sahip config'i döndürür.
    base_config verilirse her aday onunla birleştirilir (J_CRITICAL, H_CRITICAL vb. sabit kalır).

    Returns:
        (best_config, best_L, best_metrics)
    """
    if not states:
        return current_config, compute_loss(compute_metrics([]), weights), {}

    configs_to_try = candidate_configs if candidate_configs else [current_config]
    best_config = current_config
    best_L = float("inf")
    best_metrics = {}

    for config in configs_to_try:
        effective = {**(base_config or {}), **config}
        traces = run_engine_on_states(states, effective, use_context=True)
        metrics = compute_metrics(traces)
        L = compute_loss(metrics, weights)
        if L < best_L:
            best_L = L
            best_config = config
            best_metrics = metrics

    return best_config, best_L, best_metrics
