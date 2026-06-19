# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 deterministic queue pressure metrics
- Changed: added per-tick queue pressure balance fields to `metrics.csv` (`created_completed_balance_tick`, `created_worked_balance_tick`, `work_completion_gap_tick`, `backlog_pressure_tick`) and surfaced final backlog/balance totals in `summary.md` with regression coverage.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 14 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add deterministic backlog age metrics for queued tasks, including per-tick max/mean queued task age in `metrics.csv` and final age summary lines in `summary.md`.
