# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI lobe run-state different-seed regression
- Changed: added a documented-CLI different-seed regression across the full-output fixtures proving the ordered `baseline_lobe_run_id`/`baseline_lobe_current_run_length` sequence in `metrics.csv` changes between seed 1 and seed 2 while preserving the existing same-seed run-state reproducibility coverage.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_run_state_sequence" -q` passed with 4 tests and 195 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 199 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that lobe dwell-run summary aggregates change across different seeds for both full-output fixtures.
