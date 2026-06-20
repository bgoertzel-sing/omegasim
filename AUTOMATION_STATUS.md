# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 config-only normalized-config test helper
- Changed: factored the duplicated API/CLI config-only normalized-config assertions into `_assert_config_only_writes_normalized_config()`.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_config_only_preserves_stale_disabled_artifact_sentinels tests/test_run_harness.py::test_run_api_config_only_preserves_stale_disabled_artifact_sentinels -q` passed with 2 tests; `.venv-conda/bin/python -m ruff check tests/test_run_harness.py` passed; `.venv-conda/bin/python -m pytest -q` passed with 115 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: factor repeated no-manifest output flag and artifact assertions shared by CLI/API no-manifest regressions.
