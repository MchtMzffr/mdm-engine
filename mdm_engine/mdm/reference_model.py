"""
Backward-compat shim: maps legacy feature keys to generic and delegates to reference_model_generic.

Prefer reference_model_generic for new code. This module accepts mid, imbalance, depth, spread_bps
and maps them to signal_0, signal_1, state_scalar_a, state_scalar_b for the generic implementation.
"""

from __future__ import annotations

from typing import Any

from mdm_engine.mdm.reference_model_generic import (
    compute_proposal_reference as _generic_reference,
    compute_proposal_private,
)


def compute_proposal_reference(
    features: dict[str, Any],
    confidence_threshold: float = 0.5,
    imbalance_threshold: float = 0.1,
) -> Any:
    """Accept legacy or generic feature keys; delegate to domain-free implementation."""
    mapped = {
        "signal_0": features.get("signal_0", features.get("mid", 0.5)),
        "signal_1": features.get("signal_1", features.get("imbalance", 0.0)),
        "state_scalar_a": features.get("state_scalar_a", features.get("depth", 0.0)),
        "state_scalar_b": features.get("state_scalar_b", features.get("spread_bps", 0.0)),
    }
    return _generic_reference(
        mapped,
        confidence_threshold=confidence_threshold,
        signal_threshold=imbalance_threshold,
    )


__all__ = ["compute_proposal_reference", "compute_proposal_private"]
