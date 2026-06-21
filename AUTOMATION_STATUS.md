# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI summary task/queue same-seed reproducibility regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs seed 17 twice, parses top-level task and queue totals from each `summary.md`, verifies each summary matches its run's `metrics.csv`, and asserts those summary totals reproduce across repeated same-seed runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_task_and_queue_totals_reproduce" -q` passed with 2 tests and 255 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 257 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies summary-level queue pressure totals reproduce across repeated same-seed runs for both full-output fixtures while still matching each run's `metrics.csv`.
