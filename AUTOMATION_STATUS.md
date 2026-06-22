# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 reordered-actions CLI/API seed-1 artifact parity regression
- Changed: added one regression comparing documented CLI output with `run_experiment` output for `a0_reordered_actions` seed 1, verifying that all five full-output artifacts are emitted, YAML-defined action order is preserved in normalized config, manifest actions, manifest metrics schema, manifest role/action schema, and metrics headers, summary schema provenance is retained, and emitted artifact bytes are identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_reordered_actions_seed1_emit_identical_artifacts" -q` passed with 1 test and 414 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 415 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression for the documented `a0_smoke` seed 1 full-output path to compare config, manifest, metrics, events, and summary artifacts for the 100-tick baseline fixture.
