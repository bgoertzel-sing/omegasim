# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-condition trajectory-structure summaries on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 threaded existing A2 phase-space dwell and turning-point fields into top-level pressure comparison summaries.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, or per-run artifact contract changes; `ohdyn.compare_pressure` now adds a `## Pressure-condition trajectory structure` section to pressure `summary.md`, reporting fixed-policy normal/medium/high turning-point means, longest-dwell means, high-minus-normal trajectory-structure deltas, and longest-dwell label counts from the already-generated comparison rows; README and regression coverage were updated.
- Smoke run: `.venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out "$tmpdir"` produced the new `## Pressure-condition trajectory structure` summary section with baseline, research-heavy, and internal-improvement rows.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_comparison_runner_writes_fixed_policy_deltas or pressure_summary_includes_trajectory_structure'` passed with 2 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 464 tests.
- Blockers: none.
- Next step: add a machine-readable pressure trajectory-structure companion CSV so downstream analysis can consume the same dwell/turning cross-pressure summaries without Markdown parsing.
