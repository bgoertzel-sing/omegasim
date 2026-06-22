# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only reordered-actions CLI/API seed-1 artifact parity regression
- Changed: added one regression comparing documented CLI output with `run_experiment` output for `a0_manifest_only_reordered_actions` seed 1, verifying the enabled artifact set, disabled metrics/events/summary behavior, manifest output flags, manifest artifact provenance, normalized CLI/API config equality, YAML action-order schema alignment, and byte-identical `config.yaml` plus `manifest.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_manifest_only_reordered_actions_seed1_emit_identical_artifacts" -q` passed with 1 test and 409 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 410 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression for `a0_config_only_reordered_actions` seed 1 to compare normalized config bytes while preserving disabled optional-artifact behavior and YAML action-order provenance.
