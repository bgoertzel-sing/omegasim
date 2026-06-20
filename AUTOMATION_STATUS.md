# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 run API manifest-only stale disabled artifact preservation regression
- Changed: added the matching `run_experiment` API regression asserting manifest-only first runs preserve stale disabled `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte while writing only fresh `config.yaml` and `manifest.yaml`, with the manifest artifacts/output flags matching the enabled output set and deterministic simulation metrics/events still returned.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_manifest_only_preserves_stale_disabled_artifact_sentinels -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 98 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add the matching run API regression for no-manifest first runs preserving a stale disabled `manifest.yaml` sentinel byte-for-byte while writing fresh `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md`.
