# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI static bus metric parity regression
- Changed: added `bus mean degree` to `summary.md`, documented the summary's static bus metrics in `README.md`, and added `test_documented_cli_summary_static_bus_metrics_match_first_metrics_row_across_full_output_fixtures` plus `_assert_summary_static_bus_metrics_match_metrics_row` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep first-row `bus_density`, `bus_mean_degree`, and `bus_degree_centralization` aligned with the summary for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "static_bus_metrics or metrics_csv_records_bus_graph_summary" -q` passed with 3 tests and 148 deselected; `.venv-conda/bin/python -m pytest -q` passed with 151 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep first-row queue pressure fields aligned with the top-level queue pressure lines in `summary.md` across both full-output fixtures.
