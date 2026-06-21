# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 queue dynamics manifest/metrics fixture parity regression
- Changed: added `test_manifest_queue_dynamics_fields_exactly_match_metrics_columns_across_full_output_fixtures` in `tests/test_run_harness.py` to verify the `manifest.yaml` queue pressure and queued-task-age field lists exactly match emitted `metrics.csv` columns for both full-output fixtures. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_queue_dynamics_fields_exactly_match_metrics_columns_across_full_output_fixtures or manifest_records_queue_dynamics_metric_provenance" -q` passed with 3 tests and 122 deselected; `.venv-conda/bin/python -m pytest -q` passed with 125 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact regression that `summary.md` artifact schema provenance counts match the manifest schema field counts for every output fixture that writes both artifacts.
