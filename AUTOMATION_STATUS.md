# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 rerun/collision preservation helper consolidation
- Changed: added `_artifact_bytes_snapshot()` and `_assert_output_directory_preserved()` and routed full-output/config-only rerun preservation assertions through them, preserving the existing byte-level invariants without simulator behavior changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "refuses_to_overwrite_complete_run_directory or config_only_rerun" -q` passed with 6 tests and 109 deselected; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: consolidate repeated stale disabled artifact sentinel preservation assertions across manifest-only, config-only, and no-manifest collision helpers.
