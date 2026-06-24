# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis helper CLI input-contract hardening on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added documented CLI regressions for malformed-schema and policy-mismatch pressure-analysis failures.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, pressure-comparison implementation, or pressure-analysis implementation changes; `tests/test_run_harness.py` now verifies `python -m ohdyn.analyze_pressure` reports malformed pressure CSV schemas and pressure/trajectory policy mismatches without creating partial analysis outputs.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 12 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 477 tests.
- Blockers: none.
- Next step: add compact README documentation for the pressure-analysis helper's input validation and no-partial-output failure contract.
