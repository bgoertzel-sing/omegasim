# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest documented-CLI integrated summary aggregate regression
- Changed: added one documented-CLI regression for `configs/a0_no_manifest.yaml` that verifies the integrated summary task/queue, queue-pressure, queued-task-age, lobe, and role/action aggregate bundle matches `metrics.csv` while deriving actions from normalized `config.yaml` and confirming `manifest.yaml` is absent.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "integrated_summary_aggregate_bundle" -q` passed with 5 tests and 267 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 272 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: update the no-manifest schema provenance regression helper to derive actions from normalized `config.yaml` instead of a hard-coded baseline tuple.
