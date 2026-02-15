#!/usr/bin/env python
# MDM — 3 canli demo: Rutin Hayat (L0) | Gri Alan (L1) | Kriz (L2)
# Ayni model, uc farkli davranis — insana anlatmak icin.
# Kullanım: python tools/realtime_demos.py
# Dashboard: traces_live.jsonl + Otomatik yenile

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


# A: Rutin Hayat — J yuksek, H dusuk, risk dusuk -> L0 agirlikli
# B: Gri Alan  — J orta, H orta, belirsizlik -> L1, soft clamp gorunur
# C: Kriz      — kaos/kritik -> L2, human escalation
DEMO_PHASES = [
    ("Rutin Hayat (L0 agirlikli)", "easy", "scenario_test", 70),
    ("Gri Alan (L1 karisik)", "medium", "scenario_test", 70),
    ("Kriz (L2 guvenlik)", "chaos", "production_safe", 70),
]


def run_demo_phase(phase_name: str, state_profile: str, config_profile: str, steps: int,
                   collector: TraceCollector, ctx: dict, phase_tag: str,
                   csv_path: str = "", run_seed: int = 42,
                   sleep_sec: float = 0.12, start_index: int = 0) -> int:
    """run_seed her calistirmada farkli olursa her deneme ozgun veri uretir."""
    states = generate_batch(steps, profile=state_profile, seed=run_seed + start_index)
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
        entry["phase"] = phase_tag
        collector.push(entry)
        if csv_path:
            append_trace_to_csv(csv_path, entry, idx)
        level = entry.get("level", 0)
        cus = entry.get("cus")
        cus_str = f"{cus:.3f}" if cus is not None else "-"
        print(
            f"  [{idx:03d}] {phase_name[:18]:18} L{level} "
            f"cus={cus_str} clamp={entry.get('soft_clamp')} human={entry.get('human_escalation')}"
        )
        time.sleep(sleep_sec)
    return start_index + steps


def main(jsonl_path: str = "traces_live.jsonl", sleep_sec: float = 0.12):
    run_seed = int(time.time() * 1000) % (2**31)
    ctx = {"cus_history": []}
    collector = TraceCollector(max_buffer_size=500, jsonl_path=jsonl_path)
    csv_path = jsonl_path.replace(".jsonl", ".csv")
    idx = 0
    print("--- 3 demo: Rutin Hayat | Gri Alan | Kriz ---")
    print(f"Run seed: {run_seed} (her calistirmada farkli veri)")
    print(f"Cikti: {jsonl_path} + {csv_path} | Dashboard'da otomatik yenile.\n")
    tags = ["rutin", "gri", "kriz"]
    for (phase_name, state_prof, config_prof, steps), tag in zip(DEMO_PHASES, tags):
        print(f">>> {phase_name} (state={state_prof}, config={config_prof}, n={steps})")
        idx = run_demo_phase(
            phase_name,
            state_prof,
            config_prof,
            steps,
            collector,
            ctx,
            phase_tag=tag,
            csv_path=csv_path,
            run_seed=run_seed,
            sleep_sec=sleep_sec,
            start_index=idx,
        )
        print("")
    print(f"DONE: {idx} kayit -> {jsonl_path} + {csv_path}")


if __name__ == "__main__":
    main()
