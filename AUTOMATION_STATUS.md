# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI manifest-only enabled artifact collision regression
- Changed: added a parametrized documented CLI regression asserting manifest-only runs refuse collisions on each enabled artifact (`config.yaml`, `manifest.yaml`) while ignoring and preserving stale disabled `metrics.csv`, `events.csv`, and `summary.md` sentinels byte-for-byte.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_manifest_only_refuses_enabled_artifact_collisions_while_preserving_stale_disabled_artifacts -q` passed with 2 tests; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 109 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 109 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a parametrized run API manifest-only enabled artifact collision regression for `config.yaml` and `manifest.yaml` while preserving stale disabled `metrics.csv`, `events.csv`, and `summary.md` sentinels.
