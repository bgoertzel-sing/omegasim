# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison seed-set sensitivity reporting on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added a deterministic pressure-summary `Seed-set sensitivity` section.
- Changed: no simulator behavior changes; pressure comparison summaries now compare the full seed set's selected top pressure response against the prefix seed subset from already-generated per-seed rows and report whether the top response is stable. Added a regression test for the known `1,2,3` versus `1,2` top-response instability.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary or pressure_comparison_runner_is_reproducible or documented_pressure_cli'` passed with 9 selected tests; `.venv-conda/bin/python -m pytest` passed with 451 tests.
- Blockers: none.
- Next step: add README documentation for the pressure summary `Seed-set sensitivity` section and its prefix-seed interpretation.
