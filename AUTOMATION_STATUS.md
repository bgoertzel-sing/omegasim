# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 documented-CLI integrated summary aggregate bundle same-seed regression
- Changed: added one documented-CLI regression across both full-output fixtures that verifies the integrated summary task/queue, queue-pressure, queued-task-age, lobe, and role/action aggregate bundle matches `metrics.csv` and reproduces across repeated same-seed runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "integrated_summary_aggregate_bundle" -q` passed with 2 tests and 267 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 269 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies the integrated summary task/queue, queue-pressure, queued-task-age, lobe, and role/action aggregate bundle changes across different seeds for both full-output fixtures.
