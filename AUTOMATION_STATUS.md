# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action run API rerun collision coverage
- Changed: added run API rerun coverage proving `configs/a0_no_manifest_reordered_actions.yaml` refuses to overwrite existing enabled `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md` artifacts, omits disabled stale `manifest.yaml` from the collision message, preserves the first run and stale manifest byte-for-byte, and keeps normalized reordered-action provenance plus summary artifact indexing intact.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_reordered_actions_rerun_refuses_to_overwrite_enabled_artifacts_and_preserves_stale_manifest" -q` passed with 1 test and 373 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 374 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add seed-difference regression coverage for the no-manifest reordered-action fixture to confirm distinct seeds preserve schema/order invariants while producing different deterministic event or metric streams.
