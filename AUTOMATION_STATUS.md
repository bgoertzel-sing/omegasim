# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 malformed YAML CLI artifact-safety regression
- Changed: wrapped YAML syntax failures with the config path during config loading and added a subprocess regression proving malformed YAML exits nonzero through argparse without a traceback or output artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_cli_malformed_yaml_error_does_not_write_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 33 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add CLI regression coverage for missing config files before writing any run artifacts.
