# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI summary lobe transition totals regression
- Changed: added `test_documented_cli_summary_lobe_transition_totals_match_adjacent_labels_across_full_output_fixtures`, `_assert_summary_lobe_transition_totals_match_adjacent_labels`, `_summary_lobe_transition_totals`, and `_lobe_transition_totals_from_adjacent_labels` in `tests/test_run_harness.py` so `summary.md` transition totals are parsed and checked against transition counts recomputed directly from adjacent `baseline_lobe_label` rows for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "summary_lobe_transition_totals or lobe_transitions or lobe_aggregates" -q` passed with 7 tests and 156 deselected; `.venv-conda/bin/python -m pytest -q` passed with 163 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that manifest baseline lobe labels include the configured lobe vocabulary and cover every observed `baseline_lobe_label` emitted in metrics across both full-output fixtures.
