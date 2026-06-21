# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 lobe transition manifest/metrics fixture parity regression
- Changed: added `test_manifest_lobe_transition_fields_exactly_match_metrics_columns_across_full_output_fixtures` in `tests/test_run_harness.py` to verify the `manifest.yaml` lobe transition field list exactly matches emitted `baseline_lobe_*` transition columns in `metrics.csv` for both full-output fixtures. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_lobe_transition_fields_exactly_match_metrics_columns_across_full_output_fixtures or manifest_records_baseline_lobe_metric_provenance" -q` passed with 3 tests and 118 deselected; `.venv-conda/bin/python -m pytest -q` passed with 121 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact regression that the role/action field list in `manifest.yaml` exactly matches the role/action columns emitted in `metrics.csv` for every output fixture that writes both artifacts.
