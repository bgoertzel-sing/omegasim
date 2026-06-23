# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 API seed-pair reproducibility helper consolidation
- Changed: added shared `_run_api_pair` in `tests/test_run_harness.py` for running two API experiments with a common config, checking each output directory against the expected enabled artifact set, and returning the run paths/results. Refactored the same-seed byte-stability and different-seed event-change tests to use the helper and the fixture artifact registry instead of inline paths/artifact lists.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "same_seed_reproduces_byte_stable_outputs or different_seed_changes_events" -q` passed with 2 tests and 419 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review remaining same-seed byte-stability tests for one narrow reuse of `_run_api_pair` where it removes duplication without weakening per-fixture assertions.
