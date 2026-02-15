# EngineService: decide + replay; dependency injection ile testte Fake kullanılır.
from __future__ import annotations

from typing import Any, Dict, Optional, Protocol

# Lazy: gerçek implementasyon get_engine_service() içinde import edilir.


class EngineService(Protocol):
    """Engine çağrıları için arayüz (testte FakeEngineService ile değiştirilebilir)."""

    def decide_step(
        self,
        state: Dict[str, Any],
        profile: Optional[str] = None,
        deterministic: bool = True,
        seed: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        ...

    def replay_step(self, trace: Any, validate: bool = True) -> Dict[str, Any]:
        ...


class RealEngineService:
    def __init__(self) -> None:
        self._decide = None
        self._replay_trace = None

    def _lazy(self) -> None:
        if self._decide is None:
            from visualization._imports import get_decide, get_replay_trace
            self._decide = get_decide()
            self._replay_trace = get_replay_trace()

    def decide_step(
        self,
        state: Dict[str, Any],
        profile: Optional[str] = None,
        deterministic: bool = True,
        seed: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._lazy()
        ctx = dict(context) if context else {}
        if seed is not None:
            ctx["seed_used"] = seed
        return self._decide(
            state,
            profile=profile or "scenario_test",
            deterministic=deterministic,
            context=ctx if ctx else context,
        )

    def replay_step(self, trace: Any, validate: bool = True) -> Dict[str, Any]:
        self._lazy()
        return self._replay_trace(trace, validate=validate)


_default_engine: Optional[EngineService] = None


def get_engine_service(override: Optional[EngineService] = None) -> EngineService:
    """Singleton engine service; testte override ile Fake verilir."""
    global _default_engine
    if override is not None:
        _default_engine = override
        return override
    if _default_engine is None:
        _default_engine = RealEngineService()
    return _default_engine
