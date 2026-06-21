# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 metrics previous-lobe manifest-label regression
- Changed: added a documented-CLI regression across the full-output fixtures proving each emitted `baseline_lobe_previous_label` value in `metrics.csv` is blank only on the first tick and otherwise belongs to `manifest.yaml` `model.baseline_lobes.labels`; added `_assert_manifest_lobe_labels_cover_previous_metrics_labels` in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_lobe_labels_cover_previous_metrics_labels" -q` passed with 2 tests and 183 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 185 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that each non-`start`/`stable` emitted `baseline_lobe_transition` endpoint in `metrics.csv` belongs to `manifest.yaml` `model.baseline_lobes.labels` across both full-output fixtures.
