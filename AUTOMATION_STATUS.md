# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 metrics/events schema regression
- Changed: added a focused regression test that locks the documented `metrics.csv` and `events.csv` header order, including every role/action metric for the five static baseline roles.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_metrics_and_events_headers_match_documented_a0_schema -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 24 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add a focused manifest/config schema regression test for the documented A0/A1 artifact provenance.
