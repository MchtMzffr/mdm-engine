# MDM — Fail-Safe Controller (Phase 2 spec §1.5)
# J < J_crit veya H > H_crit ise override; güvenli aksiyon + insan eskalasyonu.

from dataclasses import dataclass
from typing import List

from config import H_CRITICAL, J_CRITICAL, SAFE_ACTION
from .moral_evaluator import MoralScores


@dataclass
class FailSafeResult:
    override: bool
    safe_action: List[float] | None
    human_escalation: bool


def fail_safe(
    scores: MoralScores,
    j_crit: float = J_CRITICAL,
    h_crit: float = H_CRITICAL,
) -> FailSafeResult:
    """Kritik eşik aşılırsa override=True, safe_action ve human_escalation=True."""
    if scores.J < j_crit or scores.H > h_crit:
        return FailSafeResult(
            override=True,
            safe_action=SAFE_ACTION.copy(),
            human_escalation=True,
        )
    return FailSafeResult(override=False, safe_action=None, human_escalation=False)
