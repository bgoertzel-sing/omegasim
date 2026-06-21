# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 reproducibility byte-comparison helper consolidation
- Changed: added `_assert_artifacts_are_byte_identical()` and routed same-seed/default-output/no-manifest/config-only reproducibility assertions through it, preserving the existing artifact sets and byte-level checks.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "reproduces_byte or byte_stable or same_seed" -q` passed with 7 tests and 108 deselected; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: consolidate repeated before/after output-preservation snapshot assertions in rerun and collision regressions through a shared helper.
