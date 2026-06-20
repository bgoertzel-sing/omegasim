# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 explicit CLI invalid-seed validation
- Changed: added a run-boundary seed validator requiring non-negative integer seeds before config loading, simulation, or output writing; added a documented CLI regression proving `--seed -1` fails with a clean parser error, no traceback, and no output artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_cli_invalid_seed_error_does_not_write_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 47 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add direct `run_experiment` invalid-seed regression coverage so API callers get the same no-artifact guarantee as the CLI.
