# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI summary event total parity regression
- Changed: added `test_documented_cli_summary_event_type_totals_match_events_across_full_output_fixtures` and `_assert_summary_event_type_totals_match_events` in `tests/test_run_harness.py` to verify documented full-output CLI runs keep `summary.md` event type totals aligned with emitted `events.csv` rows for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`. Simulator behavior and output schemas were unchanged.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_summary_event_type_totals_match_events_across_full_output_fixtures" -q` passed with 2 tests and 137 deselected; `.venv-conda/bin/python -m pytest -q` passed with 139 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that documented full-output runs keep top-level `summary.md` task/message/event totals aligned with emitted `metrics.csv` and `events.csv` rows across both full-output fixtures.
