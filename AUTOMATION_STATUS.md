# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 summary lobe dwell-run manifest-label regression
- Changed: added a documented-CLI regression across the full-output fixtures proving `summary.md` baseline lobe dwell-run labels use only labels declared in `manifest.yaml` `model.baseline_lobes.labels`, cover every observed metrics lobe dwell label, and match the metrics-derived dwell-run aggregates exactly; added `_summary_lobe_dwell_runs` and `_assert_summary_lobe_dwell_runs_use_only_manifest_lobe_labels` helpers in `tests/test_run_harness.py`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_lobe_dwell_runs_use_only_manifest_lobe_labels" -q` passed with 2 tests and 179 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 181 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a focused regression that `summary.md` lobe transition endpoints only use labels present in `manifest.yaml` `model.baseline_lobes.labels` for both full-output fixtures.
