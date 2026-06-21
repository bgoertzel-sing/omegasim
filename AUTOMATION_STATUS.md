# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-row role/action population conservation regression
- Changed: added a documented-CLI regression across both full-output fixtures proving every metrics row's per-role action counts sum to the manifest-declared static role population of three agents.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "role_action_counts_sum_to_role_population" -q` passed with 2 tests and 209 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 211 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that total per-tick role/action counts across all roles equal the top-level action totals on every metrics row for both full-output fixtures.
