# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 trajectory-structure summaries on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added compact A2 phase-space dwell and turning-point summaries to attention comparison outputs.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or per-run artifact contract changes; `ohdyn.compare_attention` now records per-run phase-space regime dwell runs, longest dwell label/length, turning-point encodings, and turning-point counts in `comparison_metrics.csv`, and reports per-policy dwell/turning summaries in aggregate `summary.md`; README and regression coverage were updated.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_attention --seeds 1 2 --out "$tmpdir"` produced the new `## Phase-space dwell and turning points` summary section.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_attention.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'attention_comparison_runner_writes_aggregate_summary or attention_comparison_runner_is_reproducible or high_pressure_comparison_runner_is_reproducible'` passed with 3 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 463 tests.
- Blockers: none.
- Next step: thread the new attention-comparison dwell/turning fields into the top-level pressure comparison interpretation so pressure-response summaries include trajectory structure across pressure conditions.
