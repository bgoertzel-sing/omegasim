# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented-CLI role/action summary same-seed reproducibility regression
- Changed: added a documented-CLI same-seed regression across the full-output fixtures proving parsed `summary.md` role/action totals reproduce exactly across duplicate seed 17 runs while matching metrics-derived role/action totals for each run.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "role_action_summary_totals" -q` passed with 4 tests and 201 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 205 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that the per-tick role/action metrics sequence reproduces exactly across same-seed reruns for both full-output fixtures.
