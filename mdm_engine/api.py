"""
MDM Public API - Simplified interface

This module provides a simplified, user-friendly API for the MDM (Model Oversight Engine) library.
"""

from typing import Any, Dict, List, Optional, Union

# Import from package (no sys.path hacks)
from mdm_engine.engine import moral_decision_engine as _moral_decision_engine
from mdm_engine.engine import replay as _replay


def decide(
    raw_state: Dict[str, Any],
    profile: Optional[str] = None,
    deterministic: bool = True,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Make an ethical decision based on raw state.
    
    This is the main entry point for MDM. It provides a simplified
    interface to the decision engine.
    
    Args:
        raw_state: Dictionary containing state variables (risk, severity, etc.)
        profile: Config profile name (e.g., "scenario_test", "production_safe")
                 If None, uses default "base" profile
        deterministic: If True, same input produces same output (exact match).
                       See AUDITABILITY.md for determinism contract details (default: True)
        context: Optional context dict (e.g., {"cus_history": [...]})
    
    Returns:
        Dictionary containing:
        - action: [severity, intervention, compassion, delay] (4-element list)
        - escalation: 0, 1, or 2 (L0/L1/L2 level)
        - human_escalation: True if human decision required
        - confidence: Confidence score
        - trace: Full decision trace
        - ... (other fields)
    
    Example:
        >>> from mdm_engine import decide
        >>> state = {
        ...     "risk": 0.7,
        ...     "severity": 0.8,
        ...     "physical": 0.6,
        ...     "social": 0.5,
        ...     "context": 0.4,
        ...     "compassion": 0.5,
        ...     "justice": 0.9,
        ...     "harm_sens": 0.5,
        ...     "responsibility": 0.7,
        ...     "empathy": 0.6,
        ... }
        >>> result = decide(state, profile="scenario_test")
        >>> print(f"Action: {result['action']}")
        >>> print(f"Level: {result['escalation']}")
        >>> print(f"Human escalation: {result['human_escalation']}")
    """
    config_override = profile if profile else None
    return _moral_decision_engine(
        raw_state=raw_state,
        deterministic=deterministic,
        config_override=config_override,
        context=context,
    )


def replay_trace(
    trace: Union[Dict[str, Any], List[Dict[str, Any]]],
    validate: bool = True,
    verify_hash: bool = False,
) -> Dict[str, Any]:
    """
    Replay a decision trace to reproduce the same decision.
    
    Args:
        trace: Decision trace (dict or list of steps)
        validate: If True, validates that replayed action matches original
        verify_hash: If True, verifies trace hash integrity
    
    Returns:
        Dictionary containing replayed decision result
    
    Example:
        >>> from mdm_engine import decide, replay_trace
        >>> result = decide(raw_state, profile="scenario_test")
        >>> replayed = replay_trace(result["trace"], validate=True)
        >>> assert replayed["action"] == result["action"]
    """
    return _replay(trace, validate=validate, verify_hash=verify_hash)
