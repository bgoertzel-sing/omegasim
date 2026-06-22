# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered-action CLI rerun stale-disabled coverage
- Changed: added documented CLI rerun coverage proving `configs/a0_config_only_reordered_actions.yaml` refuses to overwrite the enabled `config.yaml` artifact while ignoring, byte-preserving, and omitting disabled optional artifact sentinels from the collision error.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "config_only_reordered_actions_rerun_preserves_disabled_artifact_sentinels" -q` passed with 1 test and 368 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 369 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI rerun collision coverage for the config-only reordered-action fixture without disabled sentinels, matching the existing `run_experiment` API parity test.
