# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison interpretability on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added A2 pressure-curve response ranking table
- Changed: added a deterministic `Pressure-curve response ranking` section to pressure comparison `summary.md`; it reuses the existing pressure slope/curvature fields and ranks every policy/observable response by absolute magnitude while preserving the existing `Most pressure-sensitive curve metric` line. Added focused regression coverage and updated the README pressure artifact contract.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 43 tests and 406 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 449 tests.
- Blockers: none.
- Next step: inspect the default pressure comparison ranking output and choose one top-ranked policy/observable response for a bounded follow-up dynamics explanation.
