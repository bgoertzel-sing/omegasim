# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-21 A0/A1 stale disabled artifact assertion consolidation
- Changed: added `_assert_stale_artifacts_preserved()` and routed manifest-only, config-only, and no-manifest stale-disabled/collision preservation helpers through it, preserving the existing byte-level artifact invariants without simulator behavior changes.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "stale or collision or disabled_optional or config_only_rerun" -q` passed with 32 tests and 83 deselected; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add one compact regression test that the artifact lists reported by manifest and summary remain aligned with directory contents across all checked-in output-flag fixtures.
