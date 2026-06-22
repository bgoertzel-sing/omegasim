# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action seed-difference schema regression
- Changed: added documented CLI coverage proving `configs/a0_no_manifest_reordered_actions.yaml` emits no `manifest.yaml`, preserves normalized reordered action order in metrics role/action fields, keeps metrics/events headers stable across seeds, records the expected no-manifest artifact index in both summaries, and produces different deterministic metrics or event streams for seeds 1 and 2.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_seed_difference_preserves_schema_order" -q` passed with 1 test and 374 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 375 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add same-seed reproducibility coverage for the no-manifest reordered-action fixture to confirm repeated documented CLI runs preserve schema/order invariants while producing identical deterministic metrics and event streams.
