# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 pressure-curve comparison helper
- Changed: extended `ohdyn.compare_pressure` to run normal, medium, and high pressure policy sets together; added `medium_pressure/` comparison artifacts; added per-policy normal-to-medium slope, medium-to-high slope, and curvature metrics for value-weighted completed work, completed tasks, final queue depth, final queued-task mean age, and peak queued-task max age; updated README pressure-comparison documentation and regression coverage.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 444 tests; after final cleanup, `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 38 tests and 406 deselected.
- Blockers: none.
- Next step: add a bounded CLI smoke/regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that verifies the documented normal/medium/high directory layout and curve summary sections through the command-line entrypoint.
