# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 CLI validation artifact-safety regression
- Changed: routed CLI config/YAML/load errors through argparse validation output and added a subprocess regression proving invalid baseline actions exit nonzero without a traceback or output artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_cli_validation_error_does_not_write_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 32 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add CLI regression coverage for malformed YAML syntax errors before writing any run artifacts.
