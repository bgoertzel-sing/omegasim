# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 deterministic normal-pressure versus high-pressure comparison helper for attention-policy phase-space sensitivity experiments on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 pressure comparison helper
- Changed: added `ohdyn.compare_pressure`, which composes the existing normal-pressure and high-pressure attention comparison runs into `normal_pressure/` and `high_pressure/`, then writes `pressure_comparison_metrics.csv` and a top-level `summary.md` with fixed-policy high-minus-normal pressure deltas for phase-space regime distributions and core queue/value metrics; documented the CLI in `README.md`; added regression coverage for pressure comparison artifacts and reproducibility.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure_comparison or high_pressure_comparison_runner_is_reproducible" -q` passed with 3 tests and 435 deselected; `.venv-conda/bin/python -m ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out "$tmpdir/a2_attention_pressure_compare" && sed -n '1,90p' "$tmpdir/a2_attention_pressure_compare/summary.md"` passed and showed deterministic fixed-policy pressure deltas; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 438 tests.
- Blockers: none.
- Next step: add README output-schema documentation for `pressure_comparison_metrics.csv` fields and pressure comparison summary sections.
