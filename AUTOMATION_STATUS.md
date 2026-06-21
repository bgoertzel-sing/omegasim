# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-tick task lifecycle events-to-metrics regression
- Changed: added a documented-CLI regression across both full-output fixtures that reconstructs per-tick task creation, work, completion, cumulative task totals, queue deltas, and queue depth from events.csv and verifies they match metrics.csv.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_per_tick_task_lifecycle_matches_queue_and_task_metrics" -q` passed with 2 tests and 215 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 217 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that replaying events.csv task queue order reproduces metrics.csv queued_task_age_max_tick and queued_task_age_mean_tick for both full-output fixtures.
