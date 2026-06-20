# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 output-directory artifact assertion helper
- Changed: factored repeated output-directory artifact listing checks into `_directory_artifacts()`, `_assert_artifacts_match_output_directory()`, and `_assert_summary_written_artifacts_match_output_directory()`, then routed manifest-backed and no-manifest parity regressions through the shared helpers.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_written_artifacts_match_output_directory_contents tests/test_run_harness.py::test_summary_written_artifacts_match_output_directory_contents_without_manifest tests/test_run_harness.py::test_manifest_artifacts_match_output_directory_contents_when_manifest_only tests/test_run_harness.py::test_documented_cli_manifest_only_artifacts_match_output_directory_contents tests/test_run_harness.py::test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents tests/test_run_harness.py::test_run_api_respects_no_manifest_fixture_outputs -q` passed with 6 tests; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: consolidate the remaining direct artifact-set assertions in default-output, config-only, and stale-sentinel regressions through the shared output-directory helper.
