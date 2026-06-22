# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI integrated summary aggregate tuple reproducibility regression
- Changed: added one documented-CLI regression across both full-output fixtures that verifies the integrated summary task/queue, queue-pressure, and queued-task-age aggregate tuple matches `metrics.csv` and reproduces across repeated same-seed runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "aggregate_tuple_reproduces" -q` passed with 2 tests and 263 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 265 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies the integrated task/queue, queue-pressure, and queued-task-age summary aggregate tuple changes across different seeds for both full-output fixtures.
