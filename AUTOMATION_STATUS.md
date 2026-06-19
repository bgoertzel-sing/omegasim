# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 fixed-seed queue age summary regression coverage
- Changed: added golden regression coverage for queued task age summary values across seeds 1, 2, and 17, checking both metrics-derived values and rendered `summary.md` lines.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 16 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add fixed-seed golden regression coverage for role action totals across the existing seed set.
