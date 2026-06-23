# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 no-manifest event replay bundle assertion helper extracted
- Changed: added shared `_assert_no_manifest_event_replay_bundle_matches_metrics_and_summary` coverage in `tests/test_run_harness.py` and rewired the default-action no-manifest CLI/API/readme replay regressions to use it. The helper verifies emitted artifact contents, absence of `manifest.yaml`, config-derived roles/actions, event replay against `metrics.csv`, summary aggregate parity, and lobe label/transition/dwell reconstruction.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_default_actions_event_replay or readme_no_manifest_default_actions_event_replay_bundle_reproducibility" -q` passed with 5 tests and 416 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: apply the shared no-manifest event-replay bundle helper to the reordered-actions no-manifest replay regressions.
