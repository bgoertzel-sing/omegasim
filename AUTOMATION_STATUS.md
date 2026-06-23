# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-comparison artifact documentation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 A2 pressure comparison README schema documentation
- Changed: documented `pressure_comparison_metrics.csv` field semantics, pressure-condition subdirectory contents, and the top-level pressure comparison `summary.md` sections in `README.md`; no simulator behavior changed.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure_comparison or high_pressure_comparison_runner_is_reproducible" -q` passed with 3 tests and 435 deselected; `tmpdir=$(mktemp -d); .venv-conda/bin/python -m ohdyn.compare_pressure --seeds 1 2 --out "$tmpdir/a2_attention_pressure_compare" && sed -n '1,90p' "$tmpdir/a2_attention_pressure_compare/summary.md"` passed and showed the documented fixed-policy pressure delta section.
- Blockers: none.
- Next step: add a deterministic A2 pressure comparison test that validates the documented `pressure_comparison_metrics.csv` header exactly against `PRESSURE_COMPARISON_FIELDS`.
