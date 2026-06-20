# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 manifest-only stale-disabled-artifact test helper
- Changed: factored the repeated manifest-only stale-disabled-artifact setup and preservation assertions shared by the CLI/API preservation and enabled-artifact collision regressions into `_write_manifest_only_disabled_artifact_sentinels()`, `_assert_manifest_only_preserves_stale_disabled_artifacts()`, `_write_manifest_only_collision_sentinels()`, and `_assert_manifest_only_collision_preserves_stale_disabled_artifacts()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_manifest_only_preserves_stale_disabled_artifact_sentinels tests/test_run_harness.py::test_documented_cli_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts tests/test_run_harness.py::test_run_api_manifest_only_preserves_stale_disabled_artifact_sentinels tests/test_run_harness.py::test_run_api_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts -q` passed with 6 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated config-only stale-disabled-artifact setup/assertions shared by the CLI/API config-only preservation regressions.
