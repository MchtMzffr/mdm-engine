# Phase 6.1 — N adım optimizasyon döngüsü, history üretimi ve JSONL kaydı
# Phase 6.3 — Curriculum: epoch’a göre easy/medium/hard state üretimi

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from learning.offline_loop import run_offline_step
from learning.loss import compute_loss
from learning.policy_optimizer import PARAM_BOUNDS, suggest_candidates

# History kaydında tutulacak parametre anahtarları
HISTORY_PARAM_KEYS = [
    "J_MIN", "H_MAX", "SOFT_CLAMP_ALPHA", "SOFT_CLAMP_BETA", "SOFT_CLAMP_GAMMA",
    "DELTA_CUS_THRESHOLD", "CUS_MEAN_THRESHOLD",
]


def _history_record(
    step: int,
    config: Dict[str, Any],
    L: float,
    metrics: Dict[str, float],
    safety_gate_passed: Optional[bool] = None,
) -> Dict[str, Any]:
    """Tek bir epoch kaydı: step, L, metrikler, config (düz), isteğe bağlı safety_gate."""
    out = {
        "step": step,
        "L": round(L, 4),
        "fail_safe_rate": round(metrics.get("fail_safe_rate", 0), 4),
        "mean_cus": round(metrics.get("mean_cus", 0), 4),
        "clamp_distortion": round(metrics.get("clamp_distortion", 0), 4),
    }
    if metrics.get("non_fail_reward") is not None:
        out["non_fail_reward"] = round(metrics["non_fail_reward"], 4)
    if safety_gate_passed is not None:
        out["safety_gate"] = "PASS" if safety_gate_passed else "BLOCKED"
    for k in HISTORY_PARAM_KEYS:
        if k in config:
            out[k] = round(config[k], 4) if isinstance(config[k], (int, float)) else config[k]
    return out


def run_optimization_loop(
    initial_config: Dict[str, Any],
    states: List[Dict[str, Any]],
    num_steps: int = 5,
    num_candidates: int = 4,
    step_scale: float = 0.08,
    seed: int = 42,
    history_path: Optional[str] = None,
    base_config: Optional[Dict[str, Any]] = None,
    curriculum_schedule: Optional[List[Tuple[Optional[int], str]]] = None,
    states_per_step: int = 50,
    use_safety_gate: bool = True,
) -> List[Dict[str, Any]]:
    """
    num_steps adım optimizasyon: her adımda aday config'ler dene, en iyi config ile devam et.
    base_config verilirse (örn. scenario_test) engine her adayda onunla birleşik config kullanır.
    curriculum_schedule verilirse her adımda states_per_step state, get_curriculum_profile_for_step(step)
    ile üretilir; aksi halde verilen states listesi kullanılır.
    use_safety_gate=True: en iyi aday safety_gate'ten geçmezse mevcut config korunur.
    Returns: history (her eleman _history_record formatında).
    """
    from learning.safety_gate import safety_gate
    from simulation.scenario_generator import generate_batch, get_curriculum_profile_for_step

    history = []
    current = dict(initial_config)
    base = dict(base_config) if base_config else None
    for step in range(num_steps):
        if curriculum_schedule is not None:
            profile = get_curriculum_profile_for_step(step, curriculum_schedule)
            step_states = generate_batch(states_per_step, profile=profile, seed=seed + step)
        else:
            step_states = states
        candidates = suggest_candidates(current, num_candidates=num_candidates, step_scale=step_scale, seed=seed + step)
        candidates.insert(0, current)
        best_config, best_L, best_metrics = run_offline_step(
            step_states, current, candidate_configs=candidates, base_config=base
        )
        gate_ok = True
        if use_safety_gate:
            gate_ok, _ = safety_gate(best_metrics)
            if not gate_ok:
                best_config = current
                _, best_L, best_metrics = run_offline_step(step_states, current, base_config=base)
        rec = _history_record(step, best_config, best_L, best_metrics, safety_gate_passed=gate_ok if use_safety_gate else None)
        history.append(rec)
        current = best_config

    if history_path:
        p = Path(history_path)
        with open(p, "w", encoding="utf-8") as f:
            for rec in history:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return history
