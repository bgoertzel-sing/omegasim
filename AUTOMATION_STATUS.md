# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI summary task/queue different-seed divergence regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs seeds 1 and 2, parses summary-level task/queue totals (`tasks created`, `tasks completed`, and `final queue depth`) from each `summary.md`, verifies each summary matches its run's final `metrics.csv` row, and asserts the task/queue totals diverge across different seeds.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_task_and_queue_totals_change" -q` passed with 2 tests and 249 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 251 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies summary-level event totals diverge across different seeds for both full-output fixtures while still matching each run's `events.csv`.
