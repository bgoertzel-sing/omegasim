# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 artifact schema documentation
- Changed: documented the current baseline runner shape, 15-agent role set, lobe labels, and `config.yaml` / `manifest.yaml` / `metrics.csv` / `events.csv` / `summary.md` artifact schema in `README.md`.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 23 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add a focused metrics/events header regression test for the documented A0/A1 artifact schema.
