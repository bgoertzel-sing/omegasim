# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 summary event type totals
- Changed: rendered deterministic event type totals in `summary.md`, added focused summary coverage, and extended the fixed-seed event totals regression to assert the markdown section for seeds 1, 2, and 17.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_records_event_type_totals tests/test_run_harness.py::test_fixed_seed_event_type_totals_are_stable -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 19 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add lobe dwell/run-length summaries to `summary.md` with focused deterministic tests.
