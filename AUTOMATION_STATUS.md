# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A2 downstream pressure-analysis input-key validation on top of the stable A0/A1 local simulator harness.

## Latest Run

- Status: ok, 2026-06-24 added pressure-analysis blank/duplicate policy-key API and CLI regressions.
- Changed: no simulator, scheduling, baseline run harness, A0/A1 schema, artifact writer, or pressure-comparison implementation changed; `ohdyn.analyze_pressure` now validates `pressure_comparison_metrics.csv` policy keys with the same blank/duplicate guard already used for `pressure_trajectory_structure.csv`; `tests/test_run_harness.py` now asserts blank and duplicate policy keys in either pressure-analysis input fail before partial analysis outputs are created.
- Smoke run: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k 'pressure_analysis'` passed with 26 selected tests.
- Verified: `.venv-conda/bin/python -m ruff check ohdyn tests` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py` passed with 491 tests.
- Blockers: none.
- Next step: run one compact A2 pressure-response analysis sweep and inspect whether the pressure/trajectory ranking suggests a concrete next simulator metric rather than adding more failure-contract coverage.
