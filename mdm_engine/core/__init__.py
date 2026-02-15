# MDM core modülleri (Phase 2 spec).
# This is a compatibility shim - actual core modules are at repo root.

# Import from repo root core package
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.state_encoder import encode_state, State
from core.action_generator import generate_actions
from core.moral_evaluator import evaluate_moral, MoralScores
from core.constraint_validator import validate_constraints, ConstraintResult
from core.fail_safe import fail_safe, FailSafeResult
from core.action_selector import select_action, SelectionResult
from core.trace_logger import TraceLogger, TraceEvent
from core.confidence import compute_confidence, ConfidenceResult
from core.uncertainty import compute_uncertainty, UncertaintyResult

__all__ = [
    "encode_state",
    "State",
    "generate_actions",
    "evaluate_moral",
    "MoralScores",
    "validate_constraints",
    "ConstraintResult",
    "fail_safe",
    "FailSafeResult",
    "select_action",
    "SelectionResult",
    "TraceLogger",
    "TraceEvent",
    "compute_confidence",
    "ConfidenceResult",
    "compute_uncertainty",
    "UncertaintyResult",
]
