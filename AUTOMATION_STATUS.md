# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 full-output event replay fixture regression
- Changed: reused `_assert_full_output_event_replay_matches_metrics_and_summary` in a parametrized documented-CLI regression for `a0_default_outputs` and `a0_reordered_actions`, so default-output normalization and YAML action-order preservation now share the same event replay checks as the README A0 smoke path.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "full_output_fixture_event_replay or readme_a0_smoke_event_replay" -q` passed with 3 tests and 398 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 401 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise full-output CLI reproducibility regression that compares byte-identical enabled artifacts for `a0_default_outputs` and `a0_reordered_actions` across the same seed.
