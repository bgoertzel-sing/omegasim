# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 documented A2 pressure CLI regression
- Changed: added a subprocess smoke/regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that verifies the documented `normal_pressure/`, `medium_pressure/`, and `high_pressure/` comparison directories, top-level pressure artifacts, three policy rows, step totals, and fixed-policy pressure delta/curve summary sections through the command-line entrypoint.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 39 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 445 tests.
- Blockers: none.
- Next step: add a bounded documented CLI reproducibility regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that compares top-level pressure artifacts across two fresh output directories.
