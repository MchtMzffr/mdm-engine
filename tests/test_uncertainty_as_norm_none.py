#!/usr/bin/env python
"""
as_norm None değişikliğini doğrula: <2 aday -> as_norm None, as_norm_low tetiklenmez.
Proje kökünden: python tests/test_uncertainty_as_norm_none.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Döngüsel import'u kırmak için önce mdm_engine yükle
import mdm_engine  # noqa: F401

from core.uncertainty import (
    action_spread,
    combined_uncertainty_score,
    compute_uncertainty,
    UncertaintyResult,
)
from core.soft_override import compute_escalation_decision, compute_escalation_level


def test_action_spread_single_returns_none():
    as_raw, as_norm = action_spread([0.9])
    assert as_raw == 0.0, as_raw
    assert as_norm is None, as_norm


def test_action_spread_empty_returns_none():
    as_raw, as_norm = action_spread([])
    assert as_raw == 0.0 and as_norm is None


def test_cus_with_none_as_norm():
    cus = combined_uncertainty_score(0.5, 0.5, None)
    assert 0 <= cus <= 1.0, cus


def test_compute_uncertainty_single_candidate_as_norm_none():
    u = compute_uncertainty(0.5, 0.0, [0.9])
    assert isinstance(u, UncertaintyResult)
    assert u.as_ == 0.0 and u.as_norm is None
    assert 0 <= u.cus <= 1.0


def test_escalation_driver_no_as_norm_low_when_none():
    level, driver = compute_escalation_decision(
        confidence=0.8,
        constraint_margin=0.2,
        H=0.1,
        h_crit=0.6,
        as_norm=None,
        divergence=0.0,
    )
    assert driver != "as_norm_low", f"as_norm=None iken as_norm_low tetiklenmemeli: {driver}"
    assert level == 0 or driver == "none", (level, driver)


def test_compute_uncertainty_two_candidates_has_as_norm():
    u = compute_uncertainty(0.5, 0.0, [0.8, 0.6])
    assert u.as_norm is not None
    assert 0 <= u.as_norm <= 1.0


if __name__ == "__main__":
    test_action_spread_single_returns_none()
    print("  OK action_spread single -> None")
    test_action_spread_empty_returns_none()
    print("  OK action_spread empty -> None")
    test_cus_with_none_as_norm()
    print("  OK CUS with as_norm=None")
    test_compute_uncertainty_single_candidate_as_norm_none()
    print("  OK compute_uncertainty single -> as_norm None")
    test_escalation_driver_no_as_norm_low_when_none()
    print("  OK escalation_driver(as_norm=None) -> as_norm_low yok")
    test_compute_uncertainty_two_candidates_has_as_norm()
    print("  OK compute_uncertainty 2 aday -> as_norm dolu")
    print("Tüm uncertainty/as_norm None testleri geçti.")
