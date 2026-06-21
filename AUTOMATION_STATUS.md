# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-tick manifest agent coverage regression
- Changed: added a documented-CLI regression across both full-output fixtures that loads `manifest.yaml` and verifies each tick's `events.csv` agent IDs are unique and exactly cover the manifest agent ID set.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_per_tick_agent_ids_match_manifest" -q` passed with 2 tests and 221 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 223 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that replays `events.csv` through manifest roles and verifies per-tick role/action event counts match the emitted role/action metric fields across both full-output fixtures.
