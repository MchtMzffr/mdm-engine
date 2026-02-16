# MDM Documentation

This directory contains the **public documentation** for MDM (Model Oversight Engine) that is included in the repository. All documents are in **English**.

---

## What is in this folder (in the repo)

| Document | Description |
|----------|-------------|
| **README.md** (this file) | Overview of the docs folder and how to use it. |
| **ARCHITECTURE.md** | Core architecture: pipeline (state → action grid → moral scores → fail-safe → selection → confidence/uncertainty → escalation → soft clamp), components (core/, mdm_engine/, config_profiles/, tools/, visualization/), and data flow for the Wiki adapter. |
| **MODEL_AND_MANUAL.md** | Full core model structure (state space, action space, W/J/H/C formulas, constraints, fail-safe, confidence, uncertainty, escalation, soft clamp, temporal drift) and a user manual with “what it does, why, examples” for each part. |
| **images/** | L2 example screenshots (Suhrawardy diff, Pastoral diff, review UI). See **images/README.md** for file names and descriptions. |

All other `.md` and `.txt` files under `docs/` (specs, reports, development guides, Turkish or internal notes) are **not** in the repo; they remain local only and are listed in the project `.gitignore`.

---

## Reading order

1. **Repository root README.md** — Project overview, quick start, CLI.
2. **docs/ARCHITECTURE.md** — How the engine is structured and how data flows.
3. **docs/MODEL_AND_MANUAL.md** — Detailed model (formulas, parameters) and manual (what each part does, why, examples).
4. **USAGE_POLICY.md**, **SAFETY_LIMITATIONS.md**, **AUDITABILITY.md** (repository root) — Policy, limits, and audit trail.

---

## Images (L2 case studies)

The **images/** folder holds screenshots used to illustrate L2 (human review) examples: a Wikipedia biography edit (Suhrawardy) and a content-removal edit (Pastoral science fiction). File names and descriptions are in **images/README.md**.
