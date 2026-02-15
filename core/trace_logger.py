# MDM — Debug + Trace Logger (Phase 2 spec §1.7)
# Her adımda event kaydı; deterministik, denetlenebilir.

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class TraceEvent:
    step: int
    event_type: str
    data: Any


class TraceLogger:
    """Pipeline adımlarını sırayla kaydeder."""

    def __init__(self) -> None:
        self._trace: List[TraceEvent] = []

    def log(self, step: int, event_type: str, data: Any = None) -> None:
        self._trace.append(TraceEvent(step=step, event_type=event_type, data=data))

    @property
    def trace(self) -> List[TraceEvent]:
        return self._trace.copy()

    def clear(self) -> None:
        self._trace.clear()
