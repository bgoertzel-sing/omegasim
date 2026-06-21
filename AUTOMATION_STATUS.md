# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest role/action metrics-field schema regression
- Changed: added `test_documented_cli_manifest_role_action_fields_exactly_match_metrics_header_subset_across_full_output_fixtures` and `_assert_manifest_role_action_fields_match_metrics_header_subset` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.role_action_metrics.fields` exactly matches the role-prefixed subset of the emitted `metrics.csv` header and `role_action_metric_fields(...)` for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_role_action_fields or manifest_metrics_fields or manifest_event_fields" -q` passed with 8 tests and 165 deselected; `.venv-conda/bin/python -m pytest -q` passed with 173 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that manifest `model.queue_dynamics_metrics` pressure and queued-task-age field lists exactly match the corresponding emitted `metrics.csv` header subsets across both full-output fixtures.
