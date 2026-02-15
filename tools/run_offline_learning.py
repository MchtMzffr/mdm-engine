#!/usr/bin/env python
# MDM Phase 6.0 — Offline Learning: JSONL'dan L hesaplama veya bir adım optimizasyon.
# Kullanım (proje kökünden):
#   python tools/run_offline_learning.py jsonl traces.jsonl
#   python tools/run_offline_learning.py step --states 80 --candidates 5

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import config as _config
from learning.feedback_metrics import load_traces_from_jsonl, compute_metrics
from learning.loss import compute_loss, DEFAULT_WEIGHTS
from learning.policy_optimizer import suggest_candidates, PARAM_BOUNDS
from learning.offline_loop import run_offline_step


def current_config_from_module() -> dict:
    """config.py'deki Phase 6 parametrelerini dict yapar."""
    return {
        "J_MIN": _config.J_MIN,
        "H_MAX": _config.H_MAX,
        "SOFT_CLAMP_ALPHA": _config.SOFT_CLAMP_ALPHA,
        "SOFT_CLAMP_BETA": _config.SOFT_CLAMP_BETA,
        "SOFT_CLAMP_GAMMA": _config.SOFT_CLAMP_GAMMA,
        "DELTA_CUS_THRESHOLD": _config.DELTA_CUS_THRESHOLD,
        "CUS_MEAN_THRESHOLD": _config.CUS_MEAN_THRESHOLD,
    }


def cmd_jsonl(path: str) -> None:
    """Mevcut traces.jsonl'dan metrik ve L hesaplar."""
    traces = load_traces_from_jsonl(path)
    if not traces:
        print(f"Trace yok: {path}")
        return
    metrics = compute_metrics(traces)
    L = compute_loss(metrics, DEFAULT_WEIGHTS)
    print(f"Kayıt: {len(traces)}")
    print(f"fail_safe_rate: {metrics['fail_safe_rate']:.4f}")
    print(f"mean_cus:        {metrics['mean_cus']:.4f}")
    print(f"clamp_distortion:{metrics['clamp_distortion']:.4f}")
    print(f"L (loss):        {L:.4f}")


def _get_states(n: int, profile: str, seed: int):
    """State üretimi: simulation.scenario_generator (profil chaos/balanced/safe vb.)."""
    from simulation.scenario_generator import generate_batch
    return generate_batch(n, profile=profile or "chaos", seed=seed)


def cmd_step(states_n: int, candidates_n: int, seed: int, profile: str = "") -> None:
    """State seti üretir, aday config'lerle engine çalıştırır, en iyi config ve L'yi yazdırır."""
    current = current_config_from_module()
    states = _get_states(states_n, profile, seed)
    candidates = suggest_candidates(current, num_candidates=candidates_n, step_scale=0.08, seed=seed)
    candidates.insert(0, current)

    print("Offline step: state sayısı=%d, aday=%d, profil=%s" % (states_n, len(candidates), profile or "chaos"))
    best_config, best_L, best_metrics = run_offline_step(states, current, candidate_configs=candidates)
    print("En iyi L: %.4f" % best_L)
    print("Metrikler: fail_safe_rate=%.4f  mean_cus=%.4f  clamp_distortion=%.4f" % (
        best_metrics.get("fail_safe_rate", 0),
        best_metrics.get("mean_cus", 0),
        best_metrics.get("clamp_distortion", 0),
    ))
    print("Önerilen config:")
    for k in sorted(best_config.keys()):
        if k in PARAM_BOUNDS:
            print("  %s: %s" % (k, best_config[k]))


def cmd_optimize(steps: int, states: int, candidates: int, seed: int, out_path: str, profile: str = "", config_base: str = "") -> None:
    """N adım optimizasyon döngüsü çalıştırır, optimization_history.jsonl üretir."""
    from learning.run_optimization_loop import run_optimization_loop

    if config_base == "scenario_test":
        from config_profiles import get_config
        initial = get_config("scenario_test")
        base_config = {k: v for k, v in initial.items() if k not in PARAM_BOUNDS}
    else:
        initial = current_config_from_module()
        base_config = None
    state_list = _get_states(states, profile, seed)
    history = run_optimization_loop(
        initial, state_list,
        num_steps=steps,
        num_candidates=candidates,
        history_path=out_path,
        base_config=base_config,
    )
    print("Optimization tamamlandı: %d adım (profil=%s)" % (len(history), profile or "chaos"))
    print("L: %.4f -> %.4f" % (history[0]["L"], history[-1]["L"]))
    print("Kayıt: %s" % out_path)


def main():
    p = argparse.ArgumentParser(description="Phase 6.0 Offline Learning")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("jsonl", help="JSONL dosyasından L hesapla").add_argument("path", nargs="?", default="traces.jsonl")
    sp = sub.add_parser("step", help="Bir offline adım: state üret, aday config dene, en iyiyi seç")
    sp.add_argument("--states", type=int, default=80, help="State sayısı")
    sp.add_argument("--candidates", type=int, default=5, help="Aday config sayısı")
    sp.add_argument("--seed", type=int, default=42)
    sp.add_argument("--profile", default="", help="safe|balanced|critical|chaos (Phase 6.2, boş=chaos)")
    op = sub.add_parser("optimize", help="Phase 6.1: N adım döngü, optimization_history.jsonl üret")
    op.add_argument("--steps", type=int, default=5)
    op.add_argument("--states", type=int, default=50)
    op.add_argument("--candidates", type=int, default=4)
    op.add_argument("--seed", type=int, default=42)
    op.add_argument("--profile", default="balanced", help="safe|balanced|critical|chaos (Phase 6.2)")
    op.add_argument("--config-base", default="", help="scenario_test = L0/L1/L2 gorunur; bos = varsayilan")
    op.add_argument("--out", default="optimization_history.jsonl")
    args = p.parse_args()

    if args.cmd == "jsonl":
        cmd_jsonl(args.path)
    elif args.cmd == "step":
        cmd_step(args.states, args.candidates, args.seed, getattr(args, "profile", ""))
    else:
        cmd_optimize(
            args.steps, args.states, args.candidates, args.seed, args.out,
            getattr(args, "profile", "") or "balanced",
            getattr(args, "config_base", "") or "",
        )


if __name__ == "__main__":
    main()
