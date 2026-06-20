# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only stale-disabled-artifact test helper
- Changed: factored the repeated config-only stale-disabled-artifact setup and preservation assertions shared by the documented CLI/API config-only preservation regressions into `_write_config_only_disabled_artifact_sentinels()` and `_assert_config_only_preserves_stale_disabled_artifacts()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_config_only_preserves_stale_disabled_artifact_sentinels tests/test_run_harness.py::test_run_api_config_only_preserves_stale_disabled_artifact_sentinels -q` passed with 2 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated config-only enabled-artifact collision setup/assertions shared by the CLI/API config-only collision regressions.
