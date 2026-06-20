# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only enabled-artifact collision test helper
- Changed: factored the repeated config-only enabled-artifact collision setup and preservation assertions shared by the run API and documented CLI config-only collision regressions into `_write_config_only_collision_sentinels()` and `_assert_config_only_collision_preserves_stale_disabled_artifacts()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_artifact_collision_blocks_when_all_optional_outputs_disabled tests/test_run_harness.py::test_cli_config_artifact_collision_blocks_when_all_optional_outputs_disabled -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated no-manifest stale-disabled-manifest setup/assertions shared by the CLI/API no-manifest preservation regressions.
