# Cursor Prompt: Crypto Adapter (ORES + Dashboard Unchanged)

**Use this as a single paste prompt in Cursor** when extending the system with a new domain adapter without breaking the existing Wikipedia EventStreams + ORES + MDM live demo.

---

You are working in the public repo `git@github.com:MeetlyTR/mdm-engine.git`.

## GOAL

- Extend the system to support a new domain adapter (**Crypto Market Integrity** / manipulation vs organic move) **WITHOUT** breaking the existing Wikipedia EventStreams + ORES + MDM live demo and **WITHOUT** changing the current localhost/dashboard flow.
- Keep the same Streamlit dashboard entrypoint and UX stable: `mdm dashboard` should still open the same Proof dashboard; Wikipedia live stream must remain the **default** path and continue to pass tests.
- The existing live path is: **Streamlit dashboard** (`visualization/dashboard.py`) → “Start live stream” → **EventStreams + ORES + MDM pipeline** (`tools/live_wiki_audit.py` referenced in README). Preserve this behavior.

## NON-NEGOTIABLE CONSTRAINTS

1. **Do not break existing tests or CLI commands:**
   - `mdm dashboard`
   - `mdm realtime`
   - `mdm tests`
2. Keep current default Streamlit port behavior (8501) and current tabs/strings unless we only **add** new options in a backward-compatible way.
3. Do not remove/rename existing keys in packets. Audit schema v2 uses `mdm` packet key and dashboard expects fields like `mdm.level`, `mdm.soft_clamp`, `mdm.reason`, `latency_ms` etc. Keep compatibility.

## WHAT TO DO (Step-by-step)

### A) Baseline analysis

- Identify the current live wiki pipeline entrypoints and interfaces:
  - `visualization/dashboard.py` live runner thread(s), how it starts/stops the stream, how packets are accumulated and rendered.
  - The producer used for live wiki (likely in `tools/live_wiki_audit.py`) and how it structures decision packets: `input` / `external` / `mdm` / `final_action` / `latency` / `run_id` fields.
- Identify where ORES is called and how mismatches are computed and displayed.

### B) Create a new domain adapter (Crypto Integrity) that matches the same packet contract

- Add a new module under `tools/` (e.g. `tools/live_crypto_audit.py`) that produces packets with the **same structure** as wiki packets.
- The crypto adapter should accept an input feed abstraction (initially a **simple synthetic simulator** in `simulation/` to avoid network dependencies and keep tests stable). Later it can be connected to real exchange data; for now keep it **offline by default**.
- Define “signals” for manipulation suspicion vs organic move, but output must still map into MDM **raw_state** fields (`risk`, `severity`, `physical`, `social`, `context`, `compassion`, `justice`, `harm_sens`, `responsibility`, `empathy`) so `mdm_engine.decide()` can run unchanged.

### C) Dashboard integration (backward compatible)

- In `visualization/dashboard.py`, add a **sidebar selector**: `Data Source: Wikipedia (ORES)` (default) / `Crypto (Simulated)`.
- If **Wikipedia** selected: use existing behavior exactly.
- If **Crypto** selected: start the crypto producer and display packets in the **same** tables/charts.
- Any ORES-specific fields should be **optional**; when crypto is selected, set external decision fields to `None`/`""` and ensure charts don’t crash.

### D) Tests & smoke

- Add minimal tests to ensure:
  - Importing dashboard and starting in Wikipedia mode remains unchanged.
  - Packet schema invariants: required keys exist, types are sane.
  - `mdm realtime` and existing wiki tests still pass.
- Add/adjust `tools/smoke_test.py` (if present) to include an **offline** crypto smoke run, but **DO NOT** make it a required dependency for CI unless it’s fast and deterministic.

## SECURITY & HYGIENE

- Do not introduce secrets or hard-coded tokens.
- Any network calls must be **optional** and **disabled by default**.
- Update docs minimally: README should mention the new data source, but keep wiki instructions **primary**.

## DELIVERABLES

- New crypto live adapter: `tools/live_crypto_audit.py` (or similar).
- Dashboard updated with source selector, **backward compatible**.
- Tests + small doc update.
- A short **changelog entry** describing the addition without breaking changes.

---

*This prompt locks the goal: Wikipedia flow stays default; crypto is an optional data source. Dashboard packet fields remain unchanged.*
