# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 manifest/config provenance schema regression
- Changed: added a focused regression test that locks the documented `manifest.yaml` and normalized `config.yaml` provenance contract, including run shape, output flags, artifact list, 15 static agent IDs, role mapping, and bus graph counts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_manifest_and_config_match_documented_a0_provenance_schema -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 25 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out runs/a0_seed1` completed.
- Blockers: none.
- Next step: add focused config validation regressions for missing required sections and duplicate/unsupported baseline actions.
