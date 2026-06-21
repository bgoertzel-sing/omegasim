# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI event replay role/action metrics regression
- Changed: added a documented-CLI regression across both full-output fixtures that loads `manifest.yaml`, replays `events.csv` through manifest agent roles, and verifies each tick's role/action event counts match the emitted role/action metric fields.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_replay_to_role_action_metrics" -q` passed with 2 tests and 223 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 225 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies role/action totals replayed from `events.csv` through manifest roles match the `summary.md` role action totals across both full-output fixtures.
