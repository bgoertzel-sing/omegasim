# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-tick role/action metric seed-sensitivity regression
- Changed: added a documented-CLI different-seed regression across the full-output fixtures proving the per-tick role/action metrics sequence changes between seed 1 and seed 2 while preserving the manifest-declared role/action schema.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "role_action_metric_sequence" -q` passed with 4 tests and 205 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 209 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that role/action per-tick counts always sum to the static per-role population across every metrics row for both full-output fixtures.
