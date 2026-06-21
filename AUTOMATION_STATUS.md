# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest queue-dynamics metrics-field schema regression
- Changed: added `test_documented_cli_manifest_queue_dynamics_fields_exactly_match_metrics_header_subsets_across_full_output_fixtures` and `_assert_manifest_queue_dynamics_fields_match_metrics_header_subsets` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.queue_dynamics_metrics.pressure_fields` and `queued_task_age_fields` exactly match their emitted `metrics.csv` header subsets and the canonical queue metric constants for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_queue_dynamics_fields or manifest_role_action_fields or manifest_metrics_fields or manifest_event_fields" -q` passed with 12 tests and 163 deselected; `.venv-conda/bin/python -m pytest -q` passed with 175 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that the manifest baseline lobe vocabulary and lobe transition field list exactly match the emitted metrics header subsets and observed labels across both full-output fixtures.
