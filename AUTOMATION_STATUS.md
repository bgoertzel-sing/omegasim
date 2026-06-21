# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI summary queued-task-age same-seed reproducibility regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs seed 17 twice, parses queued-task-age aggregates from each `summary.md`, verifies each summary matches its run's `metrics.csv`, and asserts those summary aggregates reproduce across repeated same-seed runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_queued_task_age_aggregates_reproduce" -q` passed with 2 tests and 259 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 261 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies summary task/queue totals, queue-pressure totals, and queued-task-age aggregates are all present together and internally consistent with `metrics.csv` for both full-output fixtures.
