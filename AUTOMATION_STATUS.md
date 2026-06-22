# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 full-output enabled-artifact reproducibility regression
- Changed: added a parametrized documented-CLI regression for `a0_default_outputs` and `a0_reordered_actions` that runs each full-output fixture twice with the same seed, verifies enabled artifact presence plus config/manifest action and output provenance, and compares every enabled artifact byte-for-byte.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "full_output_fixture_same_seed_reproduces_byte_identical_enabled_artifacts" -q` passed with 2 tests and 401 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 403 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise documented-CLI regression that proves `a0_reordered_actions` different-seed runs preserve the same normalized config, manifest schema fields, metrics header order, and event header order while changing seed-sensitive event or metric content.
