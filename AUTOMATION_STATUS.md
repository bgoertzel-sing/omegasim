# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 documented-CLI same-seed event-replay helper reuse
- Changed: refactored documented CLI same-seed event-replay tests for role/action totals, top-level metric sequences, queue-pressure metric sequences, and queued-task-age metric sequences to use the existing `_run_documented_cli_pair` helper with identical seeds while preserving replay, metrics, summary, and reproducibility assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replayed_role_action_totals_reproduce_across_same_seed or event_replayed_top_level_metric_sequence_reproduces_across_same_seed or event_replayed_queue_pressure_metric_sequence_reproduces_across_same_seed or event_replayed_queued_task_age_metric_sequence_reproduces_across_same_seed" -q` passed with 12 tests and 409 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review the remaining documented-CLI same-seed lobe and role/action metric sequence tests for one final `_run_documented_cli_pair` helper reuse, then shift away from narrow A0/A1 test-refactor churn.
