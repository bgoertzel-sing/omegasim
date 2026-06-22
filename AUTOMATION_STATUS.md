# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action documented CLI different-seed event-replayed integrated summary aggregate regression
- Changed: added documented CLI coverage proving `configs/a0_no_manifest_reordered_actions.yaml` runs with seeds 1 and 2 emit no `manifest.yaml`, preserve reordered action order through normalized config actions, diverge at the event-row and event-derived integrated-bundle layers, and still reconstruct each integrated summary aggregate bundle from `events.csv` plus normalized config-derived baseline roles/actions, including task/queue/pressure/age, lobe aggregate, and role/action totals.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "reconstructs_from_events_across_different_seeds" -q` passed with 1 test and 384 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 385 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI no-manifest reordered-action event-replayed per-tick sequence coverage, proving top-level queue/task/pressure/age and role/action metric sequences reconstruct from `events.csv` without manifest provenance.
