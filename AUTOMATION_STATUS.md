# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 event replay regression helper extraction
- Changed: factored the README A0 smoke event replay assertion bundle into `_assert_full_output_event_replay_matches_metrics_and_summary`, preserving the first-milestone CLI coverage while making the top-level queue/task, queue pressure, queued-task age, role/action sequence, lobe sequence/run-state, metrics bundle, and summary bundle checks reusable for future full-output fixtures.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_a0_smoke_event_replay" -q` passed with 1 test and 398 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 399 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: reuse `_assert_full_output_event_replay_matches_metrics_and_summary` in one parametrized full-output fixture regression so the helper protects `a0_default_outputs` and `a0_reordered_actions` without duplicating replay logic.
