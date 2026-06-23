# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response stability artifacts on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added a machine-readable pressure-response stability agreement artifact.
- Changed: no simulator, scheduling, baseline run harness, or A0/A1 schema behavior changes; `ohdyn.compare_pressure` now writes top-level `pressure_stability_agreement.csv` with one row per proper seed prefix. The CSV records full/prefix seed sets, global top-response stability, per-class capture-pressure stability, combined agreement, both instability-cause fields, and the selected global/class policy, observable, metric, and field. Collision checks now protect the new artifact, README documents it, and regression tests cover header/order, row contents, CLI layout, reproducibility, and overwrite refusal.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out runs/a2_attention_pressure_compare_stability_csv_seed1_2` completed and wrote `pressure_stability_agreement.csv`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_stability or pressure_response_selection or pressure_summary_compares_global'` passed with 4 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 459 tests.
- Blockers: none.
- Next step: use `pressure_stability_agreement.csv` in the larger seed-set pressure inspection to compare when global and class-specific stability converge across prefixes.
