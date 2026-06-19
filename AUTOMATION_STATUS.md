# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 missing config CLI artifact-safety regression
- Changed: added a subprocess regression proving a missing config file exits nonzero through argparse, includes the requested config path, avoids tracebacks, and writes no run artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_cli_missing_config_error_does_not_write_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 34 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add artifact-safety regression coverage for output path collisions before partial run artifacts are written.
