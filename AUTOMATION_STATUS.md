# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 documented no-manifest CLI/API seed-1 artifact parity regression tightened
- Changed: strengthened the existing `a0_no_manifest` seed-1 CLI/API parity regression so it explicitly verifies normalized config equality, disabled manifest absence, output flags, metrics/event headers, role/action schema order, 3 metrics rows and 45 event rows from `run_experiment`, summary written-artifact and schema provenance, and byte-identical emitted artifacts across the documented CLI and API paths.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "documented_cli_and_run_api_no_manifest_seed1_emit_identical_artifacts" -q` passed with 1 test and 415 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 416 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one concise default-action `a0_no_manifest` event-replay regression that reconstructs lobe labels, lobe transitions, dwell runs, queue aggregates, and role/action totals from `events.csv` plus normalized `config.yaml`, without relying on `manifest.yaml`.
