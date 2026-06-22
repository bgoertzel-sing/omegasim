# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 config-only reordered-actions CLI/API seed-1 artifact parity regression
- Changed: added one regression comparing documented CLI output with `run_experiment` output for `a0_config_only_reordered_actions` seed 1, verifying that only `config.yaml` is emitted, optional artifacts stay disabled/absent, normalized CLI/API config data is equal, YAML action order is preserved, and `config.yaml` bytes are identical.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_config_only_reordered_actions_seed1_emit_identical_artifacts" -q` passed with 1 test and 410 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 411 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise CLI/API parity regression for `a0_config_only` seed 1 to compare normalized config bytes while preserving disabled optional-artifact behavior and default YAML action-order provenance.
