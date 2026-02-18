<!--
Decision Ecosystem — mdm-engine
Copyright (c) 2026 Mücahit Muzaffer Karafil (MchtMzffr)
SPDX-License-Identifier: MIT
-->
# Example / Integration Code

**Core API is proposal generation only.** Event loop, execution, and DMC integration are not part of the installed package.

- **Integration loop**: Legacy `run_loop` (MDM + DMC + execution) was removed from core. For end-to-end examples see the `decision-ecosystem-integration-harness` repo or implement your own loop using `DecisionEngine.propose()` and `dmc_core.dmc.modulate(Proposal, GuardPolicy, context)`.
- **Example domain only**: Any domain-specific demos belong here and must not be required by the core.
