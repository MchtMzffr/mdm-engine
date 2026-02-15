#!/usr/bin/env python
"""
MDM (Model Oversight Engine) CLI

Usage:
    mdm dashboard          # Start Streamlit dashboard
    mdm realtime [--duration SEC] [--profile PROFILE]  # Run live test
    mdm tests              # Run test suite
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cmd_dashboard(args):
    """Start Streamlit dashboard (simplified test interface by default)."""
    import shutil
    
    # Check if streamlit is available
    streamlit_cmd = shutil.which("streamlit")
    if not streamlit_cmd:
        print("Error: Streamlit is not installed.")
        print("\nTo install the dashboard dependencies, run:")
        print('  pip install "mdm-engine[dashboard]"')
        print("\nOr install streamlit and plotly separately:")
        print("  pip install streamlit plotly")
        sys.exit(2)
    
    dashboard_path = ROOT / "visualization" / "dashboard.py"
    print("Starting MDM Test Dashboard...")
    
    if not dashboard_path.exists():
        print(f"Error: Dashboard not found at {dashboard_path}")
        sys.exit(1)
    
    cmd = ["streamlit", "run", str(dashboard_path)]
    if args.port:
        cmd.extend(["--server.port", str(args.port)])
    print(f"Dashboard: http://localhost:{args.port or 8501}")
    subprocess.run(cmd)


def cmd_realtime(args):
    """Run live test."""
    script_path = ROOT / "tools" / "realtime_10min.py"
    if not script_path.exists():
        print(f"Error: Realtime script not found at {script_path}")
        sys.exit(1)
    cmd = [sys.executable, str(script_path), "--duration", str(args.duration)]
    if args.profile:
        cmd.extend(["--profile", args.profile])
    print(f"Running live test: {args.duration}s, profile={args.profile or 'scenario_test'}")
    subprocess.run(cmd)


def cmd_tests(args):
    """Test yapısı projeden kaldırıldı. Canlı deneme için dashboard kullanın."""
    print("Test suite kaldırıldı. Canlı deneme için: mdm dashboard")
    sys.exit(0)


def cmd_demo(args):
    """Run proof-of-concept demo with validation and summary."""
    import time
    import sys
    import json
    import csv
    from pathlib import Path
    from statistics import mean
    
    # Import from repo root
    _root = Path(__file__).resolve().parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))
    
    from mdm_engine import decide, replay_trace
    from core.trace_collector import TraceCollector, build_decision_trace
    
    output_file = args.out or "traces_demo.jsonl"
    csv_file = output_file.replace(".jsonl", ".csv")
    
    # Clear existing files
    Path(output_file).write_text("", encoding="utf-8")
    Path(csv_file).write_text("", encoding="utf-8")
    
    print("=" * 60)
    print("MDM Proof-of-Concept Demo")
    print("=" * 60)
    
    collector = TraceCollector(jsonl_path=output_file)
    ctx = {"cus_history": []}
    
    # Statistics tracking
    level_counts = {0: 0, 1: 0, 2: 0}
    human_escalations = 0
    soft_clamp_count = 0
    cus_values = []
    latencies = []
    traces = []
    
    # Generate sample decisions
    print(f"\nGenerating {args.steps} decisions...")
    for i in range(args.steps):
        raw_state = {
            "risk": 0.5 + (i * 0.05) % 0.5,
            "severity": 0.6 + (i * 0.03) % 0.4,
            "physical": 0.5,
            "social": 0.5,
            "context": 0.4,
            "compassion": 0.5,
            "justice": 0.9,
            "harm_sens": 0.5,
            "responsibility": 0.7,
            "empathy": 0.6,
        }
        
        t_before = time.perf_counter()
        result = decide(raw_state, profile=args.profile or "scenario_test", context=ctx)
        t_after = time.perf_counter()
        latency_ms = (t_after - t_before) * 1000
        
        trace = build_decision_trace(result, t=i, latency_ms=latency_ms)
        collector.push(trace)
        traces.append((result, trace))
        
        # Collect statistics
        level = trace.get("level", 0)
        level_counts[level] = level_counts.get(level, 0) + 1
        if trace.get("human_escalation"):
            human_escalations += 1
        if trace.get("soft_clamp"):
            soft_clamp_count += 1
        if trace.get("cus") is not None:
            cus_values.append(trace["cus"])
        if latency_ms is not None:
            latencies.append(latency_ms)
        
        if (i + 1) % 10 == 0:
            cus = trace.get("cus", 0)
            print(f"  [{i+1:03d}] L{level} cus={cus:.3f} "
                  f"human={trace.get('human_escalation', False)}")
    
    # CSV Export
    print("\nExporting CSV...")
    csv_columns = [
        "t", "level", "cus", "raw_action", "final_action", 
        "human_escalation", "soft_clamp", "confidence", "latency_ms"
    ]
    
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_columns)
        writer.writeheader()
        for _, trace in traces:
            row = {k: trace.get(k) for k in csv_columns}
            row["raw_action"] = str(row.get("raw_action", []))
            row["final_action"] = str(row.get("final_action", []))
            writer.writerow(row)
    
    # Replay Validation (sample)
    print("\nValidating replay (sample of 5 traces)...")
    replay_errors = 0
    sample_size = min(5, len(traces))
    for i in range(sample_size):
        result, trace = traces[i]
        try:
            replayed = replay_trace(result["trace"], validate=True)
            if replayed["action"] != result["action"]:
                replay_errors += 1
        except Exception as e:
            replay_errors += 1
    
    if replay_errors == 0:
        print(f"  [OK] Replay validation passed ({sample_size}/{sample_size})")
    else:
        print(f"  [WARN] Replay validation: {sample_size - replay_errors}/{sample_size} passed")
    
    # Summary
    print("\n" + "=" * 60)
    print("Run Summary")
    print("=" * 60)
    print(f"Total traces: {args.steps}")
    print("\nEscalation Levels:")
    print(f"  L0 (Normal):     {level_counts[0]:4d} ({level_counts[0]/args.steps*100:5.1f}%)")
    print(f"  L1 (Soft-safe): {level_counts[1]:4d} ({level_counts[1]/args.steps*100:5.1f}%)")
    print(f"  L2 (Fail-safe): {level_counts[2]:4d} ({level_counts[2]/args.steps*100:5.1f}%)")
    print("\nSafety Features:")
    print(f"  Human escalations: {human_escalations:4d} ({human_escalations/args.steps*100:5.1f}%)")
    print(f"  Soft clamp applied: {soft_clamp_count:4d} ({soft_clamp_count/args.steps*100:5.1f}%)")
    if cus_values:
        print("\nCUS Statistics:")
        print(f"  Mean CUS: {mean(cus_values):.3f}")
        print(f"  Min CUS:  {min(cus_values):.3f}")
        print(f"  Max CUS:  {max(cus_values):.3f}")
    if latencies:
        print("\nPerformance:")
        print(f"  Mean latency: {mean(latencies):.2f} ms")
        print(f"  Max latency:  {max(latencies):.2f} ms")
    
    print("\nOutput Files:")
    print(f"  JSONL: {output_file}")
    print(f"  CSV:   {csv_file}")
    print("\nNext Steps:")
    print("  1. View traces: mdm dashboard")
    print(f"  2. Load file: {output_file}")
    print(f"  3. Analyze CSV: {csv_file}")


def main():
    parser = argparse.ArgumentParser(
        description="MDM (Model Oversight Engine) CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__ + "\n\nUsage Policy: See USAGE_POLICY.md for guidelines and prohibited uses.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Dashboard command
    dash_parser = subparsers.add_parser("dashboard", help="Start Streamlit dashboard (simplified test interface)")
    dash_parser.add_argument("--port", type=int, help="Port number (default: 8501)")
    dash_parser.set_defaults(func=cmd_dashboard)

    # Realtime command
    realtime_parser = subparsers.add_parser("realtime", help="Run live test")
    realtime_parser.add_argument(
        "--duration", type=int, default=600, help="Test duration in seconds (default: 600)"
    )
    realtime_parser.add_argument(
        "--profile",
        type=str,
        help="Config profile (default: scenario_test)",
    )
    realtime_parser.set_defaults(func=cmd_realtime)

    # Tests command
    tests_parser = subparsers.add_parser("tests", help="Run test suite")
    tests_parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    tests_parser.set_defaults(func=cmd_tests)

    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run proof-of-concept demo with validation")
    demo_parser.add_argument(
        "--steps", type=int, default=30, help="Number of decisions to generate (default: 30)"
    )
    demo_parser.add_argument(
        "--profile",
        type=str,
        help="Config profile (default: scenario_test)",
    )
    demo_parser.add_argument(
        "--out",
        type=str,
        help="Output JSONL file (default: traces_demo.jsonl)",
    )
    demo_parser.set_defaults(func=cmd_demo)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
