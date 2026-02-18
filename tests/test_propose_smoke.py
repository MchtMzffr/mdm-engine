"""Smoke test: DecisionEngine.propose domain-free (no skip)."""

from decision_schema.types import Action
from mdm_engine.mdm.decision_engine import DecisionEngine


def test_propose_smoke_domain_free() -> None:
    de = DecisionEngine(confidence_threshold=0.0, signal_threshold=0.0)

    features = {
        "signal_0": 0.5,
        "signal_1": 0.2,
        "state_scalar_a": 120.0,
        "state_scalar_b": 10.0,
    }

    proposal = de.propose(features)
    assert proposal.action in (Action.HOLD, Action.ACT)
    assert 0.0 <= float(proposal.confidence) <= 1.0
    assert isinstance(proposal.reasons, list)
