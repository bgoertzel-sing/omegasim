# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 run API no-manifest enabled artifact collision regression
- Changed: added a parametrized `run_experiment` API regression asserting no-manifest runs refuse collisions on each enabled artifact (`config.yaml`, `metrics.csv`, `events.csv`, `summary.md`) while ignoring and preserving a stale disabled `manifest.yaml` sentinel byte-for-byte.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_no_manifest_refuses_enabled_artifact_collisions_while_ignoring_stale_manifest -q` passed with 4 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 103 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add the matching documented CLI no-manifest collision regression for enabled artifacts while preserving a stale disabled `manifest.yaml`.
