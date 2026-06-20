# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest API regression coverage
- Changed: added fixture-backed `run_experiment()` coverage proving the no-manifest config writes metrics/events/summary without rewriting a disabled stale manifest, and proving enabled-artifact collisions are refused without modifying existing files.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_respects_no_manifest_fixture_outputs tests/test_run_harness.py::test_run_api_without_manifest_refuses_enabled_artifact_collisions -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 72 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add config fixture coverage for omitted `outputs` defaults so the baseline smoke config behavior is pinned through both API and CLI paths.
