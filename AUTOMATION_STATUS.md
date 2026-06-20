# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest artifact/output test helper
- Changed: factored the repeated no-manifest artifact set, disabled-manifest, normalized output flag, and summary output flag assertions into `_assert_no_manifest_writes_enabled_artifacts()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents tests/test_run_harness.py::test_documented_cli_no_manifest_preserves_stale_manifest_sentinel tests/test_run_harness.py::test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel -q` passed with 3 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated stale-manifest collision assertions shared by CLI/API no-manifest collision regressions.
