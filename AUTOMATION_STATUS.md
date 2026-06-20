# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 omitted-output defaults API reproducibility coverage
- Changed: added API-level same-seed reproducibility coverage for `configs/a0_default_outputs.yaml`, asserting the omitted-output defaults fixture returns identical configs, metrics, and events through `run_experiment()` and writes byte-identical `config.yaml`, `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` artifacts for the same seed.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_omitted_outputs_same_seed_reproduces_byte_identical_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 76 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add same-seed byte-identical CLI reproducibility coverage for the omitted-outputs fixture.
