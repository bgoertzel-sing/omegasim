# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest enabled-artifact row-count test helper
- Changed: centralized no-manifest enabled-artifact CSV row-count assertions into `_assert_no_manifest_enabled_artifact_row_counts()` and routed CLI/API no-manifest output regressions through `_assert_no_manifest_writes_enabled_artifacts()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_respects_disabled_manifest_output tests/test_run_harness.py::test_run_api_respects_no_manifest_fixture_outputs tests/test_run_harness.py::test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated summary written-artifact line parsing shared by manifest-backed and no-manifest output-directory regressions.
