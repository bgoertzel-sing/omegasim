# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI event replay role/action per-tick sequence cross-seed divergence regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs the CLI with seeds 1 and 2, replays per-tick role/action metric sequences from `events.csv` through manifest agent roles, verifies each replayed sequence matches its run's `metrics.csv`, and asserts the replayed sequences differ across seeds.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replayed_role_action_metric_sequence_changes" -q` passed with 2 tests and 231 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 233 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies per-tick top-level queue/task/action metrics replayed from `events.csv` differ across different seeds for both full-output fixtures while still matching each run's `metrics.csv`.
