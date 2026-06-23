# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison reproducibility on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 documented A2 pressure CLI reproducibility regression
- Changed: added a subprocess regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that runs the documented pressure comparison CLI into two fresh output directories and verifies the top-level `pressure_comparison_metrics.csv` and `summary.md` artifacts are byte-identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 40 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 446 tests.
- Blockers: none.
- Next step: add a bounded documented CLI regression for `python -m ohdyn.compare_pressure --seeds 1 2 --out ...` that refuses to overwrite existing top-level pressure comparison artifacts without modifying the existing output directory.
