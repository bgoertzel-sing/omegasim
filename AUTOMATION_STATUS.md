# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 default-output different-seed schema-order regression
- Changed: added a documented-CLI regression for `a0_default_outputs` that runs seeds 1 and 2, verifies all full-output artifacts are present, proves omitted output flags normalize to full outputs, keeps normalized config plus manifest action/config/schema provenance aligned, checks metrics and events header order, and confirms seed-sensitive metrics or events content changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "default_outputs_different_seed_preserves_full_schema_order" -q` passed with 1 test and 404 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 405 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise documented-CLI regression that proves `a0_no_manifest` different-seed runs preserve normalized config, metrics header order, event header order, and summary schema provenance while changing seed-sensitive event or metric content without writing `manifest.yaml`.
