# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 summary written-artifact parsing helper
- Changed: centralized repeated `summary.md` written-artifact line parsing into `_summary_written_artifacts()` and routed manifest-backed, no-manifest, CLI, and API output-directory regressions through the shared helper.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_written_artifacts_match_manifest_artifacts tests/test_run_harness.py::test_summary_written_artifacts_match_output_directory_contents tests/test_run_harness.py::test_summary_written_artifacts_match_output_directory_contents_without_manifest tests/test_run_harness.py::test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents tests/test_run_harness.py::test_run_api_respects_no_manifest_fixture_outputs -q` passed with 5 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated output-directory artifact listing assertions shared by manifest-backed and no-manifest output regressions.
