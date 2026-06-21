# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-row role/action top-level action total regression
- Changed: added a documented-CLI regression across both full-output fixtures proving every metrics row's per-role action counts sum to the top-level action totals for idle, message, create_task, and work_task.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "top_level_action_totals_for_every_metrics_row" -q` passed with 2 tests and 211 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 213 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that every events.csv per-tick action/event count agrees with the corresponding metrics.csv top-level action totals for both full-output fixtures.
