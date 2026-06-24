# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 machine-readable pressure-condition trajectory-structure artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added the machine-readable A2 pressure trajectory-structure companion CSV.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or per-run artifact contract changes; `ohdyn.compare_pressure` now writes top-level `pressure_trajectory_structure.csv` with one row per fixed policy, normal/medium/high turning-point means, longest-dwell-step means, high-minus-normal deltas, and longest-dwell label-count encodings matching the existing `## Pressure-condition trajectory structure` summary section; collision checks, CLI/reproducibility coverage, README, and regression tests were updated.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_trajectory_structure or pressure_comparison_runner_writes_fixed_policy_deltas or documented_pressure_cli_writes_pressure_layout_and_curve_summary or documented_pressure_cli_reproduces_top_level_artifacts or documented_pressure_cli_refuses_existing_top_level_artifacts_without_modifying_them'` passed with 5 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 465 tests.
- Blockers: none.
- Next step: add a small deterministic README/CLI smoke note for consuming `pressure_trajectory_structure.csv` alongside `pressure_comparison_metrics.csv` in downstream analysis.
