# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 omitted-output defaults CLI collision coverage
- Changed: added CLI-level collision coverage for `configs/a0_default_outputs.yaml`, asserting `python -m ohdyn.run` refuses an output directory containing enabled default artifacts and does not write partial `manifest.yaml`, `metrics.csv`, or `summary.md` artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_omitted_outputs_refuses_collision_without_partial_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 78 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add API-level collision coverage for `configs/a0_default_outputs.yaml` to mirror the CLI omitted-output default collision behavior.
