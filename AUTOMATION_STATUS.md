# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 full-output/no-manifest event replay context helper consolidation
- Changed: added shared `_event_replay_context` in `tests/test_run_harness.py` for loading normalized config, optional manifest, summary, metrics/events rows, actions, run shape, role mapping, and event-derived lobe rows. `_assert_full_output_event_replay_matches_metrics_and_summary` now uses this common context with manifest-required roles, while `_no_manifest_event_replay_context` layers no-manifest assertions on the same loader with baseline role reconstruction.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "event_replay_reconstructs_first_milestone_summaries or full_output_fixture_event_replay_reconstructs_summaries or no_manifest_default_actions_event_replay or no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events" -q` passed with 10 tests and 411 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review same-seed/different-seed event replay tests for one small shared pair-run helper that does not change simulator behavior or artifact schemas.
