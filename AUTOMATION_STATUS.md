# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI summary queue dynamics parity regression
- Changed: added `test_documented_cli_summary_queue_dynamics_match_metrics_across_full_output_fixtures`, `_assert_summary_queue_dynamics_match_metrics`, and `_queue_pressure_totals_from_metrics` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep `summary.md` queue pressure and queued-task-age aggregates aligned with the emitted `metrics.csv` columns for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_summary_queue_dynamics_match_metrics_across_full_output_fixtures" -q` passed with 2 tests and 133 deselected; `.venv-conda/bin/python -m pytest -q` passed with 135 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that full-output documented runs keep `summary.md` baseline lobe totals, transition totals, and dwell-run aggregates aligned with the emitted `metrics.csv` lobe columns across both full-output fixtures.
