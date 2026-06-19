# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 bus graph metrics update
- Changed: added deterministic per-tick NetworkX bus graph summary metrics to `metrics.csv` (`bus_density`, `bus_mean_degree`, `bus_degree_centralization`) and surfaced density/centralization in `summary.md`.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 9 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` produced the required artifacts with the new graph metric columns.
- Blockers: none.
- Next step: add A1 per-tick role-level action metrics so coordination dynamics can be compared by agent role.
