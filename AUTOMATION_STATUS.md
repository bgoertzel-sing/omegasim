# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 artifact index regression across output fixtures
- Changed: added `test_artifact_indexes_match_directory_contents_across_output_flag_fixtures()` plus `_assert_artifact_indexes_match_directory_contents()` to verify that actual directory contents, manifest artifact lists when present, and summary written-artifact lines when present stay aligned for default-output, config-only, manifest-only, and no-manifest checked-in fixtures without simulator behavior changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "artifact_indexes_match_directory_contents" -q` passed with 4 tests and 115 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "artifact or output or manifest_only or no_manifest or config_only" -q` passed with 83 tests and 36 deselected; `.venv-conda/bin/python -m pytest -q` passed with 119 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: consolidate repeated expected artifact lists in output-flag tests into one local fixture/helper so future output artifact additions update one source in the test suite.
