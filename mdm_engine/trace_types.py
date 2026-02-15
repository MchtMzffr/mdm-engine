"""
MDM Type Definitions

Public contract for trace schema and engine results.
"""

from typing import Any, Dict, List, Optional, TypedDict

# Trace Schema Version
TRACE_VERSION = "1.0"

# Decision Packet / Audit Schema (dashboard, CSV, JSONL)
# v2.0: packet["mdm"] only; CSV columns mdm_*; dashboard rejects < 2.0
SCHEMA_VERSION = "2.0"

# Required for backward compatibility
__all__ = ["TRACE_VERSION", "SCHEMA_VERSION", "DecisionTrace", "EngineResult"]


class DecisionTrace(TypedDict, total=False):
    """
    Decision trace schema (v1.0).
    
    Required fields:
    - t: Timestamp or step index
    - level: Escalation level (0, 1, or 2)
    - raw_action: Raw action (4-element list)
    - final_action: Final action after clamp (4-element list)
    
    Optional fields:
    - cus: Cumulative Uncertainty Score
    - delta_cus: Change in CUS
    - cus_mean: Mean CUS over window
    - soft_clamp: Whether soft clamp was applied
    - human_escalation: Whether human decision is required
    - latency_ms: Decision latency in milliseconds
    - J: Justice score
    - H: Harm score
    - confidence: Confidence score
    - run_id: Test run identifier
    - batch_id: Batch sequence number
    - profile_state: State profile (easy/medium/chaos)
    - config_profile: Config profile name
    - created_at: Wall-clock timestamp
    """
    # Required
    t: float
    level: int
    raw_action: List[float]
    final_action: List[float]
    
    # Optional - CUS & Temporal
    cus: float
    delta_cus: Optional[float]
    cus_mean: Optional[float]
    
    # Optional - Escalation
    soft_clamp: bool
    human_escalation: bool
    
    # Optional - Performance
    latency_ms: Optional[float]
    
    # Optional - Scores
    J: Optional[float]
    H: Optional[float]
    confidence: Optional[float]
    
    # Optional - Metadata
    run_id: Optional[int]
    batch_id: Optional[int]
    profile_state: Optional[str]
    config_profile: Optional[str]
    created_at: Optional[float]
    
    # Optional - Other
    phase: Optional[str]
    chaos: Optional[bool]
    delta_confidence: Optional[float]
    uncertainty: Optional[float]


class EngineResult(TypedDict, total=False):
    """
    Engine result schema.
    
    Required fields:
    - action: Selected action (4-element list)
    - escalation: Escalation level (0, 1, or 2)
    - human_escalation: Whether human decision is required
    
    Optional fields:
    - raw_action: Raw action before clamp
    - trace: Full decision trace
    - reason: Selection reason
    - confidence: Confidence score
    - J, H: Justice and Harm scores
    - trace_hash: Trace hash for integrity
    """
    # Required
    action: List[float]
    escalation: int
    human_escalation: bool
    
    # Optional
    raw_action: Optional[List[float]]
    trace: Optional[List[Dict[str, Any]]]
    reason: Optional[str]
    confidence: Optional[float]
    J: Optional[float]
    H: Optional[float]
    trace_hash: Optional[str]
    
    # Optional - Additional fields
    scores: Optional[Dict[str, float]]
    override: Optional[bool]
    constraint_margin: Optional[float]
    base_confidence: Optional[float]
    margin_factor: Optional[float]
    confidence_gradient: Optional[List[float]]
    suggest_escalation: Optional[bool]
    uncertainty: Optional[Dict[str, Any]]
    temporal_drift: Optional[Dict[str, Any]]
    self_regulation: Optional[Dict[str, Any]]
