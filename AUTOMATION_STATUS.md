# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison interpretability on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added A2 top pressure-response explanation
- Changed: added a deterministic `Top pressure-response explanation` section to pressure comparison `summary.md`; it selects the top-ranked policy/observable response, reports the underlying normal/medium/high condition means, slope/curvature values, and high-minus-normal delta, and keeps the existing pressure response ranking intact. Added focused regression coverage and updated the README pressure artifact contract.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 450 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "pressure" -q` passed with 44 tests and 406 deselected; `.venv-conda/bin/ruff check ohdyn/compare_pressure.py tests/test_run_harness.py` passed.
- Blockers: none.
- Next step: run the default three-seed pressure comparison and inspect whether the explained top pressure response is stable relative to the two-seed regression fixture.
