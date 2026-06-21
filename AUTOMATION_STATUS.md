# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI first-row queue pressure parity regression
- Changed: added `test_documented_cli_first_row_queue_pressure_fields_match_summary_across_full_output_fixtures` plus `_assert_first_row_queue_pressure_fields_match_summary` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep first-row queue pressure identities valid and keep the top-level queue pressure summary lines aligned with metrics-derived final/aggregate values for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "first_row_queue_pressure or queue_dynamics or static_bus_metrics" -q` passed with 9 tests and 144 deselected; `.venv-conda/bin/python -m pytest -q` passed with 153 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep queued-task-age summary lines aligned with metrics-derived final, peak, and mean age values across both full-output fixtures.
