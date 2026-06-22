# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action run API different-seed schema regression
- Changed: added run API coverage proving `configs/a0_no_manifest_reordered_actions.yaml` runs with seeds 1 and 2 emit no `manifest.yaml`, preserve normalized reordered action order in metrics role/action fields, keep metrics/events headers stable, record the expected no-manifest artifact index in both summaries, retain identical normalized config, and still produce seed-sensitive in-memory and written metrics/events.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_reordered_actions_seed_difference_preserves_schema_order" -q` passed with 1 test and 377 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 378 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API summary aggregate parity coverage for the no-manifest reordered-action fixture to mirror the documented CLI metrics-to-summary integrity checks.
