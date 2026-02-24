# Decision Ecosystem — mdm-engine
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""MDM Engine: propose(features) -> Proposal; DecisionEngine for custom thresholds."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from decision_schema.types import Proposal

__version__ = "0.2.1"


def propose(features: dict[str, Any], confidence_threshold: float = 0.5) -> Proposal:
    """
    Single entry point: features -> Proposal (reference or private hook).

    Fail-closed reason codes: private_hook_error (hook exception), harness uses
    fail_closed_exception for pipeline exceptions. See PARAMETER_INDEX / docs.
    """
    from mdm_engine.mdm.decision_engine import DecisionEngine

    return DecisionEngine(confidence_threshold=confidence_threshold).propose(features)


__all__ = ["__version__", "propose"]
