# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison regression coverage and interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added the stable-prefix pressure-response interpretation regression.
- Changed: no simulator behavior changes; `tests/test_run_harness.py` now verifies the README-documented stable-prefix `Pressure-response interpretation` wording against a generated pressure comparison `summary.md` for seeds `1,2`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary'` passed with 6 selected tests; `.venv-conda/bin/python -m pytest` passed with 453 tests.
- Blockers: none.
- Next step: add a small pressure-response selected-top-response section to `pressure_comparison_metrics.csv` or a companion machine-readable artifact so downstream research scripts do not need to parse `summary.md`.
