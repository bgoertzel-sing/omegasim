# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 no-manifest disabled-output fixture promotion
- Changed: added checked-in `configs/a0_no_manifest.yaml`, documented its CLI invocation, and promoted the remaining no-manifest metrics/events/summary-only CLI regressions away from inline YAML fixtures.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_loads_a0_no_manifest_fixture tests/test_run_harness.py::test_documented_cli_respects_disabled_manifest_output tests/test_run_harness.py::test_documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts tests/test_run_harness.py::test_documented_cli_without_manifest_refuses_partial_output_directory -q` passed with 4 tests; `.venv-conda/bin/python -m pytest -q` passed with 70 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add fixture-backed API coverage for no-manifest output behavior and collision handling to match the CLI coverage.
