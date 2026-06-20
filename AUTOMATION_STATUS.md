# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 mandatory config artifact collision regression
- Changed: added direct API and CLI regression coverage proving `config.yaml` remains a mandatory run artifact and blocks reruns even when every optional output flag is disabled, while disabled optional artifact sentinels are ignored and left untouched.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled tests/test_run_harness.py::test_cli_config_artifact_collision_blocks_when_all_optional_outputs_disabled -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 61 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add focused direct API and CLI regressions that a config-only run with all optional outputs disabled succeeds, writes exactly `config.yaml`, and is byte-stable for the same seed.
