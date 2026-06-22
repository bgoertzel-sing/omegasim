# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest run-API different-seed emitted-schema regression
- Changed: added the run-API companion regression for `a0_no_manifest` that runs seeds 1 and 2, verifies only enabled artifacts are present, confirms `manifest.yaml` is not written, preserves normalized config/output flags plus metrics and event header order, checks summary schema provenance, and confirms seed-sensitive metrics or events content changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_different_seed_preserves_emitted_schema_order" -q` passed with 1 test and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 407 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression that compares `a0_no_manifest` seed-1 output content between documented CLI and `run_experiment` while preserving disabled-manifest behavior.
