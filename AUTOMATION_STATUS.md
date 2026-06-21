# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest lobe-label vocabulary regression
- Changed: added `test_documented_cli_manifest_lobe_labels_cover_observed_metrics_across_full_output_fixtures` and `_assert_manifest_lobe_labels_cover_observed_metrics` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.baseline_lobes.labels` matches `BASELINE_LOBE_LABELS` and covers every observed `baseline_lobe_label` emitted in `metrics.csv` for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_lobe_labels_cover_observed_metrics or baseline_lobe_metric_provenance" -q` passed with 3 tests and 162 deselected; `.venv-conda/bin/python -m pytest -q` passed with 165 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that the manifest `model.events.types` vocabulary covers every observed `event_type` emitted in `events.csv` across both full-output fixtures.
