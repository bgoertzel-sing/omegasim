# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI config-only stale disabled artifact preservation regression
- Changed: added a documented CLI regression asserting config-only first runs preserve stale disabled `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte while writing only a fresh normalized `config.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_config_only_preserves_stale_disabled_artifact_sentinels -q` passed with 1 test; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 96 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add the matching run API regression for config-only first runs preserving stale disabled `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte while writing only `config.yaml`.
