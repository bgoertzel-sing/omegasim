# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI lobe run-state parity regression
- Changed: added `test_documented_cli_lobe_run_state_matches_recomputed_dwell_runs_across_full_output_fixtures` and `_assert_lobe_run_state_matches_recomputed_dwell_runs` in `tests/test_run_harness.py` so documented full-output CLI runs keep `baseline_lobe_run_id` and `baseline_lobe_current_run_length` internally consistent with recomputed dwell runs for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "lobe_run_state or lobe_dwell_runs or lobe_aggregates" -q` passed with 10 tests and 149 deselected; `.venv-conda/bin/python -m pytest -q` passed with 159 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep each row's `baseline_lobe_previous_label`, `baseline_lobe_transition`, and `baseline_lobe_transition_tick` internally consistent with adjacent lobe labels across both full-output fixtures.
