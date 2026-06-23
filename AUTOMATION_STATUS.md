# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response machine-readable artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added machine-readable selected-source-metric pressure-condition fields to `pressure_response_selection.csv`.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or artifact layout changes; `ohdyn.compare_pressure` now includes the selected response `source_field` plus normal, medium, and high pressure source-metric mean/min/max/per-seed values on every pressure response selection row. README documents the CSV extension and regression coverage asserts that the full selection row mirrors the source-metric condition comparison values previously available only in `summary.md`.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare_source_metric_csv_seed1_3` completed. The generated `pressure_response_selection.csv` full row reports `policy=internal_improvement observable=final queue depth metric=normal_to_medium_slope source_field=queue_depth` with normal/medium/high source-metric means `20.666667`, `39.333333`, and `45.666667`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'source_metric_by_condition or pressure_response_selection'` passed with 2 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 462 tests.
- Blockers: none.
- Next step: add a small downstream-friendly smoke assertion that `pressure_response_selection.csv` source-metric condition fields stay byte-reproducible across two documented CLI runs.
