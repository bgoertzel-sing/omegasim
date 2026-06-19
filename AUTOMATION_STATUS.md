# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 role action metrics update
- Changed: added deterministic per-tick role/action count columns to `metrics.csv` for all five static baseline roles and all four A0/A1 actions; added role action totals to `summary.md`.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 10 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` produced the required artifacts with the new role/action metric columns and summary section.
- Blockers: none.
- Next step: add deterministic hand-coded per-tick baseline lobe labels from action mix and queue state.
