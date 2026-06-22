# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action documented CLI event-replayed integrated summary aggregate regression
- Changed: added documented CLI coverage proving two `configs/a0_no_manifest_reordered_actions.yaml` runs with seed 17 emit no `manifest.yaml`, preserve reordered action order through normalized config actions, reproduce identical event rows, and reconstruct the integrated summary aggregate bundle from `events.csv` plus normalized config-derived baseline roles/actions, including task/queue/pressure/age, lobe aggregate, and role/action totals.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events" -q` passed with 1 test and 383 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 384 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI no-manifest reordered-action event-replayed integrated bundle coverage for different seeds, proving event-derived bundles still match summaries while diverging across seeds.
