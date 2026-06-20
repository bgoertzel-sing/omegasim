# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI different-seed divergence regression
- Changed: added a documented CLI regression for `python -m ohdyn.run --config configs/a0_smoke.yaml --seed ... --out ...` that runs seeds 17 and 18, asserts the A0/A1 metrics/events schemas and row counts remain stable, asserts event streams differ, and confirms manifest model shape/actions remain unchanged while recording distinct seeds.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_different_seeds_change_events_but_preserve_schema -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 41 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a smoke regression that the documented CLI refuses to overwrite an existing complete run directory and leaves all existing artifacts byte-identical.
