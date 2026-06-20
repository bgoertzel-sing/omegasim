# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only rerun overwrite regression
- Changed: added direct API and CLI regression coverage proving config-only reruns refuse to overwrite an existing successful output directory, leave the existing `config.yaml` byte-identical, and do not mention disabled optional artifacts as collisions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_only_rerun_refuses_to_overwrite_existing_config tests/test_run_harness.py::test_cli_config_only_rerun_refuses_to_overwrite_existing_config -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 65 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add focused direct API and CLI regressions for config-only runs where disabled optional artifact sentinels already exist, proving reruns still block only on `config.yaml` and preserve every preexisting file.
