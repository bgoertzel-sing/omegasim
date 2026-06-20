# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 direct API output-path file collision regression
- Changed: added direct `run_experiment` regression coverage for refusing an output path that already exists as a file, proving API callers preserve the sentinel file and match the existing CLI failure guarantee without writing artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_output_path_file_does_not_overwrite -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 56 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add direct `run_experiment` artifact-collision regression coverage for a single existing optional artifact, matching `test_cli_output_artifact_collision_does_not_write_partial_artifacts`.
