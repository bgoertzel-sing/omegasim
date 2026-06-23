# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 reordered-actions no-manifest event replay helper reuse
- Changed: applied `_assert_no_manifest_event_replay_bundle_matches_metrics_and_summary` to the reordered-actions no-manifest CLI same-seed replay regression, CLI different-seed replay regression, and README lobe replay smoke test in `tests/test_run_harness.py`. The refactor keeps explicit same/different seed event-row and aggregate-bundle checks while centralizing emitted artifact, no-manifest, config action order, event replay, metrics parity, summary parity, and lobe label/transition/dwell assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events or readme_no_manifest_reordered_actions_lobe_replay_smoke_command" -q` passed with 3 tests and 418 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: add a small shared event-replay sequence helper for the remaining reordered-actions no-manifest per-tick and lobe sequence regressions without removing their sequence-specific assertions.
