# MDM Phase 4.6 — Config profile loader.
# get_config(profile_name) → engine/config_override uyumlu dict.
# This is a compatibility shim - actual config_profiles are at repo root.

from typing import Any, Dict, List

# Import from repo root config_profiles package
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config_profiles.base import DEFAULT_CONFIG
from config_profiles.production_safe import CONFIG as PRODUCTION_SAFE_CONFIG
from config_profiles.high_critical import CONFIG as HIGH_CRITICAL_CONFIG
from config_profiles.chaos_tuning import CONFIG as CHAOS_TUNING_CONFIG
from config_profiles.scenario_test import CONFIG as SCENARIO_TEST_CONFIG
from config_profiles.clamp_test import CONFIG as CLAMP_TEST_CONFIG
from config_profiles.wiki_calibrated import CONFIG as WIKI_CALIBRATED_CONFIG

PROFILES: Dict[str, Dict[str, Any]] = {
    "base": DEFAULT_CONFIG,
    "production_safe": PRODUCTION_SAFE_CONFIG,
    "high_critical": HIGH_CRITICAL_CONFIG,
    "chaos_tuning": CHAOS_TUNING_CONFIG,
    "scenario_test": SCENARIO_TEST_CONFIG,
    "clamp_test": CLAMP_TEST_CONFIG,
    "wiki_calibrated": WIKI_CALIBRATED_CONFIG,
}


def get_config(profile_name: str) -> Dict[str, Any]:
    """
    Profile adına göre eşik dict döndürür.
    Engine ve chaos/tuning config_override olarak kullanılır.
    """
    name = (profile_name or "").strip().lower()
    if name in PROFILES:
        return dict(PROFILES[name])
    return dict(DEFAULT_CONFIG)


def list_profiles() -> List[str]:
    return list(PROFILES.keys())
