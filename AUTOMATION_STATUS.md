# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream consumption notes for machine-readable pressure comparison artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 documented deterministic downstream consumption of the A2 pressure comparison CSV pair.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or artifact writer changes; README now states that downstream analysis should join `pressure_comparison_metrics.csv` and `pressure_trajectory_structure.csv` on stable `policy`, use the former for pressure-response slopes/curvature and queue/throughput/capture-pressure observables, and use the latter for fixed-policy turning-point and longest-dwell trajectory summaries; the documented pressure CLI smoke test now checks that both top-level CSVs expose the same policy row order.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k documented_pressure_cli_writes_pressure_layout_and_curve_summary` passed with 1 selected test.
- Verified: `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 465 tests.
- Blockers: none.
- Next step: add one executable A2 analysis helper that reads the pressure comparison CSV pair by `policy` and emits a compact deterministic trajectory-vs-pressure ranking artifact.
