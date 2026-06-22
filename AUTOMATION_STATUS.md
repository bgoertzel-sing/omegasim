# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action documented CLI event-replayed per-tick sequence regression
- Changed: added documented CLI coverage proving `configs/a0_no_manifest_reordered_actions.yaml` runs with seeds 1 and 2 emit no `manifest.yaml`, derive actions/ticks/roles from normalized `config.yaml`, and reconstruct per-tick top-level queue/task, queue-pressure, queued-task-age, and role/action metric sequences from `events.csv` without manifest provenance while preserving reordered action order and seed-sensitive divergence.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "per_tick_sequences_reconstruct_from_events or reconstructs_from_events_across_different_seeds" -q` passed with 2 tests and 384 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 386 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add documented CLI no-manifest reordered-action lobe-label and lobe-transition sequence replay coverage from `events.csv` plus normalized config, confirming lobe sequence provenance remains manifest-independent.
