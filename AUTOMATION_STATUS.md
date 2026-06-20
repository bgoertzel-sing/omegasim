# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest stale-manifest collision test helper
- Changed: factored the repeated stale-manifest/collision sentinel setup and preservation assertions shared by the CLI/API no-manifest enabled-artifact collision regressions into `_write_no_manifest_collision_sentinels()` and `_assert_no_manifest_collision_preserves_stale_manifest()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_no_manifest_refuses_enabled_artifact_collisions_while_preserving_stale_manifest tests/test_run_harness.py::test_run_api_no_manifest_refuses_enabled_artifact_collisions_while_ignoring_stale_manifest -q` passed with 8 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated manifest-only stale-disabled-artifact setup/assertions shared by the CLI/API manifest-only preservation regressions.
