# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis helper failure-contract coverage on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added pressure-analysis invalid-limit API and CLI regressions.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, pressure-comparison implementation, or pressure-analysis implementation changed; `tests/test_run_harness.py` now asserts non-positive API and CLI `limit` values fail before creating partial analysis outputs, and the API path also rejects boolean and non-integer limits.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 18 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 483 tests.
- Blockers: none.
- Next step: add focused API and CLI regressions for blank and duplicate pressure-analysis policy keys failing before partial outputs.
