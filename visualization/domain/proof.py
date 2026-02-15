# Proof Pack: Offline (traces only) vs Online (engine gerekir).
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from visualization.domain.metrics import compute_level_counts, compute_clamp_stats, compute_latency_percentiles


def _hash_digest(obj: Any) -> str:
    """Deterministik hash: SHA256(canonical JSON)."""
    try:
        blob = json.dumps(obj, sort_keys=True, default=str)
    except (TypeError, ValueError):
        blob = repr(obj)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def compute_offline_proof_pack(
    traces: List[Dict[str, Any]],
    trace_service: Any = None,
    goal_levels: Optional[List[int]] = None,
    csv_columns_expected: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Offline kanıtlar: trace verisiyle hesaplanır (engine çağrısı yok).
    clamp, escalation_coverage, rate_health, export_contract.
    """
    try:
        from visualization.services.trace_service import get_trace_service, CSV_COLUMNS
    except ImportError:
        CSV_COLUMNS = []
        get_trace_service = None
    trace_svc = trace_service or (get_trace_service() if get_trace_service else None)
    csv_columns_expected = csv_columns_expected or CSV_COLUMNS
    goal_levels = goal_levels or [0, 1, 2]
    valid = [t for t in traces if "error" not in t]

    clamp_stats = compute_clamp_stats(traces)
    clamp: Dict[str, Any] = {
        "pass": True,
        "detail": f"changed={clamp_stats['changed_count']}/{clamp_stats['clamp_count']}, mean_l2={clamp_stats['mean_l2']:.4f}",
        "changed_count": clamp_stats["changed_count"],
        "changed_ratio": clamp_stats["changed_ratio"],
        "mean_l2": clamp_stats["mean_l2"],
    }

    level_counts = compute_level_counts(traces)
    coverage_achieved = all(level_counts.get(lv, 0) >= 1 for lv in goal_levels)
    escalation: Dict[str, Any] = {
        "pass": coverage_achieved,
        "detail": f"L0={level_counts.get(0,0)} L1={level_counts.get(1,0)} L2={level_counts.get(2,0)}",
        "level_counts": level_counts,
        "coverage_achieved": coverage_achieved,
    }

    lat = compute_latency_percentiles(traces)
    schema_ok = True
    if trace_svc:
        ver = trace_svc.get_trace_version()
        for t in valid[:20]:
            ok, _ = trace_svc.validate_schema(t, expected_version=ver)
            if not ok:
                schema_ok = False
                break
    if not lat.get("has_latency_data"):
        lat_detail = "NO_LATENCY_DATA" if (lat.get("n") or 0) == 0 else "N/A (need ≥2 samples)"
        rate_health = {
            "pass": schema_ok,
            "detail": f"p95/p99={lat_detail} schema={'OK' if schema_ok else 'FAIL'}",
            "p95": None,
            "p99": None,
            "schema_valid": schema_ok,
            "has_latency_data": False,
        }
    else:
        p95, p99 = lat.get("p95"), lat.get("p99")
        rate_health = {
            "pass": schema_ok,
            "detail": f"p95={p95:.2f}ms p99={p99:.2f}ms schema={'OK' if schema_ok else 'FAIL'}",
            "p95": p95,
            "p99": p99,
            "schema_valid": schema_ok,
            "has_latency_data": True,
        }

    header_ok = False
    row_count = 0
    if trace_svc and valid:
        csv_str = trace_svc.traces_to_csv_string(valid)
        lines = csv_str.strip().replace("\r", "").split("\n")
        if lines:
            first_line = lines[0].strip()
            expected_header = ",".join(csv_columns_expected)
            header_ok = first_line == expected_header
        row_count = len(lines) - 1 if lines else 0
    export_contract: Dict[str, Any] = {
        "pass": header_ok and row_count == len(valid),
        "detail": f"header={'OK' if header_ok else 'MISMATCH'} rows={row_count} expected={len(valid)}",
        "csv_rows": row_count,
        "expected_rows": len(valid),
        "header_match": header_ok,
    }

    return {
        "clamp": clamp,
        "escalation_coverage": escalation,
        "rate_health": rate_health,
        "export_contract": export_contract,
    }


def compute_online_proof_pack(
    engine_service: Any,
    trace_service: Any = None,
    scenario_service: Any = None,
    seed: int = 42,
    n_determinism: int = 5,
) -> Dict[str, Dict[str, Any]]:
    """
    Online kanıtlar: tek canonical case (sabit state + config + seed). state_hash, trace_hash, result_hash;
    determinism = aynı input → aynı result_hash; replay PASS = result_hash exact match.
    """
    trace_svc = trace_service
    scenario_svc = scenario_service
    try:
        if trace_svc is None:
            from visualization.services.trace_service import get_trace_service
            trace_svc = get_trace_service()
        if scenario_svc is None:
            from visualization.services.scenario_service import get_scenario_service
            scenario_svc = get_scenario_service()
    except ImportError:
        pass

    determinism: Dict[str, Any] = {"pass": None, "detail": "Online proof not run.", "mismatch_id": None}
    replay: Dict[str, Any] = {
        "pass": None,
        "detail": "Online proof not run.",
        "failed_ids": [],
        "state_hash": None,
        "trace_hash": None,
        "result_hash": None,
    }

    if not scenario_svc or not trace_svc:
        return {"determinism": determinism, "replay": replay}

    # Canonical case: sabit state + sabit config + sabit seed (tek kaynak)
    canonical_state = scenario_svc.generate_states(1, state_profile="balanced", seed=seed)[0]
    state_hash = _hash_digest(canonical_state)

    # Determinism: aynı state+seed ile 2 run → aynı result_hash
    try:
        r1 = engine_service.decide_step(canonical_state, profile="scenario_test", deterministic=True, seed=seed)
        r2 = engine_service.decide_step(canonical_state, profile="scenario_test", deterministic=True, seed=seed)
        h1 = _hash_digest({"action": r1.get("action")})
        h2 = _hash_digest({"action": r2.get("action")})
        determinism["pass"] = h1 == h2
        determinism["detail"] = f"seed={seed} 2 runs; result_hash match=%s" % (h1 == h2)
        determinism["mismatch_id"] = None if h1 == h2 else "hash_mismatch"
    except Exception as e:
        determinism["pass"] = False
        determinism["detail"] = str(e)

    # Replay: decide → trace → replay_step; PASS = result_hash exact match
    try:
        result = engine_service.decide_step(canonical_state, profile="scenario_test", deterministic=True, seed=seed)
        full_trace = result.get("trace")
        trace_hash = result.get("trace_hash") or (_hash_digest(full_trace) if full_trace else None)
        result_hash = _hash_digest({"action": result.get("action")})
        replay["state_hash"] = state_hash
        replay["trace_hash"] = trace_hash
        replay["result_hash"] = result_hash

        if full_trace:
            replayed = engine_service.replay_step(full_trace, validate=True)
            replayed_hash = _hash_digest({"action": replayed.get("action")})
            replay["pass"] = replayed_hash == result_hash
            replay["detail"] = "Replay result_hash exact match." if replay["pass"] else "Replay result_hash mismatch."
        else:
            replay["pass"] = False
            replay["detail"] = "No trace in result."
    except Exception as e:
        replay["pass"] = False
        replay["detail"] = str(e)

    return {"determinism": determinism, "replay": replay}


def compute_proof_pack(
    traces: List[Dict[str, Any]],
    engine_service: Any = None,
    trace_service: Any = None,
    goal_levels: Optional[List[int]] = None,
    trace_version_expected: str = "1.0",
    csv_columns_expected: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Tüm kartlar: offline her zaman; determinism/replay offline'da NA (Run Online Proof ile doldurulur).
    Geriye uyumluluk için compute_offline_proof_pack + determinism/replay placeholder.
    """
    offline = compute_offline_proof_pack(traces, trace_service=trace_service, goal_levels=goal_levels, csv_columns_expected=csv_columns_expected)
    out = dict(offline)
    out["determinism"] = {"pass": None, "detail": "Run Online Proof to check.", "mismatch_id": None}
    out["replay"] = {"pass": None, "detail": "Run Online Proof to check.", "failed_ids": []}
    return out
