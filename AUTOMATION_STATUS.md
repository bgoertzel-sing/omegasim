# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share pressure-response machine-readable prefix comparisons on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic machine-readable per-class capture-pressure prefix selection rows to A2 pressure comparison outputs.
- Changed: no simulator, scheduling, or CSV header behavior changes; `ohdyn.compare_pressure` now appends `class_full` and `class_prefix` rows to `pressure_response_selection.csv` using the same class-specific capture-pressure ranking used by the summary prefix section. README documents the new row scopes, and the pressure-selection regression checks the class-specific rows and details.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_response_selection_csv'` passed with 1 test; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary or pressure_comparison'` passed with 13 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 456 tests.
- Blockers: none.
- Next step: run a larger deterministic pressure comparison seed set and inspect whether the global and per-class pressure-response selections stabilize together.
