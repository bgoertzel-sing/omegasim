# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 documented CLI no-manifest reproducibility regression
- Changed: added a documented same-seed CLI reproducibility regression for `python -m ohdyn.run --config <no-manifest-config> --seed 17 --out ...` with `write_manifest: false` and metrics/events/summary enabled; it runs two output directories, asserts `manifest.yaml` is omitted, and proves `config.yaml`, `metrics.csv`, `events.csv`, and `summary.md` are byte-identical across both runs.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_same_seed_without_manifest_reproduces_byte_identical_artifacts -q` passed; `.venv-conda/bin/python -m pytest -q` passed with 45 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add a CLI overwrite-refusal regression for partial no-manifest output directories so reruns cannot overwrite any existing subset of `config.yaml`, `metrics.csv`, `events.csv`, or `summary.md`.
