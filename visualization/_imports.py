# MDM Dashboard — tek noktadan import.
# Paket kurulumunda: yalnız mdm_engine public API. Repo-root (core/, simulation/) sadece MDM_ENGINE_DEV=1.
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Callable, List

_REPO_ROOT = Path(__file__).resolve().parents[1].parent
_loaded = False
_dev_mode = os.environ.get("MDM_ENGINE_DEV") == "1"


def _ensure_dev_path() -> None:
    """Sadece dev modda repo root'u path'e ekle."""
    if not _dev_mode:
        return
    global _loaded
    if _loaded:
        return
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))
    _loaded = True


def get_decide() -> Callable[..., Any]:
    """Her zaman mdm_engine public API."""
    if _dev_mode:
        _ensure_dev_path()
    from mdm_engine import decide
    return decide


def get_replay_trace() -> Callable[..., Any]:
    if _dev_mode:
        _ensure_dev_path()
    from mdm_engine import replay_trace
    return replay_trace


def get_build_decision_trace() -> Callable[..., Any]:
    """Dev: core.trace_collector; yoksa mdm_engine'den dene."""
    if _dev_mode:
        _ensure_dev_path()
        from core.trace_collector import build_decision_trace
        return build_decision_trace
    try:
        from mdm_engine import build_decision_trace
        return build_decision_trace
    except ImportError:
        from mdm_engine import __all__
        if "build_decision_trace" in __all__:
            from mdm_engine import build_decision_trace
            return build_decision_trace
        raise RuntimeError(
            "Dashboard build_decision_trace requires MDM_ENGINE_DEV=1 or mdm_engine[dev] install."
        ) from None


def get_generate_batch() -> Callable[..., List[Any]]:
    """Dev: simulation.scenario_generator; yoksa mdm_engine."""
    if _dev_mode:
        _ensure_dev_path()
        try:
            from simulation.scenario_generator import generate_batch
            return generate_batch
        except ImportError:
            pass
    try:
        from mdm_engine import generate_batch
        return generate_batch
    except ImportError:
        pass
    try:
        from mdm_engine.simulation import generate_batch
        return generate_batch
    except ImportError:
        raise RuntimeError(
            "Dashboard run_until_coverage requires MDM_ENGINE_DEV=1 or scenario support in mdm_engine."
        ) from None


def get_trace_version() -> str:
    if _dev_mode:
        _ensure_dev_path()
    from mdm_engine.trace_types import TRACE_VERSION
    return TRACE_VERSION


def is_dev_mode() -> bool:
    return _dev_mode
