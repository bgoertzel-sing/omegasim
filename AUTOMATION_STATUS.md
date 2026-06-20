# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI metrics/events row-count regression
- Changed: added a CLI smoke regression for the documented `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out ...` command, asserting `metrics.csv` has one row per configured tick, `events.csv` has one row per static baseline agent per tick, metric ticks are contiguous, and each tick emits exactly 15 agent events.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_smoke_writes_expected_metrics_and_events_rows -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 38 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a CLI smoke regression that the documented command's `summary.md` includes the core A0/A1 sections for event totals, lobe totals, lobe transitions, dwell runs, and role/action totals.
