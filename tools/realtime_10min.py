#!/usr/bin/env python
# MDM — Canli test: her ~10 saniyede 10 trace, L0/L1/L2 karisik.
# Baslangicta traces_live.jsonl ve traces_live.csv silinir; dashboard sifirdan izler.
# Kullanım: python tools/realtime_10min.py [--duration SEC]
#   --duration 90  → 90 saniye (Deney 1 için), 600 = 10 dk (varsayilan).

import argparse
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import moral_decision_engine
from core.trace_collector import TraceCollector, build_decision_trace
from simulation.scenario_generator import generate_batch
from tools.csv_export import append_trace_to_csv, CSV_COLUMNS

BATCH_SIZE = 10
INTERVAL_SEC = 10
DEFAULT_DURATION_SEC = 10 * 60  # 10 dakika
PROFILES = ["easy", "medium", "chaos"]
CONFIG = "scenario_test"


def clear_live_files(jsonl_path: str, csv_path: str) -> None:
    """Onceki veriyi siler; dashboard sifirdan baslar."""
    for p in (jsonl_path, csv_path):
        Path(p).write_text("", encoding="utf-8")


def run_batch(collector: TraceCollector, ctx: dict, csv_path: str,
              start_index: int, run_seed: int, profile: str,
              run_id: int, batch_id: int) -> int:
    """10 trace uretir; run_id, batch_id, profile_state, config_profile, created_at ekler."""
    states = generate_batch(BATCH_SIZE, profile=profile, seed=run_seed + start_index)
    for i, state in enumerate(states):
        idx = start_index + i
        t_before = time.perf_counter()
        result = moral_decision_engine(
            state,
            context=ctx,
            config_override=CONFIG,
        )
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000
        entry = build_decision_trace(result, t=idx, latency_ms=latency_ms)
        entry["phase"] = profile
        entry["run_id"] = run_id
        entry["batch_id"] = batch_id
        entry["profile_state"] = profile
        entry["config_profile"] = CONFIG
        entry["created_at"] = time.time()
        collector.push(entry)
        append_trace_to_csv(csv_path, entry, idx)
    return start_index + BATCH_SIZE


def main(jsonl_path: str = "traces_live.jsonl", duration_sec: int = DEFAULT_DURATION_SEC):
    csv_path = jsonl_path.replace(".jsonl", ".csv")
    clear_live_files(jsonl_path, csv_path)

    run_id = int(time.time() * 1000)
    run_seed = run_id % (2**31)
    ctx = {"cus_history": []}
    collector = TraceCollector(max_buffer_size=5000, jsonl_path=jsonl_path)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        import csv
        csv.writer(f, delimiter=",").writerow(CSV_COLUMNS)

    start_time = time.time()
    idx = 0
    batch_num = 0
    print(f"--- Canli test {duration_sec}s (her 10 sn'de 10 trace, L0/L1/L2 karisik) ---")
    print(f"Run ID: {run_id} | Seed: {run_seed} | Cikti: {jsonl_path} + {csv_path}")
    print("Dashboard: JSONL = traces_live.jsonl, Otomatik yenile = ON\n")

    while (time.time() - start_time) < duration_sec:
        batch_num += 1
        profile = random.choice(PROFILES)
        idx = run_batch(collector, ctx, csv_path, idx, run_seed, profile,
                        run_id=run_id, batch_id=batch_num - 1)
        elapsed = time.time() - start_time
        remaining = max(0, duration_sec - elapsed)
        print(f"  batch {batch_num}: +{BATCH_SIZE} (profile={profile}) -> toplam {idx} | kalan ~{remaining:.0f}s")
        if remaining <= 0:
            break
        time.sleep(INTERVAL_SEC)

    print(f"\nDONE: {idx} kayit -> {jsonl_path} + {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canli trace uretici (10 trace / 10s)")
    parser.add_argument("--duration", type=int, default=DEFAULT_DURATION_SEC, help="Test suresi (saniye); ornek 90, 300, 600")
    parser.add_argument("--jsonl", type=str, default="traces_live.jsonl", help="JSONL cikti dosyasi")
    args = parser.parse_args()
    main(jsonl_path=args.jsonl, duration_sec=args.duration)
