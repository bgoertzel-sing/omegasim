# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI per-tick event population regression
- Changed: added a documented-CLI regression across both full-output fixtures that loads the normalized config and verifies `events.csv` has exactly the configured 15-agent population on every tick, full tick coverage, and total event count equal to ticks times agents.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "events_per_tick_counts_match_configured_agent_population" -q` passed with 2 tests and 219 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 221 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one documented-CLI regression that verifies each tick's `events.csv` agent IDs are unique and exactly cover the manifest agent IDs across both full-output fixtures.
