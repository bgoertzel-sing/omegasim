# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-comparison schema regression coverage on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 pressure comparison CSV header regression coverage
- Changed: added a deterministic test that runs the pressure comparison helper, reads `pressure_comparison_metrics.csv`, and validates its header exactly against `PRESSURE_COMPARISON_FIELDS`; no simulator behavior changed.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure_comparison" -q` passed with 4 tests and 435 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 439 tests.
- Blockers: none.
- Next step: add one executable A2 pressure-sensitivity experiment fixture or comparison metric that makes the pressure-condition dynamics more informative than the current normal-versus-high binary.
