# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 attention-share pressure-response prefix comparisons on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic per-class capture-pressure prefix comparison to A2 pressure comparison summaries.
- Changed: no simulator, scheduling, or CSV schema behavior changes; `ohdyn.compare_pressure` now adds a `Per-class capture-pressure prefix comparison` summary section that filters pressure-response prefix stability down to attention-class capture-pressure observables, reports the full and last-prefix class top responses, class-response stability booleans, instability causes, and one row per proper seed prefix. README and pressure-summary tests cover the new summary contract.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary'` passed with 8 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 456 tests.
- Blockers: none.
- Next step: add machine-readable per-class capture-pressure prefix selection rows alongside the existing pressure-response selection CSV.
