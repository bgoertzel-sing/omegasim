# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 baseline lobe label update
- Changed: added deterministic per-tick `baseline_lobe_label` and `queue_delta_tick` columns to `metrics.csv`; labels are hand-coded from action mix plus queue depth/delta, and lobe totals are now included in `summary.md`.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 11 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` produced the required artifacts with lobe label columns and summary totals.
- Blockers: none.
- Next step: add deterministic lobe transition counts so A1 can compare coordination phase changes across seeds.
