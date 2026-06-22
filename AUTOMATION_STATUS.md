# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action documented CLI rerun collision coverage
- Changed: added documented CLI rerun coverage proving `configs/a0_no_manifest_reordered_actions.yaml` refuses to overwrite existing enabled `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md` artifacts, omits disabled stale `manifest.yaml` from the collision message, preserves the first run and stale manifest byte-for-byte, and keeps normalized reordered-action provenance plus summary artifact indexing intact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "cli_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts" -q` passed with 1 test and 372 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 373 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API rerun collision coverage for the no-manifest reordered-action fixture, matching the documented CLI stale-manifest preservation and enabled-artifact collision behavior.
