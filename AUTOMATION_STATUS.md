# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI integrated summary queue integrity regression
- Changed: added one documented-CLI regression across both full-output fixtures that verifies summary task/queue totals, queue-pressure totals, and queued-task-age aggregates are all present together, match `metrics.csv`, and satisfy internal queue/age consistency checks.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "task_queue_pressure_and_age_aggregates" -q` passed with 2 tests and 261 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 263 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies the integrated task/queue, queue-pressure, and queued-task-age summary aggregate tuple reproduces across repeated same-seed runs for both full-output fixtures.
