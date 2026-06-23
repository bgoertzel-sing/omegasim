# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 pressure-curve comparison multi-prefix seed-set sensitivity interpretation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-23 added deterministic multi-prefix pressure sensitivity reporting.
- Changed: no simulator behavior changes; pressure `summary.md` now preserves the existing full-vs-last-prefix lines and adds `top response stable across all prefixes` plus a table comparing the top pressure response for every proper prefix of the configured seed set. README documents the prefix table contract, and pressure-summary tests assert the new table while scoping the pressure-ranking table test to its own section.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_summary_reports_seed_set_sensitivity or pressure_summary'` passed with 4 selected tests; `.venv-conda/bin/python -m pytest` passed with 451 tests.
- Blockers: none.
- Next step: add pressure-summary interpretation text that explains whether unstable prefix rankings are caused by policy changes, observable changes, or slope-vs-curvature metric changes.
