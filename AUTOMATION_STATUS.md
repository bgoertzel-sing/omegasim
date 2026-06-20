# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI no-manifest summary artifact consistency regression
- Changed: added a documented CLI regression asserting no-manifest runs report exactly their newly written artifacts in `summary.md`, match the output directory contents for a clean run, and exclude `manifest.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_no_manifest_summary_artifacts_match_output_directory_contents -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 93 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI regression for no-manifest runs preserving a stale disabled `manifest.yaml` sentinel byte-for-byte while still writing enabled artifacts and reporting `write_manifest: disabled` in `summary.md`.
