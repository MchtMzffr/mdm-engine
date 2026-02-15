#!/usr/bin/env python
# MDM — Gerçek zamanlı doğrulama: canlı trace akışı üretir, traces_live.jsonl yazar.
# Kullanım (proje kökünden): python tools/realtime_smoke.py
# Dashboard: Data source = JSONL, file = traces_live.jsonl, Auto refresh = ON

import sys
import time
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import moral_decision_engine
from core.trace_collector import TraceCollector, build_decision_trace
from tools.csv_export import append_trace_to_csv


def random_state():
    return {
        "physical": random.random(),
        "social": random.random(),
        "context": random.random(),
        "risk": random.random(),
        "compassion": random.random(),
        "justice": random.random(),
        "harm_sens": random.random(),
        "responsibility": random.random(),
        "empathy": random.random(),
    }


def main(steps=200, sleep_sec=0.15, profile="scenario_test", jsonl_path="traces_live.jsonl"):
    ctx = {"cus_history": []}
    collector = TraceCollector(max_buffer_size=2000, jsonl_path=jsonl_path)
    csv_path = jsonl_path.replace(".jsonl", ".csv")

    for i in range(steps):
        state = random_state()
        t_before = time.perf_counter()
        result = moral_decision_engine(state, context=ctx, config_override=profile)
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000
        entry = build_decision_trace(result, t=i, latency_ms=latency_ms)
        collector.push(entry)
        append_trace_to_csv(csv_path, entry, i)

        cus = entry.get("cus")
        cus_str = f"{cus:.3f}" if cus is not None else "—"
        print(
            f"[{i:03d}] level={entry.get('level')} "
            f"cus={cus_str} "
            f"delta_cus={entry.get('delta_cus')} "
            f"soft_clamp={entry.get('soft_clamp')} "
            f"human={entry.get('human_escalation')}"
        )

        time.sleep(sleep_sec)

    print(f"DONE: {jsonl_path} + {csv_path} yazildi.")


if __name__ == "__main__":
    main()
