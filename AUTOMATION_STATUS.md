# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 run API manifest-only enabled artifact collision regression
- Changed: added a parametrized run API regression asserting manifest-only runs refuse collisions on each enabled artifact (`config.yaml`, `manifest.yaml`) while ignoring and preserving stale disabled `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts -q` passed with 2 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 111 tests; `.venv-conda/bin/python -m pytest -q` passed with 111 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a manifest-only provenance regression asserting `manifest.yaml` still records full metrics, events, lobe, queue, and role/action schemas when `metrics.csv`, `events.csv`, and `summary.md` are disabled.
