# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-19 A0/A1 config validation regression hardening
- Changed: added focused config validation regressions for missing/non-mapping required sections and invalid baseline action lists, including missing required actions, unsupported actions, and duplicate actions.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_required_config_sections_must_be_yaml_mappings tests/test_run_harness.py::test_baseline_actions_must_be_required_unique_and_supported -q` passed with 6 tests; `.venv-conda/bin/python -m pytest -q` passed with 31 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add regression coverage that the CLI exits nonzero with a clear validation error for invalid YAML configs before writing any run artifacts.
