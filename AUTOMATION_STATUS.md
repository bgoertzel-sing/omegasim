# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only reordered-action run API rerun collision coverage
- Changed: added run API rerun coverage proving `configs/a0_manifest_only_reordered_actions.yaml` refuses to overwrite existing enabled `config.yaml` and `manifest.yaml` artifacts, omits disabled `metrics.csv`/`events.csv`/`summary.md` from the collision message, preserves the first run byte-for-byte, and keeps normalized reordered-action manifest provenance intact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_manifest_only_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts" -q` passed with 1 test and 371 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 372 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI rerun collision coverage for the no-manifest reordered-action fixture, matching enabled-artifact collision behavior while preserving stale disabled manifest provenance.
