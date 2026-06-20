# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI overwrite-refusal regression
- Changed: added a documented CLI regression for `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 17 --out ...` that creates a complete run directory, reruns the same command, asserts the CLI exits with a clean argparse error instead of a traceback, and verifies all existing artifacts remain byte-identical with no extra files.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_refuses_to_overwrite_complete_run_directory -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 42 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a smoke regression that a documented CLI run with disabled optional outputs writes only `config.yaml` plus the enabled artifacts and still records the exact artifact list in `manifest.yaml`.
