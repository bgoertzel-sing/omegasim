# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only optional-output regression
- Changed: added direct API and CLI regression coverage proving a run with all optional output flags disabled succeeds, writes exactly `config.yaml`, and produces byte-identical config artifacts for the same seed.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_only_outputs_succeed_and_are_byte_stable tests/test_run_harness.py::test_cli_config_only_outputs_succeed_and_are_byte_stable -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 63 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add focused direct API and CLI regressions that config-only reruns refuse to overwrite a previously successful config-only output directory without changing its existing `config.yaml`.
