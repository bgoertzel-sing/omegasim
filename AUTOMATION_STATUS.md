# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 documented-CLI different-seed event-replay helper reuse
- Changed: refactored the documented CLI different-seed event-replay role/action totals, role/action metric sequence, top-level metric sequence, queue-pressure sequence, and queued-task-age sequence tests to use the existing `_run_documented_cli_pair` helper while preserving their replay and seed-variation assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replayed_role_action_totals_change_across_different_seeds or event_replayed_role_action_metric_sequence_changes_across_different_seeds or event_replayed_top_level_metric_sequence_changes_across_different_seeds or event_replayed_queue_pressure_metric_sequence_changes_across_different_seeds or event_replayed_queued_task_age_metric_sequence_changes_across_different_seeds" -q` passed with 15 tests and 406 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review documented-CLI different-seed summary aggregate tests for one narrow `_run_documented_cli_pair` helper reuse without changing summary or seed-variation assertions.
