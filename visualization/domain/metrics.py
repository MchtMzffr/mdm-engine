# Pure metrics: level dağılımı, clamp diff, p95/p99, last-N tablo.
from __future__ import annotations

from typing import Any, Dict, List


def compute_level_counts(traces: List[Dict[str, Any]]) -> Dict[int, int]:
    counts = {0: 0, 1: 0, 2: 0}
    for t in traces:
        if "error" in t:
            continue
        lv = t.get("level", 0)
        counts[lv] = counts.get(lv, 0) + 1
    return counts


def compute_clamp_stats(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    clamped = [t for t in traces if t.get("soft_clamp") and "error" not in t]
    changed = 0
    l2_diffs: List[float] = []
    for t in clamped:
        raw = t.get("raw_action") or [0, 0, 0, 0]
        final = t.get("final_action") or raw
        raw = (raw + [0] * 4)[:4]
        final = (final + [0] * 4)[:4]
        diff_sq = sum((a - b) ** 2 for a, b in zip(raw, final))
        l2 = diff_sq ** 0.5
        l2_diffs.append(l2)
        if l2 > 1e-6:
            changed += 1
    n = len(clamped)
    return {
        "clamp_count": n,
        "changed_count": changed,
        "changed_ratio": changed / n if n else 0.0,
        "mean_l2": sum(l2_diffs) / len(l2_diffs) if l2_diffs else 0.0,
    }


def compute_latency_percentiles(traces: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Latency percentiles. Yoksa veya <2 örnekse N/A (0 göstermiyoruz)."""
    latencies = [
        float(t["latency_ms"])
        for t in traces
        if "error" not in t and t.get("latency_ms") is not None and isinstance(t.get("latency_ms"), (int, float))
    ]
    if len(latencies) < 2:
        return {
            "has_latency_data": False,
            "n": len(latencies),
            "p50": None,
            "p95": None,
            "p99": None,
        }
    s = sorted(latencies)
    n = len(s)
    return {
        "has_latency_data": True,
        "n": n,
        "p50": s[int(n * 0.5)] if n else None,
        "p95": s[min(int(n * 0.95), n - 1)] if n else None,
        "p99": s[min(int(n * 0.99), n - 1)] if n else None,
    }


def last_n_table(traces: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """Son n trace için tablo. cus yoksa/missing ise 0 yerine '—' döner."""
    valid = [t for t in traces if "error" not in t]
    last = valid[-n:] if len(valid) >= n else valid
    out = []
    for i, t in enumerate(last):
        cus_val = t.get("cus")
        cus_display = cus_val if cus_val is not None else "—"
        out.append({
            "step": i + 1,
            "level": t.get("level"),
            "cus": cus_display,
            "soft_clamp": t.get("soft_clamp"),
            "human_escalation": t.get("human_escalation"),
        })
    return out
