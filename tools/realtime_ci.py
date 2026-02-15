#!/usr/bin/env python
"""
MDM — CI/CD için optimize edilmiş canlı trace testi
Kısa süreli (30-60 saniye) test için tasarlandı.
"""

import sys
import time
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdm_engine import decide
from core.trace_collector import TraceCollector, build_decision_trace


def random_state():
    """Rastgele state üretir."""
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
        "severity": random.random(),
    }


def main(steps=30, sleep_sec=1.0, profile="scenario_test", jsonl_path="traces_live.jsonl"):
    """
    CI/CD için optimize edilmiş canlı trace testi.
    
    Args:
        steps: Üretilecek trace sayısı (default: 30)
        sleep_sec: Her trace arası bekleme (default: 1.0s)
        profile: Config profile (default: scenario_test)
        jsonl_path: Çıktı dosyası (default: traces_live.jsonl)
    """
    # Clear existing file for clean test
    jsonl_file = Path(jsonl_path)
    if jsonl_file.exists():
        jsonl_file.write_text("", encoding="utf-8")
    
    ctx = {"cus_history": []}
    collector = TraceCollector(max_buffer_size=1000, jsonl_path=jsonl_path)
    
    print(f"Generating {steps} live traces...")
    print(f"Output: {jsonl_path}")
    
    level_counts = {0: 0, 1: 0, 2: 0}
    human_escalations = 0
    
    for i in range(steps):
        state = random_state()
        t_before = time.perf_counter()
        result = decide(state, profile=profile, context=ctx)
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000
        
        entry = build_decision_trace(result, t=i, latency_ms=latency_ms)
        collector.push(entry)
        
        level = entry.get("level", 0)
        level_counts[level] = level_counts.get(level, 0) + 1
        if entry.get("human_escalation"):
            human_escalations += 1
        
        if (i + 1) % 10 == 0:
            cus = entry.get("cus", 0)
            print(
                f"  [{i+1:03d}] L{level} cus={cus:.3f} "
                f"human={entry.get('human_escalation')} "
                f"latency={latency_ms:.2f}ms"
            )
        
        time.sleep(sleep_sec)
    
    print(f"\n[OK] Generated {steps} traces")
    print(f"   Escalation levels: L0={level_counts[0]}, L1={level_counts[1]}, L2={level_counts[2]}")
    print(f"   Human escalations: {human_escalations}")
    print(f"   File: {jsonl_path}")
    
    # Validate file exists and has content
    if Path(jsonl_path).exists():
        lines = len(Path(jsonl_path).read_text(encoding="utf-8").strip().split("\n"))
        print(f"   Lines written: {lines}")
        if lines == steps:
            print("   [OK] File validation passed")
            return 0
        else:
            print(f"   [FAIL] File validation failed: expected {steps}, got {lines}")
            return 1
    else:
        print(f"   [FAIL] File not found: {jsonl_path}")
        return 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CI/CD live trace test")
    parser.add_argument("--steps", type=int, default=30, help="Number of traces (default: 30)")
    parser.add_argument("--sleep", type=float, default=1.0, help="Sleep between traces in seconds (default: 1.0)")
    parser.add_argument("--profile", type=str, default="scenario_test", help="Config profile (default: scenario_test)")
    parser.add_argument("--output", type=str, default="traces_live.jsonl", help="Output JSONL file (default: traces_live.jsonl)")
    args = parser.parse_args()
    
    exit(main(steps=args.steps, sleep_sec=args.sleep, profile=args.profile, jsonl_path=args.output))
