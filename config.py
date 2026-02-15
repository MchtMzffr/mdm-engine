# Backward compatibility shim for config.py
# This file allows existing code to continue working:
#   import config
#   from config import DEFAULT_WEIGHTS
#
# New code should use:
#   from mdm_engine import config
#   from mdm_engine.config import DEFAULT_WEIGHTS

# Lazy import to avoid circular dependencies
import sys
from types import ModuleType

# Create a proxy module that imports from mdm_engine.config on first access
class _ConfigProxy(ModuleType):
    def __getattr__(self, name):
        # Import only when needed
        from mdm_engine import config as _real_config
        return getattr(_real_config, name)
    
    def __dir__(self):
        from mdm_engine import config as _real_config
        return dir(_real_config)

# Replace this module with the proxy
sys.modules[__name__] = _ConfigProxy(__name__)

__all__ = [
    "DEFAULT_UNKNOWN",
    "ACTION_GRID_RESOLUTION",
    "J_MIN",
    "H_MAX",
    "C_MIN",
    "C_MAX",
    "J_CRITICAL",
    "H_CRITICAL",
    "SAFE_ACTION",
    "ScoringWeights",
    "DEFAULT_WEIGHTS",
    "COMPASSION_ALPHA",
    "COMPASSION_BETA",
    "COMPASSION_GAMMA",
    "SIGMA_MAX",
    "CONFIDENCE_MARGIN_K",
    "CONFIDENCE_ESCALATION_SUGGEST",
    "CONFIDENCE_ESCALATION_FORCE",
    "CONFIDENCE_MARGIN_CLAMP",
    "UNCERTAINTY_MARGIN_K",
    "UNCERTAINTY_AS_LAMBDA",
    "CUS_WEIGHTS",
    "SEVERITY_SOFT_MAX",
    "INTERVENTION_SOFT_MAX",
    "DELAY_SOFT_MIN",
    "AS_SOFT_THRESHOLD",
    "DIVERGENCE_HARD_THRESHOLD",
    "ESCALATION_HYSTERESIS",
    "SOFT_CLAMP_ALPHA",
    "SOFT_CLAMP_BETA",
    "SOFT_CLAMP_GAMMA",
    "DELTA_CUS_THRESHOLD",
    "CUS_MEAN_WINDOW",
    "CUS_MEAN_THRESHOLD",
]
