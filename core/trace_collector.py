# MDM Phase 4.7.1 — Trace Collector (Observability Core).
# Unified decision trace, ring buffer, JSONL; Phase 6 + dashboard hazırlık.

import json
import time
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional


def build_decision_trace(
    engine_result: Dict[str, Any],
    t: Optional[float] = None,
    chaos: bool = False,
    latency_ms: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Motor çıktısından tek bir DecisionTrace kaydı üretir.
    t: timestamp (yoksa time.time()).
    latency_ms: opsiyonel; karar süresi (ms). Caller ölçüp geçebilir (gerçek zamanlı izleme).
    """
    ts = t if t is not None else time.time()
    out = engine_result
    uncertainty = out.get("uncertainty") or {}
    temporal = out.get("temporal_drift") or {}
    self_reg = out.get("self_regulation") or {}

    cus = uncertainty.get("cus")
    cus = float(cus) if cus is not None else 0.0

    rec = {
        "t": ts,
        "cus": cus,
        "delta_cus": temporal.get("delta_cus"),
        "cus_mean": temporal.get("cus_mean", cus),
        "raw_action": list(out.get("raw_action", out.get("action", []))),
        "final_action": list(out.get("action", [])),
        "soft_clamp": out.get("soft_safe_applied", False),
        "delta_confidence": self_reg.get("delta_confidence"),
        "level": out.get("escalation", 0),
        "confidence": out.get("confidence"),
        "uncertainty": cus,
        "human_escalation": out.get("human_escalation", False),
        "chaos": chaos,
    }
    if out.get("J") is not None and out.get("H") is not None:
        rec["J"] = float(out["J"])
        rec["H"] = float(out["H"])
    if latency_ms is not None:
        rec["latency_ms"] = round(latency_ms, 2)
    return rec


class TraceCollector:
    """
    Ring buffer + isteğe bağlı JSONL. push(entry), get_recent(n), get_all(), flush_jsonl().
    """

    def __init__(
        self,
        max_buffer_size: int = 1000,
        jsonl_path: Optional[str] = None,
    ):
        self._buffer: deque = deque(maxlen=max_buffer_size)
        self._jsonl_path = Path(jsonl_path) if jsonl_path else None

    def push(self, entry: Dict[str, Any]) -> None:
        self._buffer.append(entry)
        if self._jsonl_path is not None:
            with open(self._jsonl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_recent(self, n: int) -> List[Dict[str, Any]]:
        """Son n kayıt (yeniden eskiye)."""
        buf = list(self._buffer)
        return buf[-n:] if n > 0 else []

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._buffer)

    def flush_jsonl(self, path: Optional[str] = None) -> None:
        """Mevcut buffer'ı verilen path'e (veya constructor'daki jsonl_path) yazar; append."""
        p = Path(path) if path else self._jsonl_path
        if p is None:
            return
        with open(p, "a", encoding="utf-8") as f:
            for entry in self._buffer:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def __len__(self) -> int:
        return len(self._buffer)
