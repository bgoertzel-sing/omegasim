# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, summary artifact parity, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 artifact-set assertion consolidation
- Changed: routed the remaining direct output-directory artifact-set assertions in smoke, default-output, manifest-only, no-manifest, config-only, collision, stale-sentinel, and reproducibility regressions through `_assert_artifacts_match_output_directory()` while preserving sentinel byte-content checks.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py -k "artifact or artifacts or outputs or collision or config_only or no_manifest or manifest_only" -q` passed with 73 tests and 42 deselected; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: consolidate repeated byte-identical artifact comparison loops in reproducibility regressions through a shared helper.
