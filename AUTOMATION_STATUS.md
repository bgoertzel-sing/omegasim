# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis helper input-contract coverage on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 documented the pressure-analysis helper input-validation and no-partial-output failure contract.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, pressure-comparison implementation, pressure-analysis implementation, or tests changed; `README.md` now documents required pressure/trajectory CSV schemas, policy-set matching, positive `--limit`, append-safe output collision behavior, and the guarantee that validation failures do not create or modify analysis artifacts.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 12 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 477 tests.
- Blockers: none.
- Next step: add focused API and CLI regressions for invalid pressure-analysis `limit` values failing before partial outputs.
