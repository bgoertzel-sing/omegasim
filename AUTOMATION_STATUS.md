# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI manifest-only stale disabled artifact preservation regression
- Changed: added a documented CLI regression asserting manifest-only runs preserve stale disabled `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte while still writing fresh `config.yaml` and `manifest.yaml` with manifest artifacts limited to the written outputs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_manifest_only_preserves_stale_disabled_artifact_sentinels -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 95 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI regression for config-only first runs preserving stale disabled `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte while writing only `config.yaml`.
