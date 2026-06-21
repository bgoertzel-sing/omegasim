# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI queued-task-age event replay regression
- Changed: added a documented-CLI regression across both full-output fixtures that replays FIFO task queue order from events.csv and verifies the reconstructed queued_task_age_max_tick and queued_task_age_mean_tick values match metrics.csv for every tick.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replay_reproduces_queued_task_age_metrics" -q` passed with 2 tests and 217 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 219 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor the duplicated in-process and documented-CLI task queue event replay checks into one shared helper while preserving the existing metrics and summary assertions.
