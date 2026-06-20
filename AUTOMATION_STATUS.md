# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 direct API output-collision no-partial-artifact regressions
- Changed: added direct `run_experiment` regression coverage for refusing to overwrite an existing complete run directory and refusing a partial output directory with sentinel artifacts, proving API callers preserve existing files and do not write partial artifacts on output collisions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_refuses_to_overwrite_complete_run_directory tests/test_run_harness.py::test_run_experiment_refuses_partial_output_directory_without_writing_artifacts -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 55 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add direct `run_experiment` output-path-is-file regression coverage to match the existing CLI failure guarantee.
