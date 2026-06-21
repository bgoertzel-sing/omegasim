# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI event replay queue-pressure per-tick sequence different-seed divergence regression
- Changed: added a documented-CLI regression across both full-output fixtures that runs seeds 1 and 2, replays per-tick queue pressure metric sequences from each `events.csv`, verifies each replayed sequence matches its run's `metrics.csv`, and asserts the replayed sequences diverge across different seeds.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replayed_queue_pressure_metric_sequence_changes" -q` passed with 2 tests and 243 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 245 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies summary-level queue pressure totals diverge across different seeds for both full-output fixtures while still matching each run's `metrics.csv`.
