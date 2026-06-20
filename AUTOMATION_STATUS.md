# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 CLI manifest-only schema provenance regression
- Changed: added a documented CLI manifest-only regression asserting `manifest.yaml` still records the full metrics, events, lobe, queue, and role/action schemas when `metrics.csv`, `events.csv`, and `summary.md` are disabled and absent.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_manifest_only_records_full_schema_provenance_without_disabled_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 113 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI no-manifest regression proving metrics/events/summary schema provenance remains available through emitted artifacts when `manifest.yaml` is disabled.
