# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI smoke artifact regression
- Changed: added a CLI smoke test for the documented `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out ...` command, asserting it exits cleanly, writes exactly the five A0/A1 artifacts, and records the expected ordered manifest artifact list.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_smoke_writes_required_a0_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 37 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a CLI smoke regression that the documented command's `metrics.csv` and `events.csv` row counts match the configured tick count and static 15-agent baseline.
