# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 executable downstream consumption helper for machine-readable pressure comparison artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added deterministic A2 pressure analysis helper that consumes the pressure comparison CSV pair without rerunning simulations.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or artifact writer changes; added `ohdyn.analyze_pressure` CLI/API to read `pressure_comparison_metrics.csv` and `pressure_trajectory_structure.csv`, join them by `policy`, and write `trajectory_pressure_ranking.csv` plus `summary.md`; README documents the helper command and output contract; tests cover direct helper output and documented CLI reproducibility.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 2 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 467 tests.
- Blockers: none.
- Next step: add missing-input and existing-output collision regression tests for `ohdyn.analyze_pressure` before expanding the analysis surface.
