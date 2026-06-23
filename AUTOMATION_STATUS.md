# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic pressure prefix instability-cause reporting.
- Changed: no simulator behavior changes; pressure `summary.md` now reports `prefix instability causes` for the last prefix comparison and adds an `instability_causes` column to the per-prefix seed-set sensitivity table. Cause labels identify whether an unstable top pressure response changed by `policy`, `observable`, `metric`, or a comma-separated combination. README documents the new interpretation contract, and pressure-summary tests assert the emitted cause labels.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary_reports_seed_set_sensitivity or pressure_summary'` passed with 4 selected tests; `.venv-conda/bin/python -m pytest` passed with 451 tests.
- Blockers: none.
- Next step: add a compact pressure-summary interpretation paragraph that connects the top unstable cause labels to the condition means and high-minus-normal deltas already reported for the winning responses.
