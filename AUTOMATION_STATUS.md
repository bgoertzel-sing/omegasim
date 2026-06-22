# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 run-API default-action no-manifest event replay regression added
- Changed: added one concise run-API `a0_no_manifest` regression that runs with default action order and no `manifest.yaml`, derives roles from normalized `config.yaml`, reconstructs lobe labels, lobe transitions, dwell runs, task/queue pressure/age aggregates, and role/action totals from `events.csv`, then compares them against `metrics.csv`, `summary.md`, and the typed `run_experiment` result shape.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_no_manifest_default_actions_event_replay" -q` passed with 1 test and 417 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 418 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise run-API `a0_no_manifest` default-action event-replay reproducibility regression comparing same-seed and different-seed reconstructed bundles without relying on `manifest.yaml`.
