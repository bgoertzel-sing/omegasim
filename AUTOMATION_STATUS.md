# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 checked-in config-only fixture
- Changed: added `configs/a0_config_only.yaml` for the documented config-only output mode, documented its CLI invocation in `README.md`, and updated config-only CLI coverage to exercise the checked-in fixture.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_loads_a0_config_only_fixture tests/test_run_harness.py::test_cli_config_only_outputs_succeed_and_are_byte_stable -q` passed with 2 tests; `.venv-conda/bin/python -m pytest -q` passed with 68 tests; `.venv-conda/bin/python -m ruff check .` passed; `.venv-conda/bin/python -m ohdyn.run --config configs/a0_config_only.yaml --seed 1 --out "$tmpdir/run"` wrote only `config.yaml`.
- Blockers: none.
- Next step: promote one config-only collision or sentinel-preservation regression to use the checked-in `configs/a0_config_only.yaml` fixture.
