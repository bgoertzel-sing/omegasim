# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest baseline-lobe schema regression
- Changed: added `test_documented_cli_manifest_lobe_fields_match_metrics_header_and_observed_labels_across_full_output_fixtures` and `_assert_manifest_lobe_fields_match_metrics_header_and_observed_labels` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.baseline_lobes.labels` and `transition_fields` match the canonical lobe constants, the emitted `metrics.csv` lobe-transition header subset, and observed metric labels for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_lobe or lobe_fields" -q` passed with 6 tests and 171 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 177 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor the repeated documented-CLI subprocess setup in `tests/test_run_harness.py` into one small helper, then reuse it in the newest schema regression without changing simulator behavior.
