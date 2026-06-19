# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A1 fixed-seed role action totals regression coverage
- Changed: added golden regression coverage for per-role action totals across seeds 1, 2, and 17, checking both metrics-derived totals and rendered `summary.md` role action lines.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_fixed_seed_role_action_totals_are_stable -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 17 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add fixed-seed golden regression coverage for event type totals across the existing seed set.
