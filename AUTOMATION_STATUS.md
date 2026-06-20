# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 omitted-output defaults API collision coverage
- Changed: added API-level collision coverage for `configs/a0_default_outputs.yaml`, asserting `run_experiment` refuses an output directory containing enabled default artifacts, preserves sentinel artifact bytes, and does not write partial `manifest.yaml`, `metrics.csv`, or `summary.md` artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_run_api_omitted_outputs_refuses_collision_without_partial_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 79 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add manifest provenance for the baseline lobe label vocabulary and transition fields so lobe metrics are discoverable from `manifest.yaml`.
