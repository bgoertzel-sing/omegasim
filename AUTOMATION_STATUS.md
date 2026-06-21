# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-tick events-to-metrics action total regression
- Changed: added a documented-CLI regression across both full-output fixtures proving every events.csv per-tick event/action count agrees with the matching metrics.csv top-level action totals for idle, message, create_task, and work_task.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_per_tick_action_counts_match_metrics_top_level_action_totals" -q` passed with 2 tests and 213 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 215 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that every events.csv per-tick task lifecycle row agrees with metrics.csv queue deltas, task creation totals, and task completion totals for both full-output fixtures.
