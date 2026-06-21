# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI lobe dwell-run summary parity regression
- Changed: added `test_documented_cli_lobe_dwell_runs_summary_matches_metrics_across_full_output_fixtures` and factored `_assert_lobe_dwell_run_summary_matches_metrics` in `tests/test_run_harness.py` so documented full-output CLI runs keep lobe dwell-run summary lines aligned with metrics-derived runs, total ticks, max run, and mean run for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_dwell_runs or lobe_aggregates" -q` passed with 6 tests and 151 deselected; `.venv-conda/bin/python -m pytest -q` passed with 157 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep baseline lobe run IDs and current run lengths internally consistent with recomputed dwell runs across both full-output fixtures.
