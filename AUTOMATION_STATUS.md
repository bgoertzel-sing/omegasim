# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis helper input-contract hardening on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added malformed-schema and policy-mismatch regressions for the deterministic A2 pressure analysis helper.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, or pressure-comparison implementation changes; `ohdyn.analyze_pressure` now validates both input CSV headers against the documented pressure comparison/trajectory schema constants before writing outputs and rejects pressure-vs-trajectory policy-set mismatches, including extra trajectory policies.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 10 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 475 tests.
- Blockers: none.
- Next step: add documented CLI regressions for malformed pressure-analysis CSV schemas and pressure/trajectory policy mismatches before expanding the analysis surface.
