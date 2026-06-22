# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action run API summary aggregate parity regression
- Changed: added run API coverage proving `configs/a0_no_manifest_reordered_actions.yaml` emits no `manifest.yaml`, preserves reordered action order in metrics role/action fields, records the expected no-manifest artifact index in `summary.md`, and keeps the integrated summary aggregate bundle equal to the emitted metrics-derived bundle.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_matches_metrics" -q` passed with 1 test and 378 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 379 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API same-seed reproducibility coverage for the no-manifest reordered-action integrated summary aggregate bundle.
