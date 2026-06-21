# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest event-field schema regression
- Changed: added `test_documented_cli_manifest_event_fields_exactly_match_events_header_across_full_output_fixtures` and `_assert_manifest_event_fields_match_events_header` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.events.fields` exactly matches the emitted `events.csv` header and `EVENT_FIELDS` for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_event_fields or manifest_event_types_cover_observed_events" -q` passed with 4 tests and 165 deselected; `.venv-conda/bin/python -m pytest -q` passed with 169 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that manifest `model.metrics.fields` exactly matches the emitted `metrics.csv` header across both full-output fixtures.
