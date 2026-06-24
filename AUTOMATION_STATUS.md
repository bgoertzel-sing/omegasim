# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response analysis artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added the queued deterministic value-yield divergence analysis artifact while preserving the stable A0/A1 simulator baseline.
- Changed: `ohdyn.analyze_pressure` now writes `value_yield_divergence_ranking.csv` alongside the existing trajectory pressure ranking and includes a matching summary section; README and tests document and verify the new append-safe artifact contract. No real LLM calls, dashboards, Lean, Slack, browser automation, Atomspace integrations, multi-hive coupling, A0/A1 scheduling, simulator output schema, or agent population changes.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out runs/a2_value_yield_divergence_smoke_20260624` and `.venv-conda/bin/python -m ohdyn.analyze_pressure --pressure-dir runs/a2_value_yield_divergence_smoke_20260624 --out runs/a2_value_yield_divergence_smoke_20260624_analysis --limit 5` both completed successfully and emitted `value_yield_divergence_ranking.csv`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/analyze_pressure.py tests/test_run_harness.py`; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'`; `.venv-conda/bin/python -m pytest` passed with `493 passed`.
- Blockers: none.
- Next step: add a deterministic summary interpretation for the top value-yield divergence row, including whether pressure improves completion-normalized yield while degrading effort-normalized yield.
