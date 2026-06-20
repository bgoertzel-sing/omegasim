# OmegaSim Automation Status

This file is maintained by the OmegaSim research automation so progress can be checked from GitHub, including from a phone.

## Current Focus

Phase A0/A1: deterministic local simulator harness, static agents, task queue, bus graph, metrics/events output, and reproducibility tests.

## Latest Run

- Status: ok, 2026-06-20 A0/A1 omitted-output defaults CLI reproducibility coverage
- Changed: added CLI-level same-seed reproducibility coverage for `configs/a0_default_outputs.yaml`, asserting two `python -m ohdyn.run` invocations with the same seed write the full default artifact set and byte-identical `config.yaml`, `manifest.yaml`, `metrics.csv`, `events.csv`, and `summary.md` artifacts.
- Verified: `.venv-conda/bin/python -m pytest tests/test_run_harness.py::test_documented_cli_omitted_outputs_same_seed_reproduces_byte_identical_artifacts -q` passed with 1 test; `.venv-conda/bin/python -m pytest -q` passed with 77 tests; `.venv-conda/bin/python -m ruff check .` passed.
- Blockers: none.
- Next step: add CLI collision coverage for `configs/a0_default_outputs.yaml` to confirm omitted output defaults block reruns before writing partial artifacts.
