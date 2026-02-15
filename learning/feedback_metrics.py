# Phase 6.0 — Trace'lerden metrik üretimi (fail_safe_rate, mean_cus, clamp_distortion)

import json
from pathlib import Path
from typing import Any, Dict, List


def load_traces_from_jsonl(path: str) -> List[Dict[str, Any]]:
    """JSONL dosyasından DecisionTrace listesi yükler."""
    traces = []
    p = Path(path)
    if not p.exists():
        return traces
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                traces.append(json.loads(line))
            except Exception:
                continue
    return traces


def compute_metrics(traces: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Trace listesinden Phase 6 loss bileşenlerini hesaplar.
    - fail_safe_rate: level == 2 oranı (0–1)
    - mean_cus: cus ortalaması (0–1)
    - clamp_distortion: soft_clamp uygulanan kayıtlarda |final - raw| L1 ortalaması, tüm kayda normalize
    """
    if not traces:
        return {"fail_safe_rate": 0.0, "mean_cus": 0.0, "clamp_distortion": 0.0, "non_fail_reward": 0.0}

    n = len(traces)
    fail_safe_count = sum(1 for e in traces if e.get("level") == 2)
    fail_safe_rate = fail_safe_count / n

    cus_vals = [e.get("cus", 0) for e in traces]
    mean_cus = sum(cus_vals) / n if cus_vals else 0.0

    distortions = []
    for e in traces:
        if not e.get("soft_clamp"):
            continue
        raw = e.get("raw_action") or [0, 0, 0, 0]
        final = e.get("final_action") or raw
        raw = list(raw)[:4]
        final = list(final)[:4]
        diff = sum(abs(f - r) for f, r in zip(final, raw)) / max(len(raw), 1)
        distortions.append(min(1.0, diff))
    clamp_distortion = sum(distortions) / n if n else 0.0

    # Phase 6.3 — non_fail_reward: L0→1, L1→0.5, L2→0; ortalama = mean(1 - level/2)
    levels = [e.get("level", 2) for e in traces]
    non_fail_reward = sum(1.0 - (lv / 2.0) for lv in levels) / n if n else 0.0

    return {
        "fail_safe_rate": fail_safe_rate,
        "mean_cus": mean_cus,
        "clamp_distortion": clamp_distortion,
        "non_fail_reward": non_fail_reward,
    }
