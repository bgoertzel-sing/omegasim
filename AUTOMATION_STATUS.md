# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 disabled optional artifact collision regression
- Changed: added direct API and CLI regression coverage proving disabled optional artifacts (`metrics.csv`, `events.csv`, `summary.md`) are ignored when those outputs are off, while an enabled artifact collision (`manifest.yaml`) still blocks the run before `config.yaml` or partial artifacts are written.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_experiment_ignores_disabled_output_collisions_but_blocks_enabled_artifacts tests/test_run_harness.py::test_cli_ignores_disabled_output_collisions_but_blocks_enabled_artifacts -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 59 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused regression that `config.yaml` remains the first mandatory artifact and always blocks reruns even when every optional output flag is disabled.
