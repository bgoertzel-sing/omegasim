# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 queued-task-age replay helper consolidation
- Changed: refactored the in-process queued-task-age regression to reuse the shared event replay helper already used by the documented-CLI full-output fixture checks, while preserving summary assertions through the shared queued-task-age summary helper.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "queued_task_age or event_replay_reproduces_queued_task_age_metrics" -q` passed with 5 tests and 214 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 219 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies events.csv per-tick event counts always equal the configured 15-agent population across both full-output fixtures.
