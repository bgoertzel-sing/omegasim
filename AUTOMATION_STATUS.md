# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 default-output CLI/API seed-1 artifact parity regression
- Changed: added one regression comparing documented CLI output with `run_experiment` output for `a0_default_outputs` seed 1, verifying that all five default artifacts are emitted, omitted output flags normalize to enabled, normalized CLI/API config and manifest data are equal, default YAML action order is preserved, metrics/events/schema provenance is retained, summary artifact provenance is present, and emitted artifact bytes are identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_default_outputs_seed1_emit_identical_artifacts" -q` passed with 1 test and 413 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 414 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression for `a0_reordered_actions` seed 1 to compare full-output config, manifest, metrics, events, and summary artifacts while preserving YAML-defined action order.
