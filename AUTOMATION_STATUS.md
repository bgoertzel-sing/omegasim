# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI same-seed reproducibility regression
- Changed: added a documented CLI regression for `python -m ohdyn.run --config configs/a0_smoke.yaml --seed 17 --out ...` that runs two fresh output directories and asserts the A0/A1 artifacts `config.yaml`, `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` are byte-identical for the same seed.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_same_seed_reproduces_byte_identical_a0_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 40 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a documented CLI regression that different seeds produce different A0/A1 event streams while preserving the same schema and row counts.
