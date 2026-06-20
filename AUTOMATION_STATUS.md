# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only rerun disabled-sentinel regression
- Changed: added direct API and CLI regression coverage for config-only runs where disabled optional artifact sentinels already exist, proving reruns still block only on `config.yaml` and preserve every preexisting file byte-for-byte.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_config_only_rerun_preserves_disabled_artifact_sentinels tests/test_run_harness.py::test_cli_config_only_rerun_preserves_disabled_artifact_sentinels -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 67 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a concise README note documenting the config-only output mode and its overwrite/collision semantics.
