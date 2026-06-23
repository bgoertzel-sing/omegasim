# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 documented-CLI different-seed summary aggregate helper reuse
- Changed: refactored documented CLI different-seed summary aggregate tests for queue pressure totals, task/queue totals, event-type totals, queued-task-age aggregates, integrated summary bundle, queue pressure/age tuple, and role/action summary totals to use the existing `_run_documented_cli_pair` helper while preserving their summary, metrics, events, and seed-variation assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_queue_pressure_totals_change_across_different_seeds or summary_task_and_queue_totals_change_across_different_seeds or summary_event_type_totals_change_across_different_seeds or summary_queued_task_age_aggregates_change_across_different_seeds or integrated_summary_aggregate_bundle_changes_across_different_seeds or summary_task_queue_pressure_and_age_aggregate_tuple_changes_across_different_seeds or role_action_summary_totals_changes_across_different_seeds" -q` passed with 23 tests and 398 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review documented-CLI same-seed summary aggregate tests for one narrow `_run_documented_cli_pair` helper reuse without changing reproducibility assertions.
