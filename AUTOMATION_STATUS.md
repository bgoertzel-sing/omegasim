# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response summary interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added a selected-source-metric pressure-condition comparison to the pressure comparison summary.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, CSV schema, or artifact layout changes; `ohdyn.compare_pressure` now adds a deterministic `Pressure-condition source metric comparison` section for the full-seed top pressure response. The section reports the selected response's source field plus normal, medium, and high pressure per-seed values, mean, min, and max. README documents the new section and regression coverage asserts it against the generated summary.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare_source_metric_note_seed1_3` completed. The generated summary reports `policy=internal_improvement observable=final queue depth metric=normal_to_medium_slope source_field=queue_depth` with normal/medium/high means `20.666667`, `39.333333`, and `45.666667`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'source_metric_by_condition or pressure_response_interpretation or pressure_stability_convergence'` passed with 3 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 462 tests.
- Blockers: none.
- Next step: add a machine-readable companion row for the selected source-metric condition comparison so downstream scripts do not need to parse `summary.md`.
