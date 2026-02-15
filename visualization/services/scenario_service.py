# ScenarioService: state batch + run_until_coverage (L0/L1/L2 hedefe kadar koşma).
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from visualization.services.engine_service import get_engine_service
from visualization.services.trace_service import get_trace_service


def get_scenario_service() -> ScenarioService:
    return ScenarioService(engine=get_engine_service(), trace_svc=get_trace_service())


class ScenarioService:
    def __init__(
        self,
        engine: Any = None,
        trace_svc: Any = None,
    ) -> None:
        self._engine = engine or get_engine_service()
        self._trace_svc = trace_svc or get_trace_service()
        self._generate_batch = None

    def _lazy_generator(self):
        if self._generate_batch is None:
            from visualization._imports import get_generate_batch
            self._generate_batch = get_generate_batch()
        return self._generate_batch

    def generate_states(
        self,
        n: int,
        state_profile: str = "balanced",
        seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        gen = self._lazy_generator()
        return gen(n, profile=state_profile, seed=seed or 42)

    def run_batch(
        self,
        states: List[Dict[str, Any]],
        config_profile: Optional[str],
        deterministic: bool = True,
        seed: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """States üzerinde engine koşturur, trace listesi döner."""
        profile = config_profile or "scenario_test"
        context: Dict[str, Any] = {"cus_history": []}
        traces: List[Dict[str, Any]] = []
        used_seed = seed
        for i, state in enumerate(states):
            t0 = time.perf_counter()
            result = self._engine.decide_step(
                state,
                profile=profile,
                deterministic=deterministic,
                seed=used_seed,
                context=context,
            )
            latency_ms = (time.perf_counter() - t0) * 1000.0
            entry = self._trace_svc.build_trace(result, t=float(i), latency_ms=round(latency_ms, 2), seed_used=used_seed)
            traces.append(entry)
            cus = result.get("uncertainty") or {}
            cus_val = cus.get("cus")
            if cus_val is not None:
                hist = (context.get("cus_history") or [])[-99:]
                context["cus_history"] = hist + [float(cus_val)]
        return traces

    def run_until_coverage(
        self,
        goal_levels: Tuple[int, ...] = (0, 1, 2),
        max_states: int = 500,
        seed: int = 42,
        config_profile: Optional[str] = "scenario_test",
        state_profiles: Optional[List[str]] = None,
        batch_size: int = 50,
        goal_cells: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Hedef: level (L0/L1/L2) + isteğe bağlı hücre: soft_clamp True/False, CUS low (<0.3), CUS high (>0.7).
        goal_cells=True (Proof Mode): level + clamp both + CUS low ve high en az 1'er.
        Returns (traces, info) with level_counts, clamp_true/false, cus_low/high, coverage_achieved, stop_reason.
        """
        state_profiles = state_profiles or ["safe", "balanced", "chaos"]
        level_counts = {0: 0, 1: 0, 2: 0}
        has_clamp_true = False
        has_clamp_false = False
        has_cus_low = False   # cus < 0.3
        has_cus_high = False  # cus > 0.7
        all_traces: List[Dict[str, Any]] = []
        attempted = 0
        batch_idx = 0

        def covered() -> bool:
            level_ok = all(level_counts.get(lv, 0) >= 1 for lv in goal_levels)
            if not goal_cells:
                return level_ok
            return (
                level_ok
                and has_clamp_true
                and has_clamp_false
                and has_cus_low
                and has_cus_high
            )

        while attempted < max_states:
            n = min(batch_size, max_states - attempted)
            states: List[Dict[str, Any]] = []
            for i, sp in enumerate(state_profiles):
                n_per = max(1, n // len(state_profiles))
                gen = self._lazy_generator()
                try:
                    batch = gen(n_per, profile=sp, seed=seed + batch_idx * 1000 + i)
                except Exception:
                    batch = gen(n_per, seed=seed + batch_idx * 1000 + i)
                states.extend(batch)

            traces = self.run_batch(states, config_profile=config_profile, deterministic=True, seed=seed)
            for t in traces:
                if "error" in t:
                    continue
                lv = t.get("level", 0)
                level_counts[lv] = level_counts.get(lv, 0) + 1
                if t.get("soft_clamp"):
                    has_clamp_true = True
                else:
                    has_clamp_false = True
                cus = float(t.get("cus", 0))
                if cus < 0.3:
                    has_cus_low = True
                if cus > 0.7:
                    has_cus_high = True
            all_traces.extend(traces)
            attempted += len(states)
            if covered():
                break
            batch_idx += 1

        stop_reason = "coverage_achieved" if covered() else "max_states"
        coverage_spec_version = "1.0"
        n_levels = len(goal_levels)
        n_clamp = 2
        n_cus_bin = 2
        coverage_cells_total = n_levels * n_clamp * n_cus_bin
        info = {
            "level_counts": dict(level_counts),
            "has_clamp_true": has_clamp_true,
            "has_clamp_false": has_clamp_false,
            "has_cus_low": has_cus_low,
            "has_cus_high": has_cus_high,
            "coverage_achieved": covered(),
            "attempted_states": attempted,
            "stop_reason": stop_reason,
            "run_id": uuid.uuid4().hex[:12],
            "trace_version": self._trace_svc.get_trace_version(),
            "config_profile": config_profile or "scenario_test",
            "coverage_spec_version": coverage_spec_version,
            "coverage_cells": f"level({n_levels}) × clamp({n_clamp}) × cus_bin({n_cus_bin}) = {coverage_cells_total}",
            "cus_thresholds": "CUS low < 0.30, high > 0.70",
        }
        return all_traces, info
