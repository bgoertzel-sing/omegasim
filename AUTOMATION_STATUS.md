# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 reordered-actions no-manifest event replay sequence helper reuse
- Changed: added `_no_manifest_reordered_actions_event_replay_sequences` in `tests/test_run_harness.py` and reused it in the remaining reordered-actions no-manifest per-tick and lobe sequence replay regressions. The refactor centralizes normalized config, metrics/events loading, no-manifest/action-order checks, role reconstruction, event-derived queue/role/lobe sequence generation, and lobe row reconstruction while preserving each test's sequence-specific parity and different-seed assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events" -q` passed with 2 tests and 419 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review the no-manifest reordered-actions replay helpers for any remaining duplicated artifact/config loading paths that can be safely consolidated without weakening explicit reproducibility assertions.
