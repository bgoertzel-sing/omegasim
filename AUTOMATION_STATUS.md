# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI manifest-only artifact consistency regression
- Changed: added a documented CLI regression asserting manifest-only runs list exactly the actual output directory contents in `manifest.yaml` and do not write disabled metrics, events, or summary artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_manifest_only_artifacts_match_output_directory_contents -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 92 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI regression for no-manifest runs asserting `summary.md` written-artifact reporting matches the actual output directory contents and excludes `manifest.yaml`.
