# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 no-manifest event replay context helper consolidation
- Changed: added `_no_manifest_event_replay_context` in `tests/test_run_harness.py` and reused it from both `_assert_no_manifest_event_replay_bundle_matches_metrics_and_summary` and `_no_manifest_reordered_actions_event_replay_sequences`. The shared helper now centralizes normalized config, summary, metrics/events loading, no-manifest checks, role reconstruction, and event-derived lobe row reconstruction while keeping reordered-action order assertions in the reordered-only helper.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events" -q` passed with 2 tests and 419 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_default_actions_event_replay or no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events" -q` passed with 7 tests and 414 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review full-output and no-manifest event replay helpers for a small shared context loader that preserves manifest-specific assertions and avoids another action-order coupling.
