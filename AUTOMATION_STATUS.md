# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented first-milestone same-seed byte reproducibility regression
- Changed: added a compact README-linked CLI regression for `configs/a0_smoke.yaml` that runs the first-milestone command twice with seed 1, verifies the full five-artifact A0 output set, checks the 100-tick/15-agent/1500-event baseline shape, and byte-compares `config.yaml`, `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_a0_smoke_same_seed" -q` passed with 1 test and 396 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 397 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked different-seed regression for `configs/a0_smoke.yaml` that confirms the first-milestone metrics/events/summary dynamics change while schema and artifact provenance remain stable.
