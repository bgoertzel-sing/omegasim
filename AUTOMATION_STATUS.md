# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison seed-set sensitivity interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 documented the pressure-summary `Seed-set sensitivity` section and its prefix-seed interpretation.
- Changed: no simulator behavior changes; README now names `Seed-set sensitivity` as a pressure comparison `summary.md` section and explains `full_seeds`, `prefix_seeds`, and `top response stable across prefix`. Added focused README assertions to the existing pressure sensitivity regression test.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary_reports_seed_set_sensitivity or documented_pressure_cli_writes_pressure_layout_and_curve_summary or pressure_summary'` passed with 5 selected tests; `.venv-conda/bin/python -m pytest` passed with 451 tests.
- Blockers: none.
- Next step: add a deterministic multi-prefix pressure sensitivity summary that compares top pressure responses across every prefix of the configured seed set.
