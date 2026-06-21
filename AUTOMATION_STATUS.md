# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 documented CLI manifest event-type vocabulary regression
- Changed: added `test_documented_cli_manifest_event_types_cover_observed_events_across_full_output_fixtures` and `_assert_manifest_event_types_cover_observed_events` in `tests/test_run_harness.py` so the CLI path checks that manifest `model.events.types` matches `BASELINE_EVENT_TYPES` and covers every observed `event_type` emitted in `events.csv` for both `configs/a0_smoke.yaml` and `configs/a0_default_outputs.yaml`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_event_types_cover_observed_events or manifest_lobe_labels_cover_observed_metrics" -q` passed with 4 tests and 163 deselected; `.venv-conda/bin/python -m pytest -q` passed with 167 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact CLI-path regression that manifest `model.events.fields` exactly matches the emitted `events.csv` header across both full-output fixtures.
