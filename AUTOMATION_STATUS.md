# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action documented CLI event-replayed lobe sequence regression
- Changed: added documented CLI coverage proving `configs/a0_no_manifest_reordered_actions.yaml` runs with seeds 1 and 2 emit no `manifest.yaml`, derive ticks/actions from normalized `config.yaml`, reconstruct lobe label, lobe transition, and lobe run-state sequences from `events.csv`, validate reconstructed lobe transitions/dwell runs against existing invariants, and preserve seed-sensitive divergence without manifest provenance.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events or no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events" -q` passed with 4 tests and 383 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 387 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a small README/status-aligned smoke command fixture or test that documents and verifies the current no-manifest reordered-action lobe replay workflow end to end without broadening beyond the A0/A1 baseline.
