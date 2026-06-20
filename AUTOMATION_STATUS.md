# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 direct API invalid-seed regression
- Changed: added direct `run_experiment` invalid-seed regression coverage for negative, boolean, and non-integer seeds, proving API callers fail before config loading and before any output directory or artifacts are created.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_invalid_seed_error_does_not_write_artifacts -q` passed with 3 cases; `.venv-conda/bin/python -m pytest -q` passed with 50 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add direct `run_experiment` malformed-config and missing-config no-artifact regression coverage to match the existing CLI failure guarantees.
