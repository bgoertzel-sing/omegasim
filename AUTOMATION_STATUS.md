# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 summary lobe transition-endpoint manifest-label regression
- Changed: added a documented-CLI regression across the full-output fixtures proving every `summary.md` baseline lobe transition endpoint uses only labels declared in `manifest.yaml` `model.baseline_lobes.labels` and that the summary transition totals still match metrics-derived adjacent-label transitions exactly; added `_assert_summary_lobe_transition_endpoints_use_only_manifest_lobe_labels` in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_lobe_transition_endpoints_use_only_manifest_lobe_labels" -q` passed with 2 tests and 181 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 183 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused regression that each emitted `baseline_lobe_previous_label` value in `metrics.csv` is either blank on the first tick or present in `manifest.yaml` `model.baseline_lobes.labels` across both full-output fixtures.
