# Decision Ecosystem — mdm-engine
# Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
# SPDX-License-Identifier: MIT
"""MDM: domain-free proposal generation from generic features."""

from mdm_engine.mdm.reference_model_generic import compute_proposal_reference
from mdm_engine.mdm.decision_engine import DecisionEngine

__all__ = ["compute_proposal_reference", "DecisionEngine"]
