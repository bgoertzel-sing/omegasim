# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic pressure-response interpretation text.
- Changed: no simulator behavior changes; pressure `summary.md` now includes a `Pressure-response interpretation` section after the top-response explanation. The section connects the full-seed winning response to its condition means, slopes, curvature, and high-minus-normal delta, and for unstable prefixes explains the changed `policy`/`observable`/`metric` dimensions using the prefix winner's same curve values. Added a regression test for the known unstable `1,2,3` seed-set case.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary'` passed with 5 selected tests; `.venv-conda/bin/python -m pytest` passed with 452 tests.
- Blockers: none.
- Next step: document the new `Pressure-response interpretation` summary section in README so the pressure comparison output contract matches the emitted artifact.
