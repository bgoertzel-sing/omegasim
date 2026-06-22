# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 README-aligned no-manifest reordered-action lobe replay smoke regression
- Changed: documented `configs/a0_no_manifest_reordered_actions.yaml` as the current no-manifest lobe replay smoke path in README, and added a README-linked CLI smoke test that verifies the documented command remains present, emits no `manifest.yaml`, preserves reordered action/schema provenance, reconstructs lobe labels/transitions/run state from `events.csv`, and matches summary aggregate replay using normalized `config.yaml` roles/actions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "readme_no_manifest_reordered_actions_lobe_replay_smoke_command or no_manifest_reordered_actions_lobe_sequences_reconstruct_from_events or no_manifest_reordered_actions_per_tick_sequences_reconstruct_from_events or no_manifest_reordered_actions_integrated_summary_aggregate_bundle_reconstructs_from_events" -q` passed with 5 tests and 383 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 388 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a compact A0/A1 reproducibility regression for the README-documented no-manifest reordered-action smoke path that asserts same-seed byte-identical emitted artifacts while excluding disabled manifest provenance.
