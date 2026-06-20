# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest stale-disabled-manifest test helper
- Changed: factored the repeated no-manifest stale disabled `manifest.yaml` setup and preservation assertions shared by the documented CLI and run API preservation regressions into `_write_no_manifest_disabled_manifest_sentinel()` and `_assert_no_manifest_preserves_stale_disabled_manifest()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_no_manifest_preserves_stale_manifest_sentinel tests/test_run_harness.py::test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated no-manifest emitted-artifact schema provenance assertions shared by the CLI/API no-manifest schema regressions.
