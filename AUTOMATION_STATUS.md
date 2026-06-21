# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 metrics lobe-transition endpoint manifest-label regression
- Changed: added a documented-CLI regression across the full-output fixtures proving each non-`start`/`stable` emitted `baseline_lobe_transition` endpoint in `metrics.csv` belongs to `manifest.yaml` `model.baseline_lobes.labels`; added `_assert_manifest_lobe_labels_cover_metrics_transition_endpoints` in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_lobe_labels_cover_metrics_transition_endpoints" -q` passed with 2 tests and 185 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 187 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused documented-CLI regression that the non-`start`/`stable` `baseline_lobe_transition` sequence is identical across same-seed duplicate runs for both full-output fixtures.
