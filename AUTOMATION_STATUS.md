# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 API config-only byte-stability fixture promotion
- Changed: promoted `test_run_experiment_config_only_outputs_succeed_and_are_byte_stable` to use the checked-in `configs/a0_config_only.yaml` fixture instead of constructing an inline all-optional-disabled YAML file, and added normalized fixture metadata assertions matching the CLI coverage.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_only_outputs_succeed_and_are_byte_stable tests/test_run_harness.py::test_cli_config_only_outputs_succeed_and_are_byte_stable tests/test_run_harness.py::test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 68 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: promote the API-side config-only rerun overwrite regression to use the checked-in `configs/a0_config_only.yaml` fixture.
