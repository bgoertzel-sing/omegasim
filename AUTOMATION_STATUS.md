# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 direct API optional artifact collision regression
- Changed: added direct `run_experiment` regression coverage for refusing a run directory that already contains a single optional artifact (`metrics.csv`), proving API callers preserve the sentinel file and do not write partial artifacts before raising.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_output_artifact_collision_does_not_write_partial_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 57 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add CLI/API regression coverage for artifact collision behavior when optional outputs are disabled, ensuring disabled artifacts are ignored while enabled artifacts still block writes.
