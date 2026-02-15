# MDM — Constraint Validator (Phase 2 spec §1.4)
# Phase 1 kısıtlarını uygular: J >= J_min, H <= H_max, C in [C_min, C_max].

from dataclasses import dataclass
from typing import List

from config import C_MAX, C_MIN, H_MAX, J_MIN
from .moral_evaluator import MoralScores


@dataclass
class ConstraintResult:
    valid: bool
    violations: List[str]


def validate_constraints(
    scores: MoralScores,
    j_min: float = J_MIN,
    h_max: float = H_MAX,
    c_min: float = C_MIN,
    c_max: float = C_MAX,
) -> ConstraintResult:
    """Kısıtları kontrol eder; bir ihlal bile valid=False yapar."""
    violations: List[str] = []
    if scores.J < j_min:
        violations.append("J_below_min")
    if scores.H > h_max:
        violations.append("H_above_max")
    if scores.C < c_min or scores.C > c_max:
        violations.append("C_out_of_band")
    return ConstraintResult(valid=len(violations) == 0, violations=violations)
