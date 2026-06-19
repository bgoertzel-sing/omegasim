# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 deterministic queued task age metrics
- Changed: added per-tick queued backlog age fields to `metrics.csv` (`queued_task_age_max_tick`, `queued_task_age_mean_tick`) and surfaced final/peak/mean queued task age summaries in `summary.md` with event-reconstruction regression coverage.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 15 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add fixed-seed golden regression coverage for the new queue age summary values across the existing seed set.
