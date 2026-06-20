# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 direct API config-load no-artifact regressions
- Changed: added direct `run_experiment` missing-config, malformed-YAML, and invalid-config regression coverage, proving API callers fail during config loading before any output directory or artifacts are created.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_missing_config_error_does_not_write_artifacts tests/test_run_harness.py::test_run_experiment_malformed_yaml_error_does_not_write_artifacts tests/test_run_harness.py::test_run_experiment_invalid_config_error_does_not_write_artifacts -q` passed with 3 tests; `.venv-conda/bin/python -m pytest -q` passed with 53 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add direct `run_experiment` output-path collision no-partial-artifact regression coverage to match the existing CLI failure guarantees.
