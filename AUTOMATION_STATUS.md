# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI bus-count parity regression
- Changed: added `test_documented_cli_manifest_bus_counts_match_summary_and_first_metrics_row_across_full_output_fixtures` and `_assert_manifest_bus_counts_match_summary_and_metrics_row` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep manifest bus node/edge counts aligned with `summary.md` and the first `metrics.csv` row for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_bus_counts_match_summary" -q` passed with 2 tests and 147 deselected; `.venv-conda/bin/python -m pytest -q` passed with 149 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep first-row static bus density, mean degree, and degree centralization aligned with the `summary.md` bus metric lines across both full-output fixtures.
