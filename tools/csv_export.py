# MDM — Trace kayitlarini CSV olarak ekler (canli script'ler icin).
# Tek dosya: ilk cagrida header, sonra her trace icin bir satir append.

import csv
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

CSV_COLUMNS = [
    "index", "t", "cus", "delta_cus", "cus_mean", "level", "soft_clamp",
    "human_escalation", "latency_ms", "phase",
    "run_id", "batch_id", "profile_state", "config_profile", "created_at",
    "J", "H", "confidence",
    "raw_severity", "raw_intervention", "raw_compassion", "raw_delay",
    "final_severity", "final_intervention", "final_compassion", "final_delay",
]


# Eksik alanlar 0 yerine açıkça "—" (kanıt paketi tutarlılığı).
_MISSING = "—"


def _cell(val: Any) -> Any:
    """Yok/None ise —; 0 ve False korunur."""
    if val is None:
        return _MISSING
    return val


def _row_from_trace(trace: Dict[str, Any], index: int) -> list:
    raw = (trace.get("raw_action") or [0, 0, 0, 0])[:4]
    final = (trace.get("final_action") or trace.get("raw_action") or [0, 0, 0, 0])[:4]
    g = lambda k: trace.get(k)
    return [
        index,
        _cell(g("t")),
        _cell(g("cus")),
        _cell(g("delta_cus")),
        _cell(g("cus_mean")),
        _cell(g("level")),
        _cell(g("soft_clamp")),
        _cell(g("human_escalation")),
        _cell(g("latency_ms")),
        _cell(g("phase")),
        _cell(g("run_id")),
        _cell(g("batch_id")),
        _cell(g("profile_state")),
        _cell(g("config_profile")),
        _cell(g("created_at")),
        _cell(g("J")),
        _cell(g("H")),
        _cell(g("confidence")),
        raw[0] if len(raw) > 0 else _MISSING,
        raw[1] if len(raw) > 1 else _MISSING,
        raw[2] if len(raw) > 2 else _MISSING,
        raw[3] if len(raw) > 3 else _MISSING,
        final[0] if len(final) > 0 else _MISSING,
        final[1] if len(final) > 1 else _MISSING,
        final[2] if len(final) > 2 else _MISSING,
        final[3] if len(final) > 3 else _MISSING,
    ]


def append_trace_to_csv(csv_path: str, trace: Dict[str, Any], index: int) -> None:
    """Trace'i CSV dosyasina ekler; dosya yoksa header yazar (UTF-8)."""
    p = Path(csv_path)
    write_header = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",")
        if write_header:
            w.writerow(CSV_COLUMNS)
        w.writerow(_row_from_trace(trace, index))


def traces_to_csv_string(traces: List[Dict[str, Any]]) -> str:
    """Mevcut trace listesini CSV metni olarak dondurur (dashboard indirme icin)."""
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=",")
    w.writerow(CSV_COLUMNS)
    for i, trace in enumerate(traces):
        w.writerow(_row_from_trace(trace, i))
    return buf.getvalue()
