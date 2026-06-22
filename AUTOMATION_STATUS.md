# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action run API integrated summary aggregate reproducibility regression
- Changed: added run API same-seed coverage proving two `configs/a0_no_manifest_reordered_actions.yaml` runs with seed 17 emit no `manifest.yaml`, preserve reordered action order, return identical metrics/events, keep each integrated summary aggregate bundle equal to the emitted metrics-derived bundle, and reproduce that bundle exactly across runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reproduces_across_same_seed" -q` passed with 1 test and 379 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 380 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API different-seed coverage for the no-manifest reordered-action integrated summary aggregate bundle.
