# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only output documentation
- Changed: documented the config-only output mode in `README.md`, including how optional artifact flags work, append-safe collision checks, preservation of disabled artifact sentinels, and mandatory `config.yaml` rerun blocking.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_only_rerun_preserves_disabled_artifact_sentinels tests/test_run_harness.py::test_cli_config_only_rerun_preserves_disabled_artifact_sentinels -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 67 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a small checked-in config fixture for the documented config-only output mode.
