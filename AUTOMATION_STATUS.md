# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered-action same-seed schema reproducibility regression
- Changed: added documented CLI coverage proving repeated `configs/a0_no_manifest_reordered_actions.yaml` runs with seed 17 emit no `manifest.yaml`, preserve normalized reordered action order in metrics role/action fields, keep metrics/events headers stable, record the expected no-manifest artifact index in both summaries, and produce byte-identical enabled artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest_reordered_actions_same_seed_reproduces_schema_order" -q` passed with 1 test and 375 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 376 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add run API same-seed reproducibility coverage for the no-manifest reordered-action fixture to mirror the documented CLI schema/order and byte-identical artifact guarantees.
