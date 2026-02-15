#!/usr/bin/env python
"""
MDM Trace Collection Example

Demonstrates how to collect and save decision traces for analysis.
"""

from mdm_engine import decide
from core.trace_collector import TraceCollector, build_decision_trace
import time


def main():
    print("=" * 60)
    print("MDM Trace Collection Example")
    print("=" * 60)

    # Create trace collector
    collector = TraceCollector(jsonl_path="examples_traces.jsonl")

    # Generate multiple decisions
    print(f"\nGenerating 10 decisions...")
    for i in range(10):
        # Create varying states
        raw_state = {
            "risk": 0.5 + (i * 0.05),
            "severity": 0.6 + (i * 0.03),
            "physical": 0.5,
            "social": 0.5,
            "context": 0.4,
            "compassion": 0.5,
            "justice": 0.9,
            "harm_sens": 0.5,
            "responsibility": 0.7,
            "empathy": 0.6,
        }

        # Make decision
        t_before = time.perf_counter()
        result = decide(raw_state, profile="scenario_test")
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000

        # Build trace and collect
        trace = build_decision_trace(result, t=i, latency_ms=latency_ms)
        collector.push(trace)

        print(f"  [{i:02d}] L{trace['level']} action={trace['final_action']} "
              f"latency={latency_ms:.2f}ms")

    # Close collector (flushes to file)
    collector.close()

    print(f"\n✅ Collected {len(collector.buffer)} traces")
    print(f"   Saved to: {collector.jsonl_path}")
    print(f"\nNext steps:")
    print(f"  1. View traces: mdm dashboard")
    print(f"  2. Load traces: from learning.feedback_metrics import load_traces_from_jsonl")
    print(f"  3. Analyze: Check examples_traces.jsonl")


if __name__ == "__main__":
    main()
