# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 summary/manifest artifact consistency regression
- Changed: added a regression assertion that the `summary.md` written-artifact listing exactly matches `manifest.yaml` artifacts when both summary and manifest outputs are enabled.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_summary_written_artifacts_match_manifest_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 88 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_smoke.yaml --seed 1 --out /tmp/omegasim-summary-manifest-artifacts-20260620-a0/a0_seed1` wrote all five A0 artifacts and a direct YAML/summary check confirmed matching artifact lists.
- Blockers: none.
- Next step: add a regression assertion that `summary.md` written-artifact listings match the actual output directory contents for enabled-output runs.
