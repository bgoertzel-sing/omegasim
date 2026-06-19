# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 baseline lobe transition update
- Changed: added deterministic per-tick `baseline_lobe_previous_label`, `baseline_lobe_transition`, and `baseline_lobe_transition_tick` columns to `metrics.csv`; `summary.md` now includes aggregate baseline lobe transition counts excluding start/stable ticks.
- Verified: `.venv-conda/bin/python -m pytest -q` passed with 12 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` produced the required artifacts with lobe transition columns and summary counts.
- Blockers: none.
- Next step: add a bounded multi-seed A1 smoke test that compares lobe totals and transition totals across fixed seeds without introducing sweep infrastructure.
