# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-documented first-milestone different-seed dynamics regression
- Changed: added a compact README-linked CLI regression for `configs/a0_smoke.yaml` that runs the first-milestone command with seeds 1 and 2, verifies the full five-artifact A0 output set, checks stable normalized config, manifest model/artifact/output provenance, metrics/events schemas, and row counts, then confirms metrics rows, event rows, and summary aggregate dynamics change across seeds.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_a0_smoke_different_seed" -q` passed with 1 test and 397 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 398 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact README-linked event-replay regression for `configs/a0_smoke.yaml` that reconstructs lobe, queue-pressure, queued-task-age, and role/action summaries from `events.csv` for the first-milestone output.
