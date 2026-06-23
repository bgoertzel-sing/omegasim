# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-response summary interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added a convergence-vs-interpretation note to the pressure comparison summary.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, CSV schema, or artifact layout changes; `ohdyn.compare_pressure` now adds one deterministic `Pressure-stability convergence inspection` bullet contrasting the first globally stable prefix with the full-seed top response selected in `Pressure-response interpretation`. README documents the note and regression coverage asserts it against the generated summary.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 3 --out runs/a2_attention_pressure_compare_convergence_note_seed1_3` completed. The generated summary reports `pressure-response interpretation selects policy=internal_improvement observable=final queue depth metric=normal_to_medium_slope; first_global_stable_prefix=none, last_prefix=1,2, last_global_stable=false`.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_stability_convergence or pressure_summary_compares_global or pressure_response_interpretation'` passed with 3 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 461 tests.
- Blockers: none.
- Next step: add an aggregate note that compares normal, medium, and high pressure condition summaries for the selected top response's source metric.
