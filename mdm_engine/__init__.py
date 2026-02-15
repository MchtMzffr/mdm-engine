"""
MDM (Model Oversight Engine) — Model Denetim Motoru

Public API - Stable interface for external use.
"""

# Version
__version__ = "1.0.0"

# Import trace version from trace_types
from mdm_engine.trace_types import TRACE_VERSION

# Simplified API (recommended for new users)
from mdm_engine.api import decide, replay_trace

# Full API (for advanced users)
from mdm_engine.engine import moral_decision_engine, replay

# Import from repo root packages
# Note: core/ and config_profiles/ are at repo root for backward compatibility
# When installed as package, these should be accessible via setuptools package discovery
try:
    from core.trace_collector import TraceCollector, build_decision_trace
    from config_profiles import get_config, list_profiles
except ImportError:
    # Fallback: if core/config_profiles not found (shouldn't happen in normal install)
    # Try importing from shim modules
    try:
        from mdm_engine.core.trace_collector import TraceCollector, build_decision_trace
        from mdm_engine.config_profiles import get_config, list_profiles
    except ImportError:
        # Last resort: these won't be available
        TraceCollector = None
        build_decision_trace = None
        get_config = None
        list_profiles = None

# Re-export for convenience
__all__ = [
    "__version__",
    "TRACE_VERSION",
    # Simplified API (recommended)
    "decide",
    "replay_trace",
    # Full API (advanced)
    "moral_decision_engine",
    "replay",
    "TraceCollector",
    "build_decision_trace",
    "get_config",
    "list_profiles",
]
