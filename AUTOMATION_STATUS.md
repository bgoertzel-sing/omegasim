# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI queued-task-age summary parity regression
- Changed: added `test_documented_cli_queued_task_age_summary_matches_metrics_across_full_output_fixtures` plus `_assert_queued_task_age_summary_matches_metrics` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep final, peak, and mean queued-task-age summary lines aligned with metrics-derived values for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "queued_task_age_summary or queue_dynamics or first_row_queue_pressure" -q` passed with 9 tests and 146 deselected; `.venv-conda/bin/python -m pytest -q` passed with 155 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep lobe dwell-run summary lines aligned with metrics-derived runs, total ticks, max run, and mean run across both full-output fixtures.
