# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 manifest-only disabled-output fixture promotion
- Changed: added checked-in `configs/a0_manifest_only.yaml`, documented its CLI invocation, and promoted matching manifest-only API/CLI disabled-output and collision regressions away from inline YAML fixtures.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_loads_a0_manifest_only_fixture tests/test_run_harness.py::test_manifest_lists_only_written_artifacts tests/test_run_harness.py::test_documented_cli_respects_disabled_optional_outputs tests/test_run_harness.py::test_run_experiment_ignores_disabled_output_collisions_but_blocks_enabled_artifacts tests/test_run_harness.py::test_cli_ignores_disabled_output_collisions_but_blocks_enabled_artifacts -q` passed with 5 tests; `.venv-conda/bin/python -m pytest -q` passed with 69 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a checked-in no-manifest baseline fixture for the remaining inline metrics/events/summary-only output regressions.
