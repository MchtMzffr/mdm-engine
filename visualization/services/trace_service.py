# TraceService: build_trace, schema validation (tip+aralık), CSV export (tek kaynak: tools.csv_export).
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

REQUIRED_TRACE_KEYS = [
    "t", "cus", "raw_action", "final_action", "level", "soft_clamp", "human_escalation",
]

# CSV: tek kaynak; tools.csv_export varsa oradan, yoksa yerel kopya (PyPI kurulumu).
try:
    from tools.csv_export import CSV_COLUMNS, traces_to_csv_string as _tools_traces_to_csv
    _USE_TOOLS_CSV = True
except ImportError:
    CSV_COLUMNS = [
        "index", "t", "cus", "delta_cus", "cus_mean", "level", "soft_clamp",
        "human_escalation", "latency_ms", "phase",
        "run_id", "batch_id", "profile_state", "config_profile", "created_at",
        "J", "H", "confidence",
        "raw_severity", "raw_intervention", "raw_compassion", "raw_delay",
        "final_severity", "final_intervention", "final_compassion", "final_delay",
    ]
    _USE_TOOLS_CSV = False


def get_trace_service() -> "TraceService":
    return TraceService()


class TraceService:
    def __init__(self) -> None:
        self._build_decision_trace = None
        self._trace_version = None

    def _lazy(self) -> None:
        if self._build_decision_trace is None:
            from visualization._imports import get_build_decision_trace, get_trace_version
            self._build_decision_trace = get_build_decision_trace()
            self._trace_version = get_trace_version()

    def build_trace(
        self,
        engine_result: Dict[str, Any],
        t: Optional[float] = None,
        latency_ms: Optional[float] = None,
        seed_used: Optional[int] = None,
    ) -> Dict[str, Any]:
        self._lazy()
        entry = self._build_decision_trace(engine_result, t=t, latency_ms=latency_ms)
        if seed_used is not None:
            entry["seed_used"] = seed_used
        return entry

    def get_trace_version(self) -> str:
        self._lazy()
        return self._trace_version or "1.0"

    def validate_schema(
        self,
        trace: Dict[str, Any],
        expected_version: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """
        Required alanlar + tip ve aralık: level in {0,1,2}, 0<=cus<=1,
        action len 4 ve her eleman [0,1], TRACE_VERSION, created_at sayısal ise.
        """
        errors: List[str] = []
        for k in REQUIRED_TRACE_KEYS:
            if k not in trace:
                errors.append(f"missing:{k}")
            elif k in ("raw_action", "final_action"):
                v = trace[k]
                if not isinstance(v, (list, tuple)) or len(v) != 4:
                    errors.append(f"{k}: must be list of length 4")
                else:
                    for i, x in enumerate(v):
                        try:
                            xf = float(x)
                            if not (0 <= xf <= 1):
                                errors.append(f"{k}[{i}] out of [0,1]")
                        except (TypeError, ValueError):
                            errors.append(f"{k}[{i}] not in [0,1]")
            elif k == "level":
                lv = trace[k]
                if lv not in (0, 1, 2):
                    errors.append("level not in {0,1,2}")
            elif k == "cus":
                try:
                    c = float(trace[k])
                    if not (0 <= c <= 1):
                        errors.append("cus not in [0,1]")
                except (TypeError, ValueError):
                    errors.append("cus not numeric or out of [0,1]")

        if expected_version is not None and trace.get("version") is not None:
            ver = trace.get("version")
            if str(ver) != str(expected_version):
                errors.append(f"TRACE_VERSION mismatch expected {expected_version}")

        created_at = trace.get("created_at")
        if created_at is not None and created_at != "":
            try:
                float(created_at)
            except (TypeError, ValueError):
                errors.append("created_at not numeric")

        return len(errors) == 0, errors

    def traces_to_csv_string(self, traces: List[Dict[str, Any]]) -> str:
        """Tek kaynak: tools.csv_export.traces_to_csv_string kullanılır (varsa)."""
        if _USE_TOOLS_CSV:
            return _tools_traces_to_csv(traces)
        import csv
        import io
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=",")
        w.writerow(CSV_COLUMNS)
        for i, trace in enumerate(traces):
            w.writerow(_row_from_trace(trace, i))
        return buf.getvalue()


def _row_from_trace(trace: Dict[str, Any], index: int) -> List[Any]:
    raw = (trace.get("raw_action") or [0, 0, 0, 0])[:4]
    final = (trace.get("final_action") or trace.get("raw_action") or [0, 0, 0, 0])[:4]
    return [
        index,
        trace.get("t", ""),
        trace.get("cus", ""),
        trace.get("delta_cus") if trace.get("delta_cus") is not None else "",
        trace.get("cus_mean", ""),
        trace.get("level", ""),
        trace.get("soft_clamp", ""),
        trace.get("human_escalation", ""),
        trace.get("latency_ms") if trace.get("latency_ms") is not None else "",
        trace.get("phase", ""),
        trace.get("run_id") if trace.get("run_id") is not None else "",
        trace.get("batch_id") if trace.get("batch_id") is not None else "",
        trace.get("profile_state", ""),
        trace.get("config_profile", ""),
        trace.get("created_at") if trace.get("created_at") is not None else "",
        trace.get("J") if trace.get("J") is not None else "",
        trace.get("H") if trace.get("H") is not None else "",
        trace.get("confidence") if trace.get("confidence") is not None else "",
        raw[0] if len(raw) > 0 else "",
        raw[1] if len(raw) > 1 else "",
        raw[2] if len(raw) > 2 else "",
        raw[3] if len(raw) > 3 else "",
        final[0] if len(final) > 0 else "",
        final[1] if len(final) > 1 else "",
        final[2] if len(final) > 2 else "",
        final[3] if len(final) > 3 else "",
    ]
