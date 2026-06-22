# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-22 A0/A1 no-manifest reordered action-order fixture coverage
- Changed: added `configs/a0_no_manifest_reordered_actions.yaml`; added `NO_MANIFEST_REORDERED_ACTIONS` and `NO_MANIFEST_FIXTURES` test coverage; extended no-manifest schema-provenance and integrated-summary bundle checks to derive action order from normalized `config.yaml` and assert emitted `metrics.csv` role/action field order without relying on `manifest.yaml`; documented the new fixture in `README.md`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "no_manifest or reordered_actions" -q` passed with 21 tests and 334 deselected; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 355 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a manifest-only reordered-action fixture so manifest schema/order provenance is covered for non-default action order when metrics, events, and summary are disabled.
