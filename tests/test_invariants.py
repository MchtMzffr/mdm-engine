# Karar invariants testi: paket/engine ciktisinda asla bozulmamasi gereken kurallar.
# Calistirma: python tests/test_invariants.py

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mdm_engine.invariants import check_decision_invariants


def test_fail_safe_invariant():
    packet = {
        "mdm": {"level": 2, "escalation_driver": "fail_safe", "escalation_drivers": ["fail_safe"], "soft_safe_applied": False},
        "final_action": "HOLD_REVIEW",
        "clamps": [{"type": "human_review"}],
    }
    violations = check_decision_invariants(packet, strict=True)
    assert not violations, violations


def test_fail_safe_violation_level():
    packet = {
        "mdm": {"level": 1, "escalation_driver": "fail_safe"},
        "final_action": "HOLD_REVIEW",
        "clamps": [],
    }
    violations = check_decision_invariants(packet, strict=True)
    assert any("inv_fail_safe" in v[0] for v in violations)


def test_no_valid_candidates_invariant():
    packet = {
        "mdm": {"level": 2, "escalation_driver": "no_valid_candidates", "valid_candidate_count": 0},
        "final_action": "HOLD_REVIEW",
        "clamps": [],
    }
    violations = check_decision_invariants(packet, strict=True)
    assert not violations, violations


def test_l1_requires_clamp():
    packet = {
        "mdm": {"level": 1, "escalation_driver": "as_norm_low", "soft_safe_applied": True},
        "final_action": "APPLY_CLAMPED",
        "clamps": [{"type": "soft_safe"}],
    }
    violations = check_decision_invariants(packet, strict=True)
    assert not violations, violations


def test_l0_driver_none():
    packet = {
        "mdm": {"level": 0, "escalation_driver": "none", "escalation_drivers": []},
        "final_action": "APPLY",
        "clamps": [],
    }
    violations = check_decision_invariants(packet, strict=True)
    assert not violations, violations


if __name__ == "__main__":
    test_fail_safe_invariant()
    print("  OK fail_safe invariant")
    test_fail_safe_violation_level()
    print("  OK fail_safe violation detected")
    test_no_valid_candidates_invariant()
    print("  OK no_valid_candidates invariant")
    test_l1_requires_clamp()
    print("  OK L1 clamp invariant")
    test_l0_driver_none()
    print("  OK L0 driver none")
    print("Tum invariant testleri gecti.")
