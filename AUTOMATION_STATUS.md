# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 manifest-only schema provenance config-action derivation
- Changed: updated the manifest-only schema provenance regression helper to derive baseline actions from normalized `config.yaml` instead of a hard-coded tuple, preserving full manifest schema checks when metrics, events, and summary artifacts are disabled.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "manifest_only_records_full_schema_provenance" -q` passed with 2 tests and 270 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 272 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: update the full manifest/config provenance regression to derive expected actions from normalized `config.yaml` instead of a hard-coded baseline list.
