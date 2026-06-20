# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 artifact schema provenance test helper
- Changed: centralized repeated summary artifact-schema provenance assertions into `_assert_summary_records_artifact_schema_provenance()` and reused it from both the manifest-backed summary provenance regression and the no-manifest emitted-artifact schema provenance helper.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_records_artifact_schema_provenance tests/test_run_harness.py::test_documented_cli_no_manifest_emitted_artifacts_preserve_schema_provenance tests/test_run_harness.py::test_run_api_no_manifest_emitted_artifacts_preserve_schema_provenance -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated no-manifest enabled-artifact row-count assertions shared by the API and documented CLI no-manifest output regressions.
