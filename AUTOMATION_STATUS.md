# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 API no-manifest emitted-artifact schema provenance regression
- Changed: added an API no-manifest regression proving `run_experiment()` emits schema-provenanced `metrics.csv`, `events.csv`, and `summary.md` while leaving `manifest.yaml` absent when disabled.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_no_manifest_emitted_artifacts_preserve_schema_provenance -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor the repeated emitted-artifact schema provenance assertions into a local test helper shared by CLI and API no-manifest regressions.
