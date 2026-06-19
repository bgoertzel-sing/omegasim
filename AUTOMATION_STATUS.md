# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 per-tick lobe run metrics
- Changed: added `baseline_lobe_run_id` and `baseline_lobe_current_run_length` to per-tick `metrics.csv` output, added focused reconstruction coverage, and pinned fixed-seed final lobe run state for seeds 1, 2, and 17.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_metrics_csv_records_baseline_lobe_run_state tests/test_run_harness.py::test_fixed_seed_lobe_run_state_is_stable -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 23 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: document the current A0/A1 metrics/events schema in `README.md`.
