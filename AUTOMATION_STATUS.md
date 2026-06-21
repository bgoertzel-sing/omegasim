# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI event replay queued-task-age per-tick sequence same-seed reproducibility regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs two independent CLI runs with seed 17, replays per-tick queued-task-age max/mean metric sequences from each `events.csv`, verifies each replayed sequence matches its run's `metrics.csv`, and asserts the replayed sequences reproduce exactly across same-seed runs; extracted queued-task-age replay and metrics sequence helpers for reuse by the existing replay assertion.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replayed_queued_task_age_metric_sequence" -q` passed with 2 tests and 237 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 239 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies event-replayed queued-task-age metric sequences differ across seeds 1 and 2 for both full-output fixtures while still matching each run's `metrics.csv`.
