# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 omitted-output defaults regression coverage
- Changed: added `configs/a0_default_outputs.yaml` with no `outputs` section, plus API config-load coverage and CLI coverage proving omitted outputs normalize to manifest/metrics/events/summary enabled and write the full A0 artifact set.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_loads_a0_default_outputs_fixture tests/test_run_harness.py::test_documented_cli_omitted_outputs_defaults_to_full_a0_artifacts -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 74 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add API-level `run_experiment()` coverage for the omitted-outputs fixture so default artifact writing is pinned without going through the subprocess CLI path.
