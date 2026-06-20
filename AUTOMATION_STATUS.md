# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 run API no-manifest stale disabled manifest preservation regression
- Changed: added the matching `run_experiment` API regression asserting no-manifest first runs preserve a stale disabled `manifest.yaml` sentinel byte-for-byte while writing fresh `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md`, with normalized output flags, summary output flags, and deterministic simulation metrics/events still returned.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_no_manifest_preserves_stale_disabled_manifest_sentinel -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 99 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused regression that `run_experiment` without manifest refuses collisions on each enabled no-manifest artifact while continuing to ignore a stale disabled `manifest.yaml`.
