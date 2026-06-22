# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only default-actions CLI/API seed-1 artifact parity regression
- Changed: added one regression comparing documented CLI output with `run_experiment` output for `a0_manifest_only` seed 1, verifying that only `config.yaml` and `manifest.yaml` are emitted, metrics/events/summary stay disabled/absent, normalized CLI/API config and manifest data are equal, default YAML action order is preserved, manifest schema provenance is retained, and emitted artifact bytes are identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_manifest_only_seed1_emit_identical_artifacts" -q` passed with 1 test and 412 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 413 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression for `a0_default_outputs` seed 1 to compare full-output config, manifest, metrics, events, and summary artifacts while preserving default output-flag normalization.
