# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 README-anchored default-action no-manifest event replay reproducibility regression added
- Changed: added one concise README-anchored `a0_no_manifest` default-action regression that verifies the documented command text, runs same-seed and different-seed no-manifest outputs through `python -m ohdyn.run`, reconstructs integrated lobe/task-queue/role-action bundles from `events.csv` using roles derived from normalized `config.yaml`, compares those bundles against `metrics.csv` and `summary.md`, verifies no `manifest.yaml` dependency, and asserts same-seed equality plus different-seed divergence.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_no_manifest_default_actions_event_replay_bundle_reproducibility" -q` passed with 1 test and 420 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: extract a shared no-manifest event-replay bundle assertion helper to reduce duplication before adding more A0/A1 replay regressions.
