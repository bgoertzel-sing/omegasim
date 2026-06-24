# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis helper hardening on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added missing-input and existing-output collision regressions for the deterministic A2 pressure analysis helper.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, or analysis implementation changes; extended `tests/test_run_harness.py` so `ohdyn.analyze_pressure` API and documented CLI both refuse a missing pressure CSV pair without partial outputs and refuse preexisting `trajectory_pressure_ranking.csv` or `summary.md` without modifying sentinel files.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 8 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 473 tests.
- Blockers: none.
- Next step: add malformed CSV schema and mismatched-policy regression tests for `ohdyn.analyze_pressure` before expanding the analysis surface.
