# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 summary/output-directory artifact consistency regression
- Changed: added a regression assertion that the `summary.md` written-artifact listing matches the actual output directory file contents for a full enabled-output run.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_written_artifacts_match_output_directory_contents -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 89 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a regression assertion that `summary.md` written-artifact listings match the actual output directory contents when manifest output is disabled but summary output remains enabled.
