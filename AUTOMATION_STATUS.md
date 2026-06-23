# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison artifact hygiene on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 documented A2 pressure CLI overwrite-refusal regression
- Changed: added a subprocess regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that first creates a pressure comparison output directory, snapshots the top-level `pressure_comparison_metrics.csv` and `summary.md`, reruns the documented CLI into the same directory, and verifies the rerun fails without modifying those artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 41 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 447 tests.
- Blockers: none.
- Next step: add one bounded A2 pressure comparison summary metric that identifies the most pressure-sensitive policy/observable pair from the existing pressure-curve fields.
