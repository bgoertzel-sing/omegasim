# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 reordered-actions different-seed schema-order regression
- Changed: added a documented-CLI regression for `a0_reordered_actions` that runs seeds 1 and 2, verifies all full-output artifacts are present, proves normalized config plus manifest action/config/schema provenance stay aligned, checks metrics and events header order, and confirms seed-sensitive metrics or events content changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "reordered_actions_different_seed_preserves_full_schema_order" -q` passed with 1 test and 403 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 404 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise documented-CLI regression that proves `a0_default_outputs` different-seed runs preserve the same normalized config, defaulted manifest output flags, metrics header order, and event header order while changing seed-sensitive event or metric content.
