# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 lobe dwell summaries
- Changed: rendered deterministic baseline lobe dwell/run-length summaries in `summary.md`, added focused summary coverage, and added fixed-seed dwell regressions for seeds 1, 2, and 17.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_records_baseline_lobe_dwell_runs tests/test_run_harness.py::test_fixed_seed_lobe_dwell_runs_are_stable -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 21 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add per-tick lobe run identifiers and current-run lengths to `metrics.csv` with deterministic regression coverage.
