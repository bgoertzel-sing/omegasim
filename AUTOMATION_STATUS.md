# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 CLI no-manifest emitted-artifact schema provenance regression
- Changed: added a documented CLI no-manifest regression proving `metrics.csv`, `events.csv`, and `summary.md` preserve schema provenance when `manifest.yaml` is disabled and absent.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_no_manifest_emitted_artifacts_preserve_schema_provenance -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 114 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add an API no-manifest regression mirroring the emitted-artifact schema provenance checks without invoking the CLI.
