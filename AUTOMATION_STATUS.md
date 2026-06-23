# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-23 A0/A1 omitted-output API reproducibility helper reuse
- Changed: refactored `test_run_api_omitted_outputs_same_seed_reproduces_byte_identical_artifacts` to use the shared `_run_api_pair` helper while preserving its explicit config, seed, metrics, events, and byte-identical artifact assertions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "run_api_omitted_outputs_same_seed_reproduces_byte_identical_artifacts or same_seed_reproduces_byte_stable_outputs or different_seed_changes_events" -q` passed with 3 tests and 418 deselected; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m pytest tests/test_run_harness.py -q` passed with 421 tests.
- Blockers: none.
- Next step: review the documented-CLI same-seed byte-stability tests for one narrow helper extraction or reuse that reduces duplication without mixing CLI and API assertions.
