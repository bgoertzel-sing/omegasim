# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 multi-seed lobe regression smoke
- Changed: added a bounded test that runs seeds 1, 2, and 17 through the existing harness and compares deterministic baseline lobe totals plus lobe-transition totals without adding sweep infrastructure.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 13 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed and the tracked smoke artifacts remained byte-stable.
- Blockers: none.
- Next step: add deterministic queue pressure metrics to `metrics.csv` and `summary.md` for created-worked-completed balance per tick and final backlog pressure.
