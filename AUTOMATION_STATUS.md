# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison interpretability on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added A2 pressure sensitivity summary metric
- Changed: added a deterministic `Most pressure-sensitive curve metric` section to the pressure comparison `summary.md`; it scans the existing per-policy pressure slope/curvature fields and reports the policy, observable, field, signed value, and absolute value for the largest absolute pressure response. Added focused regression coverage and updated the README pressure artifact contract.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 42 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 448 tests.
- Blockers: none.
- Next step: add one bounded A2 pressure comparison summary table that ranks all policy/observable pressure-curve responses by absolute magnitude.
