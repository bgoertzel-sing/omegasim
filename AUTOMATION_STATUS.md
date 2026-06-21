# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI event replay role/action summary totals regression
- Changed: added a documented-CLI regression across both full-output fixtures that loads `manifest.yaml`, replays `events.csv` through manifest agent roles, and verifies replayed role/action totals match the `summary.md` role action totals.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_replay_to_summary_role_action_totals" -q` passed with 2 tests and 225 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 227 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies role/action totals replayed from `events.csv` through manifest roles reproduce exactly across same-seed runs for both full-output fixtures.
