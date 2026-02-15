#!/usr/bin/env python
# MDM — Gerçek yaşama yakın canlı senaryo: rutin → stres → toparlanma.
# Motor aynı; state ve config profilleri "hikaye" oluşturacak şekilde fazlı.
# Kullanım (proje kökünden): python tools/realtime_pilot.py
# Dashboard: JSONL = traces_live.jsonl, Otomatik yenile = ON

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import moral_decision_engine
from core.trace_collector import TraceCollector, build_decision_trace
from simulation.scenario_generator import generate_batch
from tools.csv_export import append_trace_to_csv


# Fazlar: (açıklama, state_profil, config_profil, adım_sayısı)
PHASES = [
    ("Rutin (dengeli gün)", "balanced", "scenario_test", 50),
    ("Stres (dikkat / sıkı kurallar)", "safe", "production_safe", 40),
    ("Toparlanma (dengeli)", "balanced", "scenario_test", 50),
]


def run_phase(phase_name: str, profile: str, config_profile: str, steps: int,
              collector: TraceCollector, ctx: dict, csv_path: str = "",
              run_seed: int = 42,
              sleep_sec: float = 0.12, start_index: int = 0) -> int:
    """Tek faz çalıştırır; run_seed her çalıştırmada farklı olursa veri özgün olur."""
    states = generate_batch(steps, profile=profile, seed=run_seed + start_index)
    for i, state in enumerate(states):
        idx = start_index + i
        t_before = time.perf_counter()
        result = moral_decision_engine(
            state,
            context=ctx,
            config_override=config_profile if config_profile else None,
        )
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000
        entry = build_decision_trace(result, t=idx, latency_ms=latency_ms)
        collector.push(entry)
        if csv_path:
            append_trace_to_csv(csv_path, entry, idx)
        level = entry.get("level", 0)
        cus = entry.get("cus")
        cus_str = f"{cus:.3f}" if cus is not None else "—"
        print(
            f"  [{idx:03d}] {phase_name[:12]:12} L{level} "
            f"cus={cus_str} human={entry.get('human_escalation')}"
        )
        time.sleep(sleep_sec)
    return start_index + steps


def main(jsonl_path: str = "traces_live.jsonl", sleep_sec: float = 0.12):
    run_seed = int(time.time() * 1000) % (2**31)
    ctx = {"cus_history": []}
    collector = TraceCollector(max_buffer_size=2000, jsonl_path=jsonl_path)
    csv_path = jsonl_path.replace(".jsonl", ".csv")
    idx = 0
    print("--- Gercek yasam pilot: rutin -> stres -> toparlanma ---")
    print(f"Run seed: {run_seed} (her calistirmada farkli veri)")
    print(f"Cikti: {jsonl_path} + {csv_path} | Dashboard'da otomatik yenile.\n")
    for phase_name, state_prof, config_prof, steps in PHASES:
        print(f">>> {phase_name} (state={state_prof}, config={config_prof}, n={steps})")
        idx = run_phase(
            phase_name,
            state_prof,
            config_prof,
            steps,
            collector,
            ctx,
            csv_path=csv_path,
            run_seed=run_seed,
            sleep_sec=sleep_sec,
            start_index=idx,
        )
        print("")
    print(f"DONE: {idx} kayit -> {jsonl_path} + {csv_path}")


if __name__ == "__main__":
    main()
